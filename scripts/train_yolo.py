import os
import argparse
import mlflow
from ultralytics import YOLO

def train_yolo(data_yaml, epochs=100, batch=16, imgsz=640, device='cuda', project='medscope_yolo', name='yolo11n_malaria'):
    """
    Fine-tunes the YOLOv11 model on the malaria dataset using GPU.
    """
    # Initialize MLflow tracking
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment("YOLO_Object_Detection")

    # Load base model
    model = YOLO('yolo11n.pt')
    
    with mlflow.start_run():
        # Log parameters
        mlflow.log_params({
            "epochs": epochs,
            "batch_size": batch,
            "imgsz": imgsz,
            "model": "yolo11n",
            "device": device
        })
        
        # Train model
        results = model.train(
            data=data_yaml,
            epochs=epochs,
            batch=batch,
            imgsz=imgsz,
            device=device,
            project=project,
            name=name
        )
        
        print("Training complete. Model saved in runs/detect/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, required=True, help='Path to data.yaml')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--batch', type=int, default=16)
    parser.add_argument('--device', type=str, default='cuda')
    
    args = parser.parse_args()
    
    train_yolo(args.data, epochs=args.epochs, batch=args.batch, device=args.device)
