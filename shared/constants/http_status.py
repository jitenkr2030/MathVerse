"""
HTTP Status Module

This module provides standardized HTTP status mappings and custom status
messages for the MathVerse API. It extends standard HTTP status codes
with application-specific statuses.
"""

from enum import Enum
from typing import Dict, Optional


class HttpStatus(Enum):
    """
    HTTP Status codes with MathVerse-specific extensions.
    
    Standard HTTP status codes are mapped to descriptive messages
    and category groupings for consistent API responses.
    """
    
    # 2xx Success
    OK = (200, "Success")
    CREATED = (201, "Created")
    ACCEPTED = (202, "Accepted")
    NO_CONTENT = (204, "No Content")
    
    # 3xx Redirection
    MOVED_PERMANENTLY = (301, "Moved Permanently")
    FOUND = (302, "Found")
    NOT_MODIFIED = (304, "Not Modified")
    
    # 4xx Client Error
    BAD_REQUEST = (400, "Bad Request")
    UNAUTHORIZED = (401, "Unauthorized")
    PAYMENT_REQUIRED = (402, "Payment Required")
    FORBIDDEN = (403, "Forbidden")
    NOT_FOUND = (404, "Not Found")
    METHOD_NOT_ALLOWED = (405, "Method Not Allowed")
    NOT_ACCEPTABLE = (406, "Not Acceptable")
    PROXY_AUTHENTICATION_REQUIRED = (407, "Proxy Authentication Required")
    REQUEST_TIMEOUT = (408, "Request Timeout")
    CONFLICT = (409, "Conflict")
    GONE = (410, "Gone")
    LENGTH_REQUIRED = (411, "Length Required")
    PRECONDITION_FAILED = (412, "Precondition Failed")
    PAYLOAD_TOO_LARGE = (413, "Payload Too Large")
    URI_TOO_LONG = (414, "URI Too Long")
    UNSUPPORTED_MEDIA_TYPE = (415, "Unsupported Media Type")
    RANGE_NOT_SATISFIABLE = (416, "Range Not Satisfiable")
    EXPECTATION_FAILED = (417, "Expectation Failed")
    UNPROCESSABLE_ENTITY = (422, "Unprocessable Entity")
    LOCKED = (423, "Locked")
    FAILED_DEPENDENCY = (424, "Failed Dependency")
    TOO_EARLY = (425, "Too Early")
    UPGRADE_REQUIRED = (426, "Upgrade Required")
    PRECONDITION_REQUIRED = (428, "Precondition Required")
    TOO_MANY_REQUESTS = (429, "Too Many Requests")
    
    # 5xx Server Error
    INTERNAL_SERVER_ERROR = (500, "Internal Server Error")
    NOT_IMPLEMENTED = (501, "Not Implemented")
    BAD_GATEWAY = (502, "Bad Gateway")
    SERVICE_UNAVAILABLE = (503, "Service Unavailable")
    GATEWAY_TIMEOUT = (504, "Gateway Timeout")
    HTTP_VERSION_NOT_SUPPORTED = (505, "HTTP Version Not Supported")
    VARIANT_ALSO_NEGOTIATES = (506, "Variant Also Negotiates")
    INSUFFICIENT_STORAGE = (507, "Insufficient Storage")
    LOOP_DETECTED = (508, "Loop Detected")
    NOT_EXTENDED = (510, "Not Extended")
    NETWORK_AUTHENTICATION_REQUIRED = (511, "Network Authentication Required")
    
    # MathVerse Custom Status Codes
    PROCESSING = (102, "Processing")
    MULTI_STATUS = (207, "Multi-Status")
    IM_USED = (226, "IM Used")
    PERMANENT_REDIRECT = (308, "Permanent Redirect")
    USER_DEFINED_START = (600, "User Defined Start")
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
    
    @property
    def category(self) -> str:
        """Get the status category."""
        if 100 <= self.code < 200:
            return "informational"
        elif 200 <= self.code < 300:
            return "success"
        elif 300 <= self.code < 400:
            return "redirection"
        elif 400 <= self.code < 500:
            return "client_error"
        elif 500 <= self.code < 600:
            return "server_error"
        else:
            return "custom"


