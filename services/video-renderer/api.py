from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import uuid
import os
import json
from pathlib import Path
import subprocess
from datetime import datetime
import shutil

app = FastAPI(title="MathVerse Video Renderer", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage
RENDER_QUEUE = {}
COMPLETED_JOBS = {}
STORAGE_PATH = Path("storage")
STORAGE_PATH.mkdir(exist_ok=True)
VIDEO_PATH = STORAGE_PATH / "videos"
THUMBNAIL_PATH = STORAGE_PATH / "thumbnails"
VIDEO_PATH.mkdir(exist_ok=True)
THUMBNAIL_PATH.mkdir(exist_ok=True)

class RenderJob(BaseModel):
    job_id: str
    scene_path: str
    scene_class: str
    quality: str = "m"
    status: str = "pending"
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_file: Optional[str] = None
    thumbnail: Optional[str] = None
    error: Optional[str] = None

class RenderRequest(BaseModel):
    scene_path: str
    scene_class: str
    quality: str = "m"

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "MathVerse Video Renderer API"}

@app.post("/render", response_model=Dict[str, str])
async def create_render_job(request: RenderRequest, background_tasks: BackgroundTasks):
    """Create a new rendering job"""
    job_id = str(uuid.uuid4())
    
    job = RenderJob(
        job_id=job_id,
        scene_path=request.scene_path,
        scene_class=request.scene_class,
        quality=request.quality,
        created_at=datetime.now()
    )
    
    RENDER_QUEUE[job_id] = job
    
    # Start rendering in background
    background_tasks.add_task(render_video, job_id)
    
    return {"job_id": job_id, "status": "queued"}

@app.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get status of a rendering job"""
    if job_id in RENDER_QUEUE:
        job = RENDER_QUEUE[job_id]
        return JobStatus(
            job_id=job.job_id,
            status=job.status,
            result={
                "output_file": job.output_file,
                "thumbnail": job.thumbnail
            } if job.output_file else None,
            error=job.error
        )
    elif job_id in COMPLETED_JOBS:
        job = COMPLETED_JOBS[job_id]
        return JobStatus(
            job_id=job.job_id,
            status=job.status,
            result={
                "output_file": job.output_file,
                "thumbnail": job.thumbnail
            } if job.output_file else None,
            error=job.error
        )
    else:
        raise HTTPException(status_code=404, detail="Job not found")

@app.get("/jobs")
async def list_jobs():
    """List all rendering jobs"""
    all_jobs = {**RENDER_QUEUE, **COMPLETED_JOBS}
    return {
        "jobs": [
            {
                "job_id": job.job_id,
                "scene_path": job.scene_path,
                "scene_class": job.scene_class,
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None
            }
            for job in all_jobs.values()
        ]
    }

@app.post("/upload-scene")
async def upload_scene(file: UploadFile = File(...)):
    """Upload a new scene file"""
    if not file.filename.endswith('.py'):
        raise HTTPException(status_code=400, detail="Only Python files are allowed")
    
    # Determine scene level from path or filename
    file_content = await file.read()
    
    # Save file
    upload_path = STORAGE_PATH / "scenes" / file.filename
    upload_path.parent.mkdir(exist_ok=True)
    
    with open(upload_path, 'wb') as f:
        f.write(file_content)
    
    return {"message": "Scene uploaded successfully", "path": str(upload_path)}

@app.get("/scenes")
async def list_scenes():
    """List available scenes"""
    scenes = []
    scenes_dir = Path("../animation-engine/manim_scenes")
    
    if scenes_dir.exists():
        for level_dir in scenes_dir.iterdir():
            if level_dir.is_dir():
                for py_file in level_dir.glob("*.py"):
                    # Extract scene classes (simplified)
                    try:
                        with open(py_file, 'r') as f:
                            content = f.read()
                        
                        import re
                        pattern = r'class\s+(\w+)\s*\(\s*[^)]*Scene[^)]*\)'
                        matches = re.findall(pattern, content)
                        
                        for scene_class in matches:
                            scenes.append({
                                "level": level_dir.name,
                                "file": py_file.name,
                                "scene": scene_class,
                                "path": str(py_file.relative_to(scenes_dir))
                            })
                    except:
                        continue
    
    return {"scenes": scenes}

@app.get("/video/{job_id}")
async def get_video(job_id: str):
    """Stream rendered video"""
    job = None
    if job_id in RENDER_QUEUE:
        job = RENDER_QUEUE[job_id]
    elif job_id in COMPLETED_JOBS:
        job = COMPLETED_JOBS[job_id]
    
    if not job or not job.output_file:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video_path = Path(job.output_file)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"{job.scene_class}.mp4"
    )

@app.get("/thumbnail/{job_id}")
async def get_thumbnail(job_id: str):
    """Get video thumbnail"""
    job = None
    if job_id in RENDER_QUEUE:
        job = RENDER_QUEUE[job_id]
    elif job_id in COMPLETED_JOBS:
        job = COMPLETED_JOBS[job_id]
    
    if not job or not job.thumbnail:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    
    thumbnail_path = Path(job.thumbnail)
    if not thumbnail_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail file not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        thumbnail_path,
        media_type="image/jpeg",
        filename=f"{job.scene_class}_thumb.jpg"
    )

async def render_video(job_id: str):
    """Background task to render video"""
    job = RENDER_QUEUE.get(job_id)
    if not job:
        return
    
    try:
        job.status = "processing"
        job.started_at = datetime.now()
        
        # Build render command
        scene_path = f"../animation-engine/manim_scenes/{job.scene_path}"
        output_file = VIDEO_PATH / f"{job.job_id}_{job.scene_class}.mp4"
        
        cmd = [
            "python", "-m", "manim",
            scene_path,
            job.scene_class,
            f"-{job.quality}",
            "--output_file", str(VIDEO_PATH),
            "--media_dir", str(STORAGE_PATH)
        ]
        
        # Run rendering
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="../animation-engine"
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # Find output file
            for file_path in VIDEO_PATH.glob(f"*{job.scene_class}*.mp4"):
                output_file = file_path
                break
            
            job.output_file = str(output_file)
            job.status = "completed"
            job.completed_at = datetime.now()
            
            # Generate thumbnail
            thumbnail_path = THUMBNAIL_PATH / f"{job.job_id}_{job.scene_class}.jpg"
            thumbnail_cmd = [
                "ffmpeg", "-i", str(output_file),
                "-ss", "00:00:05",
                "-vframes", "1",
                "-q:v", "2",
                str(thumbnail_path),
                "-y"
            ]
            
            await asyncio.create_subprocess_exec(*thumbnail_cmd)
            job.thumbnail = str(thumbnail_path)
            
            # Move to completed jobs
            COMPLETED_JOBS[job_id] = RENDER_QUEUE.pop(job_id)
            
        else:
            job.status = "failed"
            job.error = stderr.decode()
            job.completed_at = datetime.now()
            
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        job.completed_at = datetime.now()

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and its files"""
    job = None
    if job_id in RENDER_QUEUE:
        job = RENDER_QUEUE.pop(job_id)
    elif job_id in COMPLETED_JOBS:
        job = COMPLETED_JOBS.pop(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete files
    if job.output_file:
        try:
            os.remove(job.output_file)
        except:
            pass
    
    if job.thumbnail:
        try:
            os.remove(job.thumbnail)
        except:
            pass
    
    return {"message": "Job deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)