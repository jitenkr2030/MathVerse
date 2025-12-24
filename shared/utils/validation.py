"""
Validation Utilities Module

This module provides input validation utilities for the MathVerse platform,
including email validation, password strength checking, and data sanitization.
"""

import re
from typing import Optional, Tuple
from email_validator import validate_email, EmailNotValidError
import bleach


# Password regex patterns
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128


def validate_email(email_str: str) -> Tuple[bool, str]:
    """
    Validate an email address.
    
    Args:
        email_str: Email address to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        valid = validate_email(email_str)
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    
    Checks for:
    - Minimum length
    - Maximum length
    - Uppercase letters
    - Lowercase letters
    - Numbers
    - Special characters
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    errors = []
    
    # Length checks
    if len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")
    
    if len(password) > PASSWORD_MAX_LENGTH:
        errors.append(f"Password must not exceed {PASSWORD_MAX_LENGTH} characters")
    
    # Complexity checks
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character")
    
    if errors:
        return False, "; ".join(errors)
    
    return True, "Password meets strength requirements"


def validate_uuid(value: str) -> bool:
    """
    Validate if a string is a valid UUID.
    
    Args:
        value: String to validate
        
    Returns:
        True if valid UUID
    """
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(value))


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate a username.
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username must not exceed 50 characters"
    
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    if username.startswith("_") or username.endswith("_"):
        return False, "Username cannot start or end with underscore"
    
    return True, "Username is valid"


def validate_phone_number(phone: str) -> Tuple[bool, str]:
    """
    Validate a phone number.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Tuple of (is_valid, normalized_number)
    """
    # Remove all non-digit characters
    digits = re.sub(r"\D", "", phone)
    
    # Check for valid length (7-15 digits for international)
    if len(digits) < 7 or len(digits) > 15:
        return False, "Phone number must be between 7 and 15 digits"
    
    # Add country code if missing
    if len(digits) == 10:  # US format
        normalized = f"+1{digits}"
    elif len(digits) == 11 and digits.startswith("1"):  # US with country code
        normalized = f"+{digits}"
    else:
        normalized = f"+{digits}"
    
    return True, normalized


def sanitize_input(
    text: str,
    allow_tags: Optional[list] = None,
    strip: bool = True
) -> str:
    """
    Sanitize user input to prevent XSS and injection attacks.
    
    Args:
        text: Input text to sanitize
        allow_tags: List of allowed HTML tags
        strip: Whether to strip tags entirely
        
    Returns:
        Sanitized text
    """
    if strip:
        # Strip all HTML tags
        return bleach.clean(text, tags=[], strip=True)
    
    if allow_tags:
        # Allow specific HTML tags
        return bleach.clean(text, tags=allow_tags, strip=True)
    
    # Default: allow basic formatting tags
    allowed_tags = ["b", "i", "u", "strong", "em", "p", "br", "ul", "ol", "li"]
    return bleach.clean(text, tags=allowed_tags, strip=True)


def sanitize_html(
    html: str,
    allowed_attributes: Optional[dict] = None
) -> str:
    """
    Sanitize HTML content.
    
    Args:
        html: HTML content to sanitize
        allowed_attributes: Dict of tag -> allowed attributes
        
    Returns:
        Sanitized HTML
    """
    if allowed_attributes is None:
        allowed_attributes = {
            "a": ["href", "title"],
            "img": ["src", "alt", "width", "height"]
        }
    
    return bleach.clean(
        html,
        tags=list(allowed_attributes.keys()),
        attributes=allowed_attributes,
        strip=True
    )


def validate_url(url: str) -> bool:
    """
    Validate a URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid URL format
    """
    url_pattern = re.compile(
        r"^(https?:\/\/)?"
        r"([\da-z\.-]+)\.([a-z\.]{2,6})"
        r"([\/\w \.-]*)*\/?$"
    )
    return bool(url_pattern.match(url))


def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, str]:
    """
    Validate that a date range is valid.
    
    Args:
        start_date: Start date string (ISO format)
        end_date: End date string (ISO format)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    from datetime import datetime
    
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        if start > end:
            return False, "Start date must be before end date"
        
        return True, "Date range is valid"
        
    except ValueError:
        return False, "Invalid date format"


def validate_file_extension(
    filename: str,
    allowed_extensions: list
) -> Tuple[bool, str]:
    """
    Validate file extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.docx'])
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    import os
    
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in allowed_extensions:
        return False, f"File type {ext} not allowed. Allowed: {', '.join(allowed_extensions)}"
    
    return True, "File extension is valid"


def validate_file_size(size_bytes: int, max_size_mb: int = 10) -> Tuple[bool, str]:
    """
    Validate file size.
    
    Args:
        size_bytes: File size in bytes
        max_size_mb: Maximum size in megabytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if size_bytes > max_size_bytes:
        return False, f"File exceeds maximum size of {max_size_mb}MB"
    
    return True, "File size is valid"


def validate_content_type(
    content_type: str,
    allowed_types: list
) -> Tuple[bool, str]:
    """
    Validate content type (MIME type).
    
    Args:
        content_type: MIME type string
        allowed_types: List of allowed MIME types
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if content_type not in allowed_types:
        return False, f"Content type '{content_type}' not allowed"
    
    return True, "Content type is valid"


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.cleaned_data = {}
    
    def add_error(self, field: str, message: str) -> None:
        """Add a validation error."""
        self.errors.append({"field": field, "message": message})
        self.is_valid = False
    
    def add_warning(self, field: str, message: str) -> None:
        """Add a validation warning."""
        self.warnings.append({"field": field, "message": message})
    
    def set_cleaned(self, field: str, value: Any) -> None:
        """Set cleaned field value."""
        self.cleaned_data[field] = value
    
    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "cleaned_data": self.cleaned_data
        }
