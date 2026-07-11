import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Base data directory
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def setup_directories():
    """
    Sets up the directory structure for the datasets as per DATA_SPEC.md.
    """
    directories = [
        # Raw Data
        "raw/nih_malaria",
        "raw/roboflow_malaria",
        "raw/external",
        
        # Annotations
        "annotations/yolo",
        "annotations/coco",
        "annotations/masks",
        "annotations/reviews",
        
        # Processed Data
        "processed/resized",
        "processed/normalized",
        "processed/augmented",
        "processed/balanced",
        "processed/features",
        
        # Training Split
        "training/images",
        "training/labels",
        
        # Validation Split
        "validation/images",
        "validation/labels",
        
        # Testing Split
        "testing/images",
        "testing/labels",
        
        # Synthetic Data
        "synthetic/diffusion",
        "synthetic/gan",
        "synthetic/metadata",
    ]

    for d in directories:
        dir_path = DATA_DIR / d
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create a .gitkeep file so empty directories can be tracked by git
        gitkeep_path = dir_path / ".gitkeep"
        if not gitkeep_path.exists():
            gitkeep_path.touch()
            
        logging.info(f"Created directory: {dir_path}")
        
    logging.info("Dataset directory structure setup complete!")

if __name__ == "__main__":
    setup_directories()
