"""
MathVerse Backend API - Progress Module
========================================
User progress tracking endpoints.
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models import Progress, Lesson, Course, Enrollment, User, UserRole
from app.schemas import (
    ProgressUpdate, ProgressResponse, CourseProgressResponse,
    UserStatsResponse, MessageResponse
)
from app.dependencies import get_current_user, get_or_404


router = APIRouter()


@router.get("/", response_model=List[ProgressResponse])
async def get_user_progress(
    course_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's progress for all lessons or specific course.
    """
    query = select(Progress).where(Progress.user_id == current_user.id)
    
    if course_id:
        lessons_in_course = db.execute(
            select(Lesson.id).where(Lesson.course_id == course_id)
        ).scalars().all()
        query = query.where(Progress.lesson_id.in_(lessons_in_course))
    
    progress_records = db.execute(
        query.order_by(Progress.updated_at.desc())
    ).scalars().all()
    
    return progress_records


@router.get("/lesson/{lesson_id}", response_model=ProgressResponse)
async def get_lesson_progress(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's progress for a specific lesson.
    """
    progress = db.execute(
        select(Progress).where(
            and_(
                Progress.user_id == current_user.id,
                Progress.lesson_id == lesson_id
            )
        )
    ).scalar_one_or_none()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found"
        )
    
    return progress


@router.put("/lesson/{lesson_id}", response_model=ProgressResponse)
async def update_lesson_progress(
    lesson_id: int,
    progress_data: ProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's progress for a lesson.
    """
    # Verify lesson exists
    lesson = await get_or_404(Lesson, lesson_id, db, "Lesson not found")
    
    # Check if enrolled in course
    enrollment = db.execute(
        select(Enrollment).where(
            and_(
                Enrollment.user_id == current_user.id,
                Enrollment.course_id == lesson.course_id
            )
        )
    ).scalar_one_or_none()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be enrolled in the course to track progress"
        )
    
    # Get or create progress
    progress = db.execute(
        select(Progress).where(
            and_(
                Progress.user_id == current_user.id,
                Progress.lesson_id == lesson_id
            )
        )
    ).scalar_one_or_none()
    
    if not progress:
        progress = Progress(
            user_id=current_user.id,
            lesson_id=lesson_id
        )
        db.add(progress)
    
    # Update progress
    if progress_data.watch_time is not None:
        progress.watch_time = progress_data.watch_time
    
    if progress_data.last_position is not None:
        progress.last_position = progress_data.last_position
    
    if progress_data.completion_percentage is not None:
        progress.completion_percentage = progress_data.completion_percentage
        if progress_data.completion_percentage >= 100:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(progress)
    
    # Update course enrollment progress
    update_course_progress(current_user.id, lesson.course_id, db)
    
    return progress


