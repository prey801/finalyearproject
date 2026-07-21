import os
import logging
from typing import Any, Dict, List

from PIL import Image

from models.foundation.biomedclip import BiomedCLIPModel
from models.foundation.dinov2 import DINOv2Encoder
from rag.vector_store.qdrant_client import QdrantVectorStore

logger = logging.getLogger(__name__)


class CaseEmbeddingService:
    """
    Wires the two previously-unintegrated foundation models
    (models/foundation/biomedclip.py, models/foundation/dinov2.py) into two
    concrete, user-facing features:

      - Visual similarity search across past cases (BiomedCLIP image
        embeddings, stored per-case in Qdrant). Powers the "similar past
        cases" list on a report and the Copilot's "Compare to this
        patient's history" prompt.
      - Image typicality scoring (DINOv2 embeddings): how visually similar
        a new upload is to everything the system has processed before.
        This is an extra signal on top of the EfficientNet quality-check
        model — it can catch inputs the quality model wasn't trained to
        flag (wrong image type, an unrepresentative crop, etc.), which is
        exactly the kind of input mismatch that produced unreliable
        detection/classification results earlier.

    Both steps are best-effort: any failure here is logged and swallowed
    so a foundation-model hiccup never breaks the core analysis pipeline.
    """

    def __init__(self, device: str = "cpu"):
        qdrant_host = os.environ.get("QDRANT_HOST", "localhost")
        qdrant_port = int(os.environ.get("QDRANT_PORT", "6333"))

        self.biomedclip = BiomedCLIPModel(device=device)
        self.dinov2 = DINOv2Encoder(device=device)

        self.biomedclip_store = QdrantVectorStore(
            host=qdrant_host, port=qdrant_port,
            collection_name="case_biomedclip", vector_size=512,
        )
        self.dinov2_store = QdrantVectorStore(
            host=qdrant_host, port=qdrant_port,
            collection_name="case_dinov2", vector_size=384,
        )

    def index_case(
        self,
        image: Image.Image,
        sample_id: str,
        patient_id: str,
        prediction: str,
        parasitemia: float,
    ) -> float:
        """Embed and store this case in both collections. Returns an image
        typicality score in [0, 1] — the average cosine similarity to the
        5 nearest prior cases (1.0 if this is one of the first few cases
        ever indexed, since there's nothing yet to compare against)."""
        meta: Dict[str, Any] = {
            "sample_id": sample_id,
            "patient_id": patient_id,
            "prediction": prediction,
            "parasitemia": parasitemia,
        }

        typicality = 1.0
        try:
            dinov2_vec = self.dinov2.extract_features(image)[0]
            neighbors = self.dinov2_store.search(dinov2_vec, limit=5)
            if neighbors:
                scores = [n["score"] for n in neighbors]
                typicality = sum(scores) / len(scores)
            self.dinov2_store.insert([sample_id], [dinov2_vec], [meta], ids=[sample_id])
        except Exception as e:
            logger.warning("DINOv2 indexing failed (non-fatal): %s", e)

        try:
            biomedclip_vec = self.biomedclip.encode_image(image)[0]
            self.biomedclip_store.insert([sample_id], [biomedclip_vec], [meta], ids=[sample_id])
        except Exception as e:
            logger.warning("BiomedCLIP indexing failed (non-fatal): %s", e)

        return round(float(typicality), 4)

    def find_similar_cases(self, sample_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Return the nearest OTHER cases to the given (already-indexed)
        sample_id, by BiomedCLIP image similarity."""
        vec = self.biomedclip_store.retrieve_vector(sample_id)
        if vec is None:
            return []

        # +1 since the case will match itself with score 1.0
        results = self.biomedclip_store.search(vec, limit=limit + 1)
        similar = [r for r in results if r["payload"].get("sample_id") != sample_id]
        return similar[:limit]
