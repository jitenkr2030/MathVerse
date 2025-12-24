"""
MathVerse Animation Engine - Main API Application
FastAPI-based REST API for rendering mathematical animations.
"""

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from api.models import (
    RenderRequest,
    BatchRenderRequest,
    TemplateRenderRequest,
    RenderJobResponse,
    RenderProgressResponse,
    RenderResultResponse,
    SceneListResponse,
    SceneInfo,
    HealthCheckResponse,
    ErrorResponse,
    RenderStatus,
    SceneType,
    EducationalLevel,
)
from worker.celery_app import celery_app
from worker.tasks import _job_store, get_job_stats, process_render_job
from config.app_config import get_config

# Initialize job store cleanup
_job_store_cleaner = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    global _job_store_cleaner
    
    # Startup
    config = get_config()
    logger.info(f"Starting MathVerse Animation Engine v{config.version}")
    
    # Import and schedule cleanup
    from utils.cleanup import schedule_cleanup
    _job_store_cleaner = schedule_cleanup()
    
    logger.info("Animation Engine started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Animation Engine")


# Create FastAPI app
app = FastAPI(
    title="MathVerse Animation Engine",
    description="API for rendering mathematical animations using Manim",
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


# ==================== Exception Handlers ====================

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
            "detail": str(exc),
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


# ==================== Health Check ====================

@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Check the health status of the animation engine.
    
    Returns system status, dependency versions, and resource usage.
    """
    import shutil
    
    config = get_config()
    
    # Check Manim
    manim_version = None
    try:
        import manim
        manim_version = manim.__version__
    except ImportError:
        pass
    
    # Check LaTeX
    latex_installed = shutil.which("latex") is not None
    
    # Check ffmpeg
    ffmpeg_installed = shutil.which("ffmpeg") is not None
    
    # Get disk space
    disk_usage = shutil.disk_usage("/tmp")
    disk_space_mb = disk_usage.free // (1024 * 1024)
    
    # Get memory usage
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss // (1024 * 1024)
    except ImportError:
        memory_mb = None
    
    # Get job stats
    stats = get_job_stats()
    
    return HealthCheckResponse(
        status="healthy" if manim_version and latex_installed and ffmpeg_installed else "degraded",
        version=config.version,
        manim_version=manim_version,
        latex_installed=latex_installed,
        ffmpeg_installed=ffmpeg_installed,
        disk_space_mb=disk_space_mb,
        memory_usage_mb=memory_mb,
        active_jobs=stats['processing'],
        queued_jobs=stats['queued'],
    )


# ==================== Render Endpoints ====================

@app.post(
    "/api/v1/render",
    response_model=RenderJobResponse,
    status_code=202,
    tags=["Rendering"],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal error"},
    }
)
async def create_render_job(request: RenderRequest, background_tasks: BackgroundTasks):
    """
    Submit a new render job.
    
    Creates a new animation render job and returns a job ID for tracking.
    The rendering happens asynchronously in the background.
    
    - **scene_type**: Type of mathematical scene (graph, proof, geometry, etc.)
    - **level**: Educational level (primary, secondary, etc.)
    - **equations**: List of equations to display
    - **graph**: Graph configuration (for graph scenes)
    - **shapes**: Geometry shapes (for geometry scenes)
    - **proof_steps**: Proof steps (for proof scenes)
    - **quality**: Video quality (l, m, h, k)
    """
    import uuid
    
    job_id = str(uuid.uuid4())
    
    # Initialize job in store
    _job_store[job_id] = {
        'status': RenderStatus.QUEUED,
        'progress': 0.0,
        'stage': 'queued',
        'message': 'Job queued',
        'request': request.model_dump(),
        'created_at': datetime.utcnow().isoformat(),
    }
    
    # Submit to Celery queue
    try:
        celery_app.send_task(
            'worker.tasks.render_animation_task',
            args=[job_id, request.model_dump()],
            queue='render',
            priority=request.priority,
        )
    except Exception as e:
        # Fallback: run directly (for development without Celery)
        logger.warning(f"Celery unavailable, running synchronously: {e}")
        background_tasks.add_task(process_render_job, job_id, request.model_dump())
    
    return RenderJobResponse(
        job_id=job_id,
        status=RenderStatus.QUEUED,
        message="Job queued successfully. Use /api/v1/render/{job_id}/status to track progress.",
        estimated_time=120,  # Estimate 2 minutes
    )


@app.post(
    "/api/v1/render/batch",
    response_model=list[RenderJobResponse],
    status_code=202,
    tags=["Rendering"],
)
async def create_batch_render_jobs(request: BatchRenderRequest):
    """
    Submit multiple render jobs in a batch.
    
    Creates multiple animation render jobs and returns their job IDs.
    Jobs are processed according to their priority.
    """
    import uuid
    
    job_responses = []
    
    for render_request in request.requests:
        job_id = str(uuid.uuid4())
        
        _job_store[job_id] = {
            'status': RenderStatus.QUEUED,
            'progress': 0.0,
            'stage': 'queued',
            'message': 'Batch job queued',
            'request': render_request.model_dump(),
            'created_at': datetime.utcnow().isoformat(),
        }
        
        celery_app.send_task(
            'worker.tasks.render_animation_task',
            args=[job_id, render_request.model_dump()],
            queue='render',
            priority=render_request.priority if hasattr(render_request, 'priority') else 5,
        )
        
        job_responses.append(RenderJobResponse(
            job_id=job_id,
            status=RenderStatus.QUEUED,
            message="Job queued",
        ))
    
    return job_responses


@app.get(
    "/api/v1/render/{job_id}/status",
    response_model=RenderProgressResponse,
    tags=["Rendering"],
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
    }
)
async def get_render_status(job_id: str):
    """
    Get the status and progress of a render job.
    
    Returns the current stage, progress percentage, and estimated time remaining.
    """
    job_data = _job_store.get(job_id)
    
    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Parse datetime fields
    created_at = datetime.fromisoformat(job_data.get('created_at', datetime.utcnow().isoformat()))
    started_at = None
    completed_at = None
    
    if job_data.get('started_at'):
        started_at = datetime.fromisoformat(job_data['started_at'])
    if job_data.get('completed_at'):
        completed_at = datetime.fromisoformat(job_data['completed_at'])
    
    return RenderProgressResponse(
        job_id=job_id,
        status=job_data.get('status', RenderStatus.QUEUED),
        progress=job_data.get('progress', 0.0),
        stage=job_data.get('stage'),
        message=job_data.get('message'),
        created_at=created_at,
        started_at=started_at,
        completed_at=completed_at,
    )


@app.get(
    "/api/v1/render/{job_id}/result",
    response_model=RenderResultResponse,
    tags=["Rendering"],
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
        202: {"description": "Job still processing"},
    }
)
async def get_render_result(job_id: str):
    """
    Get the result of a completed render job.
    
    Returns the video URL, thumbnail URL, and metadata.
    If the job is still processing, returns 202 Accepted.
    """
    job_data = _job_store.get(job_id)
    
    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    status = job_data.get('status', RenderStatus.QUEUED)
    
    if status != RenderStatus.COMPLETED:
        raise HTTPException(
            status_code=202,
            detail=f"Job still {status.value}. Use /status endpoint to check progress."
        )
    
    # Parse datetime fields
    created_at = datetime.fromisoformat(job_data.get('created_at', datetime.utcnow().isoformat()))
    completed_at = None
    if job_data.get('completed_at'):
        completed_at = datetime.fromisoformat(job_data['completed_at'])
    
    return RenderResultResponse(
        job_id=job_id,
        status=status,
        video_url=job_data.get('video_url'),
        thumbnail_url=job_data.get('thumbnail_url'),
        duration=job_data.get('duration_estimate'),
        file_size=job_data.get('file_size'),
        created_at=created_at,
        completed_at=completed_at,
        error_message=job_data.get('error_message'),
        error_details=job_data.get('error_details'),
    )


@app.delete(
    "/api/v1/render/{job_id}",
    tags=["Rendering"],
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
    }
)
async def cancel_render_job(job_id: str):
    """
    Cancel a pending or processing render job.
    
    If the job is being processed, it will be stopped gracefully.
    """
    job_data = _job_store.get(job_id)
    
    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    status = job_data.get('status')
    
    if status == RenderStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Cannot cancel completed job")
    
    if status == RenderStatus.FAILED:
        raise HTTPException(status_code=400, detail="Job has already failed")
    
    # Revoke Celery task if possible
    try:
        celery_app.control.revoke(job_id, terminate=True)
    except Exception:
        pass
    
    _job_store[job_id]['status'] = RenderStatus.CANCELLED
    _job_store[job_id]['message'] = "Job cancelled by user"
    
    return {"message": f"Job {job_id} cancelled"}


# ==================== Scene Endpoints ====================

@app.get(
    "/api/v1/scenes",
    response_model=SceneListResponse,
    tags=["Scenes"],
)
async def list_available_scenes(
    level: Optional[EducationalLevel] = None,
    scene_type: Optional[SceneType] = None,
):
    """
    List all available scene templates and presets.
    
    Returns information about all available scenes that can be rendered.
    Optionally filter by educational level and scene type.
    """
    # Get scenes from file system
    scenes_dir = Path("manim_scenes")
    scenes = []
    
    if scenes_dir.exists():
        for level_dir in scenes_dir.iterdir():
            if level_dir.is_dir() and level_dir.name != "__pycache__":
                if level and level.value != level_dir.name:
                    continue
                
                for py_file in level_dir.glob("*.py"):
                    if py_file.name.startswith("_"):
                        continue
                    
                    scenes.append(SceneInfo(
                        id=f"{level_dir.name}/{py_file.stem}",
                        name=py_file.stem.replace("_", " ").title(),
                        scene_type=SceneType.CUSTOM,
                        level=EducationalLevel(level_dir.name),
                        description=f"Scene from {py_file.name}",
                    ))
    
    # Filter by scene type if specified
    if scene_type:
        scenes = [s for s in scenes if s.scene_type == scene_type]
    
    return SceneListResponse(scenes=scenes, total=len(scenes))


@app.get(
    "/api/v1/scenes/{scene_id}",
    response_model=SceneInfo,
    tags=["Scenes"],
    responses={
        404: {"model": ErrorResponse, "description": "Scene not found"},
    }
)
async def get_scene_info(scene_id: str):
    """
    Get detailed information about a specific scene.
    """
    # This would load from file system or database
    parts = scene_id.split("/")
    
    if len(parts) != 2:
        raise HTTPException(status_code=404, detail="Invalid scene ID format")
    
    level, name = parts
    
    return SceneInfo(
        id=scene_id,
        name=name.replace("_", " ").title(),
        scene_type=SceneType.CUSTOM,
        level=EducationalLevel(level),
        description=f"Scene: {name}",
        parameters={
            "supported_types": ["graph", "proof", "geometry"],
            "max_duration": 300,
        },
    )


# ==================== Stats Endpoints ====================

@app.get("/api/v1/stats", tags=["Stats"])
async def get_service_stats():
    """
    Get service statistics and metrics.
    """
    stats = get_job_stats()
    
    return {
        "total_jobs": len(_job_store),
        "queued": stats['queued'],
        "processing": stats['processing'],
        "completed": stats['completed'],
        "failed": stats['failed'],
        "success_rate": (
            stats['completed'] / (stats['completed'] + stats['failed'])
            if (stats['completed'] + stats['failed']) > 0
            else 0
        ),
    }


# ==================== Main Entry Point ====================

def main():
    """Run the API server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MathVerse Animation Engine")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    config = get_config()
    
    uvicorn.run(
        "api.main:app",
        host=args.host,
        port=args.port,
        workers=args.workers or config.workers,
        reload=args.reload or config.debug,
        log_level=config.log_level.lower(),
    )


if __name__ == "__main__":
    main()
