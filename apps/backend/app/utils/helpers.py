"""
MathVerse Backend API - Utility Helpers
========================================
Common utility functions and helpers.
"""

from typing import Optional, Any, Dict, List
from datetime import datetime, date
from enum import Enum
import re
import json
from sqlalchemy.orm import Session
from sqlalchemy import inspect


def snake_to_camel(name: str) -> str:
    """
    Convert snake_case to camelCase.
    
    Args:
        name: Snake case string
        
    Returns:
        Camel case string
    """
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def camel_to_snake(name: str) -> str:
    """
    Convert camelCase to snake_case.
    
    Args:
        name: Camel case string
        
    Returns:
        Snake case string
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def format_datetime(dt: datetime) -> str:
    """
    Format datetime to ISO string.
    
    Args:
        dt: Datetime object
        
    Returns:
        ISO formatted string
    """
    if dt is None:
        return None
    return dt.isoformat()


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """
    Parse datetime string to datetime object.
    
    Args:
        dt_str: Datetime string
        
    Returns:
        Datetime object or None
    """
    try:
        return datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        return None


def format_duration(seconds: int) -> str:
    """
    Format seconds to human readable duration.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def calculate_age(birthdate: date) -> int:
    """
    Calculate age from birthdate.
    
    Args:
        birthdate: Birthdate
        
    Returns:
        Age in years
    """
    today = date.today()
    age = today.year - birthdate.year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1
    return age


def generate_slug(text: str) -> str:
    """
    Generate URL-friendly slug from text.
    
    Args:
        text: Input text
        
    Returns:
        URL-friendly slug
    """
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = slug.strip('-')
    return slug


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
    """
    Return singular or plural form based on count.
    
    Args:
        count: Item count
        singular: Singular form
        plural: Plural form (auto-generated if not provided)
        
    Returns:
        Correct form based on count
    """
    if count == 1:
        return singular
    return plural or f"{singular}s"


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Amount
        currency: Currency code
        
    Returns:
        Formatted currency string
    """
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "INR": "₹"
    }
    symbol = symbols.get(currency, f"{currency} ")
    return f"{symbol}{amount:.2f}"


def clean_dict_keys(data: Dict[str, Any], convert_case: str = None) -> Dict[str, Any]:
    """
    Clean dictionary keys and optionally convert case.
    
    Args:
        data: Input dictionary
        convert_case: 'camel' or 'snake' to convert
        
    Returns:
        Cleaned dictionary
    """
    if not data:
        return {}
    
    result = {}
    for key, value in data.items():
        new_key = key
        if convert_case == 'camel':
            new_key = snake_to_camel(key)
        elif convert_case == 'snake':
            new_key = camel_to_snake(key)
        
        if isinstance(value, dict):
            value = clean_dict_keys(value, convert_case)
        elif isinstance(value, list):
            value = [
                clean_dict_keys(item, convert_case) if isinstance(item, dict) else item
                for item in value
            ]
        
        result[new_key] = value
    
    return result


def dict_from_model(model) -> Dict[str, Any]:
    """
    Convert SQLAlchemy model to dictionary.
    
    Args:
        model: SQLAlchemy model instance
        
    Returns:
        Dictionary representation
    """
    if model is None:
        return {}
    
    result = {}
    for column in inspect(model).mapper.column_attrs:
        value = getattr(model, column.key)
        if isinstance(value, Enum):
            value = value.value
        elif isinstance(value, datetime):
            value = format_datetime(value)
        result[column.key] = value
    
    return result


def paginate_results(
    items: List[Any],
    page: int,
    per_page: int,
    total: int
) -> Dict[str, Any]:
    """
    Create paginated response dictionary.
    
    Args:
        items: List of items
        page: Current page
        per_page: Items per page
        total: Total item count
        
    Returns:
        Paginated response dict
    """
    total_pages = (total + per_page - 1) // per_page if total > 0 else 0
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1
    }


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Dict with 'valid' key and any error messages
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


class PaginationParams:
    """Pagination parameters holder."""
    
    def __init__(self, page: int = 1, per_page: int = 20, max_per_page: int = 100):
        self.page = max(1, page)
        self.per_page = min(max(1, per_page), max_per_page)
        self.offset = (self.page - 1) * self.per_page
    
    @property
    def limit(self) -> int:
        return self.per_page
    
    @property
    def skip(self) -> int:
        return self.offset


def get_client_ip(request) -> str:
    """
    Extract client IP from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Client IP address
    """
    # Check X-Forwarded-For header (for proxied requests)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct client
    return request.client.host if request.client else "unknown"


def rate_limit_exceeded(
    client_id: str,
    max_requests: int,
    window_seconds: int,
    store: Dict[str, List[datetime]]
) -> tuple[bool, int]:
    """
    Check if rate limit is exceeded.
    
    Args:
        client_id: Unique client identifier
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
        store: Rate limit store
        
    Returns:
        Tuple of (is_exceeded, remaining_requests)
    """
    now = datetime.utcnow()
    
    if client_id not in store:
        store[client_id] = []
    
    # Clean old entries
    store[client_id] = [
        req_time for req_time in store[client_id]
        if (now - req_time).total_seconds() < window_seconds
    ]
    
    remaining = max_requests - len(store[client_id])
    
    if remaining <= 0:
        return True, 0
    
    store[client_id].append(now)
    return False, remaining - 1
