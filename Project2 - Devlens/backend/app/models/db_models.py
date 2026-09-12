import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    role = Column(String(20), default="developer")
    created_at = Column(DateTime, default=utc_now)

class IssueDB(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    steps_to_reproduce = Column(Text, nullable=True)
    expected_behavior = Column(Text, nullable=True)
    actual_behavior = Column(Text, nullable=True)
    environment = Column(String(100), nullable=True)
    version = Column(String(50), nullable=True)
    logs = Column(Text, nullable=True)

    predicted_category = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    is_low_confidence = Column(Boolean, default=False, index=True)
    quality_score = Column(Integer, nullable=False, default=0)
    priority_recommendation = Column(String(50), nullable=True, index=True)
    team_recommendation = Column(String(50), nullable=True, index=True)
    model_version = Column(String(50), default="v1.0.0")

    status = Column(String(20), default="open", index=True)
    created_at = Column(DateTime, default=utc_now, index=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    predictions = relationship("PredictionDB", back_populates="issue", cascade="all, delete-orphan")
    feedback = relationship("FeedbackDB", back_populates="issue", cascade="all, delete-orphan")

class PredictionDB(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=True)
    model_version = Column(String(50), nullable=False)
    predicted_label = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    top_predictions = Column(JSON, nullable=True)
    important_signals = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    issue = relationship("IssueDB", back_populates="predictions")

class FeedbackDB(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    original_prediction = Column(String(50), nullable=False)
    corrected_label = Column(String(50), nullable=False)
    model_version = Column(String(50), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    issue = relationship("IssueDB", back_populates="feedback")

class ModelVersionDB(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), unique=True, index=True, nullable=False)
    model_name = Column(String(100), nullable=False)
    dataset_version = Column(String(100), nullable=False)
    accuracy = Column(Float, nullable=False)
    macro_f1 = Column(Float, nullable=False)
    weighted_f1 = Column(Float, nullable=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=utc_now)

