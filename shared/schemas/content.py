"""
Content Schemas Module

This module provides Pydantic schemas for content-related data models.
It defines schemas for courses, lessons, videos, quizzes, concepts,
and other educational content in the MathVerse platform.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ContentType(str, Enum):
    """Type of educational content."""
    
    VIDEO = "video"
    LESSON = "lesson"
    QUIZ = "quiz"
    PRACTICE = "practice"
    INTERACTIVE = "interactive"
    ANIMATION = "animation"
    DOCUMENT = "document"
    ASSESSMENT = "assessment"
    GAME = "game"


class ContentStatus(str, Enum):
    """Status of content in the platform."""
    
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class DifficultyLevel(str, Enum):
    """Content difficulty levels."""
    
    FOUNDATIONAL = "foundational"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ContentBase(BaseModel):
    """Base content schema with common fields."""
    
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    short_description: Optional[str] = Field(default=None, max_length=200)
    content_type: ContentType
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    subject: str = Field(..., description="Subject area (e.g., algebra, geometry)")
    topics: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    language: str = Field(default="en", max_length=10)
    author_id: str = Field(..., description="Content creator ID")
    estimated_duration_minutes: int = Field(default=0, ge=0)
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContentCreate(ContentBase):
    """Schema for creating new content."""
    
    status: ContentStatus = Field(default=ContentStatus.DRAFT)
    course_id: Optional[str] = Field(default=None)
    prerequisites: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Introduction to Algebra",
                "description": "Learn the basics of algebraic expressions",
                "content_type": "lesson",
                "difficulty": "foundational",
                "subject": "algebra",
                "topics": ["expressions", "variables", "equations"],
                "author_id": "user_123",
                "estimated_duration_minutes": 30
            }
        }


class ContentUpdate(BaseModel):
    """Schema for updating content."""
    
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=5000)
    short_description: Optional[str] = Field(default=None, max_length=200)
    difficulty: Optional[DifficultyLevel] = None
    topics: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    thumbnail_url: Optional[str] = None
    preview_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[ContentStatus] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None


class ContentResponse(ContentBase):
    """Schema for content response data."""
    
    content_id: str
    status: ContentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    view_count: int = 0
    like_count: int = 0
    completion_count: int = 0
    average_rating: float = 0.0
    total_ratings: int = 0
    quality_score: Optional[float] = None
    
    class Config:
        from_attributes = True


class ConceptNode(BaseModel):
    """Schema for a learning concept node."""
    
    concept_id: str = Field(..., description="Unique concept identifier")
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    subject: str
    difficulty: DifficultyLevel
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisite concept IDs")
    related_concepts: List[str] = Field(default_factory=list, description="Related concept IDs")
    parent_concept: Optional[str] = Field(default=None, description="Parent concept ID")
    estimated_minutes: int = Field(default=15)
    importance_score: float = Field(default=0.5, ge=0, le=1)
    content_ids: List[str] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    """Base course schema."""
    
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., max_length=5000)
    short_description: Optional[str] = Field(default=None, max_length=300)
    subject: str
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    thumbnail_url: Optional[str] = None
    preview_video_url: Optional[str] = None
    estimated_hours: float = Field(default=0, ge=0)
    language: str = Field(default="en")
    tags: List[str] = Field(default_factory=list)


class CourseCreate(CourseBase):
    """Schema for creating a course."""
    
    creator_id: str
    status: ContentStatus = Field(default=ContentStatus.DRAFT)
    lesson_ids: List[str] = Field(default_factory=list)
    prerequisite_course_ids: List[str] = Field(default_factory=list)
    learning_outcomes: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete Algebra Masterclass",
                "description": "Master algebra from basics to advanced topics",
                "subject": "algebra",
                "difficulty": "intermediate",
                "creator_id": "user_123",
                "estimated_hours": 20
            }
        }


class CourseResponse(CourseBase):
    """Schema for course response."""
    
    course_id: str
    creator_id: str
    status: ContentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    lesson_count: int = 0
    enrollment_count: int = 0
    average_rating: float = 0.0
    total_reviews: int = 0
    view_count: int = 0
    
    class Config:
        from_attributes = True


class Lesson(BaseModel):
    """Schema for a lesson within a course."""
    
    lesson_id: str
    course_id: str
    title: str = Field(..., max_length=500)
    description: Optional[str] = Field(default=None)
    sequence_order: int = Field(..., ge=1)
    content_items: List[str] = Field(default_factory=list, description="Content item IDs in order")
    estimated_minutes: int = Field(default=15)
    is_preview: bool = Field(default=False)
    is_required: bool = Field(default=True)
    
    class Config:
        from_attributes = True


class VideoContent(BaseModel):
    """Schema for video content."""
    
    content_id: str
    video_url: str = Field(..., description="URL to video file")
    duration_seconds: int = Field(..., ge=0)
    resolution: str = Field(default="1080p")
    format: str = Field(default="mp4")
    thumbnail_url: Optional[str] = None
    captions_url: Optional[str] = Field(default=None, description="URL to captions file")
    transcript_url: Optional[str] = None
    chapters: List[Dict[str, int]] = Field(
        default_factory=list,
        description="List of {title, start_seconds} chapters"
    )
    
    class Config:
        from_attributes = True


class QuizQuestion(BaseModel):
    """Schema for a quiz question."""
    
    question_id: str
    question_text: str
    question_type: str = Field(default="multiple_choice", description="multiple_choice, true_false, short_answer")
    options: List[str] = Field(default_factory=list)
    correct_answer: str
    explanation: Optional[str] = Field(default=None)
    points: int = Field(default=1)
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.BEGINNER)
    topic: Optional[str] = None
    
    class Config:
        from_attributes = True


class QuizContent(BaseModel):
    """Schema for quiz content."""
    
    content_id: str
    questions: List[QuizQuestion] = Field(default_factory=list)
    passing_score: float = Field(default=0.7, ge=0, le=1)
    time_limit_minutes: Optional[int] = Field(default=None, ge=1)
    shuffle_questions: bool = Field(default=True)
    shuffle_options: bool = Field(default=True)
    show_results: bool = Field(default=True)
    allow_retakes: bool = Field(default=True)
    max_attempts: int = Field(default=3)
    
    class Config:
        from_attributes = True


class ContentProgress(BaseModel):
    """Schema for tracking user progress on content."""
    
    user_id: str
    content_id: str
    progress_percentage: float = Field(default=0.0, ge=0, le=100)
    status: str = Field(default="not_started", description="not_started, in_progress, completed")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    time_spent_seconds: int = Field(default=0)
    last_position_seconds: int = Field(default=0, description="For video/audio content")
    attempts: int = Field(default=0)
    best_score: Optional[float] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class ContentRating(BaseModel):
    """Schema for content rating."""
    
    user_id: str
    content_id: str
    rating: int = Field(default=5, ge=1, le=5)
    review: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ContentSearchParams(BaseModel):
    """Schema for content search parameters."""
    
    query: Optional[str] = Field(default=None, description="Search query")
    content_types: Optional[List[ContentType]] = None
    subjects: Optional[List[str]] = None
    difficulty: Optional[List[DifficultyLevel]] = None
    tags: Optional[List[str]] = None
    language: Optional[str] = None
    creator_id: Optional[str] = None
    is_premium: Optional[bool] = None
    min_duration_minutes: Optional[int] = None
    max_duration_minutes: Optional[int] = None
    sort_by: str = Field(default="relevance", description="relevance, popularity, rating, newest")
    sort_order: str = Field(default="desc", description="asc, desc")
