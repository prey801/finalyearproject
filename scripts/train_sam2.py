"""
MedScope AI — SAM2 Fine-tuning Script
======================================

Fine-tunes the SAM2 mask decoder (+ prompt encoder) on the Roboflow malaria
blood-smear dataset using **bounding boxes as prompts**.

The image encoder (ViT backbone) is frozen to keep VRAM usage low and
training fast on a Colab T4.

Usage (Colab):
  python -m scripts.train_sam2 \\
    --data  data/raw/roboflow_malaria \\
    --base  sam2_hiera_small.pt \\
    --out   models/weights/sam2_malaria_finetuned.pt \\
    --epochs 10 --batch 4 --device cuda

The output checkpoint is a full SAM2 state-dict that can be loaded with
  build_sam2(config_path, checkpoint_path)
and is drop-in compatible with your existing SegmentationModel wrapper.
"""

import argparse
import os
import random
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="Fine-tune SAM2 mask decoder on malaria dataset")
    p.add_argument("--data",   type=str, default="data/raw/roboflow_malaria",
                   help="Path to Roboflow YOLO dataset root (contains train/images & train/labels)")
    p.add_argument("--base",   type=str, default="models/weights/sam2_hiera_small.pt",
                   help="Path to base SAM2 checkpoint (downloaded from Meta)")
    p.add_argument("--config", type=str, default="sam2_hiera_s.yaml",
                   help="SAM2 model config name (must match checkpoint)")
    p.add_argument("--out",    type=str, default="models/weights/sam2_malaria_finetuned.pt",
                   help="Output path for fine-tuned checkpoint")
    p.add_argument("--drive",  type=str, default="",
                   help="Optional: also copy checkpoint here (e.g. Google Drive path)")
    p.add_argument("--epochs", type=int, default=10)
    p.add_argument("--batch",  type=int, default=4)
    p.add_argument("--lr",     type=float, default=1e-4)
    p.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--workers",type=int, default=2)
    p.add_argument("--seed",   type=int, default=42)
    p.add_argument("--img-size", type=int, default=1024,
                   help="SAM2 expects 1024×1024 images")
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Dataset: Roboflow YOLO format → (image, boxes, binary_masks)
# ─────────────────────────────────────────────────────────────────────────────
class YOLOMalariaSegDataset(Dataset):
    """
    Reads a YOLO-format dataset (images/ + labels/ dirs) and returns:
      image:  (3, H, W) float32 tensor, values [0, 1]
      boxes:  (N, 4) float32 tensor [x1, y1, x2, y2] in absolute pixel coords
      masks:  (N, H, W) float32 binary masks derived from bounding boxes
              (the box interior = 1, outside = 0)

    Since YOLO labels are bounding boxes only (no polygon masks), we use the
    filled bounding-box rectangle as the training target mask.
    This is the standard approach when pixel annotations are unavailable.
    """

    IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

    def __init__(self, data_dir: Path, split: str = "train", img_size: int = 1024):
        self.img_size = img_size
        # Roboflow layout: {split}/images/ and {split}/labels/
        img_dir = data_dir / split / "images"
        lbl_dir = data_dir / split / "labels"

        if not img_dir.exists():
            # Some Roboflow exports use train/ valid/ test/ at the top level
            # Try alternate layout: images/train/ labels/train/
            img_dir = data_dir / "images" / split
            lbl_dir = data_dir / "labels" / split

        if not img_dir.exists():
            raise FileNotFoundError(
                f"Could not find images directory at {data_dir}/{split}/images "
                f"or {data_dir}/images/{split}"
            )

        self.samples = []
        for img_path in sorted(img_dir.iterdir()):
            if img_path.suffix.lower() not in self.IMG_EXTS:
                continue
            lbl_path = lbl_dir / (img_path.stem + ".txt")
            if lbl_path.exists():
                self.samples.append((img_path, lbl_path))

        if not self.samples:
            raise RuntimeError(f"No annotated images found in {img_dir}")

        print(f"  [{split}] {len(self.samples)} annotated images")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, lbl_path = self.samples[idx]

        # ── Load & resize image ───────────────────────────────────────────────
        img = Image.open(img_path).convert("RGB")
        orig_w, orig_h = img.size
        img = img.resize((self.img_size, self.img_size), Image.BILINEAR)
        img_tensor = torch.from_numpy(
            np.array(img, dtype=np.float32) / 255.0
        ).permute(2, 0, 1)  # (3, H, W)

        # ── Load YOLO annotations ─────────────────────────────────────────────
        # Format: class cx cy w h   (all normalized 0-1)
        boxes = []
        with open(lbl_path) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 5:
                    continue
                _, cx, cy, bw, bh = (float(v) for v in parts[:5])
                # Convert to absolute pixel coords in resized image
                x1 = (cx - bw / 2) * self.img_size
                y1 = (cy - bh / 2) * self.img_size
                x2 = (cx + bw / 2) * self.img_size
                y2 = (cy + bh / 2) * self.img_size
                # Clamp to image bounds
                x1, y1 = max(0.0, x1), max(0.0, y1)
                x2, y2 = min(float(self.img_size), x2), min(float(self.img_size), y2)
                if x2 > x1 and y2 > y1:
                    boxes.append([x1, y1, x2, y2])

        if not boxes:
            # Return a dummy full-image box if no annotations
            boxes = [[0.0, 0.0, float(self.img_size), float(self.img_size)]]

        boxes_tensor = torch.tensor(boxes, dtype=torch.float32)  # (N, 4)

        # ── Build binary masks from boxes (GT target for mask decoder) ────────
        masks = torch.zeros(
            (len(boxes), self.img_size, self.img_size), dtype=torch.float32
        )
        for i, (x1, y1, x2, y2) in enumerate(boxes):
            xi1, yi1 = int(round(x1)), int(round(y1))
            xi2, yi2 = int(round(x2)), int(round(y2))
            masks[i, yi1:yi2, xi1:xi2] = 1.0

        return img_tensor, boxes_tensor, masks


