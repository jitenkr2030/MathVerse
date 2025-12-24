"""
MathVerse Animation Engine - Configuration Management
Loads configuration from config.yaml and environment variables.
"""

import os
from pathlib import Path
from typing import Optional
from functools import lru_cache

import yaml
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration settings"""
    host: str = "localhost"
    port: int = 5432
    name: str = "mathverse"
    user: str = "postgres"
    password: str = "postgres"
    pool_size: int = 5
    max_overflow: int = 10
    
    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisConfig(BaseModel):
    """Redis configuration for Celery broker and caching"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    
    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class StorageConfig(BaseModel):
    """Cloud storage configuration"""
    provider: str = "local"  # local, s3, gcs, azure
    base_path: str = "/tmp/mathverse_output"
    
    # S3 configuration
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_endpoint: Optional[str] = None  # For MinIO/S3-compatible storage
    
    # GCS configuration
    gcs_bucket: Optional[str] = None
    gcs_project_id: Optional[str] = None
    gcs_credentials_path: Optional[str] = None
    
    # URL expiration time in seconds
    presigned_url_expiry: int = 3600


class ManimConfig(BaseModel):
    """Manim rendering configuration"""
    quality: str = "m"  # l, m, h, k (low, medium, high, 4k)
    fps: int = 30
    preview: bool = False
    transparent: bool = False
    file_format: str = "mp4"
    timeout: int = 300  # Seconds before timeout
    memory_limit: str = "4G"
    workers: int = 2


class RenderingConfig(BaseModel):
    """Video rendering settings"""
    width: int = 1920
    height: int = 1080
    aspect_ratio: float = 16 / 9
    bitrate: str = "3M"
    codec: str = "libx264"
    audio_bitrate: str = "192k"
    audio_codec: str = "aac"
    thumbnail_offset: float = 2.0  # seconds into video
    output_formats: list = ["mp4"]


class AppConfig(BaseModel):
    """Application configuration"""
    name: str = "MathVerse Animation Engine"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Paths
    scenes_dir: str = "manim_scenes"
    templates_dir: str = "templates"
    output_dir: str = "output"
    temp_dir: str = "temp"
    
    # Rate limiting
    rate_limit: int = 10  # requests per minute
    rate_limit_window: int = 60  # seconds
    
    # Rendering queue
    max_concurrent_renders: int = 4
    render_timeout: int = 600  # 10 minutes
    
    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    manim: ManimConfig = Field(default_factory=ManimConfig)
    rendering: RenderingConfig = Field(default_factory=RenderingConfig)


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Load configuration from YAML file and environment variables.
    
    Args:
        config_path: Path to config.yaml file. If None, searches standard locations.
    
    Returns:
        AppConfig instance with all settings.
    """
    if config_path is None:
        # Search for config in standard locations
        search_paths = [
            Path.cwd() / "config.yaml",
            Path(__file__).parent.parent / "config.yaml",
            Path("/etc/mathverse/config.yaml"),
        ]
        
        for path in search_paths:
            if path.exists():
                config_path = str(path)
                break
    
    config_data = {}
    
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f) or {}
    
    # Apply environment variable overrides
    env_overrides = {
        'debug': ('MATHVERSE_DEBUG', lambda v: v.lower() == 'true'),
        'host': ('MATHVERSE_HOST', None),
        'port': ('MATHVERSE_PORT', int),
        'redis_host': ('REDIS_HOST', None),
        'redis_port': ('REDIS_PORT', int),
        's3_bucket': ('AWS_S3_BUCKET', None),
        's3_access_key': ('AWS_ACCESS_KEY_ID', None),
        's3_secret_key': ('AWS_SECRET_ACCESS_KEY', None),
    }
    
    for key, (env_var, transform) in env_overrides.items():
        value = os.environ.get(env_var)
        if value is not None:
            if transform:
                value = transform(value)
            if key in ['redis_host', 'redis_port']:
                if 'redis' not in config_data:
                    config_data['redis'] = {}
                config_data['redis'][key.replace('redis_', '')] = value
            elif key in ['s3_bucket', 's3_access_key', 's3_secret_key']:
                if 'storage' not in config_data:
                    config_data['storage'] = {}
                config_data['storage'][key.replace('s3_', '')] = value
            else:
                config_data[key] = value
    
    return AppConfig(**config_data)


@lru_cache()
def get_config() -> AppConfig:
    """Get cached configuration singleton"""
    return load_config()


# Convenience function to get specific configs
def get_redis_config() -> RedisConfig:
    return get_config().redis


def get_storage_config() -> StorageConfig:
    return get_config().storage


def get_manim_config() -> ManimConfig:
    return get_config().manim


def get_rendering_config() -> RenderingConfig:
    return get_config().rendering
