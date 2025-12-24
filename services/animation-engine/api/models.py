"""
MathVerse Animation Engine - Pydantic Models
Request and response models for API validation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator


class SceneType(str, Enum):
    """Types of mathematical scenes available"""
    GRAPH = "graph"
    PROOF = "proof"
    GEOMETRY = "geometry"
    CALCULUS = "calculus"
    ALGEBRA = "algebra"
    STATISTICS = "statistics"
    CUSTOM = "custom"


class EducationalLevel(str, Enum):
    """Educational levels for content organization"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SENIOR_SECONDARY = "senior_secondary"
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"


class RenderQuality(str, Enum):
    """Video quality settings"""
    LOW = "l"      # 480p
    MEDIUM = "m"   # 720p
    HIGH = "h"     # 1080p
    FOUR_K = "k"   # 4K


class RenderStatus(str, Enum):
    """Status of a render job"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ==================== Request Models ====================

class GraphEquation(BaseModel):
    """Graph equation specification"""
    equation: str = Field(..., description="Mathematical equation (e.g., 'x^2', 'sin(x)')")
    x_range: Optional[List[float]] = Field(default=[-10, 10], description="X-axis range")
    y_range: Optional[List[float]] = Field(default=None, description="Y-axis range")
    x_label: Optional[str] = Field(default=None, description="X-axis label")
    y_label: Optional[str] = Field(default=None, description="Y-axis label")
    show_grid: bool = Field(default=True, description="Show grid lines")
    animate: bool = Field(default=True, description="Animate the graph drawing")


class StepEquation(BaseModel):
    """Equation for step-by-step solution display"""
    equation: str = Field(..., description="The equation to display")
    explanation: Optional[str] = Field(default=None, description="Explanation of this step")


class ProofStep(BaseModel):
    """Proof step specification"""
    statement: str = Field(..., description="The mathematical statement/proof step")
    justification: Optional[str] = Field(default=None, description="Reasoning/justification")
    highlight_changes: bool = Field(default=True, description="Highlight changed parts")


class GeometryShape(BaseModel):
    """Geometry shape specification"""
    shape_type: str = Field(..., description="Type: 'circle', 'triangle', 'rectangle', 'polygon'")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Shape parameters")
    position: Optional[List[float]] = Field(default=None, description="Center position [x, y]")
    color: Optional[str] = Field(default=None, description="Shape color")
    label: Optional[str] = Field(default=None, description="Shape label")


class AnimationEffect(BaseModel):
    """Animation effect specification"""
    type: str = Field(..., description="Effect type: 'fade', 'scale', 'rotate', 'translate'")
    target: str = Field(..., description="Target element identifier")
    duration: float = Field(default=1.0, description="Animation duration in seconds")
    delay: float = Field(default=0.0, description="Delay before animation starts")


class RenderRequest(BaseModel):
    """Request model for rendering a mathematical animation"""
    
    # Scene configuration
    scene_type: SceneType = Field(..., description="Type of mathematical scene")
    level: EducationalLevel = Field(..., description="Educational level")
    title: Optional[str] = Field(default=None, description="Scene title")
    subtitle: Optional[str] = Field(default=None, description="Scene subtitle")
    
    # Content
    equations: Optional[List[Union[str, StepEquation]]] = Field(
        default=None, 
        description="Equations to display or solve"
    )
    graph: Optional[GraphEquation] = Field(default=None, description="Graph configuration")
    shapes: Optional[List[GeometryShape]] = Field(default=None, description="Geometry shapes")
    proof_steps: Optional[List[ProofStep]] = Field(default=None, description="Proof steps")
    
    # Animation
    animations: Optional[List[AnimationEffect]] = Field(
        default=None, 
        description="Custom animation effects"
    )
    
    # Style customization
    primary_color: Optional[str] = Field(default="#3B82F6", description="Primary brand color")
    secondary_color: Optional[str] = Field(default="#10B981", description="Secondary color")
    text_color: Optional[str] = Field(default="#1F2937", description="Text color")
    background_color: Optional[str] = Field(default="#FFFFFF", description="Background color")
    
    # Render settings
    quality: RenderQuality = Field(default=RenderQuality.MEDIUM, description="Video quality")
    duration: Optional[float] = Field(default=None, description="Target duration in seconds")
    resolution: Optional[List[int]] = Field(
        default=None, 
        description="Custom resolution [width, height]"
    )
    
    # Metadata
    lesson_id: Optional[str] = Field(default=None, description="Associated lesson ID")
    course_id: Optional[str] = Field(default=None, description="Associated course ID")
    priority: int = Field(default=5, ge=1, le=10, description="Render priority (1-10)")
    
    @field_validator('resolution')
    @classmethod
    def validate_resolution(cls, v):
        if v and (len(v) != 2 or v[0] <= 0 or v[1] <= 0):
            raise ValueError("Resolution must be [width, height] with positive values")
        return v


class BatchRenderRequest(BaseModel):
    """Request model for batch rendering"""
    requests: List[RenderRequest] = Field(..., description="List of render requests")
    parallel: bool = Field(default=False, description="Render in parallel if workers available")


class TemplateRenderRequest(BaseModel):
    """Request model for rendering from a template"""
    template_name: str = Field(..., description="Name of the template to use")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Template parameters")
    quality: RenderQuality = Field(default=RenderQuality.MEDIUM)
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Custom metadata")


# ==================== Response Models ====================

class RenderJobResponse(BaseModel):
    """Response model for render job creation"""
    job_id: str = Field(..., description="Unique job identifier")
    status: RenderStatus = Field(..., description="Current job status")
    message: str = Field(default="Job queued successfully")
    estimated_time: Optional[int] = Field(default=None, description="Estimated completion time in seconds")


class RenderProgressResponse(BaseModel):
    """Response model for render job progress"""
    job_id: str
    status: RenderStatus
    progress: float = Field(default=0.0, ge=0, le=1, description="Progress as fraction 0-1")
    stage: Optional[str] = Field(default=None, description="Current processing stage")
    message: Optional[str] = Field(default=None, description="Status message")
    eta_seconds: Optional[int] = Field(default=None, description="Estimated time remaining")
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class RenderResultResponse(BaseModel):
    """Response model for completed render"""
    job_id: str
    status: RenderStatus
    video_url: Optional[str] = Field(default=None, description="URL to download video")
    thumbnail_url: Optional[str] = Field(default=None, description="URL to thumbnail image")
    duration: Optional[float] = Field(default=None, description="Video duration in seconds")
    resolution: Optional[List[int]] = None
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    # Error details if failed
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None


class SceneInfo(BaseModel):
    """Information about an available scene"""
    id: str
    name: str
    scene_type: SceneType
    level: EducationalLevel
    description: Optional[str] = None
    duration_estimate: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None


class SceneListResponse(BaseModel):
    """Response model for listing available scenes"""
    scenes: List[SceneInfo]
    total: int


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str
    version: str
    manim_version: Optional[str] = None
    latex_installed: bool
    ffmpeg_installed: bool
    disk_space_mb: Optional[int] = None
    memory_usage_mb: Optional[int] = None
    active_jobs: int = 0
    queued_jobs: int = 0


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==================== Internal Models ====================

class RenderTask(BaseModel):
    """Internal model for render task data"""
    job_id: str
    request: RenderRequest
    status: RenderStatus = RenderStatus.QUEUED
    progress: float = 0.0
    stage: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
