"""
MathVerse Content Metadata Service - Configuration
"""

import os
from typing import List
from pydantic import BaseModel
from functools import lru_cache


class DatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str = "mathverse"
    user: str = "postgres"
    password: str = "postgres"
    pool_size: int = 10
    max_overflow: int = 20
    
    @property
    def async_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
    
    @property
    def sync_url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    
    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class SearchConfig(BaseModel):
    enabled: bool = False
    elasticsearch_url: str = "http://localhost:9200"
    index_prefix: str = "mathverse"


class AppConfig(BaseModel):
    name: str = "MathVerse Content Metadata Service"
    version: str = "1.0.0"
    debug: bool = False
    api_prefix: str = "/api/v1"
    
    host: str = "0.0.0.0"
    port: int = 8001
    workers: int = 1
    
    cors_origins: List[str] = ["*"]
    
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    search: SearchConfig = SearchConfig()


def load_config() -> AppConfig:
    """Load configuration from environment and defaults"""
    return AppConfig(
        database=DatabaseConfig(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", "5432")),
            name=os.environ.get("DB_NAME", "mathverse"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", "postgres"),
        ),
        redis=RedisConfig(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            password=os.environ.get("REDIS_PASSWORD"),
        ),
        search=SearchConfig(
            enabled=os.environ.get("SEARCH_ENABLED", "false").lower() == "true",
            elasticsearch_url=os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200"),
        ),
        debug=os.environ.get("DEBUG", "false").lower() == "true",
    )


@lru_cache()
def get_settings() -> AppConfig:
    """Get cached configuration"""
    return load_config()


# Create settings instance
settings = get_settings()
