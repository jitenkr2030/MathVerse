"""
MathVerse Animation Engine - Celery Tasks
Background tasks for processing render jobs.
"""

import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.app_config import get_config, get_manim_config, get_rendering_config
from api.models import RenderRequest, RenderStatus
from renderer.script_generator import ScriptGenerator
from utils.storage import get_storage_backend, OutputManager
from utils.cleanup import cleanup_temp_files

logger = logging.getLogger(__name__)


# In-memory job storage (use Redis in production)
_job_store = {}


def update_job_status(
    job_id: str,
    status: RenderStatus,
    progress: float = 0.0,
    stage: Optional[str] = None,
    message: Optional[str] = None,
    **kwargs
):
    """Update job status in the job store"""
    if job_id not in _job_store:
        _job_store[job_id] = {}
    
    _job_store[job_id].update({
        'status': status,
        'progress': progress,
        'stage': stage,
        'message': message,
        'updated_at': datetime.utcnow().isoformat(),
        **kwargs
    })
    
    logger.info(f"Job {job_id}: {status.value} - {stage or ''} ({progress*100:.0f}%)")


def get_job_status(job_id: str) -> Optional[Dict]:
    """Get current job status"""
    return _job_store.get(job_id)


def process_render_job(job_id: str, scene_data: dict, task_id: str = None) -> Dict:
    """
    Process a render job end-to-end.
    
    Args:
        job_id: Unique job identifier
        scene_data: Scene configuration dictionary
        task_id: Celery task ID
    
    Returns:
        Dictionary with render results
    """
    config = get_config()
    manim_config = get_manim_config()
    rendering_config = get_rendering_config()
    
    start_time = time.time()
    output_manager = None
    
    try:
        # Initialize output manager
        output_manager = OutputManager(get_storage_backend())
        
        # Create request object for validation
        request = RenderRequest(**scene_data)
        
        # Update status: Generating script
        update_job_status(
            job_id,
            RenderStatus.PROCESSING,
            progress=0.1,
            stage="generating_script",
            message="Generating animation script"
        )
        
        # Generate script
        script_generator = ScriptGenerator(
            templates_dir=config.templates_dir
        )
        
        script_content = script_generator.generate_script(
            scene_type=request.scene_type.value,
            title=request.title or f"{request.scene_type.value.title()} Animation",
            subtitle=request.subtitle,
            equations=request.equations or [],
            graph=request.graph.model_dump() if request.graph else None,
            shapes=[s.model_dump() for s in request.shapes] if request.shapes else None,
            proof_steps=[p.model_dump() for p in request.proof_steps] if request.proof_steps else None,
            primary_color=request.primary_color,
            secondary_color=request.secondary_color,
            text_color=request.text_color,
            background_color=request.background_color,
            level=request.level.value,
        )
        
        # Save script to temp file
        script_path = script_generator.save_script(
            script_content,
            output_dir=config.temp_dir
        )
        
        logger.info(f"Generated script: {script_path}")
        
        # Update status: Rendering
        update_job_status(
            job_id,
            RenderStatus.PROCESSING,
            progress=0.3,
            stage="rendering",
            message="Rendering animation with Manim"
        )
        
        # Run Manim render
        output_path = run_manim_render(
            script_path=script_path,
            scene_name=script_generator._generate_scene_name(
                request.scene_type.value,
                request.level.value
            ),
            quality=manim_config.quality,
            output_dir=config.output_dir,
            timeout=manim_config.timeout
        )
        
        if not output_path:
            raise RuntimeError("Manim rendering failed - no output produced")
        
        # Update status: Post-processing
        update_job_status(
            job_id,
            RenderStatus.PROCESSING,
            progress=0.7,
            stage="post_processing",
            message="Processing rendered video"
        )
        
        # Generate thumbnail
        thumbnail_path = generate_thumbnail(
            output_path,
            time_offset=rendering_config.thumbnail_offset
        )
        
        # Upload to storage
        update_job_status(
            job_id,
            RenderStatus.PROCESSING,
            progress=0.85,
            stage="uploading",
            message="Uploading to storage"
        )
        
        video_url, thumbnail_url = output_manager.save_output(
            local_video_path=output_path,
            local_thumbnail_path=thumbnail_path,
            scene_type=request.scene_type.value,
            level=request.level.value,
            job_id=job_id
        )
        
        # Get file size
        file_size = output_manager.storage.get_file_size(
            output_manager.generate_output_path(
                request.scene_type.value,
                request.level.value,
                job_id
            )
        )
        
        # Update status: Completed
        update_job_status(
            job_id,
            RenderStatus.COMPLETED,
            progress=1.0,
            stage="completed",
            message="Render completed successfully",
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            file_size=file_size,
            duration_estimate=get_video_duration(output_path)
        )
        
        # Clean up temp files
        cleanup_temp_files(3600)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Job {job_id} completed in {elapsed_time:.2f} seconds")
        
        return {
            'success': True,
            'job_id': job_id,
            'status': 'completed',
            'video_url': video_url,
            'thumbnail_url': thumbnail_url,
            'file_size': file_size,
            'elapsed_seconds': elapsed_time,
        }
        
    except Exception as e:
        error_message = str(e)
        logger.exception(f"Job {job_id} failed: {error_message}")
        
        update_job_status(
            job_id,
            RenderStatus.FAILED,
            progress=0.0,
            stage="failed",
            message=error_message,
            error_message=error_message,
            error_details={'exception_type': type(e).__name__}
        )
        
        return {
            'success': False,
            'job_id': job_id,
            'status': 'failed',
            'error_message': error_message,
        }


