from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

class IssueAnalyzeRequest(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Application crashes during file upload"})
    description: str = Field(..., json_schema_extra={"example": "When uploading large PNG files (>5MB), the system throws NullPointerException."})
    steps_to_reproduce: Optional[str] = Field(default="", json_schema_extra={"example": "1. Go to upload page\n2. Select 10MB PNG file\n3. Click upload"})
    expected_behavior: Optional[str] = Field(default="", json_schema_extra={"example": "File uploads successfully and thumbnail displays."})
    actual_behavior: Optional[str] = Field(default="", json_schema_extra={"example": "System throws 500 error and page freezes."})
    environment: Optional[str] = Field(default="", json_schema_extra={"example": "Windows 11, Chrome 120"})
    version: Optional[str] = Field(default="", json_schema_extra={"example": "v2.1.0"})
    logs: Optional[str] = Field(default="", json_schema_extra={"example": "java.lang.NullPointerException at FileHandler.java:42"})

class TopPredictionItem(BaseModel):
    category: str
    probability: float

class DuplicateMatchItem(BaseModel):
    issue_id: int
    title: str
    category: str
    similarity: float
    similarity_percentage: float
    created_at: str

class IssueAnalyzeResponse(BaseModel):
    title: str
    predicted_category: str
    confidence: float
    top_predictions: List[TopPredictionItem]
    is_low_confidence: bool
    confidence_message: str
    important_signals: List[str]
    explanation_note: str
    quality_score: int
    quality_grade: str
    quality_breakdown: Dict[str, int]
    quality_suggestions: List[str]
    priority_recommendation: Dict[str, Any]
    suggested_team: Dict[str, Any]
    duplicate_check: Dict[str, Any]
    model_name: str
    model_version: str
    extracted_file_info: Optional[Dict[str, Any]] = None
    error_rectification: Optional[Dict[str, Any]] = None

class IssueCreateRequest(IssueAnalyzeRequest):
    confirmed_category: Optional[str] = None

class IssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    steps_to_reproduce: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    environment: Optional[str] = None
    version: Optional[str] = None
    logs: Optional[str] = None
    predicted_category: str
    confidence: float
    is_low_confidence: bool
    quality_score: int
    priority_recommendation: Optional[str] = None
    team_recommendation: Optional[str] = None
    model_version: str
    status: str
    created_at: datetime

class FeedbackCreateRequest(BaseModel):
    issue_id: int
    original_prediction: str
    corrected_label: str
    comment: Optional[str] = ""

class FeedbackResponse(BaseModel):
    id: int
    issue_id: int
    original_prediction: str
    corrected_label: str
    model_version: str
    created_at: datetime
    message: str

class DuplicateCheckRequest(BaseModel):
    title: str
    description: str
    threshold: Optional[float] = 0.35

class ModelInfoResponse(BaseModel):
    model_name: str
    version: str
    training_timestamp: str
    primary_metric: str
    best_macro_f1: float
    best_accuracy: float
    dataset_source: str
    train_samples: int
    test_samples: int
    num_features: int
    label_classes: List[str]
    candidate_comparisons: List[Dict[str, Any]]

class IssueCompareRequest(BaseModel):
    issue_a_id: Optional[int] = None
    title_a: str
    description_a: str
    issue_b_id: Optional[int] = None
    title_b: str
    description_b: str

class IssueCompareResponse(BaseModel):
    similarity_score: float
    similarity_percentage: float
    common_terms: List[str]
    category_match: bool
    category_a: str
    category_b: str
    comparison_summary: str

class RetrainRequest(BaseModel):
    include_feedback: bool = True
    min_macro_f1_threshold: float = 0.85

class RetrainResponse(BaseModel):
    status: str
    previous_version: str
    new_version: str
    previous_macro_f1: float
    new_macro_f1: float
    promoted: bool
    message: str

