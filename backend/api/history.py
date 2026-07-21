import os
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database.models import PredictionRecord, User as DBUser
from backend.schemas.analysis import AnalysisResponse, ReviewRequest, MetricsSummary, SimilarCase
from backend.auth.dependencies import get_current_active_user
from rag.vector_store.qdrant_client import QdrantVectorStore

router = APIRouter(prefix="", tags=["history"])

# Lazily-created — a lightweight Qdrant connection only, not the heavy
# BiomedCLIP/DINOv2 models themselves (those only run where new images get
# indexed, i.e. the Celery worker's AnalysisPipeline). Looking up an
# already-indexed case's stored vector never needs the models loaded.
_similarity_store = None

def _get_similarity_store() -> QdrantVectorStore:
    global _similarity_store
    if _similarity_store is None:
        _similarity_store = QdrantVectorStore(
            host=os.environ.get("QDRANT_HOST", "localhost"),
            port=int(os.environ.get("QDRANT_PORT", "6333")),
            collection_name="case_biomedclip",
            vector_size=512,
        )
    return _similarity_store

RANGE_DURATIONS = {
    "today": timedelta(days=1),
    "week": timedelta(days=7),
    "month": timedelta(days=30),
}

@router.get("/history", response_model=List[AnalysisResponse])
def get_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_active_user)):
    records = db.query(PredictionRecord).filter(PredictionRecord.user_id == current_user.id).offset(skip).limit(limit).all()
    return records

@router.get("/history/summary", response_model=MetricsSummary)
def get_metrics_summary(range: str = "today", db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_active_user)):
    """Aggregate KPIs for the dashboard's Key Metrics cards, with a
    period-over-period comparison against the immediately preceding window
    of equal length (e.g. 'today' compares to yesterday). 'all' has no
    prior window, so no change percentages are returned for it.
    """
    now = datetime.now(timezone.utc)
    duration = RANGE_DURATIONS.get(range)

    base_query = db.query(PredictionRecord).filter(PredictionRecord.user_id == current_user.id)

    if duration:
        period_start = now - duration
        current_q = base_query.filter(PredictionRecord.created_at >= period_start)
        prev_start = period_start - duration
        prev_q = base_query.filter(
            PredictionRecord.created_at >= prev_start,
            PredictionRecord.created_at < period_start,
        )
    else:
        current_q = base_query
        prev_q = None

    def _summarize(q):
        total = q.count()
        flagged = q.filter(PredictionRecord.review_required.is_(True)).count()
        avg_ms = q.with_entities(sa_func.avg(PredictionRecord.processing_time_ms)).scalar()
        return total, flagged, avg_ms

    total, flagged, avg_ms = _summarize(current_q)
    flagged_rate = (flagged / total * 100) if total else 0.0
    avg_s = (avg_ms / 1000) if avg_ms is not None else None

    images_change_pct = None
    processing_change_s = None
    if prev_q is not None:
        prev_total, _, prev_avg_ms = _summarize(prev_q)
        if prev_total:
            images_change_pct = (total - prev_total) / prev_total * 100
        if avg_ms is not None and prev_avg_ms is not None:
            processing_change_s = (avg_ms - prev_avg_ms) / 1000

    return MetricsSummary(
        images_analyzed=total,
        images_analyzed_change_pct=images_change_pct,
        flagged_abnormalities=flagged,
        flagged_rate_pct=round(flagged_rate, 1),
        avg_processing_time_s=avg_s,
        avg_processing_time_change_s=processing_change_s,
    )

@router.get("/history/{sample_id}", response_model=AnalysisResponse)
def get_prediction(sample_id: str, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_active_user)):
    record = db.query(PredictionRecord).filter(PredictionRecord.sample_id == sample_id, PredictionRecord.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return record

@router.get("/history/{sample_id}/similar", response_model=List[SimilarCase])
def get_similar_cases(sample_id: str, limit: int = 5, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_active_user)):
    """Visually similar past cases, via BiomedCLIP image embeddings indexed
    at analysis time. Powers the report panel's "Similar Cases" section and
    the Copilot's "Compare to this patient's history" prompt."""
    record = db.query(PredictionRecord).filter(PredictionRecord.sample_id == sample_id, PredictionRecord.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Prediction not found")

    store = _get_similarity_store()
    vector = store.retrieve_vector(sample_id)
    if vector is None:
        return []

    # +1 since the case being queried matches itself with score 1.0
    results = store.search(vector, limit=limit + 1)
    similar = [r for r in results if r["payload"].get("sample_id") != sample_id][:limit]

    return [
        SimilarCase(
            sample_id=r["payload"].get("sample_id", ""),
            patient_id=r["payload"].get("patient_id", ""),
            prediction=r["payload"].get("prediction", ""),
            parasitemia=r["payload"].get("parasitemia", 0.0),
            similarity=round(r["score"], 4),
        )
        for r in similar
    ]

@router.post("/review/{sample_id}")
def submit_review(sample_id: str, review: ReviewRequest, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_active_user)):
    record = db.query(PredictionRecord).filter(PredictionRecord.sample_id == sample_id, PredictionRecord.user_id == current_user.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Prediction not found")
        
    record.review_required = False
    db.commit()
    
    return {"message": "Review submitted successfully", "sample_id": sample_id, "status": review.review_status}
