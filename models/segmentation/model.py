from typing import List, Dict, Any, Tuple
import torch
import numpy as np
from PIL import Image

# SAM2 packages will be imported lazily inside load_model

from models.base import BaseModel

class SegmentationModel(BaseModel):
    """
    SAM2 model to extract exact parasite and cell boundaries based on YOLO bounding boxes.
    Input: Tuple(Image, List of Bboxes [[x, y, w, h]])
    Output: List of pixel masks (as numpy arrays)
    """

    def __init__(self, checkpoint_path: str = None, config_path: str = "sam2_hiera_s.yaml", device='cpu'):
        import os
        self.device = device
        self.checkpoint_path = checkpoint_path or os.environ.get("SAM2_WEIGHTS_PATH", "sam2_hiera_small.pt")
        self.config_path = config_path
        self.predictor = None
        self.load_model()

    def load_model(self) -> None:
        try:
            from sam2.build_sam import build_sam2
            from sam2.sam2_image_predictor import SAM2ImagePredictor
        except ImportError:
            SAM2ImagePredictor = None

        if SAM2ImagePredictor is None:
            print("Warning: sam2 package not found. Using stub implementation.")
            return

        try:
            import torch
            ckpt_path = self.checkpoint_path

            # Detect whether this is a fine-tuned checkpoint from train_sam2.py
            # (which saves {'model': state_dict, 'epoch': ..., 'config': ...})
            # vs the raw Meta checkpoint (flat state dict / pickle).
            raw = torch.load(ckpt_path, map_location="cpu", weights_only=False)
            is_finetuned = isinstance(raw, dict) and "model" in raw and "epoch" in raw

            if is_finetuned:
                # Build model from base architecture first, then load fine-tuned weights
                config_from_ckpt = raw.get("config", self.config_path)
                # We still need the base checkpoint for architecture init;
                # use base path derived from fine-tuned path (strip suffix, try base name)
                import os
                base_candidates = [
                    os.path.join(os.path.dirname(ckpt_path), "sam2_hiera_small.pt"),
                    os.path.join(os.path.dirname(ckpt_path), "sam2_hiera_large.pt"),
                    "sam2_hiera_small.pt",
                ]
                base_path = next((p for p in base_candidates if os.path.exists(p)), ckpt_path)
                sam2_model = build_sam2(config_from_ckpt, base_path, device=self.device)
                sam2_model.load_state_dict(raw["model"], strict=False)
                print(f"Loaded fine-tuned SAM2 checkpoint (epoch {raw['epoch']}) ✓")
            else:
                # Standard Meta pre-trained checkpoint
                sam2_model = build_sam2(self.config_path, ckpt_path, device=self.device)

            sam2_model.eval()  # Ensure inference mode — SAM2 doesn't set this automatically
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
        
        import torch
        with torch.no_grad():
            masks, scores, logits = self.predictor.predict(
                box=box_prompts,
                multimask_output=False
            )
        
        # masks shape is usually (N, 1, H, W). We return a list of (H, W) arrays.
        result_masks = []
        for i in range(masks.shape[0]):
            result_masks.append(masks[i, 0] > 0.0) # Convert to boolean mask
            
        return result_masks
