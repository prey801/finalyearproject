import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (e.g., MLFLOW_TRACKING_URI, WANDB_API_KEY)
load_dotenv()

class MLOpsConfig:
    """
    Central configuration for MLOps tracking (MLflow, W&B, DVC).
    """
    # MLflow settings
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    
    # Weights & Biases settings
    WANDB_API_KEY = os.getenv("WANDB_API_KEY")
    WANDB_PROJECT_NAME = "medscope-ai"

    # Define standard experiment names
    EXPERIMENTS = {
        "classification": "swin_malaria_classification",
        "detection": "yolo_malaria_detection",
        "bccd": "yolo_bccd_detection",
        "leukemia": "yolo_leukemia_detection",
        "segmentation": "sam2_cell_segmentation",
        "quality": "efficientnet_quality_assessment",
    }

    # Model Registry
    MODEL_REGISTRY_BASE = "medscope_registry_"
