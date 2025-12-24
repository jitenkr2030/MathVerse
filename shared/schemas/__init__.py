"""
MathVerse Shared Schemas Package

This package provides shared Pydantic schemas and data models used
across the MathVerse platform. All services should use these schemas
to ensure consistent data structures and validation.
"""

from .common import (
    APIResponse,
    PaginationParams,
    PaginationMeta,
    ErrorResponse,
    HealthResponse,
    BaseModel
)

from .users import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    StudentProfile,
    TeacherProfile,
    AdminProfile,
    UserRole
)

from .content import (
    ContentBase,
    ContentCreate,
    ContentUpdate,
    ContentResponse,
    ContentType,
    ContentStatus,
    ConceptNode,
    Course,
    Lesson,
    VideoContent,
    QuizContent
)

__all__ = [
    # Common schemas
    "APIResponse",
    "PaginationParams", 
    "PaginationMeta",
    "ErrorResponse",
    "HealthResponse",
    "BaseModel",
    
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "StudentProfile",
    "TeacherProfile",
    "AdminProfile",
    "UserRole",
    
    # Content schemas
    "ContentBase",
    "ContentCreate",
    "ContentUpdate",
    "ContentResponse",
    "ContentType",
    "ContentStatus",
    "ConceptNode",
    "Course",
    "Lesson",
    "VideoContent",
    "QuizContent"
]
