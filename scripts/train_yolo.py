import os
import argparse
import mlflow
import torch  # FIX #8: torch was never imported; needed for device detection and result logging.
from ultralytics import YOLO


def train_yolo(
    data_yaml: str,
    epochs: int = 100,
    batch: int = 16,
    imgsz: int = 640,
    # FIX #8: Default was 'cuda', which crashes on CPU-only machines.
    # Detect at call time so the default is always safe.
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
    project: str = "medscope_yolo",
    name: str = "yolo11n_malaria",
):
    """
    Fine-tunes the YOLOv11 model on the malaria dataset.
    Falls back to CPU automatically when CUDA is not available.
    """
    # Initialize MLflow tracking
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment("YOLO_Object_Detection")

    # Load base model
    model = YOLO("yolo11n.pt")

    with mlflow.start_run():
        mlflow.log_params({
            "epochs":     epochs,
            "batch_size": batch,
            "imgsz":      imgsz,
            "model":      "yolo11n",
            "device":     device,
        })

        # Train model
        results = model.train(
            data=data_yaml,
            epochs=epochs,
            batch=batch,
            imgsz=imgsz,
            device=device,
            project=project,
            name=name,
        )

        # FIX #7: results was discarded — key metrics were never logged to MLflow.
        # ultralytics stores final metrics in results.results_dict.
        if results is not None and hasattr(results, "results_dict"):
            metrics = results.results_dict
            # Log whichever standard YOLO metrics are present.
            for key in ("metrics/mAP50(B)", "metrics/mAP50-95(B)",
                        "metrics/precision(B)", "metrics/recall(B)"):
                if key in metrics:
                    # Use a cleaner MLflow key (strip special chars).
                    mlflow_key = key.replace("/", "_").replace("(", "_").replace(")", "")
                    mlflow.log_metric(mlflow_key, metrics[key])

        print(f"Training complete. Model saved in {project}/{name}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLOv11 malaria detection model")
    parser.add_argument("--data",   type=str, required=True, help="Path to data.yaml")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch",  type=int, default=16)
    parser.add_argument("--device", type=str,
                        default="cuda" if torch.cuda.is_available() else "cpu",
                        help="Device: cpu or cuda (default: auto-detect)")

    args = parser.parse_args()

    train_yolo(args.data, epochs=args.epochs, batch=args.batch, device=args.device)
