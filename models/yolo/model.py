import os
import logging
from typing import List, Dict, Any
from PIL import Image

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
        # Fallback only — used if a loaded checkpoint has no embedded names
        # (shouldn't happen for a real Ultralytics .pt, but keeps stub/test
        # paths working). Real names always come from the checkpoint itself,
        # since that's what was actually in data.yaml at training time.
        self.classes = {0: "healthy_rbc", 1: "infected_rbc", 2: "parasite"}
        self.model = None
        self.is_custom = False
        # Ultralytics' own default (0.25) is tuned for general-purpose/COCO-scale
        # detectors. This checkpoint's real-world confidence runs much lower
        # (confirmed empirically: max ~0.21 on a genuine positive detection) —
        # at the 0.25 default every single detection gets filtered out, so
        # every analysis silently reports 0 cells / 0% parasitemia regardless
        # of what's actually in the image. Override via YOLO_CONF_THRESHOLD if
        # a re-trained/re-calibrated checkpoint needs a different value.
        self.conf_threshold = float(os.environ.get("YOLO_CONF_THRESHOLD", "0.1"))
        self.load_model()

    def load_model(self) -> None:
        from ultralytics import YOLO
        # Check if we are running in a test environment or custom weights exist.
        # `or` (not the `.get(key, default)` fallback arg) matters here: the Colab
        # notebook always *sets* YOLO_WEIGHTS_PATH, but to "" when it couldn't find
        # the weight file under models/weights/ — `.get(key, default)` only falls
        # back to default when the key is absent, so an explicit "" would otherwise
        # slip through as the (nonexistent) weights_path and silently stub out.
        self.weights_path = os.environ.get("YOLO_WEIGHTS_PATH") or "runs/detect/yolo11n_malaria/weights/best.pt"
        self.is_custom = os.path.exists(self.weights_path)

        # In a test mock context or if custom weights are found, load YOLO
        if self.is_custom or os.environ.get("TESTING") == "true":
            self.model = YOLO(self.weights_path if self.is_custom else "yolo11n.pt")
            self.model.to(self.device)
            # Use the class names actually embedded in the checkpoint (from
            # the dataset's data.yaml at training time) instead of the guessed
            # dict above — a mismatch here silently zeroed out every count,
            # since nothing downstream would match the wrong label strings.
            if getattr(self.model, "names", None):
                self.classes = self.model.names
                logging.info("YOLO class names loaded from checkpoint: %s", self.classes)
        else:
            # ERROR, not warning: this means every detection/parasitemia result
            # from here on is a silent, always-empty stub — worth surfacing loudly
            # rather than burying in Colab's scroll of INFO logs.
            logging.error(
                f"Custom YOLO weights not found at '{self.weights_path}' "
                f"(YOLO_WEIGHTS_PATH={os.environ.get('YOLO_WEIGHTS_PATH')!r}). "
                "Running in STUB mode: every analysis will report 0 detections and "
                "0% parasitemia. Check that YOLO_WEIGHT_FILE in the Colab config "
                "cell exactly matches the filename in DRIVE_WEIGHTS_DIR, and that "
                "cell 5 (Load Trained Weights from Drive) printed 'Copied: ...' for it."
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
        results = self.model(img, device=self.device, verbose=False, conf=self.conf_threshold)
        
        predictions = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                coords = box.xyxy[0]
                if hasattr(coords, 'tolist'):
                    x1, y1, x2, y2 = coords.tolist()
                else:
                    x1, y1, x2, y2 = coords
                c = box.conf[0]
                conf = float(c.item()) if hasattr(c, 'item') else float(c)
                cid = box.cls[0]
                cls_idx = int(cid.item()) if hasattr(cid, 'item') else int(cid)
                
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
