"""
Error Codes Module

This module defines standardized error codes for the MathVerse platform.
All services should use these codes to ensure consistent error handling
across the microservices architecture.

Error Code Format: <DOMAIN>_<CODE>
- DOMAIN: 3-4 character service domain (e.g., AUTH, CONTENT, REC)
- CODE: 3-digit numeric code
"""

from enum import Enum
from typing import Optional


class ErrorCode(str, Enum):
    """Base error code with message template."""
    
    def __new__(cls, value: str, message: str, http_status: int):
        member = str.__new__(cls, value)
        member._value_ = value
        member.message = message
        member.http_status = http_status
        return member
    
    # Authentication errors (AUTH_xxx)
    AUTH_INVALID_TOKEN = ("AUTH_001", "Invalid or expired authentication token", 401)
    AUTH_EXPIRED_TOKEN = ("AUTH_002", "Authentication token has expired", 401)
    AUTH_MISSING_TOKEN = ("AUTH_003", "Authentication token is missing", 401)
    AUTH_INVALID_CREDENTIALS = ("AUTH_004", "Invalid username or password", 401)
    AUTH_INSUFFICIENT_PERMISSIONS = ("AUTH_005", "Insufficient permissions for this action", 403)
    AUTH_USER_NOT_FOUND = ("AUTH_006", "User account not found", 404)
    AUTH_USER_DISABLED = ("AUTH_007", "User account is disabled", 403)
    AUTH_TOKEN_REVOKED = ("AUTH_008", "Token has been revoked", 401)
    AUTH_REFRESH_TOKEN_INVALID = ("AUTH_009", "Invalid refresh token", 401)
    AUTH_PASSWORD_TOO_WEAK = ("AUTH_010", "Password does not meet complexity requirements", 400)
    AUTH_EMAIL_NOT_VERIFIED = ("AUTH_011", "Email address has not been verified", 403)
    AUTH_2FA_REQUIRED = ("AUTH_012", "Two-factor authentication required", 403)
    AUTH_2FA_INVALID = ("AUTH_013", "Invalid two-factor authentication code", 401)
    
    # User management errors (USER_xxx)
    USER_NOT_FOUND = ("USER_404", "User not found", 404)
    USER_ALREADY_EXISTS = ("USER_409", "User with this email already exists", 409)
    USER_INVALID_INPUT = ("USER_400", "Invalid user input", 400)
    USER_PROFILE_INCOMPLETE = ("USER_412", "User profile is incomplete", 412)
    USER_ROLE_INVALID = ("USER_400", "Invalid user role specified", 400)
    USER_DELETE_FAILED = ("USER_422", "Cannot delete user with active subscriptions", 422)
    
    # Content errors (CONTENT_xxx)
    CONTENT_NOT_FOUND = ("CONTENT_404", "Content not found", 404)
    CONTENT_ALREADY_EXISTS = ("CONTENT_409", "Content with this ID already exists", 409)
    CONTENT_INVALID_INPUT = ("CONTENT_400", "Invalid content data", 400)
    CONTENT_UNAUTHORIZED_ACCESS = ("CONTENT_403", "You do not have access to this content", 403)
    CONTENT_UPLOAD_FAILED = ("CONTENT_500", "Content upload failed", 500)
    CONTENT_PROCESSING_ERROR = ("CONTENT_502", "Content processing error", 502)
    CONTENT_INVALID_TYPE = ("CONTENT_415", "Unsupported content type", 415)
    CONTENT_FILE_TOO_LARGE = ("CONTENT_413", "Content file exceeds maximum size", 413)
    CONTENT_QUOTA_EXCEEDED = ("CONTENT_429", "Content storage quota exceeded", 429)
    CONTENT_DEPENDENCY_ERROR = ("CONTENT_424", "Content has unresolved dependencies", 424)
    
    # Course errors (COURSE_xxx)
    COURSE_NOT_FOUND = ("COURSE_404", "Course not found", 404)
    COURSE_ALREADY_ENROLLED = ("COURSE_409", "Already enrolled in this course", 409)
    COURSE_FULL = ("COURSE_423", "Course enrollment limit reached", 423)
    COURSE_NOT_STARTED = ("COURSE_403", "Course has not started yet", 403)
    COURSE_COMPLETED = ("COURSE_410", "Course already completed", 410)
    COURSE_INVALID_PROGRESS = ("COURSE_400", "Invalid progress data", 400)
    COURSE_ACCESS_DENIED = ("COURSE_403", "Access denied to this course", 403)
    
    # Recommendation errors (REC_xxx)
    REC_NOT_FOUND = ("REC_404", "Recommendation not found", 404)
    REC_INVALID_PARAMS = ("REC_400", "Invalid recommendation parameters", 400)
    REC_ENGINE_ERROR = ("REC_500", "Recommendation engine error", 500)
    REC_INSUFFICIENT_DATA = ("REC_422", "Insufficient data for recommendations", 422)
    REC_PROFILE_NOT_FOUND = ("REC_404", "Student profile not found", 404)
    
    # Animation errors (ANIM_xxx)
    ANIM_NOT_FOUND = ("ANIM_404", "Animation not found", 404)
    ANIM_RENDER_FAILED = ("ANIM_500", "Animation rendering failed", 500)
    ANIM_INVALID_SCENE = ("ANIM_400", "Invalid animation scene configuration", 400)
    ANIM_QUEUE_FULL = ("ANIM_429", "Animation render queue is full", 429)
    ANIM_TIMEOUT = ("ANIM_504", "Animation rendering timed out", 504)
    
    # Video errors (VIDEO_xxx)
    VIDEO_NOT_FOUND = ("VIDEO_404", "Video not found", 404)
    VIDEO_PROCESSING = ("VIDEO_102", "Video is still processing", 102)
    VIDEO_TRANSCODING = ("VIDEO_102", "Video is being transcoded", 102)
    VIDEO_UPLOAD_FAILED = ("VIDEO_500", "Video upload failed", 500)
    VIDEO_INVALID_FORMAT = ("VIDEO_415", "Unsupported video format", 415)
    
    # Database errors (DB_xxx)
    DB_CONNECTION_FAILED = ("DB_503", "Database connection failed", 503)
    DB_TRANSACTION_FAILED = ("DB_500", "Database transaction failed", 500)
    DB_CONSTRAINT_VIOLATION = ("DB_409", "Database constraint violation", 409)
    DB_QUERY_TIMEOUT = ("DB_504", "Database query timed out", 504)
    
    # Rate limiting (RATE_xxx)
    RATE_LIMIT_EXCEEDED = ("RATE_429", "Rate limit exceeded", 429)
    RATE_LIMIT_WINDOW = ("RATE_429", "Rate limit window exceeded", 429)
    
    # Validation errors (VALID_xxx)
    VALIDATION_ERROR = ("VALID_400", "Validation error", 400)
    VALIDATION_MISSING_FIELD = ("VALID_400", "Required field is missing", 400)
    VALIDATION_INVALID_FORMAT = ("VALID_400", "Field has invalid format", 400)
    VALIDATION_OUT_OF_RANGE = ("VALID_400", "Value is out of allowed range", 400)
    
    # Internal server errors (INTERNAL_xxx)
    INTERNAL_ERROR = ("INTERNAL_500", "An internal error occurred", 500)
    SERVICE_UNAVAILABLE = ("SERVICE_503", "Service temporarily unavailable", 503)
    NOT_IMPLEMENTED = ("NOT_IMPL_501", "This feature is not implemented", 501)


