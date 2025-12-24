from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime, Enum as SQLEnum, JSON, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from enum import Enum as SQLEnum

from app.database import Base


class ConceptType(SQLEnum):
    DEFINITION = "definition"
    THEOREM = "theorem"
    FORMULA = "formula"
    PROCEDURE = "procedure"
    EXAMPLE = "example"


class DifficultyLevel(SQLEnum):
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Concept(Base):
    """
    Mathematical concept model.
    Represents definitions, theorems, formulas, procedures, and examples.
    """
    __tablename__ = "concepts"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    concept_type: Mapped[str] = mapped_column(String(50), default="definition", index=True)
    formula_latex: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Educational attributes
    difficulty: Mapped[str] = mapped_column(String(50), default="beginner", index=True)
    grade_level: Mapped[int] = mapped_column(Integer, default=6, index=True)
    keywords: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Explanation fields
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    example_problem: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    example_solution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Visual aid
    diagram_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Status
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    lesson_concepts: Mapped[List["LessonConcept"]] = relationship("LessonConcept", back_populates="concept")
    prerequisites_for: Mapped[List["ConceptPrerequisite"]] = relationship(
        "ConceptPrerequisite",
        foreign_keys="ConceptPrerequisite.concept_id",
        back_populates="concept"
    )
    prerequisites_of: Mapped[List["ConceptPrerequisite"]] = relationship(
        "ConceptPrerequisite",
        foreign_keys="ConceptPrerequisite.prerequisite_id",
        back_populates="prerequisite"
    )
    dependents_for: Mapped[List["ConceptDependency"]] = relationship(
        "ConceptDependency",
        foreign_keys="ConceptDependency.concept_id",
        back_populates="concept"
    )
    dependents_of: Mapped[List["ConceptDependency"]] = relationship(
        "ConceptDependency",
        foreign_keys="ConceptDependency.dependent_id",
        back_populates="dependent"
    )
    
    __table_args__ = (
        Index('idx_concept_difficulty', 'difficulty'),
        Index('idx_concept_grade', 'grade_level'),
        Index('idx_concept_type', 'concept_type'),
    )


class ConceptPrerequisite(Base):
    """
    Many-to-many relationship for concept prerequisites.
    A concept may require understanding of other concepts first.
    """
    __tablename__ = "concept_prerequisites"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    concept_id: Mapped[int] = mapped_column(Integer, ForeignKey("concepts.id"), nullable=False, index=True)
    prerequisite_id: Mapped[int] = mapped_column(Integer, ForeignKey("concepts.id"), nullable=False, index=True)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)
    strength: Mapped[float] = mapped_column(Float, default=1.0)  # How strongly related (0-1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[concept_id], back_populates="prerequisites_for")
    prerequisite: Mapped["Concept"] = relationship("Concept", foreign_keys=[prerequisite_id], back_populates="prerequisites_of")
    
    __table_args__ = (
        Index('idx_prereq_concept', 'concept_id'),
        Index('idx_prereq_prerequisite', 'prerequisite_id'),
    )


class ConceptDependency(Base):
    """
    Similar to prerequisites but for broader concept dependencies.
    Used for tracking concept relationships in the dependency graph.
    """
    __tablename__ = "concept_dependencies"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    concept_id: Mapped[int] = mapped_column(Integer, ForeignKey("concepts.id"), nullable=False, index=True)
    dependent_id: Mapped[int] = mapped_column(Integer, ForeignKey("concepts.id"), nullable=False, index=True)
    dependency_type: Mapped[str] = mapped_column(String(50), default="builds_on")  # builds_on, related_to,应用到
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    concept: Mapped["Concept"] = relationship("Concept", foreign_keys=[concept_id], back_populates="dependents_for")
    dependent: Mapped["Concept"] = relationship("Concept", foreign_keys=[dependent_id], back_populates="dependents_of")
    
    __table_args__ = (
        Index('idx_dep_concept', 'concept_id'),
        Index('idx_dep_dependent', 'dependent_id'),
    )
