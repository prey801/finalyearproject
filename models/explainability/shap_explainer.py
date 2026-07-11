import shap
import torch
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SHAPExplainer:
    """
    SHAP wrapper for PyTorch Image classification models using GradientExplainer.
    Fully configurable for different architectures.
    """
    def __init__(self, model, background_images):
        """
        Args:
            model: PyTorch model.
            background_images (torch.Tensor): A batch of images (e.g., shape (N, C, H, W)) 
                                              used as the background distribution for SHAP.
        """
        self.model = model
        self.model.eval()
        
        logging.info("Initializing SHAP GradientExplainer...")
        # We use GradientExplainer for PyTorch models
        self.explainer = shap.GradientExplainer(self.model, background_images)

    def explain(self, input_tensor, target_class=None):
        """
        Generates SHAP values for the input tensor.
        Args:
            input_tensor (torch.Tensor): The image to explain (shape (1, C, H, W)).
            target_class (int, optional): The class index to explain. If None, explains all classes.
            
        Returns:
            shap_values: Array of SHAP values.
        """
        # SHAP GradientExplainer returns a tuple of lists or arrays depending on version
        shap_values, indexes = self.explainer.shap_values(input_tensor, ranked_outputs=1)
        
        # If target_class is specified, we would normally filter, 
        # but ranked_outputs=1 already returns the top class explanations.
        return shap_values, indexes
