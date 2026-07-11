import os
import argparse
import mlflow
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
        # Keep only rows whose images actually exist
        self.samples = [
            (row["filename"], self.CLASS_MAP.get(row["label"], 0))
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

        import numpy as np
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
    train_meta = data_root / "training" / "metadata.csv"

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment("Classification_Malaria")

    with mlflow.start_run():
        mlflow.log_params({
            "epochs": epochs,
            "batch": batch,
            "model": model_name,
            "device": device,
        })

        train_transforms = get_transforms(split="train")
        train_dataset = MalariaDataset(train_images, train_meta, transform=train_transforms)
        train_loader = DataLoader(
            train_dataset, batch_size=batch, shuffle=True, num_workers=2, pin_memory=False
        )

        model = timm.create_model(model_name, pretrained=True, num_classes=2)
        model.to(device)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(model.parameters(), lr=1e-4)

        # Use GradScaler only when training on CUDA
        use_amp = device != "cpu" and torch.cuda.is_available()
        scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

        for epoch in range(epochs):
            model.train()
            running_loss = 0.0

            for inputs, labels in train_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                optimizer.zero_grad()

                with torch.autocast(device_type=device if device != "cpu" else "cpu", enabled=use_amp):
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)

                if use_amp:
                    scaler.scale(loss).backward()
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    loss.backward()
                    optimizer.step()

                running_loss += loss.item()

            avg_loss = running_loss / len(train_loader)
            mlflow.log_metric("train_loss", avg_loss, step=epoch)
            print(f"Epoch {epoch + 1}/{epochs} — Loss: {avg_loss:.4f}")

        # Save model weights
        out_dir = Path("runs/classification")
        out_dir.mkdir(parents=True, exist_ok=True)
        weights_path = out_dir / f"{model_name}_malaria.pth"
        torch.save(model.state_dict(), weights_path)
        mlflow.log_artifact(str(weights_path))
        print(f"Training complete. Weights saved to {weights_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train malaria cell classification model")
    parser.add_argument("--data_dir", type=str, required=True, help="Path to project data root (contains training/)")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs (default: 10 for CPU)")
    parser.add_argument("--batch", type=int, default=16, help="Batch size (default: 16 for CPU)")
    parser.add_argument("--device", type=str, default="cpu", help="Device: cpu or cuda")
    parser.add_argument("--model", type=str, default="resnet18", help="timm model name (default: resnet18)")

    args = parser.parse_args()
    train_classification(
        data_dir=args.data_dir,
        epochs=args.epochs,
        batch=args.batch,
        device=args.device,
        model_name=args.model,
    )
