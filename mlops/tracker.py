import os
import mlflow
import logging
from typing import Dict, Any, Optional

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from mlops.config import MLOpsConfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ExperimentTracker:
    """
    Unified experiment tracking wrapper for MLflow and Weights & Biases.
    """
    def __init__(self, experiment_type: str, run_name: Optional[str] = None):
        """
        Args:
            experiment_type: One of 'classification', 'detection', 'segmentation', 'quality'.
            run_name: Custom name for this training run.
        """
        if experiment_type not in MLOpsConfig.EXPERIMENTS:
            raise ValueError(f"Unknown experiment type: {experiment_type}")

        self.experiment_name = MLOpsConfig.EXPERIMENTS[experiment_type]
        self.run_name = run_name
        self.active_run = None
        self.use_wandb = bool(MLOpsConfig.WANDB_API_KEY)
        
        # Setup MLflow
        mlflow.set_tracking_uri(MLOpsConfig.MLFLOW_TRACKING_URI)
        mlflow.set_experiment(self.experiment_name)
        
        # Setup W&B if available
        if self.use_wandb:
            try:
                import wandb
                self.wandb_run = wandb.init(
                    project=MLOpsConfig.WANDB_PROJECT_NAME,
                    group=self.experiment_name,
                    name=self.run_name
                )
                logging.info("Weights & Biases initialized.")
            except ImportError:
                logging.warning("WANDB_API_KEY is set, but wandb package is not installed.")
                self.use_wandb = False

    def start_run(self):
        """Starts the MLflow tracking run."""
        self.active_run = mlflow.start_run(run_name=self.run_name)
        logging.info(f"Started MLflow run: {self.active_run.info.run_id}")
        return self.active_run

    def log_params(self, params: Dict[str, Any]):
        """Logs hyperparameters."""
        if self.active_run:
            mlflow.log_params(params)
        if self.use_wandb:
            import wandb
            wandb.config.update(params)

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Logs performance metrics (loss, accuracy, parasitemia error)."""
        if self.active_run:
            mlflow.log_metrics(metrics, step=step)
        if self.use_wandb:
            import wandb
            wandb.log(metrics, step=step)

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        """Logs local files as artifacts (heatmaps, config files, sample masks)."""
        if self.active_run:
            mlflow.log_artifact(local_path, artifact_path)
        if self.use_wandb:
            import wandb
            wandb.save(local_path, base_path=os.path.dirname(local_path))

    def end_run(self):
        """Ends the active tracking run."""
        if self.active_run:
            mlflow.end_run()
        if self.use_wandb:
            import wandb
            wandb.finish()
        logging.info("Tracking run ended.")

    def __enter__(self):
        self.start_run()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_run()
