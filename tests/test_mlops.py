import pytest
import os
from unittest.mock import patch
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from mlops.config import MLOpsConfig
from mlops.tracker import ExperimentTracker

def test_mlops_config():
    """Verify that MLOps configurations load defaults properly."""
    assert "classification" in MLOpsConfig.EXPERIMENTS
    assert MLOpsConfig.MLFLOW_TRACKING_URI is not None

@patch("mlflow.start_run")
@patch("mlflow.log_params")
@patch("mlflow.log_metrics")
@patch("mlflow.end_run")
def test_experiment_tracker(mock_end, mock_log_metrics, mock_log_params, mock_start):
    """Verify ExperimentTracker wraps MLflow properly without crashing."""
    
    with ExperimentTracker(experiment_type="classification", run_name="test_run") as tracker:
        tracker.log_params({"learning_rate": 0.001})
        tracker.log_metrics({"accuracy": 0.95})
        
    mock_start.assert_called_once()
    mock_log_params.assert_called_once_with({"learning_rate": 0.001})
    mock_log_metrics.assert_called_once_with({"accuracy": 0.95}, step=None)
    mock_end.assert_called_once()
