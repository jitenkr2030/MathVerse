"""
MathVerse Backend API - Lessons Module
=======================================
Lesson management endpoints.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models import Lesson, Course, Quiz, Progress, User, UserRole
from app.schemas import (
    LessonCreate, LessonUpdate, LessonResponse, LessonDetailResponse,
    MessageResponse, ErrorResponse, QuizPreviewResponse
)
from app.dependencies import get_current_user, get_or_404


router = APIRouter()


@router.get("/", response_model=List[LessonResponse])
async def get_lessons(
    course_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all lessons, optionally filtered by course.
    """
    offset = (page - 1) * per_page
    
    query = select(Lesson)
    
    if course_id:
        query = query.where(Lesson.course_id == course_id)
    
    # Get total count
    total_query = select(func.count(Lesson.id))
    if course_id:
        total_query = total_query.where(Lesson.course_id == course_id)
    total = db.execute(total_query).scalar()
    
    # Get paginated results
    lessons = db.execute(
        query
        .order_by(Lesson.order_index)
        .offset(offset)
        .limit(per_page)
    ).scalars().all()
    
    return lessons


@router.get("/{lesson_id}", response_model=LessonDetailResponse)
async def get_lesson(
    lesson_id: int,
    current_user: Optional[User] = None,
    db: Session = Depends(get_db)
):
    """
    Get lesson details with quizzes and progress.
    """
    lesson = db.execute(
        select(Lesson)
        .options(joinedload(Lesson.quizzes))
        .where(Lesson.id == lesson_id)
    ).unique().scalar_one_or_none()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found"
        )
    
    if not lesson.is_published:
        # Check if user is enrolled (for unpublished lessons)
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Lesson is not published"
            )
        
        enrollment = db.execute(
            select(func.count(1)).where(
                and_(
                    select(Enrollment.id).where(
                        and_(
                            Enrollment.user_id == current_user.id,
                            Enrollment.course_id == lesson.course_id
                        )
                    ).exists()
                )
            )
        ).scalar()
        
        if enrollment == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be enrolled to access this lesson"
            )
    
    # Get progress if user is authenticated
    user_progress = None
    if current_user:
        progress = db.execute(
            select(Progress).where(
                and_(
                    Progress.user_id == current_user.id,
                    Progress.lesson_id == lesson_id
                )
            )
        ).scalar_one_or_none()
        
        if progress:
            user_progress = {
                "is_completed": progress.is_completed,
                "completion_percentage": progress.completion_percentage,
                "watch_time": progress.watch_time,
                "last_position": progress.last_position,
                "completed_at": progress.completed_at
            }
    
    # Get quizzes
    quizzes = db.execute(
        select(Quiz).where(Quiz.lesson_id == lesson_id)
    ).scalars().all()
    
    quiz_previews = []
    for quiz in quizzes:
        quiz_previews.append(QuizPreviewResponse(
            id=quiz.id,
            title=quiz.title,
            description=quiz.description,
            questions_count=0  # Will be populated if needed
        ))
    
    return LessonDetailResponse(
        id=lesson.id,
        title=lesson.title,
        description=lesson.description,
        content=lesson.content,
        course_id=lesson.course_id,
        video_url=lesson.video_url,
        video_duration=lesson.video_duration,
        animation_scene_path=lesson.animation_scene_path,
        animation_class=lesson.animation_class,
        is_published=lesson.is_published,
        created_at=lesson.created_at,
        updated_at=lesson.updated_at,
        order_index=lesson.order_index,
        quizzes=quiz_previews,
        progress=user_progress
    )


