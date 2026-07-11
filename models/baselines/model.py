import torch
import torch.nn.functional as F
import timm
from torchvision import transforms
from PIL import Image

from models.base import BaseModel

class BaselineModel(BaseModel):
    """
    Unified wrapper for classical CNN and ViT baseline benchmarks.
    Supports ResNet50, DenseNet121, EfficientNetV2-S, ConvNeXt Base, and ViT Base.
    Input: RGB Image 224x224
    Output: Dictionary {"prediction": "Class", "confidence": 0.9}
    """

    SUPPORTED_MODELS = {
        'resnet50': 'resnet50',
        'densenet121': 'densenet121',
        'efficientnetv2-s': 'tf_efficientnetv2_s',
        'convnext-base': 'convnext_base',
        'vit-base': 'vit_base_patch16_224'
    }

    def __init__(self, architecture: str = 'resnet50', num_classes: int = 2, device: str = 'cpu'):
        if architecture not in self.SUPPORTED_MODELS:
            raise ValueError(f"Architecture '{architecture}' not supported. Choose from {list(self.SUPPORTED_MODELS.keys())}")
            
        self.architecture = architecture
        self.timm_model_name = self.SUPPORTED_MODELS[architecture]
        self.num_classes = num_classes
        self.device = device
        # Using a generic 2-class setup as default (e.g., Healthy vs Malaria)
        self.classes = [f"Class_{i}" for i in range(num_classes)]
        self.model = None
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self.load_model()

    def load_model(self) -> None:
        self.model = timm.create_model(self.timm_model_name, pretrained=True, num_classes=self.num_classes)
        self.model.to(self.device)
        self.model.eval()

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        if image.mode != "RGB":
            image = image.convert("RGB")
        img_tensor = self.transform(image).unsqueeze(0)
        return img_tensor.to(self.device)

    def predict(self, image: Image.Image) -> dict:
        img_tensor = self.preprocess(image)
        with torch.no_grad():
            outputs = self.model(img_tensor)
            probs = F.softmax(outputs, dim=1)
            pred_idx = torch.argmax(probs, dim=1).item()
            conf = probs[0, pred_idx].item()
        
        return {
            "prediction": self.classes[pred_idx],
            "confidence": round(conf, 4),
            "architecture": self.architecture
        }
