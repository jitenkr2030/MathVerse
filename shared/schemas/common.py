"""
Common Schemas Module

This module provides base schemas and common data models used
throughout the MathVerse platform. These include API response
wrappers, pagination models, and base configurations.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        use_enum_values=True
    )


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper.
    
    All API responses should use this wrapper for consistent formatting.
    """
    
    success: bool = Field(..., description="Whether the request was successful")
    data: Optional[T] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    error_code: Optional[str] = Field(default=None, description="Error code if failed")
    message: Optional[str] = Field(default=None, description="Additional status message")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    @classmethod
    def success_response(
        cls,
        data: T,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "APIResponse[T]":
        """Create a successful response."""
        return cls(
            success=True,
            data=data,
            message=message,
            metadata=metadata
        )
    
    @classmethod
    def error_response(
        cls,
        error: str,
        error_code: Optional[str] = None,
        message: Optional[str] = None
    ) -> "APIResponse[None]":
        """Create an error response."""
        return cls(
            success=False,
            error=error,
            error_code=error_code,
            message=message
        )


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.now)
    path: Optional[str] = Field(default=None, description="Request path")
    method: Optional[str] = Field(default=None, description="HTTP method")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""
    
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Sort field")
    sort_order: Optional[SortOrder] = Field(default=None, description="Sort order")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.limit


class SortOrder(str, Enum):
    """Sort order options."""
    
    ASC = "asc"
    DESC = "desc"


class PaginationMeta(BaseModel):
    """Pagination metadata included in responses."""
    
    current_page: int = Field(..., description="Current page number")
    items_per_page: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total items count")
    total_pages: int = Field(..., description="Total pages count")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_previous: bool = Field(..., description="Whether there are previous pages")
    
    @classmethod
    def create(
        cls,
        page: int,
        limit: int,
        total_items: int
    ) -> "PaginationMeta":
        """Create pagination metadata."""
        total_pages = (total_items + limit - 1) // limit if total_items > 0 else 0
        
        return cls(
            current_page=page,
            items_per_page=limit,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    
    items: List[T] = Field(..., description="List of items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")


class HealthStatus(str, Enum):
    """Health check status values."""
    
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: HealthStatus = Field(..., description="Service health status")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.now)
    checks: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None,
        description="Individual component health checks"
    )
    uptime_seconds: Optional[float] = Field(default=None, description="Uptime in seconds")


class TimestampMixin(BaseModel):
    """Mixin for adding timestamp fields."""
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)


class SoftDeleteMixin(BaseModel):
    """Mixin for soft delete functionality."""
    
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)


# Type variable for generic schemas
T = TypeVar("T")


class ListResponse(BaseModel, Generic[T]):
    """Generic list response model."""
    
    items: List[T]
    count: int
    total: Optional[int] = None


class IDResponse(BaseModel):
    """Response model for ID-based operations."""
    
    id: str
    message: Optional[str] = None


class StatusMessage(BaseModel):
    """Status message response model."""
    
    status: str
    message: str
    details: Optional[Dict[str, Any]] = None


class VersionInfo(BaseModel):
    """Version information model."""
    
    version: str
    commit_sha: Optional[str] = None
    build_date: Optional[str] = None
    environment: Optional[str] = None


class RateLimitInfo(BaseModel):
    """Rate limit information model."""
    
    limit: int = Field(..., description="Rate limit")
    remaining: int = Field(..., description="Remaining requests")
    reset_at: Optional[datetime] = Field(default=None, description="Reset time")
