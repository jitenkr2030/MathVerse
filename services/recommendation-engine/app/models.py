from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON, Index, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from enum import Enum as SQLEnum

from app.database import Base


class InteractionType(SQLEnum):
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


class ContentType(SQLEnum):
    VIDEO = "video"
    QUIZ = "quiz"
    EXERCISE = "exercise"
    LESSON = "lesson"
    ARTICLE = "article"
    INTERACTIVE = "interactive"
    ASSESSMENT = "assessment"


class DifficultyLevel(SQLEnum):
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LearningStyle(SQLEnum):
    VISUAL = "visual"
    TEXTUAL = "textual"
    INTERACTIVE = "interactive"
    PRACTICAL = "practical"
    ANALYTICAL = "analytical"


class StudentProfile(Base):
    """Student profile with learning preferences"""
    __tablename__ = "student_profiles"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    learning_style: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    preferred_content_types: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    daily_goal_minutes: Mapped[int] = mapped_column(Integer, default=30)
    weak_areas_focus: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Progress tracking
    total_learning_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
    current_streak_days: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Additional metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    interactions: Mapped[List["Interaction"]] = relationship("Interaction", back_populates="student")
    mastery_snapshots: Mapped[List["MasterySnapshot"]] = relationship("MasterySnapshot", back_populates="student")
    
    __table_args__ = (
        Index('idx_student_profile_style', 'learning_style'),
    )


class ContentItem(Base):
    """Content item available for recommendations"""
    __tablename__ = "content_items"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    subtopics: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Prerequisites and relationships
    prerequisites: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    related_content: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Quality metrics
    popularity_score: Mapped[float] = mapped_column(Float, default=0.0)
    effectiveness_score: Mapped[float] = mapped_column(Float, default=0.0)
    completion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    interactions: Mapped[List["Interaction"]] = relationship("Interaction", back_populates="content")
    
    __table_args__ = (
        Index('idx_content_type', 'content_type'),
        Index('idx_content_difficulty', 'difficulty'),
        Index('idx_content_topic', 'topic'),
    )


class Interaction(Base):
    """Student interaction events"""
    __tablename__ = "interactions"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("student_profiles.student_id"), nullable=False, index=True)
    content_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("content_items.content_id"), nullable=True, index=True)
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Interaction details
    topic: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    concept: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Context
    device_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="interactions")
    content: Mapped[Optional["ContentItem"]] = relationship("ContentItem", back_populates="interactions")
    
    __table_args__ = (
        Index('idx_interaction_student', 'student_id'),
        Index('idx_interaction_type', 'interaction_type'),
        Index('idx_interaction_topic', 'topic'),
        Index('idx_interaction_timestamp', 'timestamp'),
    )


class MasterySnapshot(Base):
    """Topic mastery level snapshots"""
    __tablename__ = "mastery_snapshots"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("student_profiles.student_id"), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    mastery_level: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    sample_size: Mapped[int] = mapped_column(Integer, default=0)
    
    # Prediction
    predicted_next_mastery: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timestamp
    last_interaction: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="mastery_snapshots")
    
    __table_args__ = (
        Index('idx_mastery_student_topic', 'student_id', 'topic', unique=True),
    )


class RecommendationLog(Base):
    """Log of recommendations generated"""
    __tablename__ = "recommendation_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    algorithm_used: Mapped[str] = mapped_column(String(100), nullable=False)
    recommendation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Input context
    request_context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Output
    recommended_content: Mapped[list] = mapped_column(JSON, nullable=False)
    
    # Feedback
    was_clicked: Mapped[bool] = mapped_column(Boolean, default=False)
    was_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    feedback_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Performance
    generation_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_recommendation_student', 'student_id'),
        Index('idx_recommendation_algorithm', 'algorithm_used'),
        Index('idx_recommendation_timestamp', 'created_at'),
    )


class TopicHierarchy(Base):
    """Topic hierarchy for curriculum structure"""
    __tablename__ = "topic_hierarchy"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    topic_name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    parent_topic: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    topic_level: Mapped[int] = mapped_column(Integer, default=0)
    subject_area: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    grade_level: Mapped[int] = mapped_column(Integer, default=6)
    
    # Learning sequence
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    is_prerequisite_for: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    builds_on: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    estimated_learning_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_topic_subject', 'subject_area'),
        Index('idx_topic_grade', 'grade_level'),
    )
