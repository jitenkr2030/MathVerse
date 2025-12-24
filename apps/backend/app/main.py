"""
MathVerse Backend API - Main Application Entry Point

This is the main FastAPI application for the MathVerse platform,
providing a comprehensive API for mathematics education with
animated content, personalized learning, and creator tools.
"""

import os
import sys
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import service clients for microservice integration
from services.internal_client import (
    check_all_services_healthy,
    close_all_clients,
    get_recommendation_client,
    get_content_metadata_client,
    get_animation_engine_client,
    get_video_renderer_client
)

# Import webhook handler
from services.stripe_webhook import process_stripe_webhook

# Import routers
from app.modules.auth.routes import router as auth_router
from app.modules.users.routes import router as users_router
from app.modules.courses.routes import router as courses_router
from app.modules.lessons.routes import router as lessons_router
from app.modules.videos.routes import router as videos_router
from app.modules.quizzes.routes import router as quizzes_router
from app.modules.progress.routes import router as progress_router
from app.modules.payments.routes import router as payments_router
from app.modules.creators.routes import router as creators_router

# Security scheme
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
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


# Create FastAPI application with OpenAPI metadata
app = FastAPI(
    title="MathVerse API",
    description="""
# MathVerse Platform API

Animation-first Mathematics Learning Platform API providing personalized 
educational content, creator tools, and payment processing.

## Features

- **Authentication**: JWT-based authentication with token refresh
- **Courses & Lessons**: Structured educational content with video support
- **Progress Tracking**: Monitor learning progress and mastery levels
- **Recommendations**: AI-powered personalized course recommendations
- **Content Search**: Full-text search across all educational content
- **Animations**: Manim-based mathematical animation rendering
- **Payments**: Stripe integration for course purchases and subscriptions
- **Creator Tools**: Course management and earnings tracking

## Authentication

All protected endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## Rate Limiting

Currently, no rate limiting is enforced. Future versions will include
rate limits to prevent abuse.

## Support

For API support, contact support@mathverse.com
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    terms_of_service="https://mathverse.com/terms",
    contact={
        "name": "MathVerse Support",
        "email": "support@mathverse.com",
        "url": "https://mathverse.com/contact"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom OpenAPI schema with security scheme
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT authorization header using the Bearer scheme"
        }
    }
    
    # Apply security to all endpoints
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"bearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Include routers with tags for documentation
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(courses_router, prefix="/api/courses", tags=["Courses"])
app.include_router(lessons_router, prefix="/api/lessons", tags=["Lessons"])
app.include_router(videos_router, prefix="/api/videos", tags=["Videos"])
app.include_router(quizzes_router, prefix="/api/quizzes", tags=["Quizzes"])
app.include_router(progress_router, prefix="/api/progress", tags=["Progress"])
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])
app.include_router(creators_router, prefix="/api/creators", tags=["Creators"])


# ==================== Health Check Endpoints ====================

@app.get("/", tags=["Health"])
async def root():
    """
    API root endpoint with basic information.
    """
    return {
        "message": "Welcome to MathVerse API",
        "description": "Animation-first Mathematics Learning Platform",
        "version": "1.0.0",
        "documentation": "/docs",
        "redoc_documentation": "/redoc",
        "openapi_spec": "/openapi.json"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint.
    
    Returns the status of the main backend service.
    """
    return {"status": "healthy", "service": "mathverse-backend"}


@app.get("/health/services", tags=["Health"])
async def services_health():
    """
    Check health of all microservices.
    
    Returns the status of all connected microservices including
    the recommendation engine, content metadata service,
    animation engine, and video renderer.
    """
    try:
        health = await check_all_services_healthy()
        all_healthy = all(health.values())
        return {
            "status": "healthy" if all_healthy else "degraded",
            "services": health
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e), 
            "services": {}
        }


# ==================== Webhook Endpoints ====================

