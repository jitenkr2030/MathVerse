"""
Service URLs and Configuration Module

This module provides service discovery and URL configuration for the
MathVerse microservices architecture. It defines internal service URLs,
environment-specific configurations, and endpoint mappings.
"""

from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field


class ServiceName(str, Enum):
    """Enumeration of all MathVerse services."""
    
    BACKEND = "backend"
    CONTENT_METADATA = "content-metadata"
    RECOMMENDATION_ENGINE = "recommendation-engine"
    VIDEO_RENDERER = "video-renderer"
    ANIMATION_ENGINE = "animation-engine"
    MOBILE_APP = "mobile-app"
    WEB_CLIENT = "web-client"
    CREATOR_PORTAL = "creator-portal"
    NGINX_GATEWAY = "nginx-gateway"
    POSTGRES = "postgres"
    REDIS = "redis"


class Environment(str, Enum):
    """Deployment environment types."""
    
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class ServiceConfig(BaseModel):
    """Configuration for a single service."""
    
    name: ServiceName
    host: str = Field(..., description="Service hostname")
    port: int = Field(..., ge=1, le=65535)
    protocol: str = Field(default="http", pattern="^(http|https)$")
    health_endpoint: str = Field(default="/health")
    version: str = Field(default="1.0.0")
    replicas: int = Field(default=1, ge=1)
    environment: Environment = Environment.DEVELOPMENT
    
    @property
    def base_url(self) -> str:
        """Get the base URL for the service."""
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def health_url(self) -> str:
        """Get the health check URL."""
        return f"{self.base_url}{self.health_endpoint}"
    
    def url_for(self, path: str) -> str:
        """Generate a URL for a specific path."""
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"


class ServiceUrls:
    """
    Service URL registry for MathVerse microservices.
    
    This class manages internal service URLs and provides
    service discovery capabilities.
    """
    
    # Default service configurations
    _services: Dict[ServiceName, ServiceConfig] = {}
    
    # External API prefixes
    API_PREFIX = "/api/v1"
    
    @classmethod
    def register_service(cls, config: ServiceConfig) -> None:
        """Register a service configuration."""
        cls._services[config.name] = config
    
    @classmethod
    def get_service(cls, name: ServiceName) -> Optional[ServiceConfig]:
        """Get service configuration by name."""
        return cls._services.get(name)
    
    @classmethod
    def get_url(cls, name: ServiceName, path: str = "") -> str:
        """Get full URL for a service."""
        service = cls._services.get(name)
        if service:
            return service.url_for(path) if path else service.base_url
        return ""
    
    @classmethod
    def get_health_url(cls, name: ServiceName) -> str:
        """Get health check URL for a service."""
        service = cls._services.get(name)
        if service:
            return service.health_url
        return ""
    
    @classmethod
    def list_services(cls) -> Dict[ServiceName, ServiceConfig]:
        """List all registered services."""
        return cls._services.copy()
    
    @classmethod
    def initialize_defaults(cls, environment: Environment = Environment.DEVELOPMENT) -> None:
        """
        Initialize default service configurations.
        
        Args:
            environment: Target deployment environment
        """
        # Core backend service
        cls.register_service(ServiceConfig(
            name=ServiceName.BACKEND,
            host="backend",
            port=8000,
            health_endpoint="/api/v1/health",
            environment=environment
        ))
        
        # Content metadata service
        cls.register_service(ServiceConfig(
            name=ServiceName.CONTENT_METADATA,
            host="content-metadata",
            port=8001,
            health_endpoint="/health",
            environment=environment
        ))
        
        # Recommendation engine service
        cls.register_service(ServiceConfig(
            name=ServiceName.RECOMMENDATION_ENGINE,
            host="recommendation-engine",
            port=8002,
            health_endpoint="/health",
            environment=environment
        ))
        
        # Video renderer service
        cls.register_service(ServiceConfig(
            name=ServiceName.VIDEO_RENDERER,
            host="video-renderer",
            port=8003,
            health_endpoint="/health",
            environment=environment
        ))
        
        # Animation engine service
        cls.register_service(ServiceConfig(
            name=ServiceName.ANIMATION_ENGINE,
            host="animation-engine",
            port=8004,
            health_endpoint="/health",
            environment=environment
        ))
        
        # Database services
        cls.register_service(ServiceConfig(
            name=ServiceName.POSTGRES,
            host="postgres",
            port=5432,
            protocol="postgresql",
            health_endpoint="",
            environment=environment
        ))
        
        cls.register_service(ServiceConfig(
            name=ServiceName.REDIS,
            host="redis",
            port=6379,
            protocol="redis",
            health_endpoint="",
            environment=environment
        ))
        
        # Frontend services
        cls.register_service(ServiceConfig(
            name=ServiceName.WEB_CLIENT,
            host="web-client",
            port=3000,
            health_endpoint="",
            environment=environment
        ))
        
        cls.register_service(ServiceConfig(
            name=ServiceName.CREATOR_PORTAL,
            host="creator-portal",
            port=3001,
            health_endpoint="",
            environment=environment
        ))


