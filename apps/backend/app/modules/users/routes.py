"""
MathVerse Backend API - Users Module
=====================================
User management endpoints.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models import User, Course, Enrollment, Progress, QuizAttempt, UserRole
from app.schemas import (
    UserResponse, UserUpdate, UserProfile, UserStatsResponse,
    CourseListResponse, MessageResponse, ErrorResponse
)
from app.dependencies import get_current_user, get_or_404, require_admin


router = APIRouter()


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile with statistics.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserProfile: User profile with stats
    """
    # Get enrollment counts
    enrolled_count = db.execute(
        select(func.count(Enrollment.id)).where(Enrollment.user_id == current_user.id)
    ).scalar() or 0
    
    completed_count = db.execute(
        select(func.count(Enrollment.id)).where(
            and_(
                Enrollment.user_id == current_user.id,
                Enrollment.completed_at.isnot(None)
            )
        )
    ).scalar() or 0
    
    # Get total learning time
    total_time = db.execute(
        select(func.sum(Progress.watch_time)).where(Progress.user_id == current_user.id)
    ).scalar() or 0
    
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        enrolled_courses_count=enrolled_count,
        completed_courses_count=completed_count,
        total_learning_hours=round(total_time / 3600, 2)
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    
    Args:
        user_data: Profile update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserResponse: Updated user
    """
    update_data = user_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user learning statistics.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserStatsResponse: Learning statistics
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
        select(func.avg(QuizAttempt.percentage)).where(QuizAttempt.user_id == current_user.id)
    ).scalar() or 0.0
    
    # Streak calculations (simplified)
    current_streak = 0
    longest_streak = 0
    
    # Get unique days with activity
    from sqlalchemy import distinct
    activity_days = db.execute(
        select(func.date_trunc('day', Progress.created_at))
        .where(Progress.user_id == current_user.id)
        .distinct()
    ).all()
    
    # Simplified streak calculation
    if activity_days:
        current_streak = min(len(activity_days), 7)  # Placeholder
        longest_streak = len(activity_days)
    
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


@router.get("/enrollments", response_model=CourseListResponse)
async def get_user_enrollments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    include_completed: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's enrolled courses.
    
    Args:
        page: Page number
        per_page: Items per page
        include_completed: Include completed courses
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        CourseListResponse: Paginated enrolled courses
    """
    offset = (page - 1) * per_page
    
    # Base query
    query = (
        select(Enrollment)
        .options(joinedload(Enrollment.course))
        .where(Enrollment.user_id == current_user.id)
    )
    
    if not include_completed:
        query = query.where(Enrollment.completed_at.is_(None))
    
    # Get total count
    total_query = select(func.count(Enrollment.id)).where(
        and_(
            Enrollment.user_id == current_user.id,
            Enrollment.completed_at.is_(None) if not include_completed else True
        )
    )
    total = db.execute(total_query).scalar()
    
    # Get paginated results
    enrollments = db.execute(
        query
        .order_by(Enrollment.enrolled_at.desc())
        .offset(offset)
        .limit(per_page)
    ).unique().scalars().all()
    
    # Build course responses
    courses = []
    for enrollment in enrollments:
        course = enrollment.course
        courses.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "level": course.level,
            "subject": course.subject,
            "thumbnail_url": course.thumbnail_url,
            "creator_id": course.creator_id,
            "price": course.price,
            "is_free": course.is_free,
            "is_published": course.is_published,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
            "progress_percentage": enrollment.progress_percentage
        })
    
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0
    
    return CourseListResponse(
        courses=courses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.delete("/account", response_model=MessageResponse)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account (soft delete by deactivating).
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        MessageResponse: Success message
    """
    # Soft delete - just deactivate the user
    current_user.is_active = False
    db.commit()
    
    return MessageResponse(
        message="Account deactivated successfully",
        detail="Your account has been deactivated. You can contact support to restore it."
    )


# ==================== ADMIN ENDPOINTS ====================

@router.get("/", response_model=List[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    List all users (Admin only).
    
    Args:
        page: Page number
        per_page: Items per page
        role: Filter by role
        is_active: Filter by active status
        db: Database session
        
    Returns:
        List[UserResponse]: List of users
    """
    offset = (page - 1) * per_page
    
    query = select(User)
    
    if role:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    users = db.execute(
        query
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(per_page)
    ).scalars().all()
    
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user by ID (Admin only).
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        UserResponse: User details
    """
    user = await get_or_404(User, user_id, db, "User not found")
    return user


@router.put("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Activate a user account (Admin only).
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        UserResponse: Updated user
    """
    user = await get_or_404(User, user_id, db, "User not found")
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Deactivate a user account (Admin only).
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        UserResponse: Updated user
    """
    user = await get_or_404(User, user_id, db, "User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/verify", response_model=UserResponse)
async def verify_user_email(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Verify user email (Admin only).
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        UserResponse: Updated user
    """
    user = await get_or_404(User, user_id, db, "User not found")
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role: UserRole,
    db: Session = Depends(get_db)
):
    """
    Update user role (Admin only).
    
    Args:
        user_id: User ID
        role: New role
        db: Database session
        
    Returns:
        UserResponse: Updated user
    """
    user = await get_or_404(User, user_id, db, "User not found")
    user.role = role
    db.commit()
    db.refresh(user)
    return user
