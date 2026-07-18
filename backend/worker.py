import os
import io
from PIL import Image
from celery import Celery
from backend.services.pipeline import AnalysisPipeline
from backend.database.session import SessionLocal
from backend.database.models import PredictionRecord
import logging

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
def process_analysis_task(self, filepath: str, patient_id: str, specimen_type: str, sample_id: str = None):
    global pipeline
    if pipeline is None:
        logger.info("Initializing AnalysisPipeline in Celery Worker...")
        pipeline = AnalysisPipeline()

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
        logger.error(f"Pipeline failure: {e}")
        return {"error": str(e)}
