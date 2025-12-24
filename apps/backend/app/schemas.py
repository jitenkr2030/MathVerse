"""
MathVerse Backend API - Schemas Module
=======================================
Pydantic models for request/response validation and data serialization.
"""

from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from enum import Enum


# ==================== ENUMS ====================

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    CREATOR = "creator"
    ADMIN = "admin"


class CourseLevel(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SENIOR_SECONDARY = "senior_secondary"
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"


class ContentType(str, Enum):
    VIDEO = "video"
    ANIMATION = "animation"
    INTERACTIVE = "interactive"
    TEXT = "text"
    QUIZ = "quiz"


class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    FILL_BLANK = "fill_blank"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    INSTITUTIONAL = "institutional"


# ==================== AUTH SCHEMAS ====================

class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    role: UserRole = UserRole.STUDENT

    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "username": "mathstudent",
                "password": "securepassword123",
                "full_name": "John Doe",
                "role": "student"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "student@example.com",
                "password": "securepassword123"
            }
        }


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry time in seconds")


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None
    exp: Optional[datetime] = None


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str = Field(..., description="Valid refresh token")


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="Email address to send reset link")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(..., min_length=8, description="New password")


class ChangePasswordRequest(BaseModel):
    """Schema for changing password (authenticated)."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    username: str
    full_name: str
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserProfile(UserResponse):
    """Extended user profile with additional details."""
    bio: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    enrolled_courses_count: int = 0
    completed_courses_count: int = 0
    total_learning_hours: float = 0.0


# ==================== COURSE SCHEMAS ====================

class CourseBase(BaseModel):
    """Base course schema."""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    level: CourseLevel
    subject: str
    thumbnail_url: Optional[str] = None


class CourseCreate(CourseBase):
    """Schema for creating a course."""
    price: float = Field(default=0.0, ge=0, description="Course price in USD")
    is_free: bool = True
    tags: Optional[List[str]] = None


class CourseUpdate(BaseModel):
    """Schema for updating a course."""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    is_free: Optional[bool] = None
    is_published: Optional[bool] = None
    tags: Optional[List[str]] = None


class CourseResponse(CourseBase):
    """Course response schema."""
    id: int
    creator_id: int
    price: float
    is_free: bool
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    lessons_count: int = 0
    enrollments_count: int = 0
    average_rating: float = 0.0

    class Config:
        from_attributes = True


class CourseDetailResponse(CourseResponse):
    """Detailed course response with lessons."""
    creator: UserResponse
    lessons: List["LessonPreviewResponse"] = []
    tags: List[str] = []


class CourseListResponse(BaseModel):
    """Paginated course list response."""
    courses: List[CourseResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class CourseEnrollmentResponse(BaseModel):
    """Course enrollment response."""
    enrollment_id: int
    course: CourseResponse
    enrolled_at: datetime


# ==================== LESSON SCHEMAS ====================

class LessonBase(BaseModel):
    """Base lesson schema."""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    content: Optional[str] = None


class LessonCreate(LessonBase):
    """Schema for creating a lesson."""
    course_id: int
    order_index: int = Field(default=0, ge=0)
    video_url: Optional[str] = None
    video_duration: Optional[int] = None
    animation_scene_path: Optional[str] = None
    animation_class: Optional[str] = None
    is_published: bool = False


class LessonUpdate(BaseModel):
    """Schema for updating a lesson."""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    content: Optional[str] = None
    order_index: Optional[int] = Field(None, ge=0)
    video_url: Optional[str] = None
    video_duration: Optional[int] = None
    animation_scene_path: Optional[str] = None
    animation_class: Optional[str] = None
    is_published: Optional[bool] = None


class LessonResponse(LessonBase):
    """Lesson response schema."""
    id: int
    course_id: int
    video_url: Optional[str] = None
    video_duration: Optional[int] = None
    animation_scene_path: Optional[str] = None
    animation_class: Optional[str] = None
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    order_index: int = 0

    class Config:
        from_attributes = True


class LessonDetailResponse(LessonResponse):
    """Detailed lesson response with quizzes."""
    quizzes: List["QuizPreviewResponse"] = []
    progress: Optional[Dict[str, Any]] = None


class LessonPreviewResponse(BaseModel):
    """Preview lesson for course listing."""
    id: int
    title: str
    description: Optional[str] = None
    video_duration: Optional[int] = None
    order_index: int
    is_completed: bool = False

    class Config:
        from_attributes = True


# ==================== VIDEO SCHEMAS ====================

class VideoBase(BaseModel):
    """Base video schema."""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None


class VideoCreate(VideoBase):
    """Schema for creating video metadata."""
    lesson_id: int
    url: str
    duration: int = Field(..., ge=0, description="Duration in seconds")
    quality: str = "720p"
    file_size: Optional[int] = None
    format: str = "mp4"


class VideoResponse(VideoBase):
    """Video response schema."""
    id: int
    lesson_id: int
    url: str
    duration: int
    quality: str
    file_size: Optional[int] = None
    format: str
    created_at: datetime

    class Config:
        from_attributes = True


class VideoStreamingResponse(BaseModel):
    """Video streaming response with signed URL."""
    video: VideoResponse
    streaming_url: str
    expires_at: datetime


class AnimationRenderRequest(BaseModel):
    """Request to render an animation."""
    lesson_id: int
    scene_path: str
    scene_class: str
    quality: str = "medium"
    output_format: str = "mp4"
    voiceover_text: Optional[str] = None


class AnimationRenderResponse(BaseModel):
    """Animation render job response."""
    job_id: str
    status: str
    estimated_time: int  # seconds
    created_at: datetime


# ==================== QUIZ SCHEMAS ====================

class QuestionOption(BaseModel):
    """Schema for a quiz question option."""
    id: str
    text: str
    is_correct: bool


class QuestionCreate(BaseModel):
    """Schema for creating a question."""
    quiz_id: int
    question_text: str = Field(..., min_length=10)
    question_type: QuestionType
    options: Optional[List[QuestionOption]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    points: float = Field(default=1.0, ge=0)
    order_index: int = Field(default=0, ge=0)


class QuestionResponse(BaseModel):
    """Question response schema."""
    id: int
    quiz_id: int
    question_text: str
    question_type: QuestionType
    options: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None
    points: float
    order_index: int

    class Config:
        from_attributes = True


class QuizBase(BaseModel):
    """Base quiz schema."""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None


class QuizCreate(QuizBase):
    """Schema for creating a quiz."""
    lesson_id: int
    time_limit: Optional[int] = Field(None, ge=1, description="Time limit in minutes")
    passing_score: float = Field(default=70.0, ge=0, le=100)
    questions: List[QuestionCreate] = []


class QuizUpdate(BaseModel):
    """Schema for updating a quiz."""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    time_limit: Optional[int] = Field(None, ge=1)
    passing_score: Optional[float] = Field(None, ge=0, le=100)


class QuizResponse(QuizBase):
    """Quiz response schema."""
    id: int
    lesson_id: int
    time_limit: Optional[int] = None
    passing_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class QuizDetailResponse(QuizResponse):
    """Detailed quiz response with questions."""
    questions: List[QuestionResponse] = []


class QuizPreviewResponse(BaseModel):
    """Preview quiz for lesson listing."""
    id: int
    title: str
    description: Optional[str] = None
    questions_count: int = 0

    class Config:
        from_attributes = True


class QuizAttemptCreate(BaseModel):
    """Schema for submitting a quiz attempt."""
    answers: Dict[str, str] = Field(..., description="Question ID to answer mapping")


class QuizAttemptResponse(BaseModel):
    """Quiz attempt response schema."""
    id: int
    user_id: int
    quiz_id: int
    score: Optional[float] = None
    total_points: float
    percentage: Optional[float] = None
    passed: bool = False
    started_at: datetime
    completed_at: Optional[datetime] = None
    answers: Dict[str, Any]

    class Config:
        from_attributes = True


# ==================== PROGRESS SCHEMAS ====================

class ProgressBase(BaseModel):
    """Base progress schema."""
    lesson_id: int


class ProgressUpdate(BaseModel):
    """Schema for updating progress."""
    watch_time: Optional[int] = Field(None, ge=0, description="Watch time in seconds")
    last_position: Optional[int] = Field(None, ge=0, description="Last video position in seconds")
    completion_percentage: Optional[float] = Field(None, ge=0, le=100)


class ProgressResponse(ProgressBase):
    """Progress response schema."""
    id: int
    user_id: int
    is_completed: bool
    completion_percentage: float
    watch_time: int
    last_position: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CourseProgressResponse(BaseModel):
    """Course progress response."""
    course_id: int
    course_title: str
    total_lessons: int
    completed_lessons: int
    progress_percentage: float
    last_accessed_lesson: Optional[Dict[str, Any]] = None
    estimated_time_remaining: int  # seconds


class UserStatsResponse(BaseModel):
    """User learning statistics response."""
    total_courses_enrolled: int
    total_courses_completed: int
    total_lessons_completed: int
    total_quizzes_passed: int
    total_learning_time: int  # seconds
    average_quiz_score: float
    current_streak: int  # days
    longest_streak: int  # days


# ==================== PAYMENT SCHEMAS ====================

class PaymentBase(BaseModel):
    """Base payment schema."""
    amount: float = Field(..., ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)


class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""
    course_id: int
    payment_method: str = "stripe"


class PaymentResponse(PaymentBase):
    """Payment response schema."""
    id: int
    user_id: int
    course_id: int
    status: PaymentStatus
    payment_method: str
    stripe_payment_intent_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentIntentResponse(BaseModel):
    """Payment intent response for Stripe."""
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str


class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription."""
    tier: SubscriptionTier
    payment_method_id: str