@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    lesson_data: LessonCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new lesson (course owner only).
    """
    # Verify course exists and user owns it
    course = db.execute(
        select(Course).where(Course.id == lesson_data.course_id)
    ).scalar_one_or_none()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if course.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add lessons to this course"
        )
    
    lesson = Lesson(
        title=lesson_data.title,
        description=lesson_data.description,
        content=lesson_data.content,
        course_id=lesson_data.course_id,
        order_index=lesson_data.order_index,
        video_url=lesson_data.video_url,
        video_duration=lesson_data.video_duration,
        animation_scene_path=lesson_data.animation_scene_path,
        animation_class=lesson_data.animation_class,
        is_published=lesson_data.is_published
    )
    
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    
    return lesson


@router.put("/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: int,
    lesson_data: LessonUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a lesson (course owner only).
    """
    lesson = await get_or_404(Lesson, lesson_id, db, "Lesson not found")
    
    # Verify course ownership
    course = db.execute(
        select(Course).where(Course.id == lesson.course_id)
    ).scalar_one_or_one()
    
    if course.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this lesson"
        )
    
    update_data = lesson_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(lesson, field, value)
    
    db.commit()
    db.refresh(lesson)
    
    return lesson


@router.delete("/{lesson_id}", response_model=MessageResponse)
async def delete_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a lesson (course owner only).
    """
    lesson = await get_or_404(Lesson, lesson_id, db, "Lesson not found")
    
    # Verify course ownership
    course = db.execute(
        select(Course).where(Course.id == lesson.course_id)
    ).scalar_one_or_one()
    
    if course.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this lesson"
        )
    
    db.delete(lesson)
    db.commit()
    
    return MessageResponse(
        message="Lesson deleted successfully",
        detail=f"Lesson '{lesson.title}' has been deleted"
    )


@router.put("/{lesson_id}/reorder", response_model=LessonResponse)
async def reorder_lesson(
    lesson_id: int,
    new_order: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reorder a lesson within a course.
    """
    lesson = await get_or_404(Lesson, lesson_id, db, "Lesson not found")
    
    # Verify course ownership
    course = db.execute(
        select(Course).where(Course.id == lesson.course_id)
    ).scalar_one_or_one()
    
    if course.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reorder lessons in this course"
        )
    
    # Update order
    lesson.order_index = new_order
    
    # Reorder other lessons
    all_lessons = db.execute(
        select(Lesson)
        .where(Lesson.course_id == lesson.course_id)
        .order_by(Lesson.order_index)
    ).scalars().all()
    
    current_order = 0
    for l in all_lessons:
        if l.id != lesson_id:
            l.order_index = current_order
            current_order += 1
    
    db.commit()
    db.refresh(lesson)
    
    return lesson


@router.get("/{lesson_id}/next")
async def get_next_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the next lesson in the course.
    """
    lesson = await get_or_404(Lesson, lesson_id, db, "Lesson not found")
    
    # Get next lesson by order
    next_lesson = db.execute(
        select(Lesson)
        .where(
            and_(
                Lesson.course_id == lesson.course_id,
                Lesson.order_index > lesson.order_index,
                Lesson.is_published == True
            )
        )
        .order_by(Lesson.order_index)
        .limit(1)
    ).scalar_one_or_none()
    
    if not next_lesson:
        return {"message": "This is the last lesson", "next_lesson": None}
    
    return {
        "next_lesson": {
            "id": next_lesson.id,
            "title": next_lesson.title,
            "description": next_lesson.description,
            "video_duration": next_lesson.video_duration
        }
    }


@router.get("/{lesson_id}/previous")
async def get_previous_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the previous lesson in the course.
    """
    lesson = await get_or_404(Lesson, lesson_id, db, "Lesson not found")
    
    # Get previous lesson by order
    prev_lesson = db.execute(
        select(Lesson)
        .where(
            and_(
                Lesson.course_id == lesson.course_id,
                Lesson.order_index < lesson.order_index,
                Lesson.is_published == True
            )
        )
        .order_by(Lesson.order_index.desc())
        .limit(1)
    ).scalar_one_or_none()
    
    if not prev_lesson:
        return {"message": "This is the first lesson", "previous_lesson": None}
    
    return {
        "previous_lesson": {
            "id": prev_lesson.id,
            "title": prev_lesson.title,
            "description": prev_lesson.description,
            "video_duration": prev_lesson.video_duration
        }
    }
