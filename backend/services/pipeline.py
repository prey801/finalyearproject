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
        self.rag_service = RAGService(device=device)

        if MOCK_MODELS:
            logger.info("MOCK_MODELS=True. Bypassing heavy PyTorch/YOLO model loading.")
            self.quality_model = None
            self.yolo_model = None
            self.seg_model = None
            self.classifier = None
            self.embedding_service = None
        else:
            from models.yolo.model import ObjectDetectionModel
            from models.classification.model import DiseaseClassificationModel
            from models.quality.model import QualityAssessmentModel
            from models.segmentation.model import SegmentationModel
            from backend.services.case_embeddings import CaseEmbeddingService

            try:
                self.quality_model = QualityAssessmentModel(device=device)
            except Exception as e:
                logger.warning("Failed to load QualityAssessmentModel (e.g., weights missing). Disabling quality check. Error: %s", e)
                self.quality_model = None

            try:
                self.yolo_model = ObjectDetectionModel(device=device)
            except Exception as e:
                logger.warning("Failed to load ObjectDetectionModel (e.g., weights missing/invalid). Disabling detection. Error: %s", e)
                self.yolo_model = None

            self.seg_model      = SegmentationModel(device=device)
            self.classifier     = DiseaseClassificationModel(device=device)

            try:
                self.embedding_service = CaseEmbeddingService(device=device)
            except Exception as e:
                logger.warning("Failed to load foundation models (BiomedCLIP/DINOv2). Disabling similarity search/typicality. Error: %s", e)
                self.embedding_service = None

            logger.info(
                "AnalysisPipeline initialised | device=%s | "
                "YOLO weights=%s | Swin weights loaded=%s",
                device,
                self.yolo_model.weights_path if self.yolo_model else "STUB (failed to load)",
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
        if self.quality_model is not None:
            quality_label = self.quality_model.predict(image)
            # QualityAssessmentModel returns a string: "Good", "Blurred", etc.
            quality = "good" if quality_label.lower() == "good" else "poor"
        else:
            quality = "good"

        # ── 2. Cell Detection (YOLOv11) ───────────────────────────────────────
        detections = self.yolo_model.predict(image) if self.yolo_model is not None else []

        infected_cells = 0
        total_cells    = 0

        # Class vocabulary isn't fixed — different training runs/datasets use
        # different label schemes (e.g. healthy_rbc/infected_rbc/parasite vs.
        # Parasitized/Uninfected vs. stage labels like ring/trophozoite/
        # schizont/gametocyte). Classify by keyword instead of an exact class
        # list so counting doesn't silently zero out on a scheme this code
        # wasn't hardcoded for. Every detection is one distinct cell — in the
        # actual trained checkpoint's vocabulary (confirmed empirically), a
        # stage label like "ring" bounds the infected cell itself rather than
        # overlaying a separately-boxed RBC, and there's no dataset convention
        # where that isn't the case, so there's no "standalone blob" to
        # exclude from the denominator.
        NEGATIVE_KEYWORDS = ("healthy", "uninfected", "normal", "background", "wbc", "leukocyte")
        POSITIVE_KEYWORDS = (
            "infected", "parasit", "ring", "troph", "schizont", "gameto",
            "malaria", "plasmodium",
        )

        for det in detections:
            cls = det.get("class", "").lower()
            total_cells += 1
            is_negative = any(kw in cls for kw in NEGATIVE_KEYWORDS)
            is_positive = any(kw in cls for kw in POSITIVE_KEYWORDS)
            if is_positive and not is_negative:
                infected_cells += 1

        if total_cells == 0:
            # No cells located — either YOLO is in stub mode (no weights) or
            # the detector genuinely found nothing on this image. Report the
            # real zero counts rather than fabricating a plausible-looking
            # "100 cells counted" figure — that would misrepresent a failed
            # detection as a clean negative result.
            logger.warning(
                "YOLO detected zero cells for sample %s — detection may have "
                "failed (check image quality/format/weights). Reporting "
                "actual zero counts instead of a fabricated total.",
                sample_id,
            )
            parasitemia = 0.0
        else:
            parasitemia = round((infected_cells / total_cells) * 100.0, 2)

        # Raw per-box detections, for the viewer to draw real bounding boxes
        # instead of the placeholder overlay it used to show.
        detections_out = [
            {
                "class_name": det.get("class", ""),
                "bbox": det.get("bbox", []),
                "confidence": round(float(det.get("confidence", 0.0)), 4),
            }
            for det in detections
        ]

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

        # ── 4.5. Explainability (GradCAM) ────────────────────────────────────
        heatmap_url = None
        if self.classifier and self.classifier.model:
            try:
                from models.explainability.engine import ExplainabilityEngine
                import numpy as np

                # For timm Swin models, the final layer block is typically used
                target_layers = [self.classifier.model.layers[-1]]

                # timm's Swin stages output (B, H, W, C) — channels-last, and
                # already spatial (no CLS token to drop, unlike ViT) — but
                # pytorch_grad_cam assumes (B, C, H, W). Without this, gradients/
                # activations get pooled along the wrong axis and the heatmap
                # doesn't correspond to real spatial regions of the image.
                def _swin_reshape_transform(tensor):
                    return tensor.permute(0, 3, 1, 2)

                explainer = ExplainabilityEngine(
                    model=self.classifier.model,
                    target_layers=target_layers,
                    use_cuda=self.device.startswith("cuda"),
                    reshape_transform=_swin_reshape_transform,
                )

                img_tensor = self.classifier.preprocess(image)
                # GradCAM's heatmap comes out at the model's input resolution
                # (224x224 — whatever the classifier resizes to), so the
                # overlay image must match that or show_cam_on_image's
                # elementwise blend fails with a broadcast shape mismatch
                # against the original upload's native resolution.
                original_img_np = np.array(image.convert("RGB").resize((224, 224))).astype(np.float32) / 255.0
                target_category = 1 if prediction == "malaria" else 0

                res = explainer.explain_prediction(
                    input_tensor=img_tensor,
                    original_image=original_img_np,
                    target_category=target_category,
                    save_dir=os.path.join(os.environ.get("PROJECT_DIR", "/app"), "heatmaps"),
                    filename_prefix=sample_id
                )
                if "gradcam_path" in res:
                    # e.g., /app/heatmaps/MAL-123_gradcam.png -> /heatmaps/MAL-123_gradcam.png
                    filename = os.path.basename(res["gradcam_path"])
                    heatmap_url = f"/heatmaps/{filename}"
            except Exception as e:
                logger.warning("Explainability engine failed (non-fatal): %s", e)

        # If heatmap was not generated, leave it as None

        # ── 5. Clinical Report Generation (RAG + LLM) ────────────────────────
        report = self.rag_service.generate_clinical_report(
            prediction, confidence * 100.0, parasitemia, total_cells=total_cells
        )

        # ── 5.5. Case Embeddings (BiomedCLIP similarity + DINOv2 typicality) ──
        image_typicality = None
        if self.embedding_service is not None:
            try:
                image_typicality = self.embedding_service.index_case(
                    image=image,
                    sample_id=sample_id,
                    patient_id=patient_id,
                    prediction=prediction,
                    parasitemia=parasitemia,
                )
            except Exception as e:
                logger.warning("Case embedding indexing failed (non-fatal): %s", e)

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
            detections=detections_out,
            heatmap_path=heatmap_url,
            report=report,
            review_required=True,  # always require human review — clinical safety requirement
            model_versions={
                "quality":        "efficientnet_b0",
                "detection":      "yolov11n_malaria",
                "segmentation":   "sam2_hiera_s",
                "classification": "swin_tiny_patch4_window7_224_malaria",
                "llm":            self.rag_service.llm.model_name or "stub",
            },
            image_typicality=image_typicality,
        )