def run_manim_render(
    script_path: str,
    scene_name: str,
    quality: str = "m",
    output_dir: str = "output",
    timeout: int = 300
) -> Optional[str]:
    """
    Execute Manim rendering command.
    
    Args:
        script_path: Path to the Python script
        scene_name: Name of the scene class to render
        quality: Quality setting (l, m, h, k)
        output_dir: Output directory
        timeout: Command timeout in seconds
    
    Returns:
        Path to rendered video file, or None if failed
    """
    import subprocess
    
    script_path = Path(script_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build command
    cmd = [
        sys.executable,
        "-m", "manim",
        str(script_path),
        scene_name,
        f"-{quality}",
        "--output_file", str(output_dir / scene_name),
        "-f",  # Flush output
    ]
    
    logger.info(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(script_path.parent)
        )
        
        if result.returncode != 0:
            logger.error(f"Manim stderr: {result.stderr}")
            raise RuntimeError(f"Manim render failed: {result.stderr[:500]}")
        
        # Find output file
        for ext in ['.mp4', '.mov']:
            potential_output = output_dir / f"{scene_name}{ext}"
            if potential_output.exists():
                logger.info(f"Output file: {potential_output}")
                return str(potential_output)
        
        raise RuntimeError(f"Manim completed but no output file found")
        
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Manim render timed out after {timeout} seconds")


def generate_thumbnail(video_path: str, time_offset: float = 2.0) -> Optional[str]:
    """
    Generate thumbnail from video using ffmpeg.
    
    Args:
        video_path: Path to video file
        time_offset: Time in seconds to capture frame
    
    Returns:
        Path to thumbnail file, or None if failed
    """
    import subprocess
    
    video_path = Path(video_path)
    thumbnail_path = video_path.with_suffix(".jpg")
    
    cmd = [
        "ffmpeg",
        "-ss", str(time_offset),
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",
        str(thumbnail_path),
        "-y"  # Overwrite
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        
        if result.returncode == 0 and thumbnail_path.exists():
            logger.info(f"Generated thumbnail: {thumbnail_path}")
            return str(thumbnail_path)
        
        logger.warning(f"Thumbnail generation failed: {result.stderr}")
        
    except Exception as e:
        logger.warning(f"Thumbnail generation error: {e}")
    
    return None


def get_video_duration(video_path: str) -> Optional[float]:
    """
    Get video duration in seconds using ffprobe.
    
    Args:
        video_path: Path to video file
    
    Returns:
        Duration in seconds, or None if failed
    """
    import subprocess
    import json
    
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
    
    except Exception as e:
        logger.warning(f"Failed to get video duration: {e}")
    
    return None


def get_job_stats() -> Dict:
    """Get statistics about queued and processing jobs"""
    stats = {
        'queued': 0,
        'processing': 0,
        'completed': 0,
        'failed': 0,
        'jobs': []
    }
    
    for job_id, job_data in _job_store.items():
        status = job_data.get('status', RenderStatus.QUEUED)
        
        if status == RenderStatus.QUEUED:
            stats['queued'] += 1
        elif status == RenderStatus.PROCESSING:
            stats['processing'] += 1
        elif status == RenderStatus.COMPLETED:
            stats['completed'] += 1
        elif status == RenderStatus.FAILED:
            stats['failed'] += 1
        
        stats['jobs'].append({
            'job_id': job_id,
            'status': status.value,
            'progress': job_data.get('progress', 0),
            'created_at': job_data.get('created_at'),
        })
    
    return stats
