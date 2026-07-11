import os
import argparse
import mlflow
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import timm

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from data.preprocess import get_transforms

class MalariaDataset(Dataset):
    def __init__(self, data_dir, split="train", transform=None):
        self.data_dir = Path(data_dir)
        self.split = split
        self.transform = transform
        
        # Simple loader assuming folders 'healthy' and 'malaria'
        self.classes = ['Healthy', 'Malaria']
        self.samples = []
        
        for idx, cls in enumerate(self.classes):
            cls_dir = self.data_dir / cls
            if cls_dir.exists():
                for img_path in cls_dir.glob("*.png"):
                    self.samples.append((img_path, idx))
                    
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        import numpy as np
        image = np.array(image)
        
        if self.transform:
            augmented = self.transform(image=image)
            image = augmented["image"]
            
        return image, label

def train_classification(data_dir, epochs=20, batch=32, device='cuda', model_name='swin_base_patch4_window7_224'):
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment("Classification_Swin")
    
    with mlflow.start_run():
        mlflow.log_params({"epochs": epochs, "batch": batch, "model": model_name, "device": device})
        
        train_transforms = get_transforms(split="train")
        train_dataset = MalariaDataset(data_dir=Path(data_dir)/"training"/"images", split="train", transform=train_transforms)
        train_loader = DataLoader(train_dataset, batch_size=batch, shuffle=True, num_workers=4)
        
        model = timm.create_model(model_name, pretrained=True, num_classes=2)
        model.to(device)
        
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.AdamW(model.parameters(), lr=1e-4)
        
        # Mixed Precision Scaler
        scaler = torch.cuda.amp.GradScaler()
        
        for epoch in range(epochs):
            model.train()
            running_loss = 0.0
            
            for inputs, labels in train_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                
                optimizer.zero_grad()
                
                # Forward pass with mixed precision
                with torch.cuda.amp.autocast():
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                    
                # Backward pass
                scaler.scale(loss).backward()
                scaler.step(optimizer)
                scaler.update()
                
                running_loss += loss.item()
                
            avg_loss = running_loss / len(train_loader)
            mlflow.log_metric("train_loss", avg_loss, step=epoch)
            print(f"Epoch {epoch+1}/{epochs} - Loss: {avg_loss:.4f}")
            
        # Save model
        os.makedirs("runs/classification", exist_ok=True)
        torch.save(model.state_dict(), "runs/classification/swin_malaria.pth")
        print("Training complete. Model saved in runs/classification/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, required=True, help='Path to data root directory')
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--batch', type=int, default=32)
    parser.add_argument('--device', type=str, default='cuda')
    
    args = parser.parse_args()
    
    train_classification(args.data_dir, epochs=args.epochs, batch=args.batch, device=args.device)
