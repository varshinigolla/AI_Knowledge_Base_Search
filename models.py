from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

# Handle Pydantic v1/v2 compatibility
try:
    from pydantic import Field
except ImportError:
    Field = None

class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class MissingInfoType(str, Enum):
    DOCUMENT = "document"
    DATA = "data"
    CONTEXT = "context"
    SPECIFIC_FACT = "specific_fact"

class MissingInfo(BaseModel):
    type: MissingInfoType
    description: str
    suggested_action: str
    priority: int  # 1-5, 5 being highest priority

class EnrichmentSuggestion(BaseModel):
    type: str
    description: str
    action: str
    confidence: float
    estimated_effort: str  # "low", "medium", "high"

class SearchResponse(BaseModel):
    answer: str
    confidence: float
    confidence_level: ConfidenceLevel
    sources: List[Dict[str, Any]]
    missing_info: List[MissingInfo]
    enrichment_suggestions: List[EnrichmentSuggestion]
    processing_time: float

class DocumentUpload(BaseModel):
    filename: str
    content_type: str
    size: int

class SearchQuery(BaseModel):
    query: str
    include_confidence: bool = True
    include_enrichment: bool = True

class DocumentMetadata(BaseModel):
    filename: str
    upload_date: str
    file_size: int
    content_type: str
    chunk_count: int
    processing_status: str

class AnswerRating(BaseModel):
    query: str
    rating: int  # 1-5
    feedback: Optional[str] = None
    improvement_suggestions: Optional[str] = None
