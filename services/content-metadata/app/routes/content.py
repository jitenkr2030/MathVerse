from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
import math

from app.database import get_db
from app.schemas.content_schema import (
    ContentType,
    DifficultyLevel,
    LessonType,
    ConceptType,
    ConceptCreate,
    ConceptUpdate,
    ConceptResponse,
    ConceptDetailResponse,
    LessonCreate,
    LessonUpdate,
    LessonResponse,
    LessonDetailResponse,
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    CourseDetailResponse,
    PaginationParams,
    PaginatedResponse,
    SearchQuery,
    SearchResult,
    SearchResponse,
    SyllabusNodeCreate,
    SyllabusNodeUpdate,
    SyllabusNodeResponse,
    SyllabusTreeResponse,
)
from app.models.course import Course, Syllabus
from app.models.lesson import Lesson, LessonConcept
from app.models.concept import Concept, ConceptPrerequisite, ConceptDependency
from app.services.tagging_service import TaggingService
from app.services.curriculum_mapper import CurriculumMapper


router = APIRouter()


# ==================== Content Search ====================

@router.get("/search", response_model=SearchResponse)
async def search_content(
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    content_type: Optional[List[str]] = Query(default=None, description="Filter by content types"),
    difficulty: Optional[List[str]] = Query(default=None, description="Filter by difficulty levels"),
    subject: Optional[List[str]] = Query(default=None, description="Filter by subjects"),
    grade_level: Optional[int] = Query(default=None, ge=1, le=12, description="Filter by grade level"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Search across all content types (courses, lessons, concepts).
    Returns ranked results with relevance scoring.
    """
    import time
    start_time = time.time()
    
    # Build search conditions
    search_term = f"%{q}%"
    
    # Search courses
    course_query = select(Course).where(
        and_(
            Course.is_published == True,
            or_(
                Course.title.ilike(search_term),
                Course.description.ilike(search_term),
            )
        )
    )
    if subject:
        course_query = course_query.where(Course.subject.in_(subject))
    if difficulty:
        course_query = course_query.where(Course.difficulty.in_(difficulty))
    
    course_result = await db.execute(course_query)
    courses = course_result.scalars().all()
    
    # Search lessons
    lesson_query = select(Lesson).where(
        and_(
            Lesson.is_published == True,
            or_(
                Lesson.title.ilike(search_term),
                Lesson.description.ilike(search_term),
            )
        )
    )
    if subject:
        # Join with course to filter by subject
        lesson_query = lesson_query.join(Course).where(Course.subject.in_(subject))
    if grade_level:
        lesson_query = lesson_query.join(Course).where(Course.grade_level == grade_level)
    
    lesson_result = await db.execute(lesson_query)
    lessons = lesson_result.scalars().all()
    
    # Search concepts
    concept_query = select(Concept).where(
        or_(
            Concept.name.ilike(search_term),
            Concept.description.ilike(search_term),
        )
    )
    if difficulty:
        concept_query = concept_query.where(Concept.difficulty.in_(difficulty))
    if grade_level:
        concept_query = concept_query.where(Concept.grade_level == grade_level)
    
    concept_result = await db.execute(concept_query)
    concepts = concept_result.scalars().all()
    
    # Combine and score results
    results = []
    
    for course in courses:
        score = _calculate_relevance_score(course.title, course.description or "", q)
        results.append(SearchResult(
            id=course.id,
            type="course",
            title=course.title,
            description=course.description,
            subject=course.subject,
            difficulty=course.difficulty.value if hasattr(course.difficulty, 'value') else course.difficulty,
            relevance_score=score,
        ))
    
    for lesson in lessons:
        score = _calculate_relevance_score(lesson.title, lesson.description or "", q)
        results.append(SearchResult(
            id=lesson.id,
            type="lesson",
            title=lesson.title,
            description=lesson.description,
            difficulty=lesson.difficulty.value if hasattr(lesson.difficulty, 'value') else lesson.difficulty,
            relevance_score=score,
        ))
    
    for concept in concepts:
        score = _calculate_relevance_score(concept.name, concept.description or "", q)
        results.append(SearchResult(
            id=concept.id,
            type="concept",
            title=concept.name,
            description=concept.description,
            difficulty=concept.difficulty.value if hasattr(concept.difficulty, 'value') else concept.difficulty,
            relevance_score=score,
        ))
    
    # Sort by relevance score
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    
    # Paginate
    total = len(results)
    offset = (page - 1) * per_page
    paginated_results = results[offset:offset + per_page]
    
    took_ms = (time.time() - start_time) * 1000
    
    return SearchResponse(
        query=q,
        total_results=total,
        results=paginated_results,
        took_ms=round(took_ms, 2),
    )


def _calculate_relevance_score(title: str, description: str, query: str) -> float:
    """Calculate relevance score based on title match, description match, and term frequency"""
    query_lower = query.lower()
    title_lower = title.lower()
    desc_lower = description.lower()
    
    score = 0.0
    
    # Title exact match
    if query_lower == title_lower:
        score += 10.0
    # Title starts with query
    elif title_lower.startswith(query_lower):
        score += 8.0
    # Title contains query
    elif query_lower in title_lower:
        score += 5.0
    
    # Description contains query
    if query_lower in desc_lower:
        score += 2.0
    
    # Title word match
    query_words = query_lower.split()
    title_words = title_lower.split()
    for qw in query_words:
        if qw in title_words:
            score += 1.0
    
    return round(score, 2)


# ==================== Taxonomy/Curriculum Endpoints ====================

@router.get("/curriculum/tree", response_model=List[SyllabusTreeResponse])
async def get_curriculum_tree(
    node_type: Optional[str] = Query(default=None, description="Filter by node type"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the full curriculum tree structure.
    Returns nested hierarchy of grades, subjects, units, and topics.
    """
    mapper = CurriculumMapper(db)
    return await mapper.get_curriculum_tree(node_type)


@router.get("/curriculum/path/{node_id}", response_model=SyllabusNodeResponse)
async def get_curriculum_path(
    node_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific curriculum node with its full path from root.
    """
    mapper = CurriculumMapper(db)
    return await mapper.get_node_with_path(node_id)


@router.post("/curriculum/nodes", response_model=SyllabusNodeResponse, status_code=status.HTTP_201_CREATED)
async def create_curriculum_node(
    node: SyllabusNodeCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new node in the curriculum tree.
    Parent node is optional for root nodes.
    """
    mapper = CurriculumMapper(db)
    return await mapper.create_node(node)


@router.patch("/curriculum/nodes/{node_id}", response_model=SyllabusNodeResponse)
async def update_curriculum_node(
    node_id: int,
    update: SyllabusNodeUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a curriculum node (name, description, order).
    """
    mapper = CurriculumMapper(db)
    return await mapper.update_node(node_id, update)


@router.delete("/curriculum/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_curriculum_node(
    node_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a curriculum node.
    Children will be reassigned to the deleted node's parent.
    """
    mapper = CurriculumMapper(db)
    await mapper.delete_node(node_id)


# ==================== Bulk Operations ====================

@router.post("/bulk/import", status_code=status.HTTP_202_ACCEPTED)
async def bulk_import_content(
    items: List[dict],
    item_type: str = Query(..., description="Type of items: course, lesson, concept"),
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk import content items from a list of dictionaries.
    Returns a job ID for tracking import progress.
    """
    # This would typically be processed asynchronously
    imported_count = 0
    errors = []
    
    for i, item_data in enumerate(items):
        try:
            if item_type == "course":
                course = Course(**item_data)
                db.add(course)
            elif item_type == "lesson":
                lesson = Lesson(**item_data)
                db.add(lesson)
            elif item_type == "concept":
                concept = Concept(**item_data)
                db.add(concept)
            else:
                errors.append({"index": i, "error": f"Unknown type: {item_type}"})
                continue
            
            imported_count += 1
        except Exception as e:
            errors.append({"index": i, "error": str(e)})
    
    await db.commit()
    
    return {
        "imported": imported_count,
        "errors": errors,
        "total": len(items),
    }


@router.post("/bulk/tags")
async def bulk_tag_content(
    content_ids: List[int],
    tag_names: List[str],
    db: AsyncSession = Depends(get_db),
):
    """
    Apply tags to multiple content items at once.
    """
    tagging_service = TaggingService(db)
    
    result = await tagging_service.bulk_apply_tags(content_ids, tag_names)
    return result


# ==================== Statistics ====================

@router.get("/stats/summary")
async def get_content_stats(
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    grade_level: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get content statistics summary.
    """
    # Count courses
    course_query = select(func.count(Course.id))
    if subject:
        course_query = course_query.where(Course.subject == subject)
    if difficulty:
        course_query = course_query.where(Course.difficulty == difficulty)
    if grade_level:
        course_query = course_query.where(Course.grade_level == grade_level)
    
    course_count = (await db.execute(course_query)).scalar() or 0
    
    # Count lessons
    lesson_query = select(func.count(Lesson.id))
    if subject:
        lesson_query = lesson_query.join(Course).where(Course.subject == subject)
    if grade_level:
        lesson_query = lesson_query.join(Course).where(Course.grade_level == grade_level)
    
    lesson_count = (await db.execute(lesson_query)).scalar() or 0
    
    # Count concepts
    concept_query = select(func.count(Concept.id))
    if difficulty:
        concept_query = concept_query.where(Concept.difficulty == difficulty)
    if grade_level:
        concept_query = concept_query.where(Concept.grade_level == grade_level)
    
    concept_count = (await db.execute(concept_query)).scalar() or 0
    
    return {
        "total_courses": course_count,
        "total_lessons": lesson_count,
        "total_concepts": concept_count,
        "total_items": course_count + lesson_count + concept_count,
    }


@router.get("/stats/by-subject")
async def get_stats_by_subject(db: AsyncSession = Depends(get_db)):
    """
    Get content statistics grouped by subject.
    """
    query = (
        select(
            Course.subject,
            func.count(Course.id).label("course_count"),
        )
        .where(Course.is_published == True)
        .group_by(Course.subject)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        {
            "subject": row.subject,
            "course_count": row.course_count,
        }
        for row in rows
    ]


@router.get("/stats/by-difficulty")
async def get_stats_by_difficulty(db: AsyncSession = Depends(get_db)):
    """
    Get content statistics grouped by difficulty level.
    """
    # Courses by difficulty
    course_query = (
        select(
            Course.difficulty,
            func.count(Course.id).label("count"),
        )
        .where(Course.is_published == True)
        .group_by(Course.difficulty)
    )
    
    course_result = await db.execute(course_query)
    course_stats = {row.difficulty: row.count for row in course_result}
    
    # Lessons by difficulty
    lesson_query = (
        select(
            Lesson.difficulty,
            func.count(Lesson.id).label("count"),
        )
        .where(Lesson.is_published == True)
        .group_by(Lesson.difficulty)
    )
    
    lesson_result = await db.execute(lesson_query)
    lesson_stats = {row.difficulty: row.count for row in lesson_result}
    
    # Concepts by difficulty
    concept_query = (
        select(
            Concept.difficulty,
            func.count(Concept.id).label("count"),
        )
        .group_by(Concept.difficulty)
    )
    
    concept_result = await db.execute(concept_query)
    concept_stats = {row.difficulty: row.count for row in concept_result}
    
    return {
        "courses": course_stats,
        "lessons": lesson_stats,
        "concepts": concept_stats,
    }
