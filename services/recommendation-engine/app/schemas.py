from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class InteractionType(str, Enum):
    """Types of student interactions with content"""
    VIDEO_VIEW = "video_view"
    VIDEO_COMPLETE = "video_complete"
    QUIZ_START = "quiz_start"
    QUIZ_COMPLETE = "quiz_complete"
    EXERCISE_START = "exercise_start"
    EXERCISE_COMPLETE = "exercise_complete"
    EXERCISE_CORRECT = "exercise_correct"
    EXERCISE_INCORRECT = "exercise_incorrect"
    CONCEPT_INTRODUCE = "concept_introduce"
    CONCEPT_REVIEW = "concept_review"
    STRUGGLE_DETECTED = "struggle_detected"
    HINT_REQUEST = "hint_request"


class ContentType(str, Enum):
    """Types of educational content"""
    VIDEO = "video"
    QUIZ = "quiz"
    EXERCISE = "exercise"
    LESSON = "lesson"
    ARTICLE = "article"
    INTERACTIVE = "interactive"
    ASSESSMENT = "assessment"


class DifficultyLevel(str, Enum):
    """Content difficulty levels"""
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LearningStyle(str, Enum):
    """Student learning style preferences"""
    VISUAL = "visual"
    TEXTUAL = "textual"
    INTERACTIVE = "interactive"
    PRACTICAL = "practical"
    ANALYTICAL = "analytical"


# Request Schemas
class RecommendationRequest(BaseModel):
    """Request for personalized recommendations"""
    student_id: int = Field(..., description="Student identifier")
    current_topic: Optional[str] = Field(default=None, description="Current topic being studied")
    count: int = Field(default=5, ge=1, le=20, description="Number of recommendations")
    content_types: Optional[List[ContentType]] = Field(default=None, description="Filter by content types")
    exclude_completed: bool = Field(default=True, description="Exclude already completed content")
    focus_area: Optional[str] = Field(default=None, description="Specific area to focus on")
    
    model_config = {
        "json_schema_extra": {"examples": [{"student_id": 1, "current_topic": "algebra_1", "count": 5}]}
    }


class LearningPathRequest(BaseModel):
    """Request for a complete learning path"""
    student_id: int = Field(..., description="Student identifier")
    target_topic: str = Field(..., description="Topic to learn")
    current_mastery: Dict[str, float] = Field(default_factory=dict, description="Current topic mastery levels")
    time_constraint_hours: Optional[float] = Field(default=None, description="Available learning time")
    preferred_content_types: Optional[List[ContentType]] = Field(default=None, description="Preferred content mix")


class EventIngestRequest(BaseModel):
    """Request to ingest a student interaction event"""
    student_id: int = Field(..., description="Student identifier")
    event_type: InteractionType = Field(..., description="Type of interaction")
    content_id: Optional[int] = Field(default=None, description="Content involved")
    topic_id: Optional[int] = Field(default=None, description="Topic involved")
    concept_id: Optional[int] = Field(default=None, concept_id involved")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional event data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "student_id": 1,
                "event_type": "quiz_complete",
                "content_id": 123,
                "topic_id": 5,
                "metadata": {"score": 0.85, "time_spent": 300}
            }]
        }
    }


class BulkEventRequest(BaseModel):
    """Bulk event ingestion request"""
    events: List[EventIngestRequest] = Field(..., description="List of events to ingest")


class StudentProfileUpdateRequest(BaseModel):
    """Request to update student profile"""
    learning_style: Optional[LearningStyle] = None
    preferred_content_types: Optional[List[ContentType]] = None
    daily_goal_minutes: Optional[int] = Field(default=None, ge=0, le=480)
    weak_areas_focus: Optional[List[str]] = None


# Response Schemas
class ContentRecommendation(BaseModel):
    """Individual content recommendation with reasoning"""
    content_id: int
    title: str
    content_type: ContentType
    difficulty: DifficultyLevel
    topic: str
    score: float = Field(..., ge=0, le=1, description="Recommendation score")
    reason: str = Field(..., description="Why this content is recommended")
    estimated_time_minutes: Optional[int] = None
    prerequisites: List[str] = []
    
    model_config = {"from_attributes": True}


