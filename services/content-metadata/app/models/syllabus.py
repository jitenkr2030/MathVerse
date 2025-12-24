from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime, Enum as SQLEnum, JSON, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from enum import Enum as SQLEnum

from app.database import Base


class SyllabusNodeType(SQLEnum):
    GRADE = "grade"
    SUBJECT = "subject"
    UNIT = "unit"
    TOPIC = "topic"
    SUBTOPIC = "subtopic"


class Syllabus(Base):
    """
    Curriculum structure node.
    Represents the hierarchical organization of educational content.
    """
    __tablename__ = "syllabus"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Hierarchy
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("syllabus.id"), nullable=True, index=True)
    path: Mapped[str] = mapped_column(String(1000), default="")  # Full path like "Grade 9/Mathematics/Algebra"
    depth: Mapped[int] = mapped_column(Integer, default=0)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    
    # Standards reference
    standards_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    learning_objectives: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Duration estimate
    estimated_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Self-referential relationship for tree structure
    parent: Mapped[Optional["Syllabus"]] = relationship("Syllabus", remote_side=[id], backref="children")
    
    # Relationships with content
    courses: Mapped[List["Course"]] = relationship("Course", back_populates="syllabus")
    
    __table_args__ = (
        Index('idx_syllabus_type', 'node_type'),
        Index('idx_syllabus_path', 'path'),
        Index('idx_syllabus_parent', 'parent_id'),
    )
