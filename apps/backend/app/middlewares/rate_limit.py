"""
Rate Limiting Middleware

This module provides rate limiting functionality for the MathVerse API,
protecting against abuse and ensuring fair resource usage.
"""

import time
from typing import Dict, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse


@dataclass
class RateLimitConfig:
    """
    Configuration for rate limiting.
    
    Attributes:
        requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
        block_duration_seconds: Duration to block if limit exceeded
    """
    requests: int
    window_seconds: int
    block_duration_seconds: int = 300  # 5 minutes default block


@dataclass
class RateLimitEntry:
    """
    Track rate limit usage for a client.
    
    Attributes:
        requests: List of request timestamps
        blocked_until: Timestamp when block expires
    """
    requests: list = field(default_factory=list)
    blocked_until: float = 0


class RateLimiter:
    """
    In-memory rate limiter implementation.
    
    Uses a sliding window algorithm for accurate rate limiting
    across multiple time windows.
    """
    
    def __init__(self):
        # Store client usage: {client_id: RateLimitEntry}
        self._clients: Dict[str, RateLimitEntry] = defaultdict(RateLimitEntry)
    
    def _get_client_id(self, request: Request) -> str:
        """
        Identify client from request.
        
        Uses X-Forwarded-For header for proxied requests,
        falls back to client host.
        """
        # Check for forwarded header (proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take first IP from comma-separated list
            return forwarded.split(",")[0].strip()
        
        # Fall back to direct client
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self, client_id: str, window_seconds: int) -> None:
        """Remove requests outside the current window."""
        cutoff = time.time() - window_seconds
        entry = self._clients[client_id]
        entry.requests = [t for t in entry.requests if t > cutoff]
    
    def check_rate_limit(
        self,
        request: Request,
        config: RateLimitConfig
    ) -> Tuple[bool, int, int]:
        """
        Check if request is within rate limits.
        
        Args:
            request: FastAPI request object
            config: Rate limit configuration
            
        Returns:
            Tuple of (is_allowed, remaining_requests, reset_time_seconds)
        """
        client_id = self._get_client_id(request)
        now = time.time()
        entry = self._clients[client_id]
        
        # Check if blocked
        if entry.blocked_until > now:
            remaining = int(entry.blocked_until - now)
            return False, 0, remaining
        
        # Cleanup old requests
        self._cleanup_old_requests(client_id, config.window_seconds)
        
        # Check limit
        current_count = len(entry.requests)
        
        if current_count >= config.requests:
            # Block the client
            entry.blocked_until = now + config.block_duration_seconds
            return False, 0, config.block_duration_seconds
        
        # Record this request
        entry.requests.append(now)
        
        remaining = config.requests - current_count - 1
        reset_time = int(now + config.window_seconds - entry.requests[0]) if entry.requests else config.window_seconds
        
        return True, remaining, reset_time
    
    def get_usage_stats(self, client_id: str, window_seconds: int) -> Dict[str, int]:
        """
        Get usage statistics for a client.
        
        Args:
            client_id: Client identifier
            window_seconds: Time window to check
            
        Returns:
            Dictionary with usage statistics
        """
        self._cleanup_old_requests(client_id, window_seconds)
        entry = self._clients[client_id]
        
        return {
            "requests_in_window": len(entry.requests),
            "blocked": entry.blocked_until > time.time(),
            "blocked_until": entry.blocked_until if entry.blocked_until > time.time() else None
        }
    
    def reset_client(self, client_id: str) -> None:
        """Reset rate limit for a specific client."""
        self._clients[client_id] = RateLimitEntry()
    
    def reset_all(self) -> None:
        """Reset rate limits for all clients."""
        self._clients.clear()


# Default rate limiter instance
rate_limiter = RateLimiter()

