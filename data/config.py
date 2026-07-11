from pathlib import Path

# Base data directory relative to this config file
DATA_DIR = Path(__file__).resolve().parent

class DataPaths:
    """
    Centralized configuration for dataset paths as specified in DATA_SPEC.md.
    """
    # Raw Data
    RAW_DIR = DATA_DIR / "raw"
    NIH_MALARIA_RAW = RAW_DIR / "nih_malaria"
    ROBOFLOW_MALARIA_RAW = RAW_DIR / "roboflow_malaria"
    ROBOFLOW_BCCD_RAW = RAW_DIR / "roboflow_bccd"
    ROBOFLOW_LEUKEMIA_RAW = RAW_DIR / "roboflow_leukemia"
    EXTERNAL_RAW = RAW_DIR / "external"

    # Annotations
    ANNOTATIONS_DIR = DATA_DIR / "annotations"
    YOLO_ANNOTATIONS = ANNOTATIONS_DIR / "yolo"
    COCO_ANNOTATIONS = ANNOTATIONS_DIR / "coco"
    MASKS_ANNOTATIONS = ANNOTATIONS_DIR / "masks"
    REVIEWS_ANNOTATIONS = ANNOTATIONS_DIR / "reviews"

    # Processed Data
    PROCESSED_DIR = DATA_DIR / "processed"
    RESIZED_PROCESSED = PROCESSED_DIR / "resized"
    NORMALIZED_PROCESSED = PROCESSED_DIR / "normalized"
    AUGMENTED_PROCESSED = PROCESSED_DIR / "augmented"
    BALANCED_PROCESSED = PROCESSED_DIR / "balanced"
    FEATURES_PROCESSED = PROCESSED_DIR / "features"

    # Training Split
    TRAINING_DIR = DATA_DIR / "training"
    TRAINING_IMAGES = TRAINING_DIR / "images"
    TRAINING_LABELS = TRAINING_DIR / "labels"

    # Validation Split
    VALIDATION_DIR = DATA_DIR / "validation"
    VALIDATION_IMAGES = VALIDATION_DIR / "images"
    VALIDATION_LABELS = VALIDATION_DIR / "labels"

    # Testing Split
    TESTING_DIR = DATA_DIR / "testing"
    TESTING_IMAGES = TESTING_DIR / "images"
    TESTING_LABELS = TESTING_DIR / "labels"

    # Synthetic Data
    SYNTHETIC_DIR = DATA_DIR / "synthetic"
    DIFFUSION_SYNTHETIC = SYNTHETIC_DIR / "diffusion"
    GAN_SYNTHETIC = SYNTHETIC_DIR / "gan"
    METADATA_SYNTHETIC = SYNTHETIC_DIR / "metadata"

class DatasetConfig:
    """
    Configuration regarding dataset metadata.
    """
    NIH_MALARIA_CLASSES = ["Parasitized", "Uninfected"]
    YOLO_CLASSES = {
        0: "Healthy RBC",
        1: "Infected RBC",
        2: "Parasite"
    }
    MASK_PIXEL_DEFINITIONS = {
        0: "Background",
        1: "Healthy RBC",
        2: "Infected RBC",
        3: "Parasite"
    }

    # Recommended Resize Configurations
    RESIZE_DIMS = [(224, 224), (384, 384), (640, 640)]

    # Standard Splits
    SPLIT_RATIOS = {
        "train": 0.70,
        "val": 0.15,
        "test": 0.15
    }

if __name__ == "__main__":
    print(f"Dataset root configured at: {DATA_DIR}")
    print(f"Raw NIH dataset should be located at: {DataPaths.NIH_MALARIA_RAW}")
