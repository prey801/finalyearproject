from pydantic import BaseModel, ConfigDict, field_validator
from typing import Dict, Any, List, Optional
from enum import Enum

class SpecimenType(str, Enum):
    blood_smear = "Blood Smear"
    tissue_section = "Tissue Section"
    other = "Other"

class Detection(BaseModel):
    """A single YOLO detection box, in the original upload's pixel space."""
    class_name: str
    bbox: List[float]  # [x, y, width, height]
    confidence: float

class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    sample_id: str
    patient_id: str
    specimen_type: SpecimenType
    quality: str
    prediction: str
    confidence: float
    uncertainty: Optional[float] = None
    infected_cells: int
    total_cells: int
    parasitemia: float
    detections: List[Detection] = []
    heatmap_path: Optional[str] = None
    report: str
    review_required: bool
    model_versions: Dict[str, str]
    image_path: Optional[str] = None
    image_typicality: Optional[float] = None

    @field_validator("detections", mode="before")
    @classmethod
    def _null_detections_to_empty_list(cls, v):
        # Rows created before the `detections` column existed have it as
        # NULL in the DB — from_attributes passes that through as None,
        # which fails validation against a non-Optional list.
        return v or []

class ReviewRequest(BaseModel):
    review_status: str
    notes: Optional[str] = None

class SimilarCase(BaseModel):
    sample_id: str
    patient_id: str
    prediction: str
    parasitemia: float
    similarity: float

class MetricsSummary(BaseModel):
    images_analyzed: int
    images_analyzed_change_pct: Optional[float] = None
    flagged_abnormalities: int
    flagged_rate_pct: float
    avg_processing_time_s: Optional[float] = None
    avg_processing_time_change_s: Optional[float] = None
