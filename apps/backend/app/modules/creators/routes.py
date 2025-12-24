"""
MathVerse Backend API - Creators Module
========================================
Creator portal endpoints for course creation and management.
"""

from typing import Optional, List, Dict
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload
import shutil
import os

from app.database import get_db
from app.models import (
    User, Course, Lesson, Quiz, Question, Enrollment, Payment,
    CreatorApplication, UserRole
)
from app.schemas import (
    CreatorApplicationCreate, CreatorApplicationResponse,
    CreatorDashboardResponse, CourseAnalyticsResponse,
    MessageResponse, ErrorResponse
)
from app.dependencies import get_current_user, get_or_404, require_role


router = APIRouter()


# ==================== CREATOR APPLICATION ====================

@router.post("/apply", response_model=CreatorApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_for_creator(
    application_data: CreatorApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit creator application.
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already a creator or teacher"
        )
    
    # Check for existing application
    existing = db.execute(
        select(CreatorApplication).where(
            and_(
                CreatorApplication.user_id == current_user.id,
                CreatorApplication.status == "pending"
            )
        )
    ).scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a pending application"
        )
    
    application = CreatorApplication(
        user_id=current_user.id,
        portfolio_url=application_data.portfolio_url,
        teaching_experience=application_data.teaching_experience,
        specialization=application_data.specialization,
        motivation=application_data.motivation,
        status="pending"
    )
    
    db.add(application)
    db.commit()
    db.refresh(application)
    
    return application


@router.get("/application", response_model=CreatorApplicationResponse)
async def get_application_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's creator application status.
    """
    application = db.execute(
        select(CreatorApplication).where(
            CreatorApplication.user_id == current_user.id
        )
        .order_by(CreatorApplication.created_at.desc())
    ).scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No application found"
        )
    
    return application


# ==================== CREATOR DASHBOARD ====================

@router.get("/dashboard", response_model=CreatorDashboardResponse)
async def get_creator_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get creator dashboard with overview statistics.
    """
    if current_user.role not in [UserRole.CREATOR, UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Creator access required"
        )
    
    # Get course counts
    total_courses = db.execute(
        select(func.count(Course.id)).where(Course.creator_id == current_user.id)
    ).scalar() or 0
    
    published_courses = db.execute(
        select(func.count(Course.id)).where(
            and_(
                Course.creator_id == current_user.id,
                Course.is_published == True
            )
        )
    ).scalar() or 0
    
    # Get total students
    creator_courses = db.execute(
        select(Course.id).where(Course.creator_id == current_user.id)
    ).scalars().all()
    
    total_students = 0
    if creator_courses:
        total_students = db.execute(
            select(func.count(Enrollment.id)).where(
                Enrollment.course_id.in_(creator_courses)
            )
        ).scalar() or 0
    
    # Get total revenue
    total_revenue = 0
    if creator_courses:
        total_revenue = db.execute(
            select(func.sum(Payment.amount)).where(
                and_(
                    Payment.course_id.in_(creator_courses),
                    Payment.status == "completed"
                )
            )
        ).scalar() or 0
    
    # Get average rating (simplified)
    average_rating = 0.0
    
    # Get recent enrollments
    recent_enrollments = db.execute(
        select(Enrollment)
        .options(joinedload(Enrollment.user), joinedload(Enrollment.course))
        .where(Enrollment.course_id.in_(creator_courses) if creator_courses else False)
        .order_by(Enrollment.enrolled_at.desc())
        .limit(10)
    ).unique().scalars().all()
    
    enrollment_list = []
    for enrollment in recent_enrollments:
        enrollment_list.append({
            "student_id": enrollment.user_id,
            "student_name": enrollment.user.full_name if enrollment.user else None,
            "course_id": enrollment.course_id,
            "course_title": enrollment.course.title if enrollment.course else None,
            "enrolled_at": enrollment.enrolled_at
        })
    
    # Get monthly revenue (simplified)
    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = db.execute(
        select(func.sum(Payment.amount)).where(
            and_(
                Payment.course_id.in_(creator_courses) if creator_courses else False,
                Payment.status == "completed",
                Payment.created_at >= start_of_month
            )
        )
    ).scalar() or 0
    
    revenue_by_month = [
        {"month": "Jan", "revenue": monthly_revenue},
        {"month": "Feb", "revenue": 0},
        {"month": "Mar", "revenue": 0},
        {"month": "Apr", "revenue": 0},
        {"month": "May", "revenue": 0},
        {"month": "Jun", "revenue": 0},
    ]
    
    return CreatorDashboardResponse(
        total_courses=total_courses,
        published_courses=published_courses,
        total_students=total_students,
        total_revenue=total_revenue * 0.70,  # 70% revenue share
        average_rating=average_rating,
        recent_enrollments=enrollment_list,
        revenue_by_month=revenue_by_month
    )


# ==================== COURSE MANAGEMENT ====================

