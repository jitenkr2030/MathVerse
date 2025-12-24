from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database import engine, async_session_factory
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting MathVerse Content Metadata Service v{settings.VERSION}")
    
    # Initialize database tables
    from app.models import content  # Import all models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Content Metadata Service started successfully")
    
    yield
    
    # Shutdown
    print("Shutting down Content Metadata Service")


# Create FastAPI app
app = FastAPI(
    title="MathVerse Content Metadata Service",
    description="API for managing educational content metadata, curriculum, and relationships",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "code": f"HTTP_{exc.status_code}",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
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
from app.routes.courses import router as courses_router
from app.routes.lessons import router as lessons_router
from app.routes.concepts import router as concepts_router
from app.routes.syllabus import router as syllabus_router
from app.routes.content import router as content_router

app.include_router(courses_router, prefix="/api/v1")
app.include_router(lessons_router, prefix="/api/v1")
app.include_router(concepts_router, prefix="/api/v1")
app.include_router(syllabus_router, prefix="/api/v1")
app.include_router(content_router, prefix="/api/v1")


# ==================== Health Check ====================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Check the health status of the service.
    """
    from sqlalchemy import text
    
    db_status = "unknown"
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "content-metadata",
        "version": "1.0.0",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.
    """
    from sqlalchemy import text
    
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


# ==================== Info Endpoints ====================

@app.get("/api/v1/info", tags=["Info"])
async def get_service_info():
    """
    Get service information.
    """
    return {
        "name": "MathVerse Content Metadata Service",
        "version": "1.0.0",
        "description": "Centralized management of educational math content metadata",
        "endpoints": {
            "courses": "/api/v1/courses",
            "lessons": "/api/v1/lessons",
            "concepts": "/api/v1/concepts",
            "syllabus": "/api/v1/syllabus",
            "search": "/api/v1/content/search",
            "curriculum": "/api/v1/content/curriculum",
        },
    }


# ==================== Main Entry Point ====================

def main():
    """Run the API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MathVerse Content Metadata Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind")
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