@app.post("/api/v1/webhooks/stripe", tags=["Webhooks"])
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Stripe webhook endpoint for payment events.
    
    Handles payment confirmations, subscription updates, and
    other Stripe events. Requires valid Stripe signature.
    
    ## Events Handled
    
    - checkout.session.completed
    - invoice.payment_succeeded
    - invoice.payment_failed
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - payment_intent.succeeded
    - payment_intent.payment_failed
    """
    return await process_stripe_webhook(request, background_tasks)


# ==================== Recommendation Service Proxy Endpoints ====================

@app.get("/api/v1/recommendations", tags=["Recommendations"])
async def get_recommendations(
    user_id: int,
    course_id: int = None,
    limit: int = 10
):
    """
    Get personalized course recommendations for a user.
    
    Uses AI-powered recommendation engine to suggest courses
    based on learning history, preferences, and skill level.
    """
    try:
        client = get_recommendation_client()
        return await client.get_recommendations(user_id, course_id, limit)
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Recommendation service unavailable: {str(e)}"
        )


@app.post("/api/v1/recommendations/personalize", tags=["Recommendations"])
async def personalize_recommendations(
    user_id: int,
    preferences: dict
):
    """
    Update user preferences for personalized recommendations.
    
    Allows users to specify preferred topics, difficulty levels,
    and learning goals to improve recommendation quality.
    """
    try:
        client = get_recommendation_client()
        return await client.personalize_recommendations(user_id, preferences)
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Recommendation service unavailable: {str(e)}"
        )


@app.post("/api/v1/recommendations/analyze", tags=["Recommendations"])
async def analyze_learning_progress(
    user_id: int,
    course_id: int
):
    """
    Analyze user's learning progress in a specific course.
    
    Provides detailed analytics on time spent, concepts mastered,
    areas needing improvement, and learning velocity.
    """
    try:
        client = get_recommendation_client()
        return await client.analyze_progress(user_id, course_id)
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Recommendation service unavailable: {str(e)}"
        )


@app.get("/api/v1/recommendations/weaknesses/{user_id}", tags=["Recommendations"])
async def detect_knowledge_weaknesses(user_id: int):
    """
    Detect knowledge gaps and weaknesses for a user.
    
    Identifies concepts that need more practice based on
    quiz results, progress patterns, and learning history.
    """
    try:
        client = get_recommendation_client()
        return await client.detect_weaknesses(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Recommendation service unavailable: {str(e)}"
        )


# ==================== Content Metadata Service Proxy Endpoints ====================

@app.post("/api/v1/content/search", tags=["Content"])
async def search_content(
    query: str,
    filters: dict = None,
    page: int = 1,
    limit: int = 20
):
    """
    Search for educational content across the platform.
    
    Full-text search with optional filters for content level,
    subject, and availability (free/premium).
    """
    try:
        client = get_content_metadata_client()
        return await client.search_content(query, filters, page, limit)
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Content metadata service unavailable: {str(e)}"
        )


@app.get("/api/v1/content/curriculum", tags=["Content"])
async def get_curriculum_tree(level: str = None):
    """
    Get the complete curriculum tree structure.
    
    Returns hierarchical organization of educational content
    by level (primary, secondary, undergraduate, etc.).
    """
    try:
        client = get_content_metadata_client()
        return await client.get_curriculum_tree(level)
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Content metadata service unavailable: {str(e)}"
        )


# ==================== Animation Engine Proxy Endpoints ====================

@app.post("/api/v1/animations/render", tags=["Animations"])
async def submit_animation_render(request_data: dict):
    """
    Submit a mathematical animation for rendering.
    
    Uses Manim to generate animated visualizations of
    mathematical concepts, proofs, and graphs.
    """
    try:
        client = get_animation_engine_client()
        return await client.render_animation(request_data)
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Animation engine unavailable: {str(e)}"
        )


@app.get("/api/v1/animations/render/{job_id}/status", tags=["Animations"])
async def get_animation_render_status(job_id: str):
    """
    Get the status of an animation rendering job.
    
    Returns current status (pending, processing, completed, failed)
    and progress percentage.
    """
    try:
        client = get_animation_engine_client()
        return await client.get_render_status(job_id)
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Animation engine unavailable: {str(e)}"
        )


@app.get("/api/v1/animations/render/{job_id}/result", tags=["Animations"])
async def get_animation_render_result(job_id: str):
    """
    Get the result of a completed animation render.
    
    Returns video URL, thumbnail URL, and metadata for
    the successfully rendered animation.
    """
    try:
        client = get_animation_engine_client()
        return await client.get_render_result(job_id)
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Animation engine unavailable: {str(e)}"
        )


# ==================== Video Renderer Proxy Endpoints ====================

@app.post("/api/v1/videos/process", tags=["Videos"])
async def submit_video_processing(job_data: dict):
    """
    Submit a video for processing.
    
    Handles video transcoding, thumbnail generation, and
    format conversion for optimal playback.
    """
    try:
        client = get_video_renderer_client()
        return await client.submit_video_job(job_data)
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Video renderer unavailable: {str(e)}"
        )


@app.get("/api/v1/videos/process/{job_id}/status", tags=["Videos"])
async def get_video_processing_status(job_id: str):
    """
    Get the status of a video processing job.
    
    Returns current processing status and progress.
    """
    try:
        client = get_video_renderer_client()
        return await client.get_job_status(job_id)
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Video renderer unavailable: {str(e)}"
        )


@app.get("/api/v1/videos/process/{job_id}/url", tags=["Videos"])
async def get_processed_video_url(job_id: str):
    """
    Get the URL of a processed video.
    
    Returns the download/streaming URL for the completed
    video processing job.
    """
    try:
        client = get_video_renderer_client()
        return await client.get_video_url(job_id)
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Video renderer unavailable: {str(e)}"
        )


# Application entry point
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
