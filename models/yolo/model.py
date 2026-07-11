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
        self.load_model()

    def load_model(self) -> None:
        # Load a pretrained YOLOv11 model (e.g. YOLOv11 Nano).
        # We assume ultralytics handles downloading the base weights if not present locally.
        # This acts as the scaffold until custom weights are trained.
        self.model = YOLO('yolo11n.pt')

    def preprocess(self, image: Image.Image) -> Image.Image:
        # ultralytics YOLO handles resizing and preprocessing internally.
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image

    def predict(self, image: Image.Image) -> List[Dict[str, Any]]:
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
                
                # Map generic COCO classes to our expected classes as a placeholder behavior,
                # or just return the index if out of bounds for our custom classes.
                class_name = self.classes.get(cls_idx, f"class_{cls_idx}")
                
                w = x2 - x1
                h = y2 - y1
                
                predictions.append({
                    "class": class_name,
                    "bbox": [x1, y1, w, h],
                    "confidence": conf
                })
        
        return predictions
