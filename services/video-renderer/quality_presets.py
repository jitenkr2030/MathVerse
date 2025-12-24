"""
Video Renderer Quality Presets Module

This module defines quality presets for video rendering in the MathVerse
platform, supporting multiple resolutions and quality levels for
different use cases and bandwidth requirements.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum


class VideoQuality(str, Enum):
    """Video quality levels for rendering."""
    
    DRAFT = "draft"
    SD = "sd"
    HD = "hd"
    FULL_HD = "full_hd"
    UHD_4K = "4k"


class VideoFormat(str, Enum):
    """Supported video output formats."""
    
    MP4 = "mp4"
    WEBM = "webm"
    MOV = "mov"


class AudioQuality(str, Enum):
    """Audio quality levels."""
    
    LOW = "128k"
    MEDIUM = "192k"
    HIGH = "256k"
    MAXIMUM = "320k"


@dataclass
class VideoQualityPreset:
    """
    Configuration for a video quality preset.
    
    Attributes:
        quality: Quality level identifier
        resolution: Video resolution (width x height)
        bitrate_video: Video bitrate in kbps
        bitrate_audio: Audio bitrate
        fps: Frames per second
        codec: Video codec
        audio_codec: Audio codec
        format: Output container format
        description: Human-readable description
        use_case: Recommended use case for this preset
    """
    
    quality: VideoQuality
    resolution: str
    resolution_width: int
    resolution_height: int
    bitrate_video: int
    bitrate_audio: str
    fps: int
    codec: str
    audio_codec: str
    format: VideoFormat
    description: str
    use_case: str


# Define all quality presets
QUALITY_PRESETS: Dict[VideoQuality, VideoQualityPreset] = {
    VideoQuality.DRAFT: VideoQualityPreset(
        quality=VideoQuality.DRAFT,
        resolution="1280x720",
        resolution_width=1280,
        resolution_height=720,
        bitrate_video=1500,
        bitrate_audio=AudioQuality.LOW,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        format=VideoFormat.MP4,
        description="Draft quality for quick previews and testing",
        use_case="Internal review, testing animations, quick iterations"
    ),
    
    VideoQuality.SD: VideoQualityPreset(
        quality=VideoQuality.SD,
        resolution="854x480",
        resolution_width=854,
        resolution_height=480,
        bitrate_video=1000,
        bitrate_audio=AudioQuality.LOW,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        format=VideoFormat.MP4,
        description="Standard definition for low-bandwidth connections",
        use_case="Mobile viewing, slow internet, data-saving mode"
    ),
    
    VideoQuality.HD: VideoQualityPreset(
        quality=VideoQuality.HD,
        resolution="1920x1080",
        resolution_width=1920,
        resolution_height=1080,
        bitrate_video=4500,
        bitrate_audio=AudioQuality.MEDIUM,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        format=VideoFormat.MP4,
        description="Full HD standard quality for balanced size and clarity",
        use_case="Standard web streaming, desktop viewing, general use"
    ),
    
    VideoQuality.FULL_HD: VideoQualityPreset(
        quality=VideoQuality.FULL_HD,
        resolution="1920x1080",
        resolution_width=1920,
        resolution_height=1080,
        bitrate_video=8000,
        bitrate_audio=AudioQuality.HIGH,
        fps=60,
        codec="libx264",
        audio_codec="aac",
        format=VideoFormat.MP4,
        description="Full HD high quality with smooth 60fps",
        use_case="High-quality streaming, premium content, presentations"
    ),
    
    VideoQuality.UHD_4K: VideoQualityPreset(
        quality=VideoQuality.UHD_4K,
        resolution="3840x2160",
        resolution_width=3840,
        resolution_height=2160,
        bitrate_video=20000,
        bitrate_audio=AudioQuality.MAXIMUM,
        fps=60,
        codec="libx265",
        audio_codec="aac",
        format=VideoFormat.MP4,
        description="Ultra HD 4K for maximum clarity and detail",
        use_case="Premium 4K viewing, professional presentations, archives"
    ),
}


def get_quality_preset(quality: VideoQuality) -> VideoQualityPreset:
    """
    Get a specific quality preset.
    
    Args:
        quality: The desired quality level
        
    Returns:
        VideoQualityPreset configuration
        
    Raises:
        ValueError: If quality is not recognized
    """
    if quality not in QUALITY_PRESETS:
        raise ValueError(f"Unknown quality level: {quality}")
    return QUALITY_PRESETS[quality]


def get_available_qualities() -> List[VideoQuality]:
    """
    Get list of all available quality levels.
    
    Returns:
        List of quality level identifiers
    """
    return list(QUALITY_PRESETS.keys())


def get_quality_for_bandwidth(bandwidth_kbps: int) -> VideoQuality:
    """
    Select optimal quality based on available bandwidth.
    
    Args:
        bandwidth_kbps: Available bandwidth in kbps
        
    Returns:
        Recommended quality level
    """
    if bandwidth_kbps < 2000:
        return VideoQuality.SD
    elif bandwidth_kbps < 6000:
        return VideoQuality.HD
    elif bandwidth_kbps < 12000:
        return VideoQuality.FULL_HD
    else:
        return VideoQuality.UHD_4K


def generate_ffmpeg_args(
    input_path: str,
    output_path: str,
    quality: VideoQuality,
    extra_args: Dict[str, Any] = None
) -> List[str]:
    """
    Generate FFmpeg command arguments for rendering.
    
    Args:
        input_path: Path to input file or pattern
        output_path: Path for output file
        quality: Quality preset to use
        extra_args: Additional FFmpeg arguments
        
    Returns:
        List of FFmpeg command arguments
    """
    preset = get_quality_preset(quality)
    
    args = [
        "ffmpeg",
        "-y",  # Overwrite output files without asking
        "-i", input_path,
        "-c:v", preset.codec,
        "-preset", "medium",  # Encoding speed/quality balance
        "-crf", "23",  # Constant Rate Factor for quality
        "-vf", f"scale={preset.resolution_width}:{preset.resolution_height}:force_original_aspect_ratio=decrease,pad={preset.resolution_width}:{preset.resolution_height}:(ow-iw)/2:(oh-ih)/2",
        "-b:v", f"{preset.bitrate_video}k",
        "-maxrate", f"{preset.bitrate_video}k",
        "-bufsize", f"{preset.bitrate_video * 2}k",
        "-c:a", preset.audio_codec,
        "-b:a", preset.bitrate_audio,
        "-ar", "48000",
        "-ac", "2",
        "-fps:v", str(preset.fps),
        "-movflags", "+faststart",  # Enable streaming
    ]
    
    if extra_args:
        for key, value in extra_args.items():
            if isinstance(value, bool):
                if value:
                    args.append(key)
            else:
                args.extend([key, str(value)])
    
    args.append(output_path)
    
    return args


def get_thumbnail_args(
    input_path: str,
    output_path: str,
    timestamp: str = "00:00:01",
    width: int = 320,
    height: int = 180
) -> List[str]:
    """
    Generate FFmpeg command arguments for thumbnail extraction.
    
    Args:
        input_path: Path to video file
        output_path: Path for thumbnail image
        timestamp: Timestamp to capture (HH:MM:SS)
        width: Thumbnail width
        height: Thumbnail height
        
    Returns:
        List of FFmpeg command arguments
    """
    return [
        "ffmpeg",
        "-y",
        "-ss", timestamp,
        "-i", input_path,
        "-vframes", "1",
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
        "-q:v", "2",  # High quality JPEG
        output_path
    ]


def get_preview_gif_args(
    input_path: str,
    output_path: str,
    duration: int = 3,
    width: int = 320,
    fps: int = 10
) -> List[str]:
    """
    Generate FFmpeg command arguments for GIF preview.
    
    Args:
        input_path: Path to video file
        output_path: Path for GIF output
        duration: GIF duration in seconds
        width: GIF width
        fps: Frames per second
        
    Returns:
        List of FFmpeg command arguments
    """
    return [
        "ffmpeg",
        "-y",
        "-t", str(duration),
        "-i", input_path,
        "-vf", f"fps={fps},scale={width}:-1:flags=lanczos,trim=0={duration}",
        "-g", "30",  # GOP size
        "-loop", "0",
        output_path
    ]


def estimate_file_size(
    duration_seconds: int,
    quality: VideoQuality
) -> int:
    """
    Estimate output file size for a video.
    
    Args:
        duration_seconds: Video duration in seconds
        quality: Quality preset
        
    Returns:
        Estimated file size in bytes
    """
    preset = get_quality_preset(quality)
    
    # Calculate total bitrate (video + audio)
    audio_bitrate_kbps = int(preset.bitrate_audio.replace("k", ""))
    total_bitrate_kbps = preset.bitrate_video + audio_bitrate_kbps
    
    # Estimate file size (bitrate * duration / 8 bits per byte)
    total_bytes = (total_bitrate_kbps * 1000 * duration_seconds) / 8
    
    return int(total_bytes)


def get_quality_comparison() -> List[Dict[str, Any]]:
    """
    Get comparison data for all quality presets.
    
    Returns:
        List of preset comparison data
    """
    return [
        {
            "quality": preset.quality.value,
            "resolution": preset.resolution,
            "description": preset.description,
            "use_case": preset.use_case,
            "bitrate_video_kbps": preset.bitrate_video,
            "bitrate_audio_kbps": preset.bitrate_audio,
            "fps": preset.fps
        }
        for preset in QUALITY_PRESETS.values()
    ]


class VideoRendererConfig:
    """
    Configuration class for video rendering service.
    """
    
    def __init__(
        self,
        max_concurrent_renders: int = 5,
        default_quality: VideoQuality = VideoQuality.HD,
        allowed_formats: List[VideoFormat] = None,
        output_directory: str = "/tmp/rendered",
        temp_directory: str = "/tmp/render_temp",
        storage_base_url: str = "https://cdn.mathverse.com"
    ):
        """
        Initialize video renderer configuration.
        
        Args:
            max_concurrent_renders: Maximum simultaneous render jobs
            default_quality: Default quality for renders
            allowed_formats: List of allowed output formats
            output_directory: Base directory for rendered videos
            temp_directory: Directory for temporary files
            storage_base_url: Base URL for video storage CDN
        """
        self.max_concurrent_renders = max_concurrent_renders
        self.default_quality = default_quality
        self.allowed_formats = allowed_formats or [VideoFormat.MP4, VideoFormat.WEBM]
        self.output_directory = output_directory
        self.temp_directory = temp_directory
        self.storage_base_url = storage_base_url
    
    def get_output_path(self, job_id: str, quality: VideoQuality) -> str:
        """
        Generate output path for a render job.
        
        Args:
            job_id: Unique job identifier
            quality: Video quality
            
        Returns:
            Full output file path
        """
        return f"{self.output_directory}/{job_id}_{quality.value}.mp4"
    
    def get_temp_path(self, job_id: str, suffix: str = ".tmp") -> str:
        """
        Generate temp file path for a render job.
        
        Args:
            job_id: Unique job identifier
            suffix: File suffix
            
        Returns:
            Full temp file path
        """
        return f"{self.temp_directory}/{job_id}{suffix}"
    
    def get_storage_url(self, job_id: str, quality: VideoQuality) -> str:
        """
        Generate CDN URL for a rendered video.
        
        Args:
            job_id: Unique job identifier
            quality: Video quality
            
        Returns:
            Full CDN URL
        """
        return f"{self.storage_base_url}/videos/{job_id}_{quality.value}.mp4"
    
    def get_thumbnail_url(self, job_id: str) -> str:
        """
        Generate CDN URL for a video thumbnail.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Full CDN URL
        """
        return f"{self.storage_base_url}/thumbnails/{job_id}.jpg"
    
    def get_preview_url(self, job_id: str) -> str:
        """
        Generate CDN URL for a video preview GIF.
        
        Args:
            job_id: Unique job identifier
            
        Returns:
            Full CDN URL
        """
        return f"{self.storage_base_url}/previews/{job_id}.gif"


# Default configuration instance
DEFAULT_RENDER_CONFIG = VideoRendererConfig()
