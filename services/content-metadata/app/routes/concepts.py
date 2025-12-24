from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.schemas.content_schema import (
    ConceptCreate,
    ConceptUpdate,
    ConceptResponse,
    ConceptDetailResponse,
)
from app.models.concept import Concept, ConceptPrerequisite
from app.models.course import Course
from app.models.lesson import Lesson, LessonConcept


router = APIRouter()


@router.get("/", response_model=List[ConceptResponse])
async def get_concepts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    difficulty: Optional[str] = None,
    concept_type: Optional[str] = None,
    grade_level: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all concepts with optional filtering.
    """
    query = select(Concept)
    
    # Apply filters
    if difficulty:
        query = query.where(Concept.difficulty == difficulty)
    if concept_type:
        query = query.where(Concept.concept_type == concept_type)
    if grade_level:
        query = query.where(Concept.grade_level == grade_level)
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Concept.name.ilike(search_term)) | 
            (Concept.description.ilike(search_term))
        )
    
    # Add pagination
    query = query.offset(skip).limit(limit).order_by(Concept.name)
    
    result = await db.execute(query)
    concepts = result.scalars().all()
    
    return concepts


@router.get("/{concept_id}", response_model=ConceptDetailResponse)
async def get_concept(
    concept_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific concept with all its relationships.
    """
    # Get concept with relationships
    result = await db.execute(
        select(Concept).where(Concept.id == concept_id)
    )
    concept = result.scalar_one_or_none()
    
    if not concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found"
        )
    
    # Get courses that use this concept
    courses_result = await db.execute(
        select(Course.id)
        .join(Lesson, Lesson.course_id == Course.id)
        .join(LessonConcept, LessonConcept.lesson_id == Lesson.id)
        .where(LessonConcept.concept_id == concept_id)
        .distinct()
    )
    course_ids = [row[0] for row in courses_result.all()]
    
    # Get lessons that use this concept
    lessons_result = await db.execute(
        select(Lesson.id)
        .join(LessonConcept, LessonConcept.lesson_id == Lesson.id)
        .where(LessonConcept.concept_id == concept_id)
    )
    lesson_ids = [row[0] for row in lessons_result.all()]
    
    # Get prerequisites
    prereq_result = await db.execute(
        select(Concept.id)
        .select_from(Concept)
        .join(ConceptPrerequisite, ConceptPrerequisite.prerequisite_id == Concept.id)
        .where(ConceptPrerequisite.concept_id == concept_id)
    )
    prerequisite_ids = [row[0] for row in prereq_result.all()]
    
    # Get dependents (concepts that depend on this one)
    from app.models.concept import ConceptDependency
    dependent_result = await db.execute(
        select(Concept.id)
        .select_from(Concept)
        .join(ConceptDependency, ConceptDependency.concept_id == Concept.id)
        .where(ConceptDependency.dependent_id == concept_id)
    )
    dependent_ids = [row[0] for row in dependent_result.all()]
    
    return ConceptDetailResponse(
        id=concept.id,
        name=concept.name,
        description=concept.description,
        concept_type=concept.concept_type,
        formula_latex=concept.formula_latex,
        difficulty=concept.difficulty,
        grade_level=concept.grade_level,
        keywords=concept.keywords or [],
        created_at=concept.created_at,
        updated_at=concept.updated_at,
        courses=course_ids,
        lessons=lesson_ids,
        prerequisites=prerequisite_ids,
        dependents=dependent_ids,
    )


@router.post("/", response_model=ConceptResponse, status_code=status.HTTP_201_CREATED)
async def create_concept(
    concept: ConceptCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new concept.
    """
    db_concept = Concept(**concept.model_dump())
    db.add(db_concept)
    
    try:
        await db.commit()
        await db.refresh(db_concept)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create concept: {str(e)}"
        )
    
    return db_concept


@router.patch("/{concept_id}", response_model=ConceptResponse)
async def update_concept(
    concept_id: int,
    concept_update: ConceptUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing concept.
    """
    result = await db.execute(
        select(Concept).where(Concept.id == concept_id)
    )
    db_concept = result.scalar_one_or_none()
    
    if not db_concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found"
        )
    
    # Update fields
    update_data = concept_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_concept, field, value)
    
    db_concept.updated_at = datetime.utcnow()
    
    try:
        await db.commit()
        await db.refresh(db_concept)
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update concept: {str(e)}"
        )
    
    return db_concept


@router.delete("/{concept_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_concept(
    concept_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a concept and its relationships.
    """
    result = await db.execute(
        select(Concept).where(Concept.id == concept_id)
    )
    db_concept = result.scalar_one_or_none()
    
    if not db_concept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept {concept_id} not found"
        )
    
    try:
        await db.delete(db_concept)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete concept: {str(e)}"
        )
