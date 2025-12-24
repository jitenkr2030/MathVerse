from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime, Enum, JSON, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from enum import Enum as SQLEnum

from app.database import Base


class ContentType(SQLEnum):
    VIDEO = "video"
    EXERCISE = "exercise"
    WORKSHEET = "worksheet"
    ARTICLE = "article"
    INTERACTIVE = "interactive"
    ANIMATION = "animation"


class DifficultyLevel(SQLEnum):
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ContentItem(Base):
    """
    Core content item model for educational content.
    Represents videos, exercises, worksheets, articles, etc.
    """
    __tablename__ = "content_items"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Basic Information
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Resource Information
    resource_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Educational Attributes
    difficulty: Mapped[str] = mapped_column(String(50), default="beginner", index=True)
    grade_level: Mapped[int] = mapped_column(Integer, default=6, index=True)
    subject: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    topic: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    
    # Standards Alignment
    standards_codes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    learning_objectives: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Metadata
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    course_contents: Mapped[List["CourseContent"]] = relationship("CourseContent", back_populates="content_item")
    content_tags: Mapped[List["ContentTag"]] = relationship("ContentTag", back_populates="content_item")
    
    # Indexes
    __table_args__ = (
        Index('idx_content_difficulty_grade', 'difficulty', 'grade_level'),
        Index('idx_content_subject_topic', 'subject', 'topic'),
    )


class TaxonomyNode(Base):
    """
    Curriculum tree structure for organizing educational content.
    Supports hierarchy: Grade → Subject → Unit → Topic → Subtopic
    """
    __tablename__ = "taxonomy_nodes"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # grade, subject, unit, topic, subtopic
    
    # Hierarchy
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("taxonomy_nodes.id"), nullable=True, index=True)
    path: Mapped[str] = mapped_column(String(1000), default="")  # Full path like "Grade 9/Mathematics/Algebra/Linear Equations"
    depth: Mapped[int] = mapped_column(Integer, default=0)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # Standards reference
    standards_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Self-referential relationship for tree structure
    parent: Mapped[Optional["TaxonomyNode"]] = relationship("TaxonomyNode", remote_side=[id], backref="children")
    content_associations: Mapped[List["TaxonomyContent"]] = relationship("TaxonomyContent", back_populates="taxonomy_node")
    
    __table_args__ = (
        Index('idx_taxonomy_type', 'node_type'),
        Index('idx_taxonomy_path', 'path'),
    )


class StandardTag(Base):
    """
    Educational standards tags (Common Core, TEKS, etc.)
    """
    __tablename__ = "standard_tags"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    grade_range: Mapped[str] = mapped_column(String(50), nullable=True)  # e.g., "6-8", "9-12"
    standard_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # e.g., "CCSS", "TEKS", "NGSS"
    
    # Hierarchy
    parent_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    content_associations: Mapped[List["ContentStandard"]] = relationship("ContentStandard", back_populates="standard_tag")
    
    __table_args__ = (
        Index('idx_standard_subject', 'subject'),
        Index('idx_standard_grade', 'grade_range'),
    )


class ContentTag(Base):
    """
    Flexible content tags for categorization and search
    """
    __tablename__ = "content_tags"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)  # e.g., "skill", "method", "application"
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    content_items: Mapped[List["ContentItem"]] = relationship("ContentTag", back_populates="tag")
    
    __table_args__ = (
        Index('idx_tag_category', 'category'),
    )


# Association tables for many-to-many relationships
class TaxonomyContent(Base):
    """Association table for ContentItem ↔ TaxonomyNode"""
    __tablename__ = "taxonomy_content"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("content_items.id"), nullable=False)
    taxonomy_node_id: Mapped[int] = mapped_column(Integer, ForeignKey("taxonomy_nodes.id"), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)  # Primary classification
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    content_item: Mapped["ContentItem"] = relationship("ContentItem")
    taxonomy_node: Mapped["TaxonomyNode"] = relationship("TaxonomyNode", back_populates="content_associations")
    
    __table_args__ = (
        Index('idx_taxonomy_content_item', 'content_item_id'),
        Index('idx_taxonomy_content_node', 'taxonomy_node_id'),
    )


class ContentStandard(Base):
    """Association table for ContentItem ↔ StandardTag"""
    __tablename__ = "content_standards"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("content_items.id"), nullable=False)
    standard_tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("standard_tags.id"), nullable=False)
    alignment_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., "directly_aligned", "supporting"
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    content_item: Mapped["ContentItem"] = relationship("ContentItem")
    standard_tag: Mapped["StandardTag"] = relationship("StandardTag", back_populates="content_associations")
    
    __table_args__ = (
        Index('idx_content_standard_content', 'content_item_id'),
        Index('idx_content_standard_tag', 'standard_tag_id'),
    )


# Update forward references for existing relationships
from app.models.course import Course, Lesson, Concept, Syllabus, Prerequisite
from app.models.lesson import LessonConcept, LessonPrerequisite
