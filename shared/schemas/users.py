"""
User Schemas Module

This module provides Pydantic schemas for user-related data models.
It defines user base schemas, creation, update, and response models
for the MathVerse platform.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"
    CREATOR = "creator"


class LearningStyle(str, Enum):
    """Student learning style enumeration."""
    
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"
    MIXED = "mixed"


class UserBase(BaseModel):
    """Base user schema with common fields."""
    
    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, pattern=r"^\+?[1-9]\d{1,14}$")
    avatar_url: Optional[str] = Field(default=None, description="URL to user avatar")
    bio: Optional[str] = Field(default=None, max_length=500)
    language: str = Field(default="en", max_length=10)
    timezone: str = Field(default="UTC", max_length=50)


class UserCreate(UserBase):
    """Schema for creating a new user."""
    
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = Field(default=UserRole.STUDENT)
    terms_accepted: bool = Field(..., description="Acceptance of terms of service")
    marketing_consent: bool = Field(default=False, description="Marketing email consent")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "securepassword123",
                "role": "student",
                "terms_accepted": True
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, pattern=r"^\+?[1-9]\d{1,14}$")
    avatar_url: Optional[str] = default=None
    bio: Optional[str] = Field(default=None, max_length=500)
    language: Optional[str] = Field(default=None, max_length=10)
    timezone: Optional[str] = Field(default=None, max_length=50)
    preferences: Optional[Dict[str, Any]] = default=None


class UserResponse(UserBase):
    """Schema for user response data."""
    
    id: str = Field(..., description="Unique user identifier")
    role: UserRole
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login request."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    remember_me: bool = Field(default=False, description="Extended session duration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "securepassword123",
                "remember_me": True
            }
        }


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    
    refresh_token: str = Field(..., description="Refresh token")


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    
    email: EmailStr = Field(..., description="User email address")
    
    class Config:
        json_schema_extra = {
            "example": {"email": "student@example.com"}
        }


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128)


class PasswordChange(BaseModel):
    """Schema for password change."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128)


class StudentProfile(BaseModel):
    """Schema for student-specific profile data."""
    
    student_id: str = Field(..., description="Reference to user ID")
    grade_level: Optional[int] = Field(default=None, ge=1, le=12)
    learning_style: LearningStyle = Field(default=LearningStyle.MIXED)
    preferred_difficulty: str = Field(default="intermediate")
    daily_goal_minutes: int = Field(default=30, ge=5, ge=180)
    weak_areas: List[str] = Field(default_factory=list)
    strong_areas: List[str] = Field(default_factory=list)
    completed_courses: List[str] = Field(default_factory=list)
    current_courses: List[str] = Field(default_factory=list)
    total_points: int = Field(default=0)
    achievements: List[str] = Field(default_factory=list)
    streak_days: int = Field(default=0)
    last_activity_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TeacherProfile(BaseModel):
    """Schema for teacher-specific profile data."""
    
    teacher_id: str = Field(..., description="Reference to user ID")
    subject_specialization: List[str] = Field(default_factory=list)
    years_experience: Optional[int] = Field(default=None, ge=0)
    qualifications: List[str] = Field(default_factory=list)
    school: Optional[str] = None
    classes: List[str] = Field(default_factory=list)
    total_students: int = Field(default=0)
    courses_created: int = Field(default=0)
    average_rating: float = Field(default=0.0)
    total_reviews: int = Field(default=0)
    
    class Config:
        from_attributes = True


class AdminProfile(BaseModel):
    """Schema for admin-specific profile data."""
    
    admin_id: str = Field(..., description="Reference to user ID")
    permissions: List[str] = Field(default_factory=list)
    department: Optional[str] = None
    superuser: bool = Field(default=False)
    audit_log_access: bool = Field(default=False)
    
    class Config:
        from_attributes = True


class UserPreferences(BaseModel):
    """Schema for user preferences."""
    
    user_id: str
    theme: str = Field(default="light")
    language: str = Field(default="en")
    notifications: Dict[str, bool] = Field(default_factory=lambda: {
        "email": True,
        "push": True,
        "sms": False,
        "weekly_progress": True,
        "marketing": False
    })
    privacy_settings: Dict[str, bool] = Field(default_factory=lambda: {
        "show_profile": True,
        "show_progress": True,
        "allow_analytics": True
    })
    display_settings: Dict[str, Any] = Field(default_factory=lambda: {
        "items_per_page": 20,
        "auto_play_videos": True,
        "show_subtitles": True
    })
    updated_at: datetime = Field(default_factory=datetime.now)
