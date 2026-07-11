import torch
from PIL import Image
try:
    import open_clip
except ImportError:
    open_clip = None

class BiomedCLIPModel:
    """
    Multimodal Foundation Model using BiomedCLIP.
    Purpose: Medical image-text embeddings for visual similarity search
    and multimodal retrieval.
    """

    def __init__(self, model_name: str = "hf-hub:microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224", device: str = 'cpu'):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.preprocess_img = None
        self.tokenizer = None
        self.load_model()

    def load_model(self) -> None:
        if open_clip is None:
            print("Warning: open_clip_torch not installed. BiomedCLIP using stub.")
            return
            
        try:
            self.model, _, self.preprocess_img = open_clip.create_model_and_transforms(self.model_name)
            self.tokenizer = open_clip.get_tokenizer(self.model_name)
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"Warning: Failed to load BiomedCLIP ({e}). Using stub.")

    def encode_image(self, image: Image.Image) -> torch.Tensor:
        """Returns normalized image embeddings."""
        if self.model is None or self.preprocess_img is None:
            return torch.randn(1, 512) # Stub dim
            
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        img_tensor = self.preprocess_img(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            image_features = self.model.encode_image(img_tensor)
            image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features

    def encode_text(self, text: str) -> torch.Tensor:
        """Returns normalized text embeddings."""
        if self.model is None or self.tokenizer is None:
            return torch.randn(1, 512) # Stub dim
            
        text_tensor = self.tokenizer([text]).to(self.device)
        with torch.no_grad():
            text_features = self.model.encode_text(text_tensor)
            text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features
