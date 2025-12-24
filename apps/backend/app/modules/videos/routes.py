"""
MathVerse Backend API - Videos Module
======================================
Video and animation rendering endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
import httpx
import json

from app.database import get_db
from app.models import Video, Lesson, User, UserRole
from app.schemas import (
    VideoCreate, VideoResponse, VideoStreamingResponse,
    AnimationRenderRequest, AnimationRenderResponse, MessageResponse
)
from app.dependencies import get_current_user, get_or_404, require_creator


router = APIRouter()


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: int, db: Session = Depends(get_db)):
    """
    Get video metadata by ID.
    """
    video = await get_or_404(Video, video_id, db, "Video not found")
    return video


@router.get("/lesson/{lesson_id}", response_model=VideoResponse)
async def get_lesson_video(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get video for a specific lesson.
    """
    lesson = await get_or_404(Lesson, lesson_id, db, "Lesson not found")
    
    if not lesson.video_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No video available for this lesson"
        )
    
    # Create or get video record
    video = db.execute(
        select(Video).where(Video.lesson_id == lesson_id)
    ).scalar_one_or_none()
    
    if not video:
        video = Video(
            title=lesson.title,
            description=lesson.description or "",
            lesson_id=lesson_id,
            url=lesson.video_url,
            duration=lesson.video_duration or 0,
            format="mp4"
        )
        db.add(video)
        db.commit()
        db.refresh(video)
    
    return video


@router.post("/", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def create_video(
    video_data: VideoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create video metadata (creator only).
    """
    if current_user.role not in [UserRole.TEACHER, UserRole.CREATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only creators can add videos"
        )
    
    lesson = await get_or_404(Lesson, video_data.lesson_id, db, "Lesson not found")
    
    video = Video(
        title=video_data.title,
        description=video_data.description,
        lesson_id=video_data.lesson_id,
        url=video_data.url,
        duration=video_data.duration,
        quality=video_data.quality,
        file_size=video_data.file_size,
        format=video_data.format
    )
    
    db.add(video)
    db.commit()
    db.refresh(video)
    
    return video


@router.delete("/{video_id}", response_model=MessageResponse)
async def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete video (creator only).
    """
    video = await get_or_404(Video, video_id, db, "Video not found")
    
    if current_user.role != UserRole.ADMIN:
        lesson = await get_or_404(Lesson, video.lesson_id, db, "Lesson not found")
        if lesson.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this video"
            )
    
    db.delete(video)
    db.commit()
    
    return MessageResponse(
        message="Video deleted successfully",
        detail="Video metadata has been removed"
    )


# ==================== ANIMATION RENDERING ====================

@router.post("/render/animation", response_model=AnimationRenderResponse)
async def render_animation(
    render_request: AnimationRenderRequest,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Request animation rendering from the animation engine service.
    """
    lesson = await get_or_404(Lesson, render_request.lesson_id, db, "Lesson not found")
    
    # Validate animation parameters
    if not render_request.scene_path or not render_request.scene_class:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scene path and class are required"
        )
    
    # Generate job ID
    import uuid
    job_id = str(uuid.uuid4())
    
    # In production, this would call the animation-engine service
    # For now, we return a mock response
    estimated_time = 60  # seconds
    
    # Background task to call animation engine (commented out for now)
    """
    async def call_animation_engine():
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.ANIMATION_ENGINE_URL}/render",
                    json={
                        "job_id": job_id,
                        "scene_path": render_request.scene_path,
                        "scene_class": render_request.scene_class,
                        "quality": render_request.quality,
                        "output_format": render_request.output_format,
                        "voiceover_text": render_request.voiceover_text
                    },
                    timeout=60.0
                )
                if response.status_code != 200:
                    # Handle error
                    pass
            except httpx.RequestError as e:
                # Handle request error
                pass
    
    if background_tasks:
        background_tasks.add_task(call_animation_engine)
    """
    
    return AnimationRenderResponse(
        job_id=job_id,
        status="queued",
        estimated_time=estimated_time,
        created_at=__import__('datetime').datetime.utcnow()
    )


@router.get("/render/status/{job_id}")
async def get_render_status(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get animation rendering job status.
    """
    # In production, this would check with the animation-engine service
    # For now, return mock status
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "output_url": f"/api/videos/download/{job_id}",
        "completed_at": __import__('datetime').datetime.utcnow()
    }


@router.get("/render/queue")
async def get_render_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's rendering queue.
    """
    # In production, this would query the animation engine
    return {
        "queue": [],
        "active_jobs": 0,
        "completed_today": 0
    }


@router.post("/render/cancel/{job_id}", response_model=MessageResponse)
async def cancel_render_job(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a rendering job.
    """
    # In production, this would cancel with the animation engine
    return MessageResponse(
        message="Render job cancelled",
        detail=f"Job {job_id} has been cancelled"
    )


@router.get("/download/{job_id}")
async def download_rendered_video(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get download URL for rendered video.
    """
    # In production, this would return a signed URL
    return {
        "download_url": f"/api/videos/static/{job_id}.mp4",
        "expires_in": 3600
    }