class APIEndpoints:
    """
    Standardized API endpoint paths.
    
    These paths are prefixed with the API version and should be
    consistent across all services.
    """
    
    # Authentication endpoints
    AUTH = f"{ServiceUrls.API_PREFIX}/auth"
    AUTH_LOGIN = f"{AUTH}/login"
    AUTH_LOGOUT = f"{AUTH}/logout"
    AUTH_REGISTER = f"{AUTH}/register"
    AUTH_REFRESH = f"{AUTH}/refresh"
    AUTH_VERIFY = f"{AUTH}/verify"
    AUTH_PASSWORD_RESET = f"{AUTH}/password/reset"
    AUTH_PASSWORD_UPDATE = f"{AUTH}/password/update"
    
    # User endpoints
    USERS = f"{ServiceUrls.API_PREFIX}/users"
    USER_PROFILE = f"{USERS}/profile"
    USER_PREFERENCES = f"{USERS}/preferences"
    
    # Content endpoints
    CONTENT = f"{ServiceUrls.API_PREFIX}/content"
    CONTENT_SEARCH = f"{CONTENT}/search"
    CONTENT_UPLOAD = f"{CONTENT}/upload"
    
    # Course endpoints
    COURSES = f"{ServiceUrls.API_PREFIX}/courses"
    COURSE_ENROLL = f"{COURSES}/enroll"
    COURSE_PROGRESS = f"{COURSES}/progress"
    
    # Recommendation endpoints
    RECOMMEND = f"{ServiceUrls.API_PREFIX}/recommend"
    RECOMMEND_CONTENT = f"{RECOMMEND}/content"
    RECOMMEND_LEARNING_PATH = f"{RECOMMEND}/learning-path"
    RECOMMEND_CONCEPTS = f"{RECOMMEND}/concepts"
    
    # Animation endpoints
    ANIMATIONS = f"{ServiceUrls.API_PREFIX}/animations"
    ANIMATION_RENDER = f"{ANIMATIONS}/render"
    ANIMATION_STATUS = f"{ANIMATIONS}/status"
    
    # Video endpoints
    VIDEOS = f"{ServiceUrls.API_PREFIX}/videos"
    VIDEO_UPLOAD = f"{VIDEOS}/upload"
    VIDEO_PROCESS = f"{VIDEOS}/process"
    
    # Analytics endpoints
    ANALYTICS = f"{ServiceUrls.API_PREFIX}/analytics"
    ANALYTICS_PROGRESS = f"{ANALYTICS}/progress"
    ANALYTICS_PERFORMANCE = f"{ANALYTICS}/performance"


# External service URLs (for frontend and external access)
EXTERNAL_SERVICE_URLS: Dict[str, str] = {
    "api_gateway": "http://localhost:80",
    "web_app": "http://localhost:3000",
    "creator_portal": "http://localhost:3001",
    "mobile_app": "http://localhost:8080",
    "documentation": "http://localhost:8000/docs",
    "health_check": "http://localhost:80/health",
}


def get_external_url(service_key: str) -> Optional[str]:
    """
    Get external service URL by key.
    
    Args:
        service_key: Service identifier key
        
    Returns:
        External URL or None if not found
    """
    return EXTERNAL_SERVICE_URLS.get(service_key)


# Initialize default configurations
ServiceUrls.initialize_defaults()
