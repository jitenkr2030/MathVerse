"""
MathVerse Recommendation Engine - Main API Application
FastAPI-based REST API for personalized learning recommendations.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
import time
import logging

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, async_session_factory
from app.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    LearningPathRequest,
    LearningPathResponse,
    EventIngestRequest,
    BulkEventRequest,
    StudentProfileUpdateRequest,
    ContentRecommendation,
    HealthCheckResponse,
    StatsResponse,
)
from app.models import (
    StudentProfile,
    ContentItem,
    Interaction,
    MasterySnapshot,
    RecommendationLog,
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request counter
request_count = 0
start_time = datetime.utcnow()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    global start_time
    start_time = datetime.utcnow()
    
    logger.info(f"Starting MathVerse Recommendation Engine v{settings.VERSION}")
    
    # Initialize database tables
    from app.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Load mock data if database is empty
    await _load_initial_data()
    
    logger.info("Recommendation Engine started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Recommendation Engine")


# Create FastAPI app
app = FastAPI(
    title="MathVerse Recommendation Engine",
    description="API for personalized learning recommendations and analytics",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": f"HTTP_{exc.status_code}",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    logger.exception(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else None,
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


# Import and include routers
from app.routes.recommend import router as recommend_router

app.include_router(recommend_router, prefix="/api/v1")


# ==================== Health Check ====================

@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Check the health status of the recommendation engine.
    """
    from sqlalchemy import text
    
    db_connected = False
    redis_connected = False
    
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            db_connected = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    try:
        import redis
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        r.ping()
        redis_connected = True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
    
    # Count records
    try:
        async with async_session_factory() as session:
            student_count = (await session.execute(
                text("SELECT COUNT(*) FROM student_profiles")
            )).scalar() or 0
            
            content_count = (await session.execute(
                text("SELECT COUNT(*) FROM content_items")
            )).scalar() or 0
            
            rec_count = (await session.execute(
                text("SELECT COUNT(*) FROM recommendation_logs WHERE created_at > NOW() - INTERVAL '1 hour'")
            )).scalar() or 0
    except:
        student_count = 0
        content_count = 0
        rec_count = 0
    
    return HealthCheckResponse(
        status="healthy" if db_connected else "degraded",
        version=settings.VERSION,
        model_loaded=True,
        database_connected=db_connected,
        redis_connected=redis_connected,
        total_students=student_count,
        total_content_items=content_count,
        active_recommendations=rec_count,
        timestamp=datetime.utcnow(),
    )


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.
    """
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")


@app.get("/live", tags=["Health"])
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    """
    return {"alive": True}


# ==================== Event Ingestion ====================

@app.post("/api/v1/events/ingest", status_code=status.HTTP_202_ACCEPTED, tags=["Events"])
async def ingest_event(
    event: EventIngestRequest,
    background_tasks: BackgroundTasks,
):
    """
    Ingest a single student interaction event.
    Events are processed asynchronously to avoid blocking the API.
    """
    global request_count
    request_count += 1
    
    background_tasks.add_task(_process_event, event)
    
    return {
        "message": "Event accepted for processing",
        "event_id": f"evt_{int(time.time() * 1000)}",
    }


@app.post("/api/v1/events/bulk", status_code=status.HTTP_202_ACCEPTED, tags=["Events"])
async def ingest_bulk_events(
    request: BulkEventRequest,
    background_tasks: BackgroundTasks,
):
    """
    Ingest multiple events in bulk.
    """
    global request_count
    request_count += len(request.events)
    
    background_tasks.add_task(_process_bulk_events, request.events)
    
    return {
        "message": f"Accepted {len(request.events)} events for processing",
        "count": len(request.events),
    }


