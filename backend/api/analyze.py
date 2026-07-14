import io
import asyncio
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from PIL import Image
from backend.schemas.analysis import AnalysisResponse
from backend.services.pipeline import AnalysisPipeline
from backend.database.session import get_db
from backend.database.models import PredictionRecord, User
from sqlalchemy.orm import Session
from backend.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/analyze", tags=["analysis"])

# Initialize pipeline lazily or globally
# This holds model weights in memory.
pipeline = None

def get_pipeline():
    global pipeline
    if pipeline is None:
        pipeline = AnalysisPipeline()
    return pipeline

@router.post("/", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    specimen_type: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    try:
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")
        
    try:
        p = get_pipeline()
        result = await asyncio.to_thread(p.process_image, image, patient_id=patient_id, specimen_type=specimen_type)
        
        # Save to database
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
        
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
