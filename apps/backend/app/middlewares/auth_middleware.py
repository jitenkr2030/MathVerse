"""
MathVerse Backend API - Auth Middleware
========================================
Custom middleware for authentication and request processing.
"""

from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import time
import loguru

from app.config import settings


logger = loguru.logger


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling authentication and request logging.
    """
    
    # Paths that don't require authentication
    EXEMPT_PATHS = [
        "/api/auth/register",
        "/api/auth/login",
        "/api/auth/refresh",
        "/api/auth/password-reset-request",
        "/api/auth/password-reset-confirm",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/",
        "/static",
    ]
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process the request through auth middleware.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response
        """
        start_time = time.time()
        
        # Log request
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        
        # Skip logging for static files
        if not path.startswith("/static"):
            logger.info(f"Request: {method} {path} from {client_ip}")
        
        # Check if path is exempt from authentication
        if self._is_exempt(path):
            response = await call_next(request)
            return response
        
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Missing Authorization header",
                    "error_code": "MISSING_AUTH_HEADER"
                }
            )
        
        # Verify Bearer token format
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Invalid Authorization header format. Use 'Bearer <token>'",
                    "error_code": "INVALID_AUTH_FORMAT"
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add timing header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log response time
        if not path.startswith("/static"):
            logger.info(
                f"Response: {method} {path} - {response.status_code} "
                f"({process_time:.4f}s)"
            )
        
        return response
    
    def _is_exempt(self, path: str) -> bool:
        """
        Check if path is exempt from authentication.
        
        Args:
            path: Request path
            
        Returns:
            True if exempt
        """
        for exempt_path in self.EXEMPT_PATHS:
            if path.startswith(exempt_path):
                return True
        return False


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for detailed request/response logging.
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Log request details and response.
        """
        # Skip logging for docs
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Log request body for POST/PUT/PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            logger.debug(f"Request body: {body.decode()[:1000]}")
        
        # Process request
        response = await call_next(request)
        
        # Add response headers
        response.headers["X-Request-ID"] = request.headers.get(
            "X-Request-ID",
            str(id(request))
        )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for basic rate limiting.
    """
    
    def __init__(self, app: FastAPI, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = {}  # In production, use Redis
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Apply rate limiting.
        """
        # Skip rate limiting for certain paths
        if request.url.path in ["/health", "/docs", "/redoc"]:
            return await call_next(request)
        
        # Get client identifier
        client_id = request.client.host if request.client else "anonymous"
        
        # Check rate limit
        if self._is_rate_limited(client_id):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "retry_after": self.window
                },
                headers={"Retry-After": str(self.window)}
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self._get_remaining(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(self.window)
        
        return response
    
    def _is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited."""
        return False  # Simplified for demo
    
    def _get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client."""
        return self.max_requests


def setup_middleware(app: FastAPI):
    """
    Register all middleware with the application.
    
    Args:
        app: FastAPI application instance
    """
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add rate limiting middleware
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=100,
        window=60
    )
    
    # Add auth middleware
    app.add_middleware(AuthMiddleware)