class AppErrorCode(Enum):
    """
    Application-level error codes for programmatic use.
    
    These codes can be used in code logic to handle specific error types.
    """
    
    # Authentication
    INVALID_TOKEN = "AUTH_INVALID_TOKEN"
    EXPIRED_TOKEN = "AUTH_EXPIRED_TOKEN"
    MISSING_TOKEN = "AUTH_MISSING_TOKEN"
    INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    INSUFFICIENT_PERMISSIONS = "AUTH_INSUFFICIENT_PERMISSIONS"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    
    # Content
    CONTENT_NOT_FOUND = "CONTENT_NOT_FOUND"
    CONTENT_ACCESS_DENIED = "CONTENT_ACCESS_DENIED"
    CONTENT_UPLOAD_FAILED = "CONTENT_UPLOAD_FAILED"
    
    # Business Logic
    ALREADY_EXISTS = "ALREADY_EXISTS"
    NOT_FOUND = "NOT_FOUND"
    INVALID_STATE = "INVALID_STATE"
    CONFLICT = "CONFLICT"
    
    # System
    DATABASE_ERROR = "DATABASE_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    TIMEOUT = "TIMEOUT"


def get_error_by_code(code: str) -> Optional[ErrorCode]:
    """
    Get ErrorCode enum member by code string.
    
    Args:
        code: Error code string (e.g., "AUTH_001")
        
    Returns:
        ErrorCode enum member or None if not found
    """
    for member in ErrorCode:
        if member.value[0] == code:
            return member
    return None


def parse_error_code(error_code: str) -> tuple:
    """
    Parse an error code string into components.
    
    Args:
        error_code: Error code string (e.g., "AUTH_001")
        
    Returns:
        Tuple of (domain, number) or None if invalid
    """
    if not isinstance(error_code, str):
        return None
    
    parts = error_code.split("_")
    if len(parts) != 2:
        return None
    
    domain, number = parts
    if not domain.isalpha() or not number.isdigit():
        return None
    
    return (domain, number)
