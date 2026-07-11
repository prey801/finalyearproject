import torch
import torch.nn.functional as F
import timm
from torchvision import transforms
from PIL import Image

from models.base import BaseModel

class DiseaseClassificationModel(BaseModel):
    """
    Swin Transformer Base model to determine infection status from an ROI.
    Input: RGB Image 224x224 (Region of Interest)
    Output: Dictionary {"prediction": "Malaria", "confidence": 0.98}
    Classes: Healthy, Malaria
    """

    def __init__(self, device='cpu'):
        self.device = device
        self.classes = ["Healthy", "Malaria"]
        self.model = None
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self.load_model()

    def load_model(self) -> None:
        # Load Swin Transformer Base
        self.model = timm.create_model('swin_base_patch4_window7_224', pretrained=True, num_classes=len(self.classes))
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
            "confidence": round(conf, 4)
        }
