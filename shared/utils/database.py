"""
Database Utilities Module

This module provides database connection and session management utilities
for the MathVerse platform using SQLAlchemy. It includes both synchronous
and asynchronous database support.
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional, Type

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base, SessionLocal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import QueuePool


# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://recommendation_user:recommendation_pass@localhost:5432/mathverse"
)

ASYNC_DATABASE_URL = os.getenv(
    "ASYNC_DATABASE_URL",
    "postgresql+asyncpg://recommendation_user:recommendation_pass@localhost:5432/mathverse"
)


# Create base class for models
Base = declarative_base()


def get_database_url() -> str:
    """
    Get the database URL from environment.
    
    Returns:
        Database connection URL
    """
    return DATABASE_URL


def get_async_database_url() -> str:
    """
    Get the async database URL from environment.
    
    Returns:
        Async database connection URL
    """
    return ASYNC_DATABASE_URL


# Synchronous engine and session factory
_engine = None
_SessionLocal = None


def get_engine():
    """
    Get or create the synchronous database engine.
    
    Returns:
        SQLAlchemy engine instance
    """
    global _engine
    
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
    
    return _engine


def get_session_local() -> sessionmaker:
    """
    Get or create the session factory.
    
    Returns:
        Session factory
    """
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting a database session.
    
    Yields:
        SQLAlchemy Session
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Context manager for database session with automatic commit/rollback.
    
    Usage:
        with session_scope() as session:
            session.add(new_object)
    
    Yields:
        SQLAlchemy Session
    """
    SessionLocal = get_session_local()
    session = SessionLocal()
    
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Async engine and session factory
_async_engine = None
_async_session_factory = None


def get_async_engine():
    """
    Get or create the async database engine.
    
    Returns:
        Async SQLAlchemy engine instance
    """
    global _async_engine
    
    if _async_engine is None:
        _async_engine = create_async_engine(
            ASYNC_DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
    
    return _async_engine


def get_async_session_factory() -> async_sessionmaker:
    """
    Get or create the async session factory.
    
    Returns:
        Async session factory
    """
    global _async_session_factory
    
    if _async_session_factory is None:
        engine = get_async_engine()
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    
    return _async_session_factory


async def get_async_session() -> AsyncSession:
    """
    Dependency for getting an async database session.
    
    Returns:
        AsyncSession instance
    """
    SessionFactory = get_async_session_factory()
    async with SessionFactory() as session:
        yield session


@contextmanager
async def async_session_scope() -> Generator[AsyncSession, None, None]:
    """
    Context manager for async database session.
    
    Usage:
        async with async_session_scope() as session:
            await session.add(new_object)
    
    Yields:
        AsyncSession
    """
    SessionFactory = get_async_session_factory()
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def init_db(engine=None) -> None:
    """
    Initialize database tables.
    
    Args:
        engine: Optional database engine (uses default if not provided)
    """
    if engine is None:
        engine = get_engine()
    
    # Import all models to ensure they're registered
    from . import models  # noqa: F401
    
    Base.metadata.create_all(bind=engine)


def create_tables(engine=None) -> None:
    """
    Create all database tables.
    
    Args:
        engine: Optional database engine
    """
    init_db(engine)


def drop_tables(engine=None) -> None:
    """
    Drop all database tables (use with caution).
    
    Args:
        engine: Optional database engine
    """
    if engine is None:
        engine = get_engine()
    
    Base.metadata.drop_all(bind=engine)


def run_migrations(target: str, revision: str = "head") -> None:
    """
    Run database migrations using Alembic.
    
    Args:
        target: Migration target
        revision: Migration revision
    """
    from alembic.config import Config
    from alembic import command
    
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, revision)


class DatabaseHealthCheck:
    """
    Utility for checking database connectivity.
    """
    
    @staticmethod
    def check_sync() -> bool:
        """
        Check synchronous database connection.
        
        Returns:
            True if connection is healthy
        """
        try:
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    @staticmethod
    async def check_async() -> bool:
        """
        Check asynchronous database connection.
        
        Returns:
            True if connection is healthy
        """
        try:
            engine = get_async_engine()
            async with engine.connect() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception:
            return False


class TransactionManager:
    """
    Manager for complex database transactions.
    """
    
    def __init__(self, session: Session):
        """Initialize with a database session."""
        self.session = session
        self.operations = []
    
    def add_operation(self, func, *args, **kwargs):
        """
        Add an operation to the transaction.
        
        Args:
            func: Callable to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        self.operations.append((func, args, kwargs))
    
    def execute(self) -> list:
        """
        Execute all operations in a single transaction.
        
        Returns:
            List of operation results
        """
        results = []
        
        try:
            for func, args, kwargs in self.operations:
                result = func(*args, **kwargs)
                results.append(result)
            
            self.session.flush()
            return results
            
        except Exception:
            self.session.rollback()
            raise
    
    def execute_nested(self) -> list:
        """
        Execute operations with savepoints for partial rollback.
        
        Returns:
            List of operation results
        """
        results = []
        
        for i, (func, args, kwargs) in enumerate(self.operations):
            savepoint_name = f"sp_{i}"
            
            try:
                self.session.execute(f"SAVEPOINT {savepoint_name}")
                result = func(*args, **kwargs)
                results.append(result)
                
            except Exception:
                self.session.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                results.append(None)
        
        return results


# Re-export for convenience
SessionLocal = get_session_local
Session = Session
AsyncSession = AsyncSession
