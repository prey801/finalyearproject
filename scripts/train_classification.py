import os
import argparse
import mlflow
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import timm
import pandas as pd

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from data.preprocess import get_transforms

# Resolve project root once — used for safe, CWD-independent output paths.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent


class MalariaDataset(Dataset):
    """
    Loads images from metadata.csv which has columns: filename, label.
    Labels are 'Parasitized' or 'Uninfected' (NIH malaria dataset naming).
    Falls back gracefully if images are symlinks.
    """
    CLASS_MAP = {"Uninfected": 0, "Healthy": 0, "Parasitized": 1, "Malaria": 1}

    def __init__(self, images_dir: Path, metadata_csv: Path, transform=None):
        self.images_dir = Path(images_dir)
        self.transform = transform

        df = pd.read_csv(metadata_csv)

        # FIX #2: Validate every label strictly before training starts.
        # Using .get(..., 0) silently corrupted labels for unknown classes.
        unknown = set(df["label"].unique()) - set(self.CLASS_MAP.keys())
        if unknown:
            raise ValueError(
                f"metadata.csv contains unknown label(s): {unknown}. "
                f"Expected one of: {set(self.CLASS_MAP.keys())}"
            )

        # Keep only rows whose images actually exist on disk.
        self.samples = [
            (row["filename"], self.CLASS_MAP[row["label"]])
            for _, row in df.iterrows()
            if (self.images_dir / row["filename"]).exists()
        ]
        if not self.samples:
            raise RuntimeError(
                f"No images found in {images_dir}. "
                "Run 'python3 -m scripts.split_data' first."
            )
        print(f"Loaded {len(self.samples)} samples from {metadata_csv.name}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        filename, label = self.samples[idx]
        img_path = self.images_dir / filename
        image = Image.open(img_path).convert("RGB")

        # FIX #3: numpy import moved to module level — not repeated per sample.
        image = np.array(image)

        if self.transform:
            augmented = self.transform(image=image)
            image = augmented["image"]

        return image, label


def train_classification(
    data_dir: str,
    epochs: int = 10,
    batch: int = 16,
    device: str = "cpu",
    model_name: str = "resnet18",
):
    """
    Fine-tunes an image classification model on the NIH malaria cell dataset.

    Default model is resnet18 — fast and practical for CPU-only environments.
    Use model_name='swin_base_patch4_window7_224' for a larger Swin Transformer
    if a GPU is available.
    """
    data_root = Path(data_dir)
    train_images = data_root / "training" / "images"
    train_meta   = data_root / "training" / "metadata.csv"
    val_images   = data_root / "validation" / "images"
    val_meta     = data_root / "validation" / "metadata.csv"

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment("Classification_Malaria")

    # FIX #1: device_type for autocast must be "cuda" or "cpu" — never "cuda:0".
    # Stripping the index ensures torch.autocast accepts the string on multi-GPU machines.
    autocast_device_type = "cuda" if device.startswith("cuda") else "cpu"

    # pin_memory only helps when CUDA is actually available.
    _pin = torch.cuda.is_available()

    with mlflow.start_run():
        mlflow.log_params({
            "epochs":    epochs,
            "batch":     batch,
            "model":     model_name,
            "device":    device,
        })

        # --- Datasets & loaders ---
        train_transforms = get_transforms(split="train")
        val_transforms   = get_transforms(split="val")

        train_dataset = MalariaDataset(train_images, train_meta, transform=train_transforms)
        train_loader  = DataLoader(
            train_dataset, batch_size=batch, shuffle=True,
            num_workers=2, pin_memory=_pin,
        )

        # FIX #4: Validation loop added — critical for detecting overfitting.
        val_dataset = MalariaDataset(val_images, val_meta, transform=val_transforms)
        val_loader  = DataLoader(
            val_dataset, batch_size=batch, shuffle=False,
            num_workers=2, pin_memory=_pin,
        )

        # --- Model ---
        model = timm.create_model(model_name, pretrained=True, num_classes=2)
        model.to(device)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(model.parameters(), lr=1e-4)

        # Use GradScaler only when training on CUDA.
        use_amp = autocast_device_type == "cuda" and torch.cuda.is_available()
        scaler  = torch.amp.GradScaler("cuda", enabled=use_amp)

        best_val_loss = float("inf")

        for epoch in range(epochs):
            # ── Training phase ────────────────────────────────────────────────
            model.train()
            running_loss = 0.0

            for inputs, labels in train_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                optimizer.zero_grad()

                with torch.autocast(device_type=autocast_device_type, enabled=use_amp):
                    outputs = model(inputs)
                    loss    = criterion(outputs, labels)

                if use_amp:
                    scaler.scale(loss).backward()
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    loss.backward()
                    optimizer.step()

                running_loss += loss.item()

            avg_train_loss = running_loss / len(train_loader)
            mlflow.log_metric("train_loss", avg_train_loss, step=epoch)

            # ── Validation phase ──────────────────────────────────────────────
            model.eval()
            val_loss    = 0.0
            correct     = 0
            total       = 0

            with torch.no_grad():
                for inputs, labels in val_loader:
                    inputs, labels = inputs.to(device), labels.to(device)

                    with torch.autocast(device_type=autocast_device_type, enabled=use_amp):
                        outputs = model(inputs)
                        loss    = criterion(outputs, labels)

                    val_loss += loss.item()
                    preds     = outputs.argmax(dim=1)
                    correct  += (preds == labels).sum().item()
                    total    += labels.size(0)

            avg_val_loss = val_loss / len(val_loader)
            val_acc      = correct / total if total > 0 else 0.0

            mlflow.log_metric("val_loss",     avg_val_loss, step=epoch)
            mlflow.log_metric("val_accuracy", val_acc,      step=epoch)

            print(
                f"Epoch {epoch + 1}/{epochs} — "
                f"Train Loss: {avg_train_loss:.4f} | "
                f"Val Loss: {avg_val_loss:.4f} | "
                f"Val Acc: {val_acc:.4f}"
            )

            # Track best checkpoint by validation loss.
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss

        # FIX #5: Save path anchored to project root — not CWD-dependent.
        out_dir = _PROJECT_ROOT / "runs" / "classification"
        out_dir.mkdir(parents=True, exist_ok=True)
        weights_path = out_dir / f"{model_name}_malaria.pth"
        torch.save(model.state_dict(), weights_path)
        mlflow.log_artifact(str(weights_path))
        print(f"Training complete. Weights saved to {weights_path}")
        print(f"Best validation loss: {best_val_loss:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train malaria cell classification model")
    parser.add_argument("--data_dir", type=str, required=True,
                        help="Path to project data root (contains training/ and validation/)")
    parser.add_argument("--epochs", type=int, default=10,
                        help="Number of training epochs (default: 10 for CPU)")
    parser.add_argument("--batch",   type=int, default=16,
                        help="Batch size (default: 16 for CPU)")
    parser.add_argument("--device",  type=str, default="cpu",
                        help="Device: cpu or cuda (or cuda:0, cuda:1, …)")
    parser.add_argument("--model",   type=str, default="resnet18",
                        help="timm model name (default: resnet18)")

    args = parser.parse_args()
    train_classification(
        data_dir=args.data_dir,
        epochs=args.epochs,
        batch=args.batch,
        device=args.device,
        model_name=args.model,
    )