@router.post("/lesson/{lesson_id}/complete", response_model=ProgressResponse)
async def complete_lesson(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a lesson as completed.
    """
    lesson = await get_or_404(Lesson, lesson_id, db, "Lesson not found")
    
    # Get or create progress
    progress = db.execute(
        select(Progress).where(
            and_(
                Progress.user_id == current_user.id,
                Progress.lesson_id == lesson_id
            )
        )
    ).scalar_one_or_none()
    
    if not progress:
        progress = Progress(
            user_id=current_user.id,
            lesson_id=lesson_id
        )
        db.add(progress)
    
    progress.is_completed = True
    progress.completion_percentage = 100
    progress.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(progress)
    
    # Update course enrollment progress
    update_course_progress(current_user.id, lesson.course_id, db)
    
    return progress


@router.get("/course/{course_id}", response_model=CourseProgressResponse)
async def get_course_progress(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's progress for a specific course.
    """
    # Verify enrollment
    enrollment = db.execute(
        select(Enrollment).where(
            and_(
                Enrollment.user_id == current_user.id,
                Enrollment.course_id == course_id
            )
        )
    ).scalar_one_or_none()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enrolled in this course"
        )
    
    # Get course
    course = await get_or_404(Course, course_id, db, "Course not found")
    
    # Get all published lessons
    lessons = db.execute(
        select(Lesson).where(
            and_(Lesson.course_id == course_id, Lesson.is_published == True)
        )
    ).scalars().all()
    
    # Get completed lessons
    completed_count = db.execute(
        select(func.count(Progress.id)).where(
            and_(
                Progress.user_id == current_user.id,
                Progress.lesson_id.in_([l.id for l in lessons]),
                Progress.is_completed == True
            )
        )
    ).scalar() or 0
    
    # Get last accessed lesson
    last_progress = db.execute(
        select(Progress)
        .where(
            and_(
                Progress.user_id == current_user.id,
                Progress.lesson_id.in_([l.id for l in lessons])
            )
        )
        .order_by(Progress.updated_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    
    last_lesson = None
    if last_progress:
        last_lesson_obj = db.execute(
            select(Lesson).where(Lesson.id == last_progress.lesson_id)
        ).scalar_one_or_one()
        last_lesson = {
            "id": last_lesson_obj.id,
            "title": last_lesson_obj.title,
            "last_position": last_progress.last_position
        }
    
    # Calculate progress
    total_lessons = len(lessons)
    progress_percentage = (completed_count / total_lessons * 100) if total_lessons > 0 else 0
    
    # Calculate time remaining
    total_duration = sum(l.video_duration or 0 for l in lessons)
    watched_duration = db.execute(
        select(func.sum(Progress.watch_time)).where(
            and_(
                Progress.user_id == current_user.id,
                Progress.lesson_id.in_([l.id for l in lessons])
            )
        )
    ).scalar() or 0
    
    remaining_time = max(0, total_duration - watched_duration)
    
    return CourseProgressResponse(
        course_id=course_id,
        course_title=course.title,
        total_lessons=total_lessons,
        completed_lessons=completed_count,
        progress_percentage=round(progress_percentage, 2),
        last_accessed_lesson=last_lesson,
        estimated_time_remaining=remaining_time
    )


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive user learning statistics.
    """
    # Course statistics
    total_enrolled = db.execute(
        select(func.count(Enrollment.id)).where(Enrollment.user_id == current_user.id)
    ).scalar() or 0
    
    total_completed = db.execute(
        select(func.count(Enrollment.id)).where(
            and_(
                Enrollment.user_id == current_user.id,
                Enrollment.completed_at.isnot(None)
            )
        )
    ).scalar() or 0
    
    # Lesson statistics
    lessons_completed = db.execute(
        select(func.count(Progress.id)).where(
            and_(
                Progress.user_id == current_user.id,
                Progress.is_completed == True
            )
        )
    ).scalar() or 0
    
    # Quiz statistics
    from app.models import QuizAttempt
    quizzes_passed = db.execute(
        select(func.count(QuizAttempt.id)).where(
            and_(
                QuizAttempt.user_id == current_user.id,
                QuizAttempt.percentage >= 70
            )
        )
    ).scalar() or 0
    
    # Total learning time
    total_time = db.execute(
        select(func.sum(Progress.watch_time)).where(Progress.user_id == current_user.id)
    ).scalar() or 0
    
    # Average quiz score
    avg_score = db.execute(
        select(func.avg(QuizAttempt.percentage)).where(
            and_(
                QuizAttempt.user_id == current_user.id,
                QuizAttempt.completed_at.isnot(None)
            )
        )
    ).scalar() or 0.0
    
    # Streak calculation (simplified)
    activity_dates = db.execute(
        select(func.date_trunc('day', Progress.created_at))
        .where(Progress.user_id == current_user.id)
        .distinct()
    ).all()
    
    current_streak = min(len(activity_dates), 7) if activity_dates else 0
    longest_streak = len(activity_dates) if activity_dates else 0
    
    return UserStatsResponse(
        total_courses_enrolled=total_enrolled,
        total_courses_completed=total_completed,
        total_lessons_completed=lessons_completed,
        total_quizzes_passed=quizzes_passed,
        total_learning_time=total_time,
        average_quiz_score=round(avg_score, 2),
        current_streak=current_streak,
        longest_streak=longest_streak
    )


@router.get("/heatmap")
async def get_learning_heatmap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get learning activity heatmap data for the last year.
    """
    # Get unique activity dates with lesson counts
    from sqlalchemy import text
    
    result = db.execute(
        text("""
            SELECT DATE(created_at) as activity_date, COUNT(*) as lessons_completed
            FROM progress
            WHERE user_id = :user_id
              AND is_completed = true
              AND created_at >= DATE_SUB(NOW(), INTERVAL 365 DAY)
            GROUP BY DATE(created_at)
        """),
        {"user_id": current_user.id}
    ).all()
    
    heatmap_data = {}
    for row in result:
        heatmap_data[str(row.activity_date)] = row.lessons_completed
    
    return {
        "data": heatmap_data,
        "total_days_active": len(result)
    }


def update_course_progress(user_id: int, course_id: int, db: Session):
    """
    Update course enrollment progress percentage.
    """
    # Get enrollment
    enrollment = db.execute(
        select(Enrollment).where(
            and_(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id
            )
        )
    ).scalar_one_or_none()
    
    if not enrollment:
        return
    
    # Get all published lessons
    lessons = db.execute(
        select(Lesson.id).where(
            and_(Lesson.course_id == course_id, Lesson.is_published == True)
        )
    ).scalars().all()
    
    if not lessons:
        return
    
    # Get completed lessons
    completed = db.execute(
        select(func.count(Progress.id)).where(
            and_(
                Progress.user_id == user_id,
                Progress.lesson_id.in_(lessons),
                Progress.is_completed == True
            )
        )
    ).scalar() or 0
    
    # Update enrollment
    enrollment.progress_percentage = (completed / len(lessons)) * 100
    
    # Check if course is completed
    if enrollment.progress_percentage >= 100:
        enrollment.completed_at = datetime.utcnow()
    
    db.commit()