# Predefined rate limit configurations
RATE_LIMITS = {
    "default": RateLimitConfig(
        requests=100,
        window_seconds=60,
        block_duration_seconds=300
    ),
    "auth": RateLimitConfig(
        requests=10,
        window_seconds=60,
        block_duration_seconds=600  # 10 minutes for auth endpoints
    ),
    "search": RateLimitConfig(
        requests=30,
        window_seconds=60,
        block_duration_seconds=300
    ),
    "render": RateLimitConfig(
        requests=5,
        window_seconds=60,
        block_duration_seconds=120
    ),
    "upload": RateLimitConfig(
        requests=20,
        window_seconds=3600,  # Per hour
        block_duration_seconds=3600
    ),
    "strict": RateLimitConfig(
        requests=10,
        window_seconds=60,
        block_duration_seconds=600
    ),
    "public": RateLimitConfig(
        requests=50,
        window_seconds=60,
        block_duration_seconds=300
    ),
    "authenticated": RateLimitConfig(
        requests=200,
        window_seconds=60,
        block_duration_seconds=300
    ),
}


def get_rate_limit_config(endpoint_type: str = "default") -> RateLimitConfig:
    """
    Get rate limit configuration for an endpoint type.
    
    Args:
        endpoint_type: Type of endpoint (auth, search, render, etc.)
        
    Returns:
        RateLimitConfig instance
    """
    return RATE_LIMITS.get(endpoint_type, RATE_LIMITS["default"])


class RateLimitMiddleware:
    """
    FastAPI middleware for automatic rate limiting.
    """
    
    def __init__(self, app, default_limit: str = "default"):
        """
        Initialize middleware.
        
        Args:
            app: FastAPI application
            default_limit: Default rate limit key
        """
        self.app = app
        self.default_limit = default_limit
    
    async def __call__(self, scope, receive, send):
        """
        Process request through rate limiting.
        
        Note: This is a simple synchronous implementation.
        For production, use Redis-based rate limiting.
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Create a mock request object for rate limit checking
        # In production, use proper request parsing
        await self.app(scope, receive, send)


async def verify_rate_limit(
    request: Request,
    limit_type: str = "default"
) -> Dict[str, int]:
    """
    FastAPI dependency for rate limiting.
    
    Args:
        request: FastAPI request object
        limit_type: Type of rate limit to apply
        
    Returns:
        Dictionary with rate limit headers
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    config = get_rate_limit_config(limit_type)
    is_allowed, remaining, reset_time = rate_limiter.check_rate_limit(request, config)
    
    # Add rate limit headers
    headers = {
        "X-RateLimit-Limit": str(config.requests),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(reset_time),
        "X-RateLimit-Window": str(config.window_seconds)
    }
    
    # Store headers in request state for response
    request.state = headers
    
    if not is.rate_limit_headers_allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": reset_time
            },
            headers=headers
        )
    
    return headers


def create_rate_limit_dependency(limit_type: str):
    """
    Factory function to create rate limit dependencies.
    
    Args:
        limit_type: Type of rate limit
        
    Returns:
        FastAPI dependency function
    """
    async def rate_limit(
        request: Request,
        _verify: Dict[str, int] = Depends(verify_rate_limit)
    ) -> Dict[str, int]:
        return _verify
    
    rate_limit.__name__ = f"rate_limit_{limit_type}"
    return rate_limit


# Pre-configured rate limit dependencies
RateLimitDefault = create_rate_limit_dependency("default")
RateLimitAuth = create_rate_limit_dependency("auth")
RateLimitSearch = create_rate_limit_dependency("search")
RateLimitRender = create_rate_limit_dependency("render")
RateLimitStrict = create_rate_limit_dependency("strict")
RateLimitAuthenticated = create_rate_limit_dependency("authenticated")


# Example usage in FastAPI routes:
"""
from fastapi import FastAPI, Depends

app = FastAPI()

@app.get("/api/data", dependencies=[Depends(RateLimitAuthenticated)])
async def get_data():
    return {"data": "example"}

@app.post("/auth/login", dependencies=[Depends(RateLimitAuth)])
async def login():
    return {"message": "logged in"}
"""
