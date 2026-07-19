from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional
from enum import Enum

class SpecimenType(str, Enum):
    blood_smear = "Blood Smear"
    tissue_section = "Tissue Section"
    other = "Other"

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
    heatmap_path: Optional[str] = None
    report: str
    review_required: bool
    model_versions: Dict[str, str]

class ReviewRequest(BaseModel):
    review_status: str
    notes: Optional[str] = None
