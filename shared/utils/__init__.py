"""
MathVerse Utilities Package

This package provides common utility functions used across the
MathVerse platform, including logging, security, database helpers,
and validation utilities.
"""

from .logger import (
    setup_logging,
    get_logger,
    LogContext,
    log_function,
    LoggerMixin
)

from .security import (
    create_access_token,
    verify_token,
    hash_password,
    verify_password,
    generate_secret_key,
    encrypt_data,
    decrypt_data,
    generate_otp,
    verify_otp
)

from .database import (
    get_database_url,
    get_engine,
    get_session,
    get_async_session,
    init_db,
    create_tables,
    Base,
    session_scope,
    async_session_scope
)

from .validation import (
    validate_email,
    validate_password_strength,
    validate_uuid,
    sanitize_input,
    normalize_phone_number
)

from .formatters import (
    format_duration,
    format_number,
    format_percentage,
    format_date,
    format_datetime
)

from .helpers import (
    generate_unique_id,
    retry_operation,
    chunk_list,
    flatten_dict,
    deep_merge
)

__all__ = [
    # Logging utilities
    "setup_logging",
    "get_logger",
    "LogContext",
    "log_function",
    "LoggerMixin",
    
    # Security utilities
    "create_access_token",
    "verify_token",
    "hash_password",
    "verify_password",
    "generate_secret_key",
    "encrypt_data",
    "decrypt_data",
    "generate_otp",
    "verify_otp",
    
    # Database utilities
    "get_database_url",
    "get_engine",
    "get_session",
    "get_async_session",
    "init_db",
    "create_tables",
    "Base",
    "session_scope",
    "async_session_scope",
    
    # Validation utilities
    "validate_email",
    "validate_password_strength",
    "validate_uuid",
    "sanitize_input",
    "normalize_phone_number",
    
    # Formatters
    "format_duration",
    "format_number",
    "format_percentage",
    "format_date",
    "format_datetime",
    
    # Helpers
    "generate_unique_id",
    "retry_operation",
    "chunk_list",
    "flatten_dict",
    "deep_merge"
]
