from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database.models import PredictionRecord, User as DBUser
from backend.schemas.analysis import AnalysisResponse, ReviewRequest
from backend.auth.dependencies import get_current_active_user

router = APIRouter(prefix="", tags=["history"])

@router.get("/history", response_model=List[AnalysisResponse])
def get_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_active_user)):
    records = db.query(PredictionRecord).offset(skip).limit(limit).all()
    return records

@router.get("/history/{sample_id}", response_model=AnalysisResponse)
def get_prediction(sample_id: str, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_active_user)):
    record = db.query(PredictionRecord).filter(PredictionRecord.sample_id == sample_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return record

@router.post("/review/{sample_id}")
def submit_review(sample_id: str, review: ReviewRequest, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_active_user)):
    record = db.query(PredictionRecord).filter(PredictionRecord.sample_id == sample_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Prediction not found")
        
    record.review_required = False
    db.commit()
    
    return {"message": "Review submitted successfully", "sample_id": sample_id, "status": review.review_status}