async def _process_event(event: EventIngestRequest):
    """Process a single event"""
    try:
        async with async_session_factory() as session:
            # Ensure student profile exists
            profile = await session.execute(
                text("SELECT * FROM student_profiles WHERE student_id = :sid"),
                {"sid": event.student_id}
            )
            profile = profile.fetchone()
            
            if not profile:
                new_profile = StudentProfile(
                    student_id=event.student_id,
                    total_learning_time_minutes=0,
                )
                session.add(new_profile)
            
            # Record interaction
            interaction = Interaction(
                student_id=event.student_id,
                content_id=event.content_id,
                interaction_type=event.event_type.value if hasattr(event.event_type, 'value') else event.event_type,
                topic_id=event.topic_id,
                concept=event.concept_id,
                metadata=event.metadata,
                timestamp=event.timestamp,
            )
            session.add(interaction)
            
            await session.commit()
            
    except Exception as e:
        logger.error(f"Failed to process event: {e}")


async def _process_bulk_events(events: list):
    """Process multiple events"""
    for event in events:
        await _process_event(event)


# ==================== Student Profile Management ====================

@app.get("/api/v1/students/{student_id}/profile", tags=["Students"])
async def get_student_profile(student_id: int):
    """
    Get a student's profile and learning statistics.
    """
    try:
        async with async_session_factory() as session:
            # Get profile
            result = await session.execute(
                text("""
                    SELECT sp.*, 
                           COUNT(DISTINCT i.id) as total_interactions,
                           SUM(CASE WHEN i.interaction_type = 'video_complete' OR i.interaction_type = 'quiz_complete' THEN 1 ELSE 0 END) as completed_content
                    FROM student_profiles sp
                    LEFT JOIN interactions i ON sp.student_id = i.student_id
                    WHERE sp.student_id = :sid
                    GROUP BY sp.id
                """),
                {"sid": student_id}
            )
            profile = result.fetchone()
            
            if not profile:
                raise HTTPException(status_code=404, detail="Student not found")
            
            # Get mastery levels
            mastery_result = await session.execute(
                text("""
                    SELECT topic, mastery_level, last_interaction
                    FROM mastery_snapshots
                    WHERE student_id = :sid
                    ORDER BY mastery_level ASC
                """),
                {"sid": student_id}
            )
            mastery_levels = [
                {"topic": row.topic, "mastery": row.mastery_level}
                for row in mastery_result.fetchall()
            ]
            
            return {
                "student_id": student_id,
                "learning_style": profile.learning_style,
                "preferred_content_types": profile.preferred_content_types or [],
                "daily_goal_minutes": profile.daily_goal_minutes,
                "weak_areas_focus": profile.weak_areas_focus or [],
                "total_learning_time_minutes": profile.total_learning_time_minutes,
                "current_streak_days": profile.current_streak_days,
                "total_interactions": profile.total_interactions or 0,
                "completed_content": profile.completed_content or 0,
                "mastery_levels": mastery_levels,
                "last_active": profile.last_active_date.isoformat() if profile.last_active_date else None,
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/v1/students/{student_id}/profile", tags=["Students"])
async def update_student_profile(
    student_id: int,
    update: StudentProfileUpdateRequest,
):
    """
    Update a student's profile preferences.
    """
    try:
        async with async_session_factory() as session:
            # Check if profile exists
            result = await session.execute(
                text("SELECT id FROM student_profiles WHERE student_id = :sid"),
                {"sid": student_id}
            )
            existing = result.fetchone()
            
            if not existing:
                # Create new profile
                new_profile = StudentProfile(
                    student_id=student_id,
                    learning_style=update.learning_style.value if update.learning_style else None,
                    preferred_content_types=[ct.value for ct in update.preferred_content_types] if update.preferred_content_types else None,
                    daily_goal_minutes=update.daily_goal_minutes or 30,
                    weak_areas_focus=update.weak_areas_focus or [],
                )
                session.add(new_profile)
            else:
                # Update existing
                update_data = {}
                if update.learning_style:
                    update_data["learning_style"] = update.learning_style.value
                if update.preferred_content_types:
                    update_data["preferred_content_types"] = [ct.value for ct in update.preferred_content_types]
                if update.daily_goal_minutes:
                    update_data["daily_goal_minutes"] = update.daily_goal_minutes
                if update.weak_areas_focus is not None:
                    update_data["weak_areas_focus"] = update.weak_areas_focus
                
                if update_data:
                    update_data["updated_at"] = datetime.utcnow()
                    await session.execute(
                        text("""
                            UPDATE student_profiles 
                            SET updated_at = :updated_at
                            WHERE student_id = :sid
                        """),
                        {"sid": student_id, "updated_at": datetime.utcnow()}
                    )
            
            await session.commit()
            
            return {"message": "Profile updated successfully"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Statistics ====================

@app.get("/api/v1/stats", response_model=StatsResponse, tags=["Statistics"])
async def get_service_stats():
    """
    Get service statistics and metrics.
    """
    global request_count
    
    try:
        async with async_session_factory() as session:
            # Active students in last 24h
            active_result = await session.execute(
                text("""
                    SELECT COUNT(DISTINCT student_id) 
                    FROM interactions 
                    WHERE timestamp > NOW() - INTERVAL '24 hours'
                """)
            )
            active_students = active_result.scalar() or 0
            
            # Recommendations in last 24h
            rec_result = await session.execute(
                text("""
                    SELECT COUNT(*) 
                    FROM recommendation_logs 
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                """)
            )
            rec_24h = rec_result.scalar() or 0
            
            # Average latency (simulated)
            avg_latency = 45.2  # In production, track this metric
            
            # Cache hit rate (simulated)
            cache_hit_rate = 0.78
            
            # Popular content
            popular_result = await session.execute(
                text("""
                    SELECT content_id, COUNT(*) as interaction_count
                    FROM interactions
                    WHERE content_id IS NOT NULL
                    GROUP BY content_id
                    ORDER BY interaction_count DESC
                    LIMIT 5
                """)
            )
            popular_content = [
                {"content_id": row.content_id, "interactions": row.interaction_count}
                for row in popular_result.fetchall()
            ]
            
            return StatsResponse(
                total_requests=request_count,
                average_latency_ms=avg_latency,
                cache_hit_rate=cache_hit_rate,
                popular_content=popular_content,
                active_students_24h=active_students,
                recommendations_generated_24h=rec_24h,
            )
            
    except Exception as e:
        return StatsResponse(
            total_requests=request_count,
            average_latency_ms=0,
            cache_hit_rate=0,
            popular_content=[],
            active_students_24h=0,
            recommendations_generated_24h=0,
        )


# ==================== Content Endpoints ====================

@app.get("/api/v1/content", tags=["Content"])
async def list_content(
    content_type: Optional[str] = Query(default=None),
    topic: Optional[str] = Query(default=None),
    difficulty: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    List available content items with optional filtering.
    """
    try:
        async with async_session_factory() as session:
            query = "SELECT * FROM content_items WHERE is_active = true"
            params = {}
            
            if content_type:
                query += " AND content_type = :ctype"
                params["ctype"] = content_type
            if topic:
                query += " AND topic = :topic"
                params["topic"] = topic
            if difficulty:
                query += " AND difficulty = :diff"
                params["diff"] = difficulty
            
            query += f" ORDER BY popularity_score DESC LIMIT :limit OFFSET :offset"
            params["limit"] = limit
            params["offset"] = offset
            
            result = await session.execute(text(query), params)
            items = result.fetchall()
            
            return {
                "items": [
                    {
                        "content_id": item.content_id,
                        "title": item.title,
                        "content_type": item.content_type,
                        "difficulty": item.difficulty,
                        "topic": item.topic,
                        "duration_minutes": item.duration_minutes,
                        "popularity_score": item.popularity_score,
                    }
                    for item in items
                ],
                "total": len(items),
                "limit": limit,
                "offset": offset,
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Mastery Endpoints ====================

@app.get("/api/v1/students/{student_id}/mastery", tags=["Mastery"])
async def get_student_mastery(student_id: int):
    """
    Get a student's current mastery levels across topics.
    """
    try:
        async with async_session_factory() as session:
            result = await session.execute(
                text("""
                    SELECT topic, mastery_level, confidence, sample_size, 
                           last_interaction, predicted_next_mastery
                    FROM mastery_snapshots
                    WHERE student_id = :sid
                    ORDER BY mastery_level DESC
                """),
                {"sid": student_id}
            )
            snapshots = result.fetchall()
            
            if not snapshots:
                return {
                    "student_id": student_id,
                    "mastery_levels": [],
                    "average_mastery": 0.0,
                    "strong_areas": [],
                    "weak_areas": [],
                }
            
            mastery_list = [
                {
                    "topic": s.topic,
                    "mastery_level": s.mastery_level,
                    "confidence": s.confidence,
                    "sample_size": s.sample_size,
                    "last_interaction": s.last_interaction.isoformat() if s.last_interaction else None,
                    "predicted_next_mastery": s.predicted_next_mastery,
                }
                for s in snapshots
            ]
            
            avg_mastery = sum(s.mastery_level for s in snapshots) / len(snapshots)
            strong_areas = [s.topic for s in snapshots if s.mastery_level >= 0.7]
            weak_areas = [s.topic for s in snapshots if s.mastery_level < 0.4]
            
            return {
                "student_id": student_id,
                "mastery_levels": mastery_list,
                "average_mastery": avg_mastery,
                "strong_areas": strong_areas,
                "weak_areas": weak_areas,
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Info Endpoints ====================

@app.get("/api/v1/info", tags=["Info"])
async def get_service_info():
    """
    Get service information.
    """
    return {
        "name": "MathVerse Recommendation Engine",
        "version": "1.0.0",
        "description": "ML-powered personalized learning recommendations",
        "algorithms": [
            "rule_based",
            "adaptive",
            "graph_based",
        ],
        "endpoints": {
            "recommendations": "/api/v1/recommend",
            "learning_path": "/api/v1/learning-path",
            "concepts": "/api/v1/concepts/recommend",
            "weaknesses": "/api/v1/weaknesses",
            "progress": "/api/v1/progress",
        },
    }


# ==================== Utilities ====================

async def _load_initial_data():
    """Load initial mock data if database is empty"""
    try:
        async with async_session_factory() as session:
            # Check if data exists
            result = await session.execute(text("SELECT COUNT(*) FROM content_items"))
            count = result.scalar() or 0
            
            if count == 0:
                logger.info("Loading initial content data...")
                # Load from mock_profiles.json or create default content
                from pathlib import Path
                import json
                
                mock_path = Path(__file__).parent.parent / "data" / "mock_profiles.json"
                if mock_path.exists():
                    # Create sample content items
                    sample_content = [
                        {"content_id": 1, "title": "Introduction to Algebra", "content_type": "video", "difficulty": "beginner", "topic": "algebra_1", "duration_minutes": 15, "popularity_score": 0.9},
                        {"content_id": 2, "title": "Linear Equations Quiz", "content_type": "quiz", "difficulty": "beginner", "topic": "algebra_1", "duration_minutes": 10, "popularity_score": 0.85},
                        {"content_id": 3, "title": "Variables and Expressions", "content_type": "video", "difficulty": "beginner", "topic": "algebra_1", "duration_minutes": 20, "popularity_score": 0.88},
                        {"content_id": 4, "title": "Practice: Solving Equations", "content_type": "exercise", "difficulty": "elementary", "topic": "algebra_1", "duration_minutes": 25, "popularity_score": 0.82},
                        {"content_id": 5, "title": "Graphing Linear Functions", "content_type": "video", "difficulty": "intermediate", "topic": "linear_functions", "duration_minutes": 18, "popularity_score": 0.87},
                    ]
                    
                    for item in sample_content:
                        content = ContentItem(**item)
                        session.add(content)
                    
                    await session.commit()
                    logger.info(f"Loaded {len(sample_content)} sample content items")
                    
    except Exception as e:
        logger.warning(f"Failed to load initial data: {e}")


# ==================== Main Entry Point ====================

def main():
    """Run the API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MathVerse Recommendation Engine")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8003, help="Port to bind")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        workers=args.workers,
        reload=args.reload or settings.DEBUG,
        log_level="info",
    )


if __name__ == "__main__":
    main()
