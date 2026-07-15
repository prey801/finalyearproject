import os
import argparse
import cv2

# ── Thread-safety: must be set before any other import touches OpenCV/OMP ──────
cv2.setNumThreads(0)
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import mlflow
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import OneCycleLR
from torch.utils.data import DataLoader, Dataset
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

    Perf notes:
      - cv2.imread (IMREAD_COLOR) is 3-5× faster than PIL for JPEG/PNG decoding.
      - __init__ uses vectorised pandas ops instead of iterrows() — O(N) not O(N²).
    """
    CLASS_MAP = {"Uninfected": 0, "Healthy": 0, "Parasitized": 1, "Malaria": 1}

    def __init__(self, images_dir: Path, metadata_csv: Path, transform=None):
        self.images_dir = Path(images_dir)
        self.transform = transform

        df = pd.read_csv(metadata_csv)

        # Validate every label strictly before training starts.
        unknown = set(df["label"].unique()) - set(self.CLASS_MAP.keys())
        if unknown:
            raise ValueError(
                f"metadata.csv contains unknown label(s): {unknown}. "
                f"Expected one of: {set(self.CLASS_MAP.keys())}"
            )

        # Vectorised: map labels, build full paths, filter existing — no iterrows().
        df["_label_int"] = df["label"].map(self.CLASS_MAP)
        df["_path"]      = df["filename"].apply(lambda f: self.images_dir / f)
        df = df[df["_path"].apply(lambda p: p.exists())].reset_index(drop=True)

        self.filenames = df["filename"].tolist()
        self.labels    = df["_label_int"].tolist()

        if not self.filenames:
            raise RuntimeError(
                f"No images found in {images_dir}. "
                "Run 'python3 -m scripts.split_data' first."
            )
        print(f"Loaded {len(self.filenames)} samples from {metadata_csv.name}")

    def __len__(self):
        return len(self.filenames)

    def __getitem__(self, idx):
        img_path = self.images_dir / self.filenames[idx]
        label    = self.labels[idx]

        # cv2.imread is substantially faster than PIL for JPEG decoding.
        image = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
        if image is None:
            raise RuntimeError(f"cv2 could not read image: {img_path}")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        if self.transform:
            augmented = self.transform(image=image)
            image = augmented["image"]

        return image, label


def train_classification(
    data_dir: str,
    epochs: int = 10,
    batch: int = 64,
    device: str = "cuda",
    model_name: str = "swin_tiny_patch4_window7_224",
    lr: float = 2e-4,
    image_size: int = 224,
    compile_model: bool = False,
    num_workers: int = -1,         # -1 = auto-detect
):
    """
    Fine-tunes a Swin Transformer (or any timm model) on the NIH malaria cell dataset.

    GPU throughput optimisations applied:
      - cv2 image decoding (3-5× faster than PIL)
      - Vectorised dataset __init__ (no iterrows)
      - cudnn.benchmark=True for fixed image sizes
      - channels_last memory format (~10% free on Ampere/Turing)
      - DataLoader: auto num_workers, persistent_workers, prefetch_factor=2
      - zero_grad(set_to_none=True) — skips zeroing memory
      - OneCycleLR scheduler — cosine warmup + decay per batch
      - torch.compile() opt-in (PyTorch >= 2.0, requires Triton on GPU)
      - Best checkpoint saved at lowest val loss (not just end of training)
      - Mixed precision (AMP) with GradScaler on CUDA
    """
    data_root = Path(data_dir)
    train_images = data_root / "training"   / "images"
    train_meta   = data_root / "training"   / "metadata.csv"
    val_images   = data_root / "validation" / "images"
    val_meta     = data_root / "validation" / "metadata.csv"

    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment("Classification_Malaria")

    # device_type for autocast must be "cuda" or "cpu" — never "cuda:0".
    autocast_device_type = "cuda" if device.startswith("cuda") else "cpu"

    # pin_memory only helps when CUDA is actually available.
    _cuda = torch.cuda.is_available()
    _pin  = _cuda

    # cuDNN benchmark: for fixed input sizes, finds the fastest convolution algo.
    # Free ~5-10% throughput gain with zero code changes.
    if _cuda:
        torch.backends.cudnn.benchmark = True

    # ── DataLoader workers ────────────────────────────────────────────────────
    # Auto-detect: cap at 4 to stay within Colab RAM limits; respect explicit arg.
    if num_workers < 0:
        _workers = min(os.cpu_count() or 2, 4)
    else:
        _workers = num_workers
    _persistent = _workers > 0
    # prefetch_factor=2 (not 4) — 4 workers × 4 prefetch × batch≈64 images burns RAM fast.
    _prefetch   = 2 if _workers > 0 else None
    print(f"DataLoader: num_workers={_workers}, persistent={_persistent}, "
          f"prefetch_factor={_prefetch}")

    with mlflow.start_run():
        mlflow.log_params({
            "epochs":       epochs,
            "batch":        batch,
            "model":        model_name,
            "device":       device,
            "lr":           lr,
            "image_size":   image_size,
            "compile":      compile_model,
            "num_workers":  _workers,
        })

        # ── Datasets & loaders ────────────────────────────────────────────────
        train_transforms = get_transforms(split="train",  image_size=image_size)
        val_transforms   = get_transforms(split="val",    image_size=image_size)

        train_dataset = MalariaDataset(train_images, train_meta, transform=train_transforms)
        train_loader  = DataLoader(
            train_dataset,
            batch_size=batch,
            shuffle=True,
            num_workers=_workers,
            pin_memory=_pin,
            persistent_workers=_persistent,
            prefetch_factor=_prefetch,
        )

        val_dataset = MalariaDataset(val_images, val_meta, transform=val_transforms)
        val_loader  = DataLoader(
            val_dataset,
            batch_size=batch,
            shuffle=False,
            num_workers=_workers,
            pin_memory=_pin,
            persistent_workers=_persistent,
            prefetch_factor=_prefetch,
        )

        # ── Model ─────────────────────────────────────────────────────────────
        model = timm.create_model(model_name, pretrained=True, num_classes=2)

        # channels_last: stores activations in NHWC order instead of NCHW.
        # Swin processes patches so this gives ~10% free throughput on Turing/Ampere.
        if _cuda:
            model = model.to(memory_format=torch.channels_last)
        model.to(device)

        # torch.compile() gives ~20-30% throughput improvement on PyTorch >= 2.0.
        # Requires Triton on GPU (available on Colab T4/A100).
        if compile_model:
            if hasattr(torch, "compile"):
                print("Applying torch.compile() — first epoch will be slower (tracing).")
                model = torch.compile(model)
            else:
                print("torch.compile() not available (PyTorch < 2.0) — skipping.")

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)

        # OneCycleLR: cosine warmup for first 30% of steps, then cosine decay.
        # Steps per epoch = number of train batches; scheduler is stepped per batch.
        scheduler = OneCycleLR(
            optimizer,
            max_lr=lr,
            steps_per_epoch=len(train_loader),
            epochs=epochs,
            pct_start=0.3,
            anneal_strategy="cos",
        )

        # Use GradScaler only when training on CUDA.
        use_amp = autocast_device_type == "cuda" and torch.cuda.is_available()
        scaler  = torch.amp.GradScaler("cuda", enabled=use_amp)

        best_val_loss = float("inf")

        # Paths for best and final checkpoints.
        out_dir = _PROJECT_ROOT / "runs" / "classification"
        out_dir.mkdir(parents=True, exist_ok=True)
        best_weights_path  = out_dir / f"{model_name}_malaria_best.pth"
        final_weights_path = out_dir / f"{model_name}_malaria.pth"

        for epoch in range(epochs):
            # ── Training phase ─────────────────────────────────────────────────
            model.train()
            running_loss = 0.0

            for inputs, labels in train_loader:
                # channels_last contiguous on-device for consistent memory layout.
                inputs = inputs.to(device, non_blocking=True, memory_format=torch.channels_last)
                labels = labels.to(device, non_blocking=True)

                # set_to_none=True skips the zero-fill, saving memory bandwidth.
                optimizer.zero_grad(set_to_none=True)

                with torch.autocast(device_type=autocast_device_type, enabled=use_amp):
                    outputs = model(inputs)
                    loss    = criterion(outputs, labels)

                if use_amp:
                    scaler.scale(loss).backward()
                    # Gradient clipping — important for Swin stability.
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                    optimizer.step()

                # Step LR scheduler every batch (OneCycleLR is per-step).
                scheduler.step()

                running_loss += loss.item()

            avg_train_loss = running_loss / len(train_loader)
            current_lr     = scheduler.get_last_lr()[0]
            mlflow.log_metric("train_loss", avg_train_loss, step=epoch)
            mlflow.log_metric("lr",         current_lr,     step=epoch)

            # ── Validation phase ───────────────────────────────────────────────
            model.eval()
            val_loss = 0.0
            correct  = 0
            total    = 0

            with torch.no_grad():
                for inputs, labels in val_loader:
                    inputs, labels = inputs.to(device, non_blocking=True), labels.to(device, non_blocking=True)

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
                f"Val Acc: {val_acc:.4f} | "
                f"LR: {current_lr:.2e}"
            )

            # Save best checkpoint at the epoch with lowest validation loss.
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                # Unwrap compiled model before saving so weights are portable.
                state = (model._orig_mod if hasattr(model, "_orig_mod") else model).state_dict()
                torch.save(state, best_weights_path)
                print(f"  ✓ New best checkpoint saved (val_loss={best_val_loss:.4f})")

        # Save final weights regardless.
        state = (model._orig_mod if hasattr(model, "_orig_mod") else model).state_dict()
        torch.save(state, final_weights_path)
        mlflow.log_artifact(str(best_weights_path))
        mlflow.log_artifact(str(final_weights_path))

        print(f"\nTraining complete.")
        print(f"  Best checkpoint: {best_weights_path}  (val_loss={best_val_loss:.4f})")
        print(f"  Final weights:   {final_weights_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train malaria cell classification model")
    parser.add_argument("--data_dir",    type=str,   required=True,
                        help="Path to project data root (contains training/ and validation/)")
    parser.add_argument("--epochs",      type=int,   default=20,
                        help="Number of training epochs (default: 20)")
    parser.add_argument("--batch",       type=int,   default=64,
                        help="Batch size (default: 64; T4 GPU can handle 64-128 for Swin-tiny)")
    parser.add_argument("--device",      type=str,   default="cuda",
                        help="Device: cpu | cuda | cuda:0 | cuda:1 …")
    parser.add_argument("--model",       type=str,   default="swin_tiny_patch4_window7_224",
                        help="timm model name (default: swin_tiny_patch4_window7_224)")
    parser.add_argument("--lr",          type=float, default=2e-4,
                        help="Peak learning rate for OneCycleLR (default: 2e-4)")
    parser.add_argument("--image_size",  type=int,   default=224,
                        help="Input image size in pixels (default: 224)")
    parser.add_argument("--compile",     action="store_true", default=False,
                        help="Apply torch.compile() for ~20-30%% extra throughput "
                             "(requires PyTorch >= 2.0 + Triton; first epoch is slow)")
    parser.add_argument("--num_workers", type=int,   default=-1,
                        help="DataLoader workers (-1 = auto, up to 8)")

    args = parser.parse_args()
    train_classification(
        data_dir=args.data_dir,
        epochs=args.epochs,
        batch=args.batch,
        device=args.device,
        model_name=args.model,
        lr=args.lr,
        image_size=args.image_size,
        compile_model=args.compile,
        num_workers=args.num_workers,
    )
