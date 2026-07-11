import os
import logging
from typing import List, Dict, Any
from PIL import Image
from ultralytics import YOLO

from models.base import BaseModel

class ObjectDetectionModel(BaseModel):
    """
    YOLOv11 model to locate cells and parasites.
    Input: Image (internally resized to 640x640)
    Output: List of dicts [{"class": "parasite", "bbox": [100, 120, 40, 40], "confidence": 0.95}]
    Classes: healthy_rbc, infected_rbc, parasite
    """

    def __init__(self, device='cpu'):
        self.device = device
        self.classes = {0: "healthy_rbc", 1: "infected_rbc", 2: "parasite"}
        self.model = None
        self.is_custom = False
        self.load_model()

    def load_model(self) -> None:
        # Check if we are running in a test environment or custom weights exist
        self.weights_path = os.environ.get("YOLO_WEIGHTS_PATH", "models/yolo/best.pt")
        self.is_custom = os.path.exists(self.weights_path)
        
        # In a test mock context or if custom weights are found, load YOLO
        if self.is_custom or os.environ.get("TESTING") == "true":
            self.model = YOLO(self.weights_path if self.is_custom else "yolo11n.pt")
        else:
            logging.warning(
                f"Custom YOLO weights not found at {self.weights_path}. "
                "Running in STUB mode (returns empty detections to prevent misclassifying COCO classes as blood cells)."
            )
            self.model = None

    def preprocess(self, image: Image.Image) -> Image.Image:
        # ultralytics YOLO handles resizing and preprocessing internally.
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image

    def predict(self, image: Image.Image) -> List[Dict[str, Any]]:
        if self.model is None:
            return []
            
        img = self.preprocess(image)
        # Run inference
        results = self.model(img, device=self.device, verbose=False)
        
        predictions = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                cls_idx = int(box.cls[0].item())
                
                # Map class index to class name
                class_name = self.classes.get(cls_idx, f"class_{cls_idx}")
                
                w = x2 - x1
                h = y2 - y1
                
                predictions.append({
                    "class": class_name,
                    "bbox": [x1, y1, w, h],
                    "confidence": conf
                })
        
        return predictions
