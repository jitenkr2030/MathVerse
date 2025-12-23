from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import Course, User, Enrollment
from app.modules.auth.routes import get_current_user

router = APIRouter()

class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    level: str
    subject: str
    price: float = 0.0
    is_free: bool = True
    thumbnail_url: Optional[str] = None

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None
    subject: Optional[str] = None
    price: Optional[float] = None
    is_free: Optional[bool] = None
    thumbnail_url: Optional[str] = None
    is_published: Optional[bool] = None

class CourseResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    level: str
    subject: str
    price: float
    is_free: bool
    thumbnail_url: Optional[str]
    is_published: bool
    creator_id: int
    created_at: str
    updated_at: Optional[str]
    enrollment_count: Optional[int] = 0

@router.get("/", response_model=List[CourseResponse])
async def get_courses(
    skip: int = 0,
    limit: int = 20,
    level: Optional[str] = None,
    subject: Optional[str] = None,
    is_free: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Course).filter(Course.is_published == True)
    
    if level:
        query = query.filter(Course.level == level)
    if subject:
        query = query.filter(Course.subject == subject)
    if is_free is not None:
        query = query.filter(Course.is_free == is_free)
    
    courses = query.offset(skip).limit(limit).all()
    
    course_responses = []
    for course in courses:
        enrollment_count = db.query(Enrollment).filter(Enrollment.course_id == course.id).count()
        course_responses.append({
            **course.__dict__,
            "enrollment_count": enrollment_count,
            "created_at": course.created_at.isoformat() if course.created_at else None,
            "updated_at": course.updated_at.isoformat() if course.updated_at else None
        })
    
    return course_responses

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    enrollment_count = db.query(Enrollment).filter(Enrollment.course_id == course.id).count()
    
    return {
        **course.__dict__,
        "enrollment_count": enrollment_count,
        "created_at": course.created_at.isoformat() if course.created_at else None,
        "updated_at": course.updated_at.isoformat() if course.updated_at else None
    }

@router.post("/", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = Course(
        title=course_data.title,
        description=course_data.description,
        level=course_data.level,
        subject=course_data.subject,
        price=course_data.price,
        is_free=course_data.is_free,
        thumbnail_url=course_data.thumbnail_url,
        creator_id=current_user.id
    )
    
    db.add(course)
    db.commit()
    db.refresh(course)
    
    return {
        **course.__dict__,
        "enrollment_count": 0,
        "created_at": course.created_at.isoformat() if course.created_at else None,
        "updated_at": course.updated_at.isoformat() if course.updated_at else None
    }

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if course.creator_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this course"
        )
    
    # Update course fields
    update_data = course_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    
    enrollment_count = db.query(Enrollment).filter(Enrollment.course_id == course.id).count()
    
    return {
        **course.__dict__,
        "enrollment_count": enrollment_count,
        "created_at": course.created_at.isoformat() if course.created_at else None,
        "updated_at": course.updated_at.isoformat() if course.updated_at else None
    }

@router.delete("/{course_id}")
async def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if course.creator_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this course"
        )
    
    db.delete(course)
    db.commit()
    
    return {"message": "Course deleted successfully"}

@router.post("/{course_id}/enroll")
async def enroll_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if already enrolled
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    # Create enrollment
    enrollment = Enrollment(
        user_id=current_user.id,
        course_id=course_id
    )
    
    db.add(enrollment)
    db.commit()
    
    return {"message": "Successfully enrolled in course"}