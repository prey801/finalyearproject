import os
import shutil
import random
import logging
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from data.config import DataPaths, DatasetConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# FIX #11: Support both PNG and JPEG — the NIH dataset is PNG-primary but any
# converted copies (e.g. from data augmentation pipelines) would be silently
# skipped if we only glob *.png.
_IMAGE_EXTENSIONS = ("*.png", "*.jpg", "*.jpeg")

def split_nih_malaria():
    """
    Splits the raw NIH Malaria dataset into training, validation, and testing sets
    (70/15/15) and generates a metadata.csv for each split.
    """
    raw_dir = DataPaths.NIH_MALARIA_RAW

    if not raw_dir.exists() or not list(raw_dir.iterdir()):
        logging.error(f"Raw NIH data not found at {raw_dir}. Please download first.")
        return

    # Check if the extracted data is inside a subfolder "cell_images"
    cell_images_dir = raw_dir / "cell_images"
    if cell_images_dir.exists() and cell_images_dir.is_dir():
        base_search_dir = cell_images_dir
    else:
        base_search_dir = raw_dir

    classes = DatasetConfig.NIH_MALARIA_CLASSES

    all_files = []
    for class_name in classes:
        class_dir = base_search_dir / class_name
        if not class_dir.exists():
            continue
        # FIX #11: Glob for all supported image formats, not just .png.
        for ext in _IMAGE_EXTENSIONS:
            for f in class_dir.glob(ext):
                all_files.append((f, class_name))

    if not all_files:
        logging.error("No images found for NIH Malaria dataset.")
        return

    # Shuffle for random split
    random.seed(42)
    random.shuffle(all_files)

    total     = len(all_files)
    train_end = int(total * DatasetConfig.SPLIT_RATIOS["train"])
    val_end   = train_end + int(total * DatasetConfig.SPLIT_RATIOS["val"])

    splits = {
        "training":   all_files[:train_end],
        "validation": all_files[train_end:val_end],
        "testing":    all_files[val_end:]
    }

    dest_dirs = {
        "training":   DataPaths.TRAINING_DIR,
        "validation": DataPaths.VALIDATION_DIR,
        "testing":    DataPaths.TESTING_DIR,
    }

    logging.info(f"Total images: {total}")
    for split_name, files in splits.items():
        logging.info(f"Processing {split_name} split ({len(files)} images)...")
        dest_base   = dest_dirs[split_name]
        dest_images = dest_base / "images"
        dest_images.mkdir(parents=True, exist_ok=True)

        metadata = []
        for file_path, class_name in files:
            # Preserve original extension in the prefixed filename.
            new_filename = f"{class_name}_{file_path.name}"
            dest_path    = dest_images / new_filename

            # Create symlink instead of physical copying to save disk space.
            if not dest_path.exists():
                try:
                    dest_path.symlink_to(file_path.resolve())
                except Exception:
                    # Fallback to physical copy if symlinking fails (e.g. cross-device).
                    shutil.copy2(file_path, dest_path)

            metadata.append({"filename": new_filename, "label": class_name})

        # Save metadata.csv
        df = pd.DataFrame(metadata)
        df.to_csv(dest_base / "metadata.csv", index=False)
        logging.info(f"Saved {split_name} metadata to {dest_base / 'metadata.csv'}")


def organize_roboflow():
    """
    Roboflow usually downloads pre-split.
    This function ensures the data matches our directory structure.
    """
    raw_dir = DataPaths.ROBOFLOW_MALARIA_RAW
    if not raw_dir.exists() or not list(raw_dir.glob("data.yaml")):
        logging.warning("Roboflow data not found or data.yaml missing. Skipping Roboflow organize.")
        return

    logging.info("Roboflow data detected. Usually Roboflow structure is already compatible with YOLO.")
    # Here we could map train/valid/test from roboflow raw to our training/validation/testing
    # But since YOLOv11 uses data.yaml directly, we might just use the raw dir as-is or copy.
    # For now, we will simply point to it in the config or dataset loaders.


if __name__ == "__main__":
    split_nih_malaria()
    organize_roboflow()
