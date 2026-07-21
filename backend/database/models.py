from sqlalchemy import Column, String, Float, Integer, Boolean, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from .session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)

class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    sample_id = Column(String, unique=True, index=True, nullable=False)
    patient_id = Column(String, index=True, nullable=False)
    specimen_type = Column(String, nullable=False)
    quality = Column(String, nullable=False)
    prediction = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=True)
    infected_cells = Column(Integer, nullable=False)
    total_cells = Column(Integer, nullable=False)
    parasitemia = Column(Float, nullable=False)
    heatmap_path = Column(String, nullable=True)
    report = Column(Text, nullable=False)
    review_required = Column(Boolean, default=True)
    model_versions = Column(JSON, nullable=True)
    processing_time_ms = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