class SubscriptionResponse(BaseModel):
    """Subscription response schema."""
    id: int
    user_id: int
    tier: SubscriptionTier
    starts_at: datetime
    expires_at: datetime
    is_active: bool


class CreatorEarningsResponse(BaseModel):
    """Creator earnings response."""
    total_earnings: float
    pending_earnings: float
    paid_earnings: float
    this_month_earnings: float
    transactions: List[Dict[str, Any]] = []


# ==================== CREATOR SCHEMAS ====================

class CreatorApplicationBase(BaseModel):
    """Base creator application schema."""
    portfolio_url: Optional[str] = None
    teaching_experience: Optional[str] = None
    specialization: List[str] = []
    motivation: str = Field(..., min_length=50)


class CreatorApplicationCreate(CreatorApplicationBase):
    """Schema for creator application."""
    pass


class CreatorApplicationResponse(CreatorApplicationBase):
    """Creator application response."""
    id: int
    user_id: int
    status: str
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[int] = None
    created_at: datetime


class CreatorDashboardResponse(BaseModel):
    """Creator dashboard response."""
    total_courses: int
    published_courses: int
    total_students: int
    total_revenue: float
    average_rating: float
    recent_enrollments: List[Dict[str, Any]] = []
    revenue_by_month: List[Dict[str, Any]] = []


class CourseAnalyticsResponse(BaseModel):
    """Course analytics response."""
    course_id: int
    views: int
    unique_viewers: int
    enrollments: int
    completion_rate: float
    average_rating: float
    revenue: float
    daily_views: List[Dict[str, Any]] = []


# ==================== COMMON SCHEMAS ====================

class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    error_code: Optional[str] = None
    additional_info: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    items: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
    timestamp: datetime
    dependencies: Dict[str, str] = {}


class SearchQuery(BaseModel):
    """Search query schema."""
    query: str = Field(..., min_length=2, max_length=200)
    type: Optional[str] = None  # course, lesson, video
    level: Optional[CourseLevel] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class SearchResultItem(BaseModel):
    """Search result item."""
    id: int
    type: str
    title: str
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    url: str
    relevance_score: float


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str
    total_results: int
    results: List[SearchResultItem]
    page: int
    total_pages: int


# Update forward references
CourseDetailResponse.model_rebuild()
LessonDetailResponse.model_rebuild()
