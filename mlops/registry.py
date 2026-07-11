import logging
import mlflow
from mlflow.tracking import MlflowClient

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from mlops.config import MLOpsConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ModelRegistry:
    """
    Handles registering and transitioning models between lifecycle stages.
    Stages: "None", "Staging", "Production", "Archived".
    """
    def __init__(self):
        mlflow.set_tracking_uri(MLOpsConfig.MLFLOW_TRACKING_URI)
        self.client = MlflowClient()

    def _get_registry_name(self, experiment_type: str) -> str:
        """Constructs the registry model name based on experiment type."""
        return f"{MLOpsConfig.MODEL_REGISTRY_BASE}{experiment_type}"

    def register_model(self, run_id: str, experiment_type: str, model_path: str = "model"):
        """
        Registers a model from a specific run to the Model Registry.
        """
        registry_name = self._get_registry_name(experiment_type)
        model_uri = f"runs:/{run_id}/{model_path}"
        
        logging.info(f"Registering model from run {run_id} as {registry_name}...")
        model_version = mlflow.register_model(model_uri, registry_name)
        logging.info(f"Model successfully registered. Version: {model_version.version}")
        
        return model_version

    def transition_model_stage(self, experiment_type: str, version: int, stage: str):
        """
        Transitions a model to a new stage (e.g., 'Staging' -> 'Production').
        """
        valid_stages = ["None", "Staging", "Production", "Archived"]
        if stage not in valid_stages:
            raise ValueError(f"Invalid stage. Must be one of {valid_stages}")

        registry_name = self._get_registry_name(experiment_type)
        
        logging.info(f"Transitioning {registry_name} v{version} to {stage}...")
        self.client.transition_model_version_stage(
            name=registry_name,
            version=version,
            stage=stage,
            archive_existing_versions=(stage == "Production")
        )
        logging.info(f"Transition complete.")

    def get_production_model_uri(self, experiment_type: str) -> str:
        """
        Retrieves the URI of the model currently in Production stage.
        Useful for the inference API to always load the latest production model.
        """
        registry_name = self._get_registry_name(experiment_type)
        
        # Search for production models
        latest_versions = self.client.get_latest_versions(registry_name, stages=["Production"])
        if not latest_versions:
            logging.warning(f"No Production model found for {registry_name}.")
            return None
            
        prod_model = latest_versions[0]
        model_uri = f"models:/{registry_name}/Production"
        logging.info(f"Found production model for {registry_name}: v{prod_model.version}")
        return model_uri

if __name__ == "__main__":
    # Example usage / health check
    registry = ModelRegistry()
    print("MLflow Tracking URI:", MLOpsConfig.MLFLOW_TRACKING_URI)
