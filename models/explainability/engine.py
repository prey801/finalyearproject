import torch
import numpy as np
import cv2
import logging
from pathlib import Path

from .gradcam import GradCAMExplainer
from .shap_explainer import SHAPExplainer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ExplainabilityEngine:
    """
    Unified engine to run explainability algorithms (GradCAM/SHAP) on model predictions.
    """
    def __init__(self, model, target_layers, background_images=None, use_cuda=False, reshape_transform=None):
        """
        Args:
            model: PyTorch model to explain.
            target_layers: List of target layers for GradCAM (e.g. [model.layer4[-1]]).
            background_images: Optional background tensor for SHAP initialization.
            use_cuda: Whether to use GPU.
            reshape_transform: Optional callable for transformer backbones — see
                GradCAMExplainer for details.
        """
        self.model = model
        self.use_cuda = use_cuda

        if self.use_cuda:
            self.model = self.model.cuda()
            if background_images is not None:
                background_images = background_images.cuda()

        self.gradcam = GradCAMExplainer(model, target_layers, use_cuda=use_cuda, reshape_transform=reshape_transform)
        self.shap_explainer = None
        
        if background_images is not None:
            self.shap_explainer = SHAPExplainer(model, background_images)

    def explain_prediction(self, input_tensor, original_image=None, target_category=None, save_dir=None, filename_prefix="explanation"):
        """
        Runs the explainability suite and optionally saves visual artifacts.
        
        Args:
            input_tensor (torch.Tensor): Preprocessed image tensor (1, C, H, W).
            original_image (np.ndarray): Original image array (H, W, C) scaled 0-1 for visualization overlay.
            target_category (int): Class index to explain.
            save_dir (str/Path): Directory to save output images.
            filename_prefix (str): Prefix for saved files.
            
        Returns:
            dict: Containing paths to saved artifacts or the raw matrices.
        """
        if self.use_cuda:
            input_tensor = input_tensor.cuda()

        results = {}
        
        # 1. GradCAM
        logging.info("Generating GradCAM++ heatmap...")
        raw_heatmap, cam_overlay = self.gradcam.generate_heatmap(
            input_tensor, 
            target_category=target_category, 
            original_image=original_image
        )
        
        if save_dir and cam_overlay is not None:
            save_path = Path(save_dir) / f"{filename_prefix}_gradcam.png"
            save_path.parent.mkdir(parents=True, exist_ok=True)
            # OpenCV expects BGR for saving
            cam_bgr = cv2.cvtColor(cam_overlay, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(save_path), cam_bgr)
            results["gradcam_path"] = str(save_path)
            logging.info(f"Saved GradCAM overlay to {save_path}")
        else:
            results["gradcam_heatmap"] = raw_heatmap
            results["gradcam_overlay"] = cam_overlay

        # 2. SHAP (if initialized)
        if self.shap_explainer is not None:
            logging.info("Generating SHAP feature attributions...")
            shap_vals, indexes = self.shap_explainer.explain(input_tensor)
            results["shap_values"] = shap_vals
            # SHAP saving is complex (often requires matplotlib), 
            # so we return the values for the frontend/API to process.
            
        return results
