import os
import logging
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from pathlib import Path

from models.base import BaseModel

logger = logging.getLogger(__name__)

# Canonical weight path — relative to project root.
_DEFAULT_WEIGHTS = Path("models/weights/swin_malaria_best.pth")
# Architecture must match training (swin_tiny was used in train_classification.py).
_ARCHITECTURE = "swin_tiny_patch4_window7_224"


class DiseaseClassificationModel(BaseModel):
    """
    Fine-tuned Swin Transformer (tiny) for malaria cell classification.

    Input:  RGB PIL Image (any size — resized internally to 224x224)
    Output: {"prediction": "Malaria"|"Healthy", "confidence": float 0-1}
    Classes: 0 = Healthy, 1 = Malaria

    Weight loading priority:
      1. SWIN_WEIGHTS_PATH environment variable
      2. models/weights/swin_malaria_best.pth  (canonical repo path)
      3. ImageNet pretrained weights only       (fallback, logs a warning)
    """

    CLASSES = ["Healthy", "Malaria"]

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.model = None
        self.weights_loaded = False
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])
        self.load_model()

    # ── BaseModel interface ───────────────────────────────────────────────────

    def load_model(self) -> None:
        import timm
        # Build the timm architecture first (always succeeds).
        self.model = timm.create_model(
            _ARCHITECTURE, pretrained=False, num_classes=len(self.CLASSES)
        )

        # Resolve weight path.
        weights_path = Path(
            os.environ.get("SWIN_WEIGHTS_PATH", str(_DEFAULT_WEIGHTS))
        )

        if weights_path.exists():
            try:
                state_dict = torch.load(
                    weights_path,
                    map_location=self.device,
                    weights_only=True,
                )
                self.model.load_state_dict(state_dict)
                self.weights_loaded = True
                logger.info(
                    "DiseaseClassificationModel: loaded fine-tuned weights "
                    "from %s", weights_path
                )
            except Exception as exc:
                logger.error(
                    "DiseaseClassificationModel: failed to load weights from "
                    "%s — falling back to ImageNet pretrained. Error: %s",
                    weights_path, exc,
                )
                # Re-create with pretrained ImageNet weights as a safe fallback.
                self.model = timm.create_model(
                    _ARCHITECTURE, pretrained=True, num_classes=len(self.CLASSES)
                )
        else:
            logger.warning(
                "DiseaseClassificationModel: fine-tuned weights not found at "
                "%s. Using ImageNet pretrained only — predictions will be "
                "unreliable. Set SWIN_WEIGHTS_PATH or place weights at %s.",
                weights_path, _DEFAULT_WEIGHTS,
            )
            # Fall back to ImageNet pretrained so the API remains functional.
            self.model = timm.create_model(
                _ARCHITECTURE, pretrained=True, num_classes=len(self.CLASSES)
            )

        self.model.to(self.device)
        self.model.eval()

    def preprocess(self, image: Image.Image) -> torch.Tensor:
        if image.mode != "RGB":
            image = image.convert("RGB")
        return self.transform(image).unsqueeze(0).to(self.device)

    def predict(self, image: Image.Image) -> dict:
        img_tensor = self.preprocess(image)
        with torch.no_grad():
            # autocast gives ~2x throughput on T4/A100 with no accuracy loss.
            with torch.amp.autocast(device_type=self.device if self.device.startswith("cuda") else "cpu", enabled=self.device.startswith("cuda")):
                logits = self.model(img_tensor)
            probs  = F.softmax(logits.float(), dim=1)  # softmax always in FP32
            pred_idx = torch.argmax(probs, dim=1).item()
            confidence = probs[0, pred_idx].item()

        return {
            "prediction":    self.CLASSES[pred_idx],
            "confidence":    round(confidence, 4),
            # Return both class probabilities for uncertainty computation.
            "probabilities": {
                cls: round(probs[0, i].item(), 4)
                for i, cls in enumerate(self.CLASSES)
            },
            "weights_loaded": self.weights_loaded,
        }
