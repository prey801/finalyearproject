import pytest
import torch
import numpy as np
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.explainability.gradcam import GradCAMExplainer
from models.explainability.engine import ExplainabilityEngine

# Dummy PyTorch model for testing
import torch.nn as nn

class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(16 * 16 * 16, 2)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

def test_gradcam():
    model = SimpleCNN()
    model.eval()
    # Target the last conv layer
    target_layers = [model.features[-3]] 
    
    explainer = GradCAMExplainer(model, target_layers, use_cuda=False)
    
    # Dummy input tensor (Batch, Channels, Height, Width)
    dummy_input = torch.randn(1, 3, 32, 32)
    # Dummy original image
    dummy_image = np.random.rand(32, 32, 3).astype(np.float32)
    
    heatmap, overlay = explainer.generate_heatmap(dummy_input, target_category=0, original_image=dummy_image)
    
    assert heatmap is not None
    assert heatmap.shape == (32, 32)
    assert overlay is not None
    assert overlay.shape == (32, 32, 3)

def test_explainability_engine():
    model = SimpleCNN()
    model.eval()
    target_layers = [model.features[-3]]
    
    # We won't test SHAP extensively here because it requires a background dataset and is slow
    engine = ExplainabilityEngine(model, target_layers, use_cuda=False)
    
    dummy_input = torch.randn(1, 3, 32, 32)
    dummy_image = np.random.rand(32, 32, 3).astype(np.float32)
    
    results = engine.explain_prediction(dummy_input, original_image=dummy_image, target_category=1)
    
    assert "gradcam_heatmap" in results
    assert "gradcam_overlay" in results
