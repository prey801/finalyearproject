import os
import uuid
import logging
from PIL import Image

from backend.services.rag import RAGService
from backend.schemas.analysis import AnalysisResponse

logger = logging.getLogger(__name__)

MOCK_MODELS = os.getenv("MOCK_MODELS", "False").lower() in ("true", "1", "yes")

class AnalysisPipeline:
    """
    Full MedScope AI inference pipeline.

    Stage order:
      1. Quality assessment    (EfficientNet-B0)
      2. Cell detection        (YOLOv11 — trained on Roboflow malaria dataset)
      3. Segmentation          (SAM2 — bounding-box guided, optional)
      4. Disease classification(Swin Transformer — trained on NIH malaria dataset)
      5. Report generation     (RAG + LLM)

    All models load on CPU by default; set device='cuda' for GPU inference.
    """

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.rag_service = RAGService()

        if MOCK_MODELS:
            logger.info("MOCK_MODELS=True. Bypassing heavy PyTorch/YOLO model loading.")
            self.quality_model = None
            self.yolo_model = None
            self.seg_model = None
            self.classifier = None
        else:
            from models.yolo.model import ObjectDetectionModel
            from models.classification.model import DiseaseClassificationModel
            from models.quality.model import QualityAssessmentModel
            from models.segmentation.model import SegmentationModel

            self.quality_model  = QualityAssessmentModel(device=device)
            self.yolo_model     = ObjectDetectionModel(device=device)
            self.seg_model      = SegmentationModel(device=device)
            self.classifier     = DiseaseClassificationModel(device=device)

            logger.info(
                "AnalysisPipeline initialised | device=%s | "
                "YOLO weights=%s | Swin weights loaded=%s",
                device,
                self.yolo_model.weights_path,
                self.classifier.weights_loaded,
            )

    def process_image(
        self,
        image: Image.Image,
        patient_id: str,
        specimen_type: str,
        sample_id: str = None,
    ) -> AnalysisResponse:
        if not sample_id:
            sample_id = f"MAL-{uuid.uuid4().hex[:6].upper()}"

        if MOCK_MODELS:
            return AnalysisResponse(
                sample_id=sample_id,
                patient_id=patient_id,
                specimen_type=specimen_type,
                quality="good",
                prediction="malaria",
                confidence=95.5,
                uncertainty=2.0,
                infected_cells=15,
                total_cells=100,
                parasitemia=15.0,
                heatmap_path=f"/heatmaps/{sample_id}.png",
                report="**MOCK REPORT**\n\nThe sample indicates malaria infection (simulated).",
                review_required=True,
                model_versions={"mock": "true"}
            )

        # ── 1. Image Quality Check ────────────────────────────────────────────
        quality_label = self.quality_model.predict(image)
        # QualityAssessmentModel returns a string: "Good", "Blurred", etc.
        quality = "good" if quality_label.lower() == "good" else "poor"

        # ── 2. Cell Detection (YOLOv11) ───────────────────────────────────────
        detections = self.yolo_model.predict(image)

        infected_cells = 0
        total_cells    = 0

        for det in detections:
            cls = det.get("class", "")
            if "rbc" in cls or "parasite" in cls:
                total_cells += 1
            if "infected" in cls or "parasite" in cls:
                infected_cells += 1

        # Fallback when YOLO runs in stub mode (no weights available)
        if total_cells == 0:
            logger.warning(
                "YOLO returned no detections for sample %s — using fallback counts.",
                sample_id,
            )
            total_cells    = 100
            infected_cells = 0

        parasitemia = round((infected_cells / total_cells) * 100.0, 2)

        # ── 3. Segmentation (SAM2 — optional, bbox-guided) ────────────────────
        bboxes = [d["bbox"] for d in detections if d.get("bbox")]
        if bboxes:
            try:
                self.seg_model.predict((image, bboxes))
            except Exception as exc:
                logger.warning("Segmentation step failed (non-fatal): %s", exc)

        # ── 4. Disease Classification (Swin Transformer) ─────────────────────
        class_result = self.classifier.predict(image)
        swin_label   = class_result["prediction"]   # "Healthy" or "Malaria"
        confidence   = class_result["confidence"]   # 0.0 – 1.0

        # Primary prediction: Swin classifier is the authoritative signal.
        # YOLO parasitemia is a supporting metric, not the decision maker.
        prediction = swin_label.lower()             # "healthy" | "malaria"

        # Uncertainty: margin between the two class probabilities.
        # Small margin → high uncertainty. Formula: (1 - margin) * 100
        probs     = class_result.get("probabilities", {})
        p_malaria = probs.get("Malaria", confidence if prediction == "malaria" else 1 - confidence)
        p_healthy = probs.get("Healthy", 1 - p_malaria)
        margin    = abs(p_malaria - p_healthy)
        uncertainty = round((1.0 - margin) * 100.0, 2)

        # ── 5. Clinical Report Generation (RAG + LLM) ────────────────────────
        report = self.rag_service.generate_clinical_report(
            prediction, confidence * 100.0, parasitemia
        )

        # ── 6. Construct Response ─────────────────────────────────────────────
        return AnalysisResponse(
            sample_id=sample_id,
            patient_id=patient_id,
            specimen_type=specimen_type,
            quality=quality,
            prediction=prediction,
            confidence=round(confidence * 100.0, 2),
            uncertainty=uncertainty,
            infected_cells=infected_cells,
            total_cells=total_cells,
            parasitemia=parasitemia,
            heatmap_path=f"/heatmaps/{sample_id}.png",  # populated by explainability engine later
            report=report,
            review_required=True,  # always require human review — clinical safety requirement
            model_versions={
                "quality":        "efficientnet_b0",
                "detection":      "yolov11n_malaria",
                "segmentation":   "sam2_hiera_s",
                "classification": "swin_tiny_patch4_window7_224_malaria",
                "llm":            self.rag_service.llm.model_name,
            },
        )