@router.get("/courses", response_model=List[dict])
async def get_creator_courses(
    include_unpublished: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all courses created by the current user.
    """
    query = select(Course).where(Course.creator_id == current_user.id)
    
    if not include_unpublished:
        query = query.where(Course.is_published == True)
    
    courses = db.execute(query.order_by(Course.created_at.desc())).scalars().all()
    
    course_list = []
    for course in courses:
        lessons_count = db.execute(
            select(func.count(Lesson.id)).where(Lesson.course_id == course.id)
        ).scalar() or 0
        
        enrollments_count = db.execute(
            select(func.count(Enrollment.id)).where(Enrollment.course_id == course.id)
        ).scalar() or 0
        
        revenue = db.execute(
            select(func.sum(Payment.amount)).where(
                and_(
                    Payment.course_id == course.id,
                    Payment.status == "completed"
                )
            )
        ).scalar() or 0
        
        course_list.append({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "level": course.level,
            "subject": course.subject,
            "is_published": course.is_published,
            "is_free": course.is_free,
            "price": course.price,
            "lessons_count": lessons_count,
            "enrollments_count": enrollments_count,
            "revenue": revenue * 0.70,
            "created_at": course.created_at,
            "updated_at": course.updated_at
        })
    
    return course_list


@router.get("/courses/{course_id}/analytics", response_model=CourseAnalyticsResponse)
async def get_course_analytics(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for a specific course.
    """
    course = await get_or_404(Course, course_id, db, "Course not found")
    
    if course.creator_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this course's analytics"
        )
    
    # Views (simplified - would track in production)
    views = 0
    
    # Unique viewers
    unique_viewers = db.execute(
        select(func.count(func.distinct(Enrollment.user_id))).where(
            Enrollment.course_id == course_id
        )
    ).scalar() or 0
    
    # Enrollments
    enrollments = db.execute(
        select(func.count(Enrollment.id)).where(Enrollment.course_id == course_id)
    ).scalar() or 0
    
    # Completion rate
    completed = db.execute(
        select(func.count(Enrollment.id)).where(
            and_(
                Enrollment.course_id == course_id,
                Enrollment.completed_at.isnot(None)
            )
        )
    ).scalar() or 0
    
    completion_rate = (completed / enrollments * 100) if enrollments > 0 else 0
    
    # Revenue
    revenue = db.execute(
        select(func.sum(Payment.amount)).where(
            and_(
                Payment.course_id == course_id,
                Payment.status == "completed"
            )
        )
    ).scalar() or 0
    
    return CourseAnalyticsResponse(
        course_id=course_id,
        views=views,
        unique_viewers=unique_viewers,
        enrollments=enrollments,
        completion_rate=round(completion_rate, 2),
        average_rating=0.0,  # Would calculate from reviews
        revenue=revenue * 0.70,
        daily_views=[]  # Would track daily views
    )


# ==================== CONTENT MANAGEMENT ====================

@router.post("/upload/thumbnail")
async def upload_thumbnail(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a course thumbnail.
    """
    # In production, upload to cloud storage
    # For now, save locally
    
    upload_dir = "uploads/thumbnails"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{current_user.id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "url": f"/uploads/thumbnails/{current_user.id}_{file.filename}",
        "filename": file.filename
    }


@router.post("/upload/video")
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a lesson video.
    """
    # In production, upload to cloud storage (S3, etc.)
    
    upload_dir = "uploads/videos"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, f"{current_user.id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "url": f"/uploads/videos/{current_user.id}_{file.filename}",
        "filename": file.filename,
        "size": os.path.getsize(file_path)
    }


# ==================== STUDENT MANAGEMENT ====================

@router.get("/students")
async def get_enrolled_students(
    course_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of students enrolled in creator's courses.
    """
    creator_courses = db.execute(
        select(Course.id).where(Course.creator_id == current_user.id)
    ).scalars().all()
    
    if not creator_courses:
        return {"students": [], "total": 0}
    
    query_courses = creator_courses
    if course_id:
        query_courses = [course_id]
    
    offset = (page - 1) * per_page
    
    enrollments = db.execute(
        select(Enrollment)
        .options(joinedload(Enrollment.user))
        .where(Enrollment.course_id.in_(query_courses))
        .order_by(Enrollment.enrolled_at.desc())
        .offset(offset)
        .limit(per_page)
    ).unique().scalars().all()
    
    total = db.execute(
        select(func.count(Enrollment.id)).where(
            Enrollment.course_id.in_(query_courses)
        )
    ).scalar()
    
    student_list = []
    for enrollment in enrollments:
        student_list.append({
            "id": enrollment.user.id if enrollment.user else None,
            "name": enrollment.user.full_name if enrollment.user else None,
            "email": enrollment.user.email if enrollment.user else None,
            "course_id": enrollment.course_id,
            "progress": enrollment.progress_percentage,
            "enrolled_at": enrollment.enrolled_at,
            "completed_at": enrollment.completed_at
        })
    
    return {
        "students": student_list,
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.get("/students/{student_id}")
async def get_student_details(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific student.
    """
    student = db.execute(
        select(User).where(User.id == student_id)
    ).scalar_one_or_none()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get courses this student is enrolled in from this creator
    creator_courses = db.execute(
        select(Course.id).where(Course.creator_id == current_user.id)
    ).scalars().all()
    
    if not creator_courses:
        return {
            "student": {
                "id": student.id,
                "name": student.full_name,
                "email": student.email
            },
            "courses": []
        }
    
    enrollments = db.execute(
        select(Enrollment)
        .options(joinedload(Enrollment.course))
        .where(
            and_(
                Enrollment.user_id == student_id,
                Enrollment.course_id.in_(creator_courses)
            )
        )
    ).unique().scalars().all()
    
    course_list = []
    for enrollment in enrollments:
        course_list.append({
            "course_id": enrollment.course_id,
            "course_title": enrollment.course.title if enrollment.course else None,
            "progress": enrollment.progress_percentage,
            "enrolled_at": enrollment.enrolled_at,
            "completed_at": enrollment.completed_at
        })
    
    return {
        "student": {
            "id": student.id,
            "name": student.full_name,
            "email": student.email,
            "avatar_url": student.avatar_url
        },
        "courses": course_list
    }