def collate_fn(batch):
    """Variable-length boxes/masks per image → keep as a list."""
    images, boxes_list, masks_list = zip(*batch)
    return torch.stack(images), list(boxes_list), list(masks_list)


# ─────────────────────────────────────────────────────────────────────────────
# Loss functions
# ─────────────────────────────────────────────────────────────────────────────
def focal_loss(pred: torch.Tensor, target: torch.Tensor,
               alpha: float = 0.25, gamma: float = 2.0) -> torch.Tensor:
    """Binary Focal Loss."""
    bce = F.binary_cross_entropy_with_logits(pred, target, reduction="none")
    p_t = torch.exp(-bce)
    loss = alpha * (1 - p_t) ** gamma * bce
    return loss.mean()


def dice_loss(pred: torch.Tensor, target: torch.Tensor, eps: float = 1e-6) -> torch.Tensor:
    """Soft Dice Loss (works on logits via sigmoid)."""
    p = torch.sigmoid(pred)
    inter = (p * target).sum(dim=(-2, -1))
    union = p.sum(dim=(-2, -1)) + target.sum(dim=(-2, -1))
    dice = (2.0 * inter + eps) / (union + eps)
    return (1.0 - dice).mean()


def segmentation_loss(pred_logits: torch.Tensor,
                      target_masks: torch.Tensor) -> torch.Tensor:
    return focal_loss(pred_logits, target_masks) + dice_loss(pred_logits, target_masks)


# ─────────────────────────────────────────────────────────────────────────────
# Training
# ─────────────────────────────────────────────────────────────────────────────
def train_one_epoch(model, predictor_cls, loader, optimizer, device, img_size):
    """
    SAM2 doesn't use a standard forward() call — we use SAM2ImagePredictor
    for image encoding, then directly call the mask decoder.
    """
    model.train()
    # Keep image encoder frozen (eval mode so BN stats don't update)
    model.image_encoder.eval()

    total_loss = 0.0
    n_batches  = 0

    for images, boxes_list, masks_list in tqdm(loader, desc="  train", leave=False):
        images = images.to(device)  # (B, 3, H, W) already 0-1

        batch_loss = torch.tensor(0.0, device=device, requires_grad=False)
        n_instances = 0

        for b_idx in range(images.shape[0]):
            img_np = (images[b_idx].permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8)
            boxes  = boxes_list[b_idx].to(device)   # (N, 4)
            gt_masks = masks_list[b_idx].to(device) # (N, H, W)

            if boxes.shape[0] == 0:
                continue

            # ── Encode image ──────────────────────────────────────────────────
            with torch.no_grad():
                from sam2.sam2_image_predictor import SAM2ImagePredictor
                # We re-use the model's image encoder directly
                # SAM2's image_encoder expects (1, 3, H, W) float [0,1]
                img_t = images[b_idx:b_idx+1]  # (1, 3, H, W)
                image_features = model.image_encoder(img_t)

            # ── Encode box prompts ────────────────────────────────────────────
            # SAM2 prompt_encoder expects boxes as (N, 4) in [0,1] or absolute
            # We pass absolute pixel coords normalized to [0, 1]
            boxes_norm = boxes / img_size  # normalize to [0,1]

            sparse_embeddings, dense_embeddings = model.sam_prompt_encoder(
                points=None,
                boxes=boxes.unsqueeze(1),  # (N, 1, 4)
                masks=None,
            )

            # ── Decode masks ──────────────────────────────────────────────────
            low_res_masks, iou_predictions, _, _ = model.sam_mask_decoder(
                image_embeddings=image_features["vision_features"],
                image_pe=model.sam_prompt_encoder.get_dense_pe(),
                sparse_prompt_embeddings=sparse_embeddings,
                dense_prompt_embeddings=dense_embeddings,
                multimask_output=False,
                repeat_image=False,
                high_res_features=image_features.get("backbone_fpn"),
            )
            # low_res_masks: (N, 1, H/4, W/4) logits

            # Upsample to original resolution
            pred_masks = F.interpolate(
                low_res_masks,
                size=(img_size, img_size),
                mode="bilinear",
                align_corners=False,
            ).squeeze(1)  # (N, H, W)

            loss = segmentation_loss(pred_masks, gt_masks)
            batch_loss = batch_loss + loss
            n_instances += 1

        if n_instances > 0:
            batch_loss = batch_loss / n_instances
            optimizer.zero_grad()
            batch_loss.backward()
            # Gradient clip to prevent instability
            torch.nn.utils.clip_grad_norm_(
                [p for p in model.parameters() if p.requires_grad], max_norm=1.0
            )
            optimizer.step()
            total_loss += batch_loss.item()
            n_batches  += 1

    return total_loss / max(n_batches, 1)


