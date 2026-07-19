import os
import io
from PIL import Image
from celery import Celery
from backend.services.pipeline import AnalysisPipeline
from backend.database.session import SessionLocal
from backend.database.models import PredictionRecord
import logging

try:
    import torch
    _torch_available = True
except ImportError:
    _torch_available = False

logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("medscope_worker", broker=REDIS_URL, backend=REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

pipeline = None

@celery_app.task(bind=True, name="process_analysis_task")
def process_analysis_task(self, filepath: str, patient_id: str, specimen_type: str, sample_id: str = None, user_id: int = None):
    global pipeline
    if pipeline is None:
        if _torch_available:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            device = "cpu"
        logger.info(f"Initializing AnalysisPipeline in Celery Worker on device={device}...")
        pipeline = AnalysisPipeline(device=device)

    logger.info(f"Processing image {filepath}")
    
    try:
        image = Image.open(filepath).convert("RGB")
    except Exception as e:
        logger.error(f"Failed to open image at {filepath}: {e}")
        return {"error": f"Failed to load image: {str(e)}"}

    try:
        # Run inference
        result = pipeline.process_image(
            image=image, 
            patient_id=patient_id, 
            specimen_type=specimen_type, 
            sample_id=sample_id
        )

        # Save to database
        db = SessionLocal()
        try:
            db_record = PredictionRecord(
                user_id=user_id,
                sample_id=result.sample_id,
                patient_id=result.patient_id,
                specimen_type=result.specimen_type,
                quality=result.quality,
                prediction=result.prediction,
                confidence=result.confidence,
                uncertainty=result.uncertainty,
                infected_cells=result.infected_cells,
                total_cells=result.total_cells,
                parasitemia=result.parasitemia,
                heatmap_path=result.heatmap_path,
                report=result.report,
                review_required=result.review_required,
                model_versions=result.model_versions
            )
            db.add(db_record)
            db.commit()
        except Exception as db_err:
            db.rollback()
            logger.error(f"Failed to save to database: {db_err}")
            return {"error": "Database error while saving results"}
        finally:
            db.close()

        # Clean up temporary file
        if os.path.exists(filepath):
            os.remove(filepath)

        return {
            "sample_id": result.sample_id,
            "status": "completed"
        }
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        logger.error(f"Pipeline failure: {e}")
        # If CUDA OOM, free VRAM and reset the pipeline so the next task
        # can re-initialise cleanly rather than inheriting a broken state.
        if _torch_available and torch.cuda.is_available():
            oom_keywords = ("out of memory", "cuda", "cudnn")
            if any(kw in str(e).lower() for kw in oom_keywords):
                logger.warning("CUDA OOM detected — clearing cache and resetting pipeline.")
                torch.cuda.empty_cache()
                pipeline = None
        return {"error": str(e)}
