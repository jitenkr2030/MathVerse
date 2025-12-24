from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn

from app.modules.auth.routes import router as auth_router
from app.modules.users.routes import router as users_router
from app.modules.courses.routes import router as courses_router
from app.modules.lessons.routes import router as lessons_router
from app.modules.videos.routes import router as videos_router
from app.modules.quizzes.routes import router as quizzes_router
from app.modules.progress.routes import router as progress_router
from app.modules.payments.routes import router as payments_router
from app.modules.creators.routes import router as creators_router

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
import asyncio

from app.modules.auth.routes import router as auth_router
from app.modules.users.routes import router as users_router
from app.modules.courses.routes import router as courses_router
from app.modules.lessons.routes import router as lessons_router
from app.modules.videos.routes import router as videos_router
from app.modules.quizzes.routes import router as quizzes_router
from app.modules.progress.routes import router as progress_router
from app.modules.payments.routes import router as payments_router
from app.modules.creators.routes import router as creators_router

# Import service clients for microservice integration
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.internal_client import (
    check_all_services_healthy,
    close_all_clients,
    get_recommendation_client,
    get_content_metadata_client,
    get_animation_engine_client,
    get_video_renderer_client
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("MathVerse Backend API starting up...")
    print("Initializing microservice clients...")
    try:
        health = await check_all_services_healthy()
        for service, status in health.items():
            status_str = "healthy" if status else "unavailable"
            print(f"  {service}: {status_str}")
    except Exception as e:
        print(f"Warning: Could not check service health: {e}")
    yield
    # Shutdown
    print("MathVerse Backend API shutting down...")
    await close_all_clients()

app = FastAPI(
    title="MathVerse API",
    description="Animation-first Mathematics Learning Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(courses_router, prefix="/api/courses", tags=["Courses"])
app.include_router(lessons_router, prefix="/api/lessons", tags=["Lessons"])
app.include_router(videos_router, prefix="/api/videos", tags=["Videos"])
app.include_router(quizzes_router, prefix="/api/quizzes", tags=["Quizzes"])
app.include_router(progress_router, prefix="/api/progress", tags=["Progress"])
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])
app.include_router(creators_router, prefix="/api/creators", tags=["Creators"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to MathVerse API",
        "description": "Animation-first Mathematics Learning Platform",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mathverse-backend"}

# Microservices Health Check Endpoints
@app.get("/health/services")
async def services_health():
    """Check health of all microservices."""
    try:
        health = await check_all_services_healthy()
        all_healthy = all(health.values())
        return {
            "status": "healthy" if all_healthy else "degraded",
            "services": health
        }
    except Exception as e:
        return {"status": "error", "message": str(e), "services": {}}

# Recommendation Service Proxy Endpoints
@app.get("/api/v1/recommendations")
async def get_recommendations(user_id: int, course_id: int = None, limit: int = 10):
    """Get personalized course recommendations."""
    try:
        client = get_recommendation_client()
        return await client.get_recommendations(user_id, course_id, limit)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Recommendation service unavailable: {str(e)}")

@app.post("/api/v1/recommendations/personalize")
async def personalize_recommendations(user_id: int, preferences: dict):
    """Update user preferences for recommendations."""
    try:
        client = get_recommendation_client()
        return await client.personalize_recommendations(user_id, preferences)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Recommendation service unavailable: {str(e)}")

@app.post("/api/v1/recommendations/analyze")
async def analyze_progress(user_id: int, course_id: int):
    """Analyze user's learning progress."""
    try:
        client = get_recommendation_client()
        return await client.analyze_progress(user_id, course_id)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Recommendation service unavailable: {str(e)}")

@app.get("/api/v1/recommendations/weaknesses/{user_id}")
async def detect_weaknesses(user_id: int):
    """Detect user's knowledge gaps and weaknesses."""
    try:
        client = get_recommendation_client()
        return await client.detect_weaknesses(user_id)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Recommendation service unavailable: {str(e)}")

# Content Metadata Service Proxy Endpoints
@app.post("/api/v1/content/search")
async def search_content(query: str, filters: dict = None, page: int = 1, limit: int = 20):
    """Search for educational content."""
    try:
        client = get_content_metadata_client()
        return await client.search_content(query, filters, page, limit)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Content metadata service unavailable: {str(e)}")

@app.get("/api/v1/content/curriculum")
async def get_curriculum_tree(level: str = None):
    """Get curriculum tree structure."""
    try:
        client = get_content_metadata_client()
        return await client.get_curriculum_tree(level)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Content metadata service unavailable: {str(e)}")

# Animation Engine Proxy Endpoints
@app.post("/api/v1/animations/render")
async def render_animation(request_data: dict):
    """Submit animation rendering request."""
    try:
        client = get_animation_engine_client()
        return await client.render_animation(request_data)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Animation engine unavailable: {str(e)}")

@app.get("/api/v1/animations/render/{job_id}/status")
async def get_render_status(job_id: str):
    """Get animation rendering job status."""
    try:
        client = get_animation_engine_client()
        return await client.get_render_status(job_id)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Animation engine unavailable: {str(e)}")

@app.get("/api/v1/animations/render/{job_id}/result")
async def get_render_result(job_id: str):
    """Get animation rendering result."""
    try:
        client = get_animation_engine_client()
        return await client.get_render_result(job_id)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Animation engine unavailable: {str(e)}")

# Video Renderer Proxy Endpoints
@app.post("/api/v1/videos/process")
async def process_video(job_data: dict):
    """Submit video processing request."""
    try:
        client = get_video_renderer_client()
        return await client.submit_video_job(job_data)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Video renderer unavailable: {str(e)}")

@app.get("/api/v1/videos/process/{job_id}/status")
async def get_video_status(job_id: str):
    """Get video processing job status."""
    try:
        client = get_video_renderer_client()
        return await client.get_job_status(job_id)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Video renderer unavailable: {str(e)}")

@app.get("/api/v1/videos/process/{job_id}/url")
async def get_video_url(job_id: str):
    """Get processed video URL."""
    try:
        client = get_video_renderer_client()
        return await client.get_video_url(job_id)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Video renderer unavailable: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )