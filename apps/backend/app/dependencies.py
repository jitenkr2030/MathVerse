"""
MathVerse Backend API - Dependencies Module
============================================
FastAPI dependencies for authentication, database sessions, and common utilities.
"""

from typing import Optional, Generator
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.database import get_db
from app.config import settings
from app.models import User, UserRole
from app.schemas import TokenData


# ==================== SECURITY ====================

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token with longer expiry."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(
            user_id=int(user_id),
            email=email,
            role=UserRole(role) if role else None,
            exp=datetime.fromtimestamp(payload.get("exp"))
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ==================== AUTH DEPENDENCIES ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials from Authorization header
        db: Database session
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    token_data = decode_token(token)
    
    # Query user from database
    user = db.execute(
        select(User).where(User.id == token_data.user_id)
    ).scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is active.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        User: The authenticated and active user
        
    Raises:
        HTTPException: If user account is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user has verified their email.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        User: The authenticated user with verified email
        
    Raises:
        HTTPException: If email is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    return current_user


def require_role(allowed_roles: list[UserRole]):
    """
    Factory function to create a role verification dependency.
    
    Args:
        allowed_roles: List of roles that are allowed access
        
    Returns:
        Dependency function
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' not authorized. Required: {allowed_roles}"
            )
        return current_user
    
    return role_checker


# Pre-defined role dependencies
require_admin = require_role([UserRole.ADMIN])
require_teacher = require_role([UserRole.TEACHER, UserRole.ADMIN])
require_creator = require_role([UserRole.CREATOR, UserRole.ADMIN])
require_student = require_role([UserRole.STUDENT, UserRole.TEACHER, UserRole.CREATOR, UserRole.ADMIN])


# ==================== PAGINATION ====================

class PaginationParams:
    """Pagination parameters dependency."""
    
    def __init__(
        self,
        page: int = 1,
        per_page: int = 20,
        max_per_page: int = 100
    ):
        self.page = max(1, page)
        self.per_page = min(max(1, per_page), max_per_page)
        self.offset = (self.page - 1) * self.per_page


def get_pagination(
    page: int = 1,
    per_page: int = 20,
    max_per_page: int = 100
) -> PaginationParams:
    """
    Dependency for pagination parameters.
    
    Args:
        page: Page number (1-indexed)
        per_page: Items per page
        max_per_page: Maximum items per page
        
    Returns:
        PaginationParams: Pagination parameters
    """
    return PaginationParams(page, per_page, max_per_page)


# ==================== COMMON DEPENDENCIES ====================

async def get_or_404(
    model,
    object_id: int,
    db: Session,
    detail: str = "Object not found"
) -> model:
    """
    Dependency to get an object or raise 404.
    
    Args:
        model: SQLAlchemy model class
        object_id: ID of the object to fetch
        db: Database session
        detail: Error message for 404
        
    Returns:
        The fetched object
        
    Raises:
        HTTPException: 404 if not found
    """
    obj = db.execute(
        select(model).where(model.id == object_id)
    ).scalar_one_or_none()
    
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
    
    return obj


async def check_ownership(
    obj,
    owner_id_field: str,
    current_user: User = Depends(get_current_user)
) -> bool:
    """
    Dependency to check if current user owns an object.
    
    Args:
        obj: Object with owner_id field
        owner_id_field: Name of the owner ID field
        current_user: Current authenticated user
        
    Returns:
        bool: True if user owns the object
        
    Raises:
        HTTPException: 403 if not owner
    """
    owner_id = getattr(obj, owner_id_field)
    
    if owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )
    
    return True


# ==================== RATE LIMITING ====================

# Simple in-memory rate limiting (use Redis in production)
class RateLimiter:
    """Simple rate limiter using dictionary."""
    
    def __init__(self, requests: int = 100, window: int = 60):
        self.requests = requests
        self.window = window
        self.clients: dict = {}
    
    def check_limit(self, client_id: str) -> tuple[bool, int]:
        """
        Check if client has exceeded rate limit.
        
        Args:
            client_id: Unique client identifier
            
        Returns:
            tuple: (is_allowed, remaining_requests)
        """
        now = datetime.utcnow()
        
        if client_id not in self.clients:
            self.clients[client_id] = []
        
        # Remove old requests outside the window
        self.clients[client_id] = [
            req_time for req_time in self.clients[client_id]
            if (now - req_time).total_seconds() < self.window
        ]
        
        if len(self.clients[client_id]) >= self.requests:
            return False, 0
        
        self.clients[client_id].append(now)
        return True, self.requests - len(self.clients[client_id])


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_rate_limit(
    user: User = Depends(get_current_user)
) -> dict:
    """
    Dependency to check rate limit for current user.
    
    Args:
        user: Current authenticated user
        
    Returns:
        dict: Rate limit status
        
    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    allowed, remaining = rate_limiter.check_limit(str(user.id))
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"X-RateLimit-Remaining": "0"}
        )
    
    return {"remaining": remaining}
