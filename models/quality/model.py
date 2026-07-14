import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np

from models.base import BaseModel

class QualityAssessmentModel(BaseModel):
    """
    EfficientNet-B0 model to reject poor quality microscope images.
    Input: RGB Image 224x224
    Output: String (Good, Blurred, Overexposed, Underexposed, Poor Staining)
    """

    def __init__(self, device='cpu'):
        self.device = device
        self.classes = ["Good", "Blurred", "Overexposed", "Underexposed", "Poor Staining"]
        self.model = None
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self.load_model()

    def load_model(self) -> None:
        import timm
        # Load a pretrained EfficientNet-B0. 
        # For now, we use standard ImageNet weights, adjusting the head for 5 classes.
        self.model = timm.create_model('efficientnet_b0', pretrained=True, num_classes=len(self.classes))
        self.model.to(self.device)
        self.model.eval()

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        if image.mode != "RGB":
            image = image.convert("RGB")
        img_tensor = self.transform(image).unsqueeze(0)
        return img_tensor.to(self.device)

    def predict(self, image: Image.Image) -> str:
        img_tensor = self.preprocess(image)
        with torch.no_grad():
            outputs = self.model(img_tensor)
            probs = F.softmax(outputs, dim=1)
            pred_idx = torch.argmax(probs, dim=1).item()
        
        return self.classes[pred_idx]
