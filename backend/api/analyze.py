import os
import io
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from backend.schemas.analysis import AnalysisResponse
from backend.database.session import get_db
from backend.database.models import PredictionRecord, User
from sqlalchemy.orm import Session
from backend.auth.dependencies import get_current_active_user
from backend.worker import process_analysis_task, celery_app

router = APIRouter(prefix="/analyze", tags=["analysis"])

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def analyze_image(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    specimen_type: str = Form(...),
    current_user: User = Depends(get_current_active_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    try:
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
        
        # Magic byte check
        magic = contents[:4]
        if not (magic.startswith(b'\xff\xd8') or magic.startswith(b'\x89PNG') or magic.startswith(b'GIF8') or magic.startswith(b'BM') or magic.startswith(b'II*\x00') or magic.startswith(b'MM\x00*')):
            raise HTTPException(status_code=400, detail="Invalid image file format (magic byte check failed).")
        
        # Save to shared volume for Celery
        file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else "jpg"
        if file_ext not in {"jpg", "jpeg", "png", "tif", "tiff", "bmp", "gif"}:
            file_ext = "jpg"

        sample_id = f"MAL-{uuid.uuid4().hex[:6].upper()}"
        filepath = os.path.join(UPLOAD_DIR, f"{sample_id}.{file_ext}")
        
        with open(filepath, "wb") as f:
            f.write(contents)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")
        
    try:
        # Trigger Celery task
        task = process_analysis_task.delay(filepath, patient_id, specimen_type, sample_id, current_user.id)
        
        return {
            "task_id": task.id,
            "sample_id": sample_id,
            "status": "processing"
        }
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        raise HTTPException(status_code=500, detail=f"Failed to queue task: {str(e)}")

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    if task_result.state == 'PENDING':
        return {"status": "processing"}
    elif task_result.state == 'SUCCESS':
        res = task_result.result
        if res.get("error"):
            return {"status": "failed", "error": res["error"]}
        return {"status": "completed", "sample_id": res.get("sample_id")}
    elif task_result.state == 'FAILURE':
        return {"status": "failed", "error": str(task_result.info)}
    else:
        return {"status": task_result.state.lower()}

@router.get("/result/{sample_id}", response_model=AnalysisResponse)
async def get_analysis_result(
    sample_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    record = db.query(PredictionRecord).filter(PredictionRecord.sample_id == sample_id, PredictionRecord.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Result not found or still processing")
    return record
