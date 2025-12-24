"""
Internal Service Client for Microservices Communication

This module provides a unified interface for the main backend to communicate
with other microservices in the MathVerse platform.

Services:
- recommendation-engine: Port 8003
- content-metadata: Port 8004
- animation-engine: Port 8002
- video-renderer: Port 8001
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from contextlib import asynccontextmanager
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Configuration for a microservice."""
    name: str
    host: str
    port: int
    health_endpoint: str = "/health"
    timeout: float = 30.0


class CircuitBreaker:
    """Circuit breaker pattern for service resilience."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    async def __aenter__(self):
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
            else:
                raise ServiceUnavailableError(f"Service unavailable - circuit breaker open")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.failures += 1
            self.last_failure_time = asyncio.get_event_loop().time()
            if self.failures >= self.failure_threshold:
                self.state = "open"
            logger.error(f"Service call failed: {exc_val}")
        else:
            self.failures = 0
            self.state = "closed"
    
    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return True
        return (asyncio.get_event_loop().time() - 
                self.last_failure_time) >= self.recovery_timeout


class ServiceUnavailableError(Exception):
    """Raised when a service is unavailable due to circuit breaker."""
    pass


class InternalServiceClient:
    """
    Base client for microservice communication with retry and circuit breaker support.
    """
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.base_url = f"http://{config.host}:{config.port}"
        self.circuit_breaker = CircuitBreaker()
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                follow_redirects=True
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def health_check(self) -> bool:
        """Check if service is healthy."""
        try:
            response = await self.client.get(f"{self.base_url}{self.config.health_endpoint}")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Health check failed for {self.config.name}: {e}")
            return False
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException))
    )
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request with retry logic."""
        async with self.circuit_breaker:
            response = await self.client.get(
                f"{self.base_url}{endpoint}",
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException))
    )
    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """POST request with retry logic."""
        async with self.circuit_breaker:
            response = await self.client.post(
                f"{self.base_url}{endpoint}",
                json=data
            )
            response.raise_for_status()
            return response.json()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException))
    )
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE request with retry logic."""
        async with self.circuit_breaker:
            response = await self.client.delete(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()


class RecommendationServiceClient(InternalServiceClient):
    """Client for the recommendation engine service."""
    
    def __init__(self):
        config = ServiceConfig(
            name="recommendation-engine",
            host="localhost",
            port=8003,
            health_endpoint="/health"
        )
        super().__init__(config)
    
    async def get_recommendations(
        self,
        user_id: int,
        course_id: Optional[int] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get personalized course recommendations."""
        return await self.post("/recommendations", {
            "user_id": user_id,
            "course_id": course_id,
            "limit": limit
        })
    
    async def personalize_recommendations(
        self,
        user_id: int,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user preferences for better recommendations."""
        return await self.post("/personalize", {
            "user_id": user_id,
            "preferences": preferences
        })
    
    async def analyze_progress(
        self,
        user_id: int,
        course_id: int
    ) -> Dict[str, Any]:
        """Analyze user's progress and identify areas for improvement."""
        return await self.post("/analyze", {
            "user_id": user_id,
            "course_id": course_id
        })
    
    async def detect_weaknesses(
        self,
        user_id: int
    ) -> Dict[str, Any]:
        """Detect knowledge gaps and weaknesses."""
        return await self.post("/weaknesses", {
            "user_id": user_id
        })


class ContentMetadataServiceClient(InternalServiceClient):
    """Client for the content metadata service."""
    
    def __init__(self):
        config = ServiceConfig(
            name="content-metadata",
            host="localhost",
            port=8004,
            health_endpoint="/health"
        )
        super().__init__(config)
    
    async def search_content(
        self,
        query: str,
        filters: Optional[Dict] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Search for educational content."""
        return await self.post("/api/v1/content/search", {
            "query": query,
            "filters": filters or {},
            "page": page,
            "limit": limit
        })
    
    async def get_curriculum_tree(
        self,
        level: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get the curriculum tree structure."""
        params = {"level": level} if level else {}
        return await self.get("/api/v1/content/curriculum/tree", params)
    
    async def get_concept_dependencies(
        self,
        concept_id: int
    ) -> Dict[str, Any]:
        """Get concept dependency graph."""
        return await self.get(f"/api/v1/concepts/{concept_id}/dependencies")
    
    async def create_course(
        self,
        course_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new course."""
        return await self.post("/api/v1/courses", course_data)
    
    async def create_lesson(
        self,
        lesson_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new lesson."""
        return await self.post("/api/v1/lessons", lesson_data)
    
    async def get_syllabus(
        self,
        course_id: int
    ) -> Dict[str, Any]:
        """Get syllabus for a course."""
        return await self.get(f"/api/v1/courses/{course_id}/syllabus")


class AnimationEngineClient(InternalServiceClient):
    """Client for the animation engine service."""
    
    def __init__(self):
        config = ServiceConfig(
            name="animation-engine",
            host="localhost",
            port=8002,
            health_endpoint="/health"
        )
        super().__init__(config)
    
    async def render_animation(
        self,
        request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit a rendering request."""
        return await self.post("/api/v1/render", request_data)
    
    async def get_render_status(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """Get the status of a rendering job."""
        return await self.get(f"/api/v1/render/{job_id}/status")
    
    async def get_render_result(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """Get the result of a completed rendering job."""
        return await self.get(f"/api/v1/render/{job_id}/result")
    
    async def cancel_render(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """Cancel a running rendering job."""
        return await self.delete(f"/api/v1/render/{job_id}")


class VideoRendererClient(InternalServiceClient):
    """Client for the video renderer service."""
    
    def __init__(self):
        config = ServiceConfig(
            name="video-renderer",
            host="localhost",
            port=8001,
            health_endpoint="/health"
        )
        super().__init__(config)
    
    async def submit_video_job(
        self,
        job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit a video processing job."""
        return await self.post("/api/v1/process", job_data)
    
    async def get_job_status(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """Get the status of a video processing job."""
        return await self.get(f"/api/v1/jobs/{job_id}/status")
    
    async def get_video_url(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """Get the URL of a processed video."""
        return await self.get(f"/api/v1/jobs/{job_id}/url")


# Service registry for dependency injection
_service_clients: Dict[str, InternalServiceClient] = {}


def get_recommendation_client() -> RecommendationServiceClient:
    """Get or create the recommendation service client."""
    if "recommendation" not in _service_clients:
        _service_clients["recommendation"] = RecommendationServiceClient()
    return _service_clients["recommendation"]


def get_content_metadata_client() -> ContentMetadataServiceClient:
    """Get or create the content metadata service client."""
    if "content_metadata" not in _service_clients:
        _service_clients["content_metadata"] = ContentMetadataServiceClient()
    return _service_clients["content_metadata"]


def get_animation_engine_client() -> AnimationEngineClient:
    """Get or create the animation engine client."""
    if "animation" not in _service_clients:
        _service_clients["animation"] = AnimationEngineClient()
    return _service_clients["animation"]


def get_video_renderer_client() -> VideoRendererClient:
    """Get or create the video renderer client."""
    if "video" not in _service_clients:
        _service_clients["video"] = VideoRendererClient()
    return _service_clients["video"]


async def close_all_clients():
    """Close all service clients."""
    for client in _service_clients.values():
        await client.close()
    _service_clients.clear()


async def check_all_services_healthy() -> Dict[str, bool]:
    """Check health of all microservices."""
    results = {}
    clients = {
        "recommendation": get_recommendation_client(),
        "content_metadata": get_content_metadata_client(),
        "animation": get_animation_engine_client(),
        "video": get_video_renderer_client()
    }
    
    for name, client in clients.items():
        results[name] = await client.health_check()
    
    return results
