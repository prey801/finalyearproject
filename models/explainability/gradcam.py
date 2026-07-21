import cv2
import numpy as np
import torch
from pytorch_grad_cam import GradCAM, GradCAMPlusPlus
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GradCAMExplainer:
    """
    Fully configurable GradCAM and GradCAM++ explainer.
    Allows specifying custom target layers for any CNN/Transformer architecture.
    """
    def __init__(self, model, target_layers, use_cuda=False, method="gradcam++", reshape_transform=None):
        """
        Args:
            model: PyTorch model.
            target_layers: List of target layers (e.g., [model.layer4[-1]]).
            use_cuda: Whether to use GPU.
            method: 'gradcam' or 'gradcam++'.
            reshape_transform: Optional callable converting a target layer's raw
                output into (B, C, H, W). Required for transformer backbones
                (e.g. Swin stages output (B, H, W, C)) — without it, pytorch_grad_cam
                pools gradients/activations along the wrong axis and produces a
                heatmap that doesn't correspond to real spatial regions.
        """
        self.model = model
        self.target_layers = target_layers
        self.use_cuda = use_cuda

        if method.lower() == "gradcam++":
            self.cam = GradCAMPlusPlus(model=model, target_layers=target_layers, reshape_transform=reshape_transform)
        else:
            self.cam = GradCAM(model=model, target_layers=target_layers, reshape_transform=reshape_transform)

    def generate_heatmap(self, input_tensor, target_category=None, original_image=None):
        """
        Generates the heatmap.
        Args:
            input_tensor (torch.Tensor): Preprocessed image tensor of shape (1, C, H, W).
            target_category (int, optional): The class index to explain. If None, uses the highest scoring category.
            original_image (np.ndarray, optional): The original image (normalized 0-1) to overlay the heatmap on.
        
        Returns:
            heatmap (np.ndarray): The raw grayscale heatmap.
            visualization (np.ndarray): The heatmap overlaid on the original image (if original_image provided).
        """
        targets = [ClassifierOutputTarget(target_category)] if target_category is not None else None
        
        # Generate the CAM
        grayscale_cam = self.cam(input_tensor=input_tensor, targets=targets)
        grayscale_cam = grayscale_cam[0, :] # Batch size 1
        
        visualization = None
        if original_image is not None:
            # Normalize original image if not already
            if original_image.max() > 1.0:
                original_image = original_image.astype(np.float32) / 255.0
            visualization = show_cam_on_image(original_image, grayscale_cam, use_rgb=True)
            
        return grayscale_cam, visualization
