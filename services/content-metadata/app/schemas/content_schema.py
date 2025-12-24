from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


# Enums
class ContentType(str, Enum):
    VIDEO = "video"
    EXERCISE = "exercise"
    WORKSHEET = "worksheet"
    ARTICLE = "article"
    INTERACTIVE = "interactive"
    ANIMATION = "animation"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LessonType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    INTERACTIVE = "interactive"
    QUIZ = "quiz"
    EXERCISE = "exercise"
    ASSIGNMENT = "assignment"


class ConceptType(str, Enum):
    DEFINITION = "definition"
    THEOREM = "theorem"
    FORMULA = "formula"
    PROCEDURE = "procedure"
    EXAMPLE = "example"


# Course Schemas
class ConceptBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    concept_type: ConceptType = ConceptType.DEFINITION
    formula_latex: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    grade_level: int = Field(default=6, ge=1, ge=12)
    keywords: List[str] = []


class ConceptCreate(ConceptBase):
    pass


class ConceptUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    concept_type: Optional[ConceptType] = None
    formula_latex: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    grade_level: Optional[int] = Field(None, ge=1, ge=12)
    keywords: Optional[List[str]] = None


class ConceptResponse(ConceptBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ConceptDetailResponse(ConceptResponse):
    courses: List[int] = []
    lessons: List[int] = []
    prerequisites: List[int] = []
    dependents: List[int] = []


# Lesson Schemas
class LessonBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    content_type: LessonType = LessonType.VIDEO
    video_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    order_index: int = 0
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER


class LessonCreate(LessonBase):
    course_id: int
    concept_ids: List[int] = []


class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    content_type: Optional[LessonType] = None
    video_url: Optional[str] = None
    duration_minutes: Optional[int] = None
    order_index: Optional[int] = None
    difficulty: Optional[DifficultyLevel] = None
    is_published: Optional[bool] = None


class LessonResponse(LessonBase):
    id: int
    course_id: int
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class LessonDetailResponse(LessonResponse):
    concepts: List[ConceptResponse] = []


# Course Schemas
class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    subject: str = Field(..., min_length=1, max_length=100)
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    grade_level: int = Field(default=6, ge=1, ge=12)
    is_premium: bool = False
    estimated_hours: Optional[float] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=100)
    difficulty: Optional[DifficultyLevel] = None
    grade_level: Optional[int] = Field(None, ge=1, ge=12)
    is_premium: Optional[bool] = None
    estimated_hours: Optional[float] = None
    is_published: Optional[bool] = None


class CourseResponse(CourseBase):
    id: int
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CourseDetailResponse(CourseResponse):
    lessons: List[LessonResponse] = []
    total_duration_minutes: Optional[int] = None
    total_lessons: int = 0


# Pagination Schemas
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    per_page: int
    pages: int


# Search Schemas
class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    type_filter: Optional[List[str]] = None
    difficulty_filter: Optional[List[str]] = None
    subject_filter: Optional[List[str]] = None
    grade_level: Optional[int] = None


class SearchResult(BaseModel):
    id: int
    type: str
    title: str
    description: Optional[str] = None
    subject: Optional[str] = None
    difficulty: Optional[str] = None
    relevance_score: float


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResult]
    took_ms: float


# Curriculum/Taxonomy Schemas
class SyllabusNodeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    node_type: str = Field(..., description="grade, subject, unit, topic")
    order_index: int = 0


class SyllabusNodeCreate(SyllabusNodeBase):
    parent_id: Optional[int] = None


class SyllabusNodeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    order_index: Optional[int] = None


class SyllabusNodeResponse(SyllabusNodeBase):
    id: int
    parent_id: Optional[int] = None
    path: str = ""
    depth: int = 0

    class Config:
        from_attributes = True


class SyllabusTreeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    node_type: str
    children: List = []