class StatusMessage:
    """
    Standardized status messages for common API operations.
    
    These messages ensure consistent communication across all
    MathVerse services.
    """
    
    # Success messages
    SUCCESS = "Operation completed successfully"
    CREATED = "Resource created successfully"
    UPDATED = "Resource updated successfully"
    DELETED = "Resource deleted successfully"
    FOUND = "Resource found successfully"
    
    # Authentication messages
    LOGIN_SUCCESS = "Login successful"
    LOGOUT_SUCCESS = "Logout successful"
    TOKEN_REFRESHED = "Token refreshed successfully"
    PASSWORD_RESET = "Password reset email sent"
    PASSWORD_UPDATED = "Password updated successfully"
    EMAIL_VERIFIED = "Email verified successfully"
    
    # Content messages
    CONTENT_UPLOADED = "Content uploaded successfully"
    CONTENT_PROCESSED = "Content processed successfully"
    CONTENT_DELETED = "Content deleted successfully"
    CONTENT_SHARED = "Content shared successfully"
    
    # Enrollment messages
    ENROLLED = "Successfully enrolled in course"
    UNENROLLED = "Successfully unenrolled from course"
    COMPLETED = "Course completed successfully"
    PROGRESS_UPDATED = "Progress updated successfully"
    
    # Recommendation messages
    RECOMMENDATIONS_GENERATED = "Recommendations generated successfully"
    LEARNING_PATH_CREATED = "Learning path created successfully"
    
    # Error messages
    INVALID_REQUEST = "The request is invalid"
    UNAUTHORIZED_ACCESS = "You are not authorized to access this resource"
    RESOURCE_NOT_FOUND = "The requested resource was not found"
    RATE_LIMIT_EXCEEDED = "Too many requests, please try again later"
    SERVER_ERROR = "An unexpected error occurred"


class ResponseStatus:
    """
    Standardized response status indicators for API responses.
    """
    
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"


# Status code mappings for common scenarios
SCENARIO_STATUS_MAPPINGS: Dict[str, HttpStatus] = {
    "authentication_required": HttpStatus.UNAUTHORIZED,
    "invalid_credentials": HttpStatus.UNAUTHORIZED,
    "access_denied": HttpStatus.FORBIDDEN,
    "resource_not_found": HttpStatus.NOT_FOUND,
    "duplicate_resource": HttpStatus.CONFLICT,
    "validation_failed": HttpStatus.BAD_REQUEST,
    "rate_limited": HttpStatus.TOO_MANY_REQUESTS,
    "server_error": HttpStatus.INTERNAL_SERVER_ERROR,
    "service_unavailable": HttpStatus.SERVICE_UNAVAILABLE,
    "timeout": HttpStatus.GATEWAY_TIMEOUT,
}


def get_status_for_scenario(scenario: str) -> HttpStatus:
    """
    Get the appropriate HTTP status for a given scenario.
    
    Args:
        scenario: Scenario identifier string
        
    Returns:
        HttpStatus enum member
    """
    return SCENARIO_STATUS_MAPPINGS.get(
        scenario,
        HttpStatus.INTERNAL_SERVER_ERROR
    )


def is_success_status(status_code: int) -> bool:
    """
    Check if a status code indicates success.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        True if success status (2xx)
    """
    return 200 <= status_code < 300


def is_client_error(status_code: int) -> bool:
    """
    Check if a status code indicates a client error.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        True if client error (4xx)
    """
    return 400 <= status_code < 500


def is_server_error(status_code: int) -> bool:
    """
    Check if a status code indicates a server error.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        True if server error (5xx)
    """
    return 500 <= status_code < 600
