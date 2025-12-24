"""
MathVerse Animation Engine - Cleanup Utilities
Manages temporary file cleanup and storage optimization.
"""

import os
import time
import glob
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def cleanup_temp_files(max_age_seconds: int = 3600) -> int:
    """
    Clean up temporary files older than max_age_seconds.
    
    Args:
        max_age_seconds: Maximum age of files in seconds
    
    Returns:
        Number of files cleaned up
    """
    temp_dirs = [
        "temp",
        "/tmp/mathverse_temp",
        "/tmp/manim_temp",
    ]
    
    cleaned_count = 0
    current_time = time.time()
    max_age = max_age_seconds
    
    for temp_dir in temp_dirs:
        temp_path = Path(temp_dir)
        
        if not temp_path.exists():
            continue
        
        # Clean up temp files
        for file_path in temp_path.glob("scene_*.py"):
            try:
                file_mtime = os.path.getmtime(file_path)
                age = current_time - file_mtime
                
                if age > max_age:
                    file_path.unlink()
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")
        
        # Clean up old render logs
        for file_path in temp_path.glob("*.log"):
            try:
                file_mtime = os.path.getmtime(file_path)
                age = current_time - file_mtime
                
                if age > max_age:
                    file_path.unlink()
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")
    
    if cleaned_count > 0:
        logger.info(f"Cleaned up {cleaned_count} temporary files")
    
    return cleaned_count


def cleanup_old_outputs(max_age_seconds: int = 86400) -> int:
    """
    Clean up old rendered output files.
    
    Args:
        max_age_seconds: Maximum age of files in seconds
    
    Returns:
        Number of files cleaned up
    """
    output_dirs = [
        "output",
        "/tmp/mathverse_output",
    ]
    
    cleaned_count = 0
    current_time = time.time()
    
    for output_dir in output_dirs:
        output_path = Path(output_dir)
        
        if not output_path.exists():
            continue
        
        # Clean up old video files
        for file_path in output_path.glob("**/*.mp4"):
            try:
                file_mtime = os.path.getmtime(file_path)
                age = current_time - file_mtime
                
                if age > max_age_seconds:
                    file_path.unlink()
                    cleaned_count += 1
                    
                    # Also try to remove thumbnail
                    thumb_path = file_path.with_suffix(".jpg")
                    if thumb_path.exists():
                        thumb_path.unlink()
                        cleaned_count += 1
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")
    
    if cleaned_count > 0:
        logger.info(f"Cleaned up {cleaned_count} output files")
    
    return cleaned_count


def cleanup_empty_directories(base_path: str = "output") -> int:
    """
    Remove empty directories recursively.
    
    Args:
        base_path: Base directory to start cleanup
    
    Returns:
        Number of directories removed
    """
    cleaned_count = 0
    base = Path(base_path)
    
    if not base.exists():
        return 0
    
    # Walk directory tree bottom-up
    for dirpath, dirnames, filenames in os.walk(base, topdown=False):
        # Check if directory is empty
        if not dirnames and not filenames:
            try:
                Path(dirpath).rmdir()
                cleaned_count += 1
                logger.debug(f"Removed empty directory: {dirpath}")
            except Exception as e:
                logger.warning(f"Failed to remove directory {dirpath}: {e}")
    
    return cleaned_count


def get_disk_usage(path: str = "/tmp") -> dict:
    """
    Get disk usage statistics.
    
    Args:
        path: Path to check
    
    Returns:
        Dictionary with usage information
    """
    import shutil
    
    usage = shutil.disk_usage(path)
    
    return {
        'total': usage.total,
        'used': usage.used,
        'free': usage.free,
        'percent_used': round((usage.used / usage.total) * 100, 2),
    }


def get_directory_size(path: str) -> int:
    """
    Get total size of a directory in bytes.
    
    Args:
        path: Directory path
    
    Returns:
        Total size in bytes
    """
    total_size = 0
    
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = Path(dirpath) / f
            try:
                total_size += fp.stat().st_size
            except (OSError, IOError):
                pass
    
    return total_size


def format_bytes(size: int) -> str:
    """Format bytes to human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    
    return f"{size:.2f} PB"


def cleanup_by_size(max_size_mb: int = 1000, base_path: str = "output") -> int:
    """
    Clean up oldest files until directory is under size limit.
    
    Args:
        max_size_mb: Maximum directory size in MB
        base_path: Directory to clean
    
    Returns:
        Number of files removed
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    current_size = get_directory_size(base_path)
    
    if current_size < max_size_bytes:
        return 0
    
    # Get all files sorted by modification time
    files = []
    for file_path in Path(base_path).glob("**/*"):
        if file_path.is_file():
            try:
                mtime = file_path.stat().st_mtime
                files.append((file_path, mtime))
            except Exception:
                pass
    
    # Sort by modification time (oldest first)
    files.sort(key=lambda x: x[1])
    
    cleaned_count = 0
    
    # Delete oldest files until under limit
    for file_path, _ in files:
        if current_size < max_size_bytes:
            break
        
        try:
            file_size = file_path.stat().st_size
            file_path.unlink()
            current_size -= file_size
            cleaned_count += 1
            
            # Also remove thumbnail if exists
            thumb = file_path.with_suffix(".jpg")
            if thumb.exists():
                try:
                    current_size -= thumb.stat().st_size
                    thumb.unlink()
                    cleaned_count += 1
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Failed to cleanup {file_path}: {e}")
    
    logger.info(f"Cleaned up {cleaned_count} files to free space")
    return cleaned_count


def schedule_cleanup():
    """Schedule periodic cleanup (to be called from worker)"""
    import threading
    import time
    
    def cleanup_loop():
        while True:
            try:
                # Clean temp files older than 1 hour
                cleanup_temp_files(3600)
                
                # Clean output files older than 24 hours
                cleanup_old_outputs(86400)
                
                # Remove empty directories
                cleanup_empty_directories("output")
                
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
            
            # Sleep for 1 hour
            time.sleep(3600)
    
    # Run cleanup in background thread
    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
    
    return thread
