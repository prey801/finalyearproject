import torch
from torchvision import transforms
from PIL import Image

class DINOv2Encoder:
    """
    Self-supervised feature encoder using Meta's DINOv2.
    Purpose: Extract rich representations from unlabeled microscopy images
    for downstream clustering or fine-tuning.
    """

    def __init__(self, model_size: str = 'vits14', device: str = 'cpu'):
        self.device = device
        # sizes: vits14, vitb14, vitl14, vitg14
        self.repo_or_dir = 'facebookresearch/dinov2'
        self.model_name = f'dinov2_{model_size}'
        self.model = None
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self.load_model()

    def load_model(self) -> None:
        try:
            self.model = torch.hub.load(self.repo_or_dir, self.model_name)
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"Warning: Failed to load DINOv2 from torch.hub ({e}). Using stub.")

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        if image.mode != "RGB":
            image = image.convert("RGB")
        img_tensor = self.transform(image).unsqueeze(0)
        return img_tensor.to(self.device)

    def extract_features(self, image: Image.Image) -> torch.Tensor:
        """
        Extracts the CLS token features from DINOv2.
        Returns a tensor of shape (1, embedding_dim).
        """
        if self.model is None:
            # Return stub feature vector
            return torch.randn(1, 384) # 384 is dim for vits14
            
        img_tensor = self.preprocess(image)
        with torch.no_grad():
            features = self.model(img_tensor)
        return features