class RecommendationResponse(BaseModel):
    """Response containing recommendations"""
    student_id: int
    recommendations: List[ContentRecommendation]
    generated_at: datetime
    algorithm_used: str
    generation_time_ms: float


class ConceptRecommendation(BaseModel):
    """Concept recommendation with mastery prediction"""
    concept_id: int
    concept_name: str
    current_mastery: float = Field(..., ge=0, le=1)
    predicted_mastery: float = Field(..., ge=0, le=1)
    improvement: float
    priority: int
    recommended_content: List[int] = []
    
    model_config = {"from_attributes": True}


class ConceptRecommendationResponse(BaseModel):
    """Response for concept recommendations"""
    student_id: int
    concepts: List[ConceptRecommendation]
    focus_areas: List[str] = []
    generated_at: datetime


class LearningPathNode(BaseModel):
    """Individual node in a learning path"""
    content_id: int
    title: str
    content_type: ContentType
    difficulty: DifficultyLevel
    topic: str
    duration_minutes: int
    order: int
    prerequisites: List[str] = []
    expected_mastery_gain: float = 0.0


class LearningPathResponse(BaseModel):
    """Complete learning path response"""
    student_id: int
    target_topic: str
    path: List[LearningPathNode]
    total_duration_minutes: int
    estimated_completion_hours: float
    prerequisite_topics: List[str] = []
    generated_at: datetime
    algorithm_used: str


class WeaknessAnalysis(BaseModel):
    """Analysis of student weaknesses"""
    concept_id: int
    concept_name: str
    weakness_score: float = Field(..., ge=0, le=1)
    evidence_count: int
    related_concepts: List[str] = []
    recommended_focus: float = Field(..., ge=0, le=1)


class WeaknessAnalysisResponse(BaseModel):
    """Response containing weakness analysis"""
    student_id: int
    analysis: List[WeaknessAnalysis]
    overall_weaker_areas: List[str] = []
    suggested_action: str
    generated_at: datetime


class ProgressAnalytics(BaseModel):
    """Student progress analytics"""
    student_id: int
    total_time_spent_minutes: int
    content_completed_count: int
    average_mastery_gain: float
    current_streak_days: int
    topics_covered: List[str] = []
    strong_areas: List[str] = []
    weak_areas: List[str] = []
    recommended_daily_goal_minutes: int
    predicted_mastery_levels: Dict[str, float] = {}
    generated_at: datetime


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    model_loaded: bool
    database_connected: bool
    redis_connected: bool
    total_students: int
    total_content_items: int
    active_recommendations: int
    timestamp: datetime


class StatsResponse(BaseModel):
    """Service statistics response"""
    total_requests: int
    average_latency_ms: float
    cache_hit_rate: float
    popular_content: List[Dict] = []
    active_students_24h: int
    recommendations_generated_24h: int


# Model Schemas for Database
class StudentProfileModel(BaseModel):
    """Student profile for database storage"""
    student_id: int
    learning_style: Optional[str] = None
    preferred_content_types: List[str] = []
    daily_goal_minutes: int = 30
    weak_areas_focus: List[str] = []
    last_active: datetime = Field(default_factory=datetime.utcnow)
    total_learning_time_minutes: int = 0
    streak_days: int = 0
    metadata: Dict[str, Any] = {}
    
    model_config = {"from_attributes": True}


class ContentModel(BaseModel):
    """Content item for recommendation database"""
    content_id: int
    title: str
    content_type: str
    difficulty: str
    topic: str
    subtopics: List[str] = []
    duration_minutes: int
    prerequisites: List[str] = []
    popularity_score: float = 0.0
    effectiveness_score: float = 0.0
    metadata: Dict[str, Any] = {}
    
    model_config = {"from_attributes": True}


class InteractionModel(BaseModel):
    """Student interaction for tracking"""
    interaction_id: int
    student_id: int
    content_id: Optional[int] = None
    interaction_type: str
    topic: Optional[str] = None
    concept: Optional[str] = None
    score: Optional[float] = None
    time_spent_seconds: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}
    
    model_config = {"from_attributes": True}


class MasterySnapshotModel(BaseModel):
    """Mastery level snapshot"""
    snapshot_id: int
    student_id: int
    topic: str
    mastery_level: float
    confidence: float
    sample_size: int
    last_interaction: datetime
    predicted_next_mastery: float
    
    model_config = {"from_attributes": True}