@torch.no_grad()
def validate(model, loader, device, img_size):
    model.eval()
    total_loss = 0.0
    n_batches  = 0

    for images, boxes_list, masks_list in tqdm(loader, desc="  val  ", leave=False):
        images = images.to(device)

        batch_loss  = torch.tensor(0.0, device=device)
        n_instances = 0

        for b_idx in range(images.shape[0]):
            boxes    = boxes_list[b_idx].to(device)
            gt_masks = masks_list[b_idx].to(device)
            if boxes.shape[0] == 0:
                continue

            img_t = images[b_idx:b_idx+1]
            image_features = model.image_encoder(img_t)

            sparse_embeddings, dense_embeddings = model.sam_prompt_encoder(
                points=None,
                boxes=boxes.unsqueeze(1),
                masks=None,
            )
            low_res_masks, iou_predictions, _, _ = model.sam_mask_decoder(
                image_embeddings=image_features["vision_features"],
                image_pe=model.sam_prompt_encoder.get_dense_pe(),
                sparse_prompt_embeddings=sparse_embeddings,
                dense_prompt_embeddings=dense_embeddings,
                multimask_output=False,
                repeat_image=False,
                high_res_features=image_features.get("backbone_fpn"),
            )
            pred_masks = F.interpolate(
                low_res_masks,
                size=(img_size, img_size),
                mode="bilinear",
                align_corners=False,
            ).squeeze(1)

            loss = segmentation_loss(pred_masks, gt_masks)
            batch_loss  = batch_loss + loss
            n_instances += 1

        if n_instances > 0:
            total_loss += (batch_loss / n_instances).item()
            n_batches  += 1

    return total_loss / max(n_batches, 1)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    args = parse_args()

    # ── Reproducibility ───────────────────────────────────────────────────────
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if args.device == "cuda":
        torch.cuda.manual_seed_all(args.seed)

    device = torch.device(args.device)
    print(f"\n{'='*60}")
    print(f"  SAM2 Fine-tuning for Malaria Segmentation")
    print(f"{'='*60}")
    print(f"  Device:     {device}")
    print(f"  Data dir:   {args.data}")
    print(f"  Base ckpt:  {args.base}")
    print(f"  Output:     {args.out}")
    print(f"  Epochs:     {args.epochs}")
    print(f"  Batch size: {args.batch}")
    print(f"  LR:         {args.lr}")
    print(f"{'='*60}\n")

    # ── Install SAM2 if needed ────────────────────────────────────────────────
    try:
        from sam2.build_sam import build_sam2
    except ImportError:
        print("SAM2 not installed. Installing from GitHub...")
        os.system(
            "pip install -q 'git+https://github.com/facebookresearch/sam2.git'"
        )
        from sam2.build_sam import build_sam2

    # ── Download base checkpoint if not present ───────────────────────────────
    base_ckpt = Path(args.base)
    if not base_ckpt.exists():
        print(f"Base checkpoint not found at {base_ckpt}. Downloading...")
        base_ckpt.parent.mkdir(parents=True, exist_ok=True)
        os.system(
            f"wget -q --show-progress "
            f"https://dl.fbaipublicfiles.com/segment_anything_2/072824/sam2_hiera_small.pt "
            f"-O {base_ckpt}"
        )
        print("Downloaded ✓")

    # ── Build model ───────────────────────────────────────────────────────────
    print("Loading base SAM2 model...")
    model = build_sam2(args.config, str(base_ckpt), device=device)
    model.to(device)

    # ── Freeze image encoder; train only mask decoder + prompt encoder ────────
    for param in model.image_encoder.parameters():
        param.requires_grad = False

    for param in model.sam_mask_decoder.parameters():
        param.requires_grad = True

    for param in model.sam_prompt_encoder.parameters():
        param.requires_grad = True

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total     = sum(p.numel() for p in model.parameters())
    print(f"Trainable parameters: {trainable:,} / {total:,} "
          f"({100*trainable/total:.1f}%)")

    # ── Datasets ──────────────────────────────────────────────────────────────
    data_dir = Path(args.data)
    print("\nBuilding datasets...")
    train_ds = YOLOMalariaSegDataset(data_dir, split="train", img_size=args.img_size)

    # Try 'valid' then 'val' for the validation split (Roboflow uses 'valid')
    val_split = "valid" if (data_dir / "valid" / "images").exists() else "val"
    try:
        val_ds = YOLOMalariaSegDataset(data_dir, split=val_split, img_size=args.img_size)
    except FileNotFoundError:
        print("  No validation split found — using 10% of training data.")
        n_val = max(1, len(train_ds) // 10)
        n_train = len(train_ds) - n_val
        train_ds, val_ds = torch.utils.data.random_split(
            train_ds, [n_train, n_val],
            generator=torch.Generator().manual_seed(args.seed)
        )

    train_loader = DataLoader(
        train_ds, batch_size=args.batch, shuffle=True,
        num_workers=args.workers, collate_fn=collate_fn, pin_memory=(device.type == "cuda")
    )
    val_loader = DataLoader(
        val_ds, batch_size=args.batch, shuffle=False,
        num_workers=args.workers, collate_fn=collate_fn, pin_memory=(device.type == "cuda")
    )

    # ── Optimizer & scheduler ─────────────────────────────────────────────────
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=args.lr,
        weight_decay=1e-4,
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=args.epochs, eta_min=args.lr * 0.01
    )

    # ── Training loop ─────────────────────────────────────────────────────────
    best_val_loss = float("inf")
    out_path      = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nStarting training for {args.epochs} epochs...\n")

    for epoch in range(1, args.epochs + 1):
        print(f"Epoch {epoch}/{args.epochs}")

        train_loss = train_one_epoch(
            model, None, train_loader, optimizer, device, args.img_size
        )
        val_loss = validate(model, val_loader, device, args.img_size)
        scheduler.step()

        lr_now = optimizer.param_groups[0]["lr"]
        print(f"  train_loss={train_loss:.4f}  val_loss={val_loss:.4f}  lr={lr_now:.2e}")

        # Save best checkpoint
        if val_loss < best_val_loss:
            best_val_loss = val_loss

            # SAM2 checkpoint: save full state_dict
            save_dict = {
                "epoch":          epoch,
                "model":          model.state_dict(),
                "val_loss":       val_loss,
                "config":         args.config,
            }
            torch.save(save_dict, str(out_path))
            print(f"  ✓ Best checkpoint saved → {out_path}  (val_loss={val_loss:.4f})")

            # Optionally copy to Drive
            if args.drive:
                drive_path = Path(args.drive) / out_path.name
                drive_path.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(str(out_path), str(drive_path))
                print(f"  ✓ Copied to Drive → {drive_path}")

    print(f"\n{'='*60}")
    print(f"  Training complete.")
    print(f"  Best val loss: {best_val_loss:.4f}")
    print(f"  Checkpoint:    {out_path}")
    print(f"{'='*60}\n")

    # ── Final smoke-test: load checkpoint back ────────────────────────────────
    print("Smoke-testing saved checkpoint...")
    ckpt = torch.load(str(out_path), map_location="cpu", weights_only=False)
    model_verify = build_sam2(args.config, str(base_ckpt), device="cpu")
    model_verify.load_state_dict(ckpt["model"])
    print(f"✓ Checkpoint loads cleanly (trained {ckpt['epoch']} epochs).\n")
    print("Done ✓")


if __name__ == "__main__":
    main()
