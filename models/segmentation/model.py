from typing import List, Dict, Any, Tuple
import torch
import numpy as np
from PIL import Image

# Using documented SAM2 imports. If the environment uses a different package structure,
# this import may need to be adjusted (e.g. from sam2.build_sam import build_sam2)
try:
    from sam2.build_sam import build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor
except ImportError:
    SAM2ImagePredictor = None

from models.base import BaseModel

class SegmentationModel(BaseModel):
    """
    SAM2 model to extract exact parasite and cell boundaries based on YOLO bounding boxes.
    Input: Tuple(Image, List of Bboxes [[x, y, w, h]])
    Output: List of pixel masks (as numpy arrays)
    """

    def __init__(self, checkpoint_path: str = "sam2_hiera_small.pt", config_path: str = "sam2_hiera_s.yaml", device='cpu'):
        self.device = device
        self.checkpoint_path = checkpoint_path
        self.config_path = config_path
        self.predictor = None
        self.load_model()

    def load_model(self) -> None:
        if SAM2ImagePredictor is None:
            print("Warning: sam2 package not found. Using stub implementation.")
            return

        # Initialize SAM2 Predictor with documented weights
        try:
            sam2_model = build_sam2(self.config_path, self.checkpoint_path, device=self.device)
            self.predictor = SAM2ImagePredictor(sam2_model)
        except Exception as e:
            print(f"Warning: Failed to load SAM2 model ({e}). Using stub implementation.")

    def preprocess(self, inputs: Tuple[Image.Image, List[List[float]]]) -> Tuple[np.ndarray, np.ndarray]:
        image, bboxes = inputs
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        img_np = np.array(image)
        
        # Convert [x, y, w, h] to [x1, y1, x2, y2] for SAM
        box_prompts = []
        for box in bboxes:
            x, y, w, h = box
            box_prompts.append([x, y, x + w, y + h])
            
        return img_np, np.array(box_prompts)

    def predict(self, inputs: Tuple[Image.Image, List[List[float]]]) -> List[np.ndarray]:
        img_np, box_prompts = self.preprocess(inputs)
        
        if self.predictor is None or len(box_prompts) == 0:
            # Stub implementation: return empty masks for each box
            return [np.zeros((img_np.shape[0], img_np.shape[1]), dtype=bool) for _ in box_prompts]

        self.predictor.set_image(img_np)
        
        masks, scores, logits = self.predictor.predict(
            box=box_prompts,
            multimask_output=False
        )
        
        # masks shape is usually (N, 1, H, W). We return a list of (H, W) arrays.
        result_masks = []
        for i in range(masks.shape[0]):
            result_masks.append(masks[i, 0] > 0.0) # Convert to boolean mask
            
        return result_masks
