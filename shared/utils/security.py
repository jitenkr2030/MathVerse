"""
Security Utilities Module

This module provides security and authentication utilities for the
MathVerse platform, including JWT token handling, password hashing,
and data encryption.
"""

import secrets
import hashlib
import hmac
import base64
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from enum import Enum

from jose import JWTError, jwt
from passlib.context import CryptContext
import cryptocompare


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class TokenType(str, Enum):
    """JWT token types."""
    
    ACCESS = "access"
    REFRESH = "refresh"
    VERIFY = "verify"
    RESET = "reset"


class TokenPayload(BaseModel):
    """JWT token payload structure."""
    
    sub: str  # Subject (user ID)
    type: TokenType
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None
    jti: Optional[str] = None  # JWT ID
    email: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[list] = None


def create_access_token(
    user_id: str,
    email: Optional[str] = None,
    role: Optional[str] = None,
    permissions: Optional[list] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: User identifier
        email: User email
        role: User role
        permissions: User permissions
        additional_claims: Additional JWT claims
        expires_delta: Custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    now = datetime.utcnow()
    
    payload = {
        "sub": user_id,
        "type": TokenType.ACCESS.value,
        "exp": expire,
        "iat": now,
        "jti": secrets.token_hex(8),
        "email": email,
        "role": role,
        "permissions": permissions or []
    }
    
    if additional_claims:
        payload.update(additional_claims)
    
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    user_id: str,
    email: Optional[str] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        user_id: User identifier
        email: User email
        
    Returns:
        Encoded JWT refresh token string
    """
    expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    now = datetime.utcnow()
    
    payload = {
        "sub": user_id,
        "type": TokenType.REFRESH.value,
        "exp": expire,
        "iat": now,
        "jti": secrets.token_hex(8),
        "email": email
    }
    
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_verify_token(user_id: str, email: str) -> str:
    """
    Create an email verification token.
    
    Args:
        user_id: User identifier
        email: User email
        
    Returns:
        Encoded verification token
    """
    expire = datetime.utcnow() + timedelta(hours=24)
    now = datetime.utcnow()
    
    payload = {
        "sub": user_id,
        "type": TokenType.VERIFY.value,
        "exp": expire,
        "iat": now,
        "jti": secrets.token_hex(8),
        "email": email
    }
    
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_password_reset_token(user_id: str) -> str:
    """
    Create a password reset token.
    
    Args:
        user_id: User identifier
        
    Returns:
        Encoded reset token
    """
    expire = datetime.utcnow() + timedelta(hours=1)
    now = datetime.utcnow()
    
    payload = {
        "sub": user_id,
        "type": TokenType.RESET.value,
        "exp": expire,
        "iat": now,
        "jti": secrets.token_hex(8)
    }
    
    encoded_jwt = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str, expected_type: TokenType = TokenType.ACCESS) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        expected_type: Expected token type
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        
        # Verify token type
        token_type = payload.get("type")
        if token_type != expected_type.value:
            return None
        
        return payload
        
    except JWTError:
        return None


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token without verification (for inspection).
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload or None if invalid
    """
    try:
        return jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": False}
        )
    except JWTError:
        return None


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Stored password hash
        
    Returns:
        True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_secret_key(length: int = 32) -> str:
    """
    Generate a secure random secret key.
    
    Args:
        length: Key length in bytes
        
    Returns:
        Hex-encoded secret key
    """
    return secrets.token_hex(length)


def generate_api_key(prefix: str = "mv") -> Tuple[str, str]:
    """
    Generate a secure API key.
    
    Args:
        prefix: Key prefix for identification
        
    Returns:
        Tuple of (public_key, secret_key)
    """
    public_key = f"{prefix}_{secrets.token_hex(8)}"
    secret_key = f"{prefix}_sk_{secrets.token_hex(24)}"
    
    return public_key, secret_key


def hash_api_key_secret(secret: str) -> str:
    """
    Hash an API key secret for storage.
    
    Args:
        secret: Plain text secret
        
    Returns:
        Hashed secret
    """
    return hash_password(secret)


def encrypt_data(data: str, key: Optional[bytes] = None) -> str:
    """
    Encrypt data using AES-256-CBC.
    
    Args:
        data: Plain text data to encrypt
        key: Encryption key (generated if not provided)
        
    Returns:
        Base64-encoded encrypted data with IV
    """
    if key is None:
        key = generate_secret_key(32).encode()
    
    iv = os.urandom(16)
    cipher = cryptocompare.new(key, cryptocompare.MODE_CBC, iv)
    
    # Pad data to block size
    padding_length = 16 - len(data) % 16
    padded_data = data + chr(padding_length) * padding_length
    
    encrypted = cipher.encrypt(padded_data.encode())
    
    # Combine IV and encrypted data
    combined = iv + encrypted
    
    return base64.b64encode(combined).decode()


def decrypt_data(encrypted_data: str, key: bytes) -> str:
    """
    Decrypt AES-256-CBC encrypted data.
    
    Args:
        encrypted_data: Base64-encoded encrypted data
        key: Decryption key
        
    Returns:
        Decrypted plain text
    """
    combined = base64.b64decode(encrypted_data.encode())
    
    iv = combined[:16]
    encrypted = combined[16:]
    
    cipher = cryptocompare.new(key, cryptocompare.MODE_CBC, iv)
    
    decrypted = cipher.decrypt(encrypted)
    
    # Remove padding
    padding_length = decrypted[-1]
    plain_text = decrypted[:-padding_length].decode()
    
    return plain_text


def generate_otp(length: int = 6) -> str:
    """
    Generate a one-time password.
    
    Args:
        length: OTP length (default 6)
        
    Returns:
        OTP string
    """
    return ''.join(str(secrets.randbelow(10)) for _ in range(length))


def verify_otp(otp: str, stored_otp: str, expiry_seconds: int = 300) -> bool:
    """
    Verify a one-time password.
    
    Args:
        otp: User-provided OTP
        stored_otp: Stored OTP with timestamp
        expiry_seconds: OTP validity period
        
    Returns:
        True if OTP is valid
    """
    try:
        stored_otp, timestamp_str = stored_otp.split("|")
        timestamp = datetime.fromisoformat(timestamp_str)
        
        # Check expiry
        if datetime.now() - timestamp > timedelta(seconds=expiry_seconds):
            return False
        
        return secrets.compare_digest(otp, stored_otp)
    except (ValueError, AttributeError):
        return False


def create_otp_storage(otp: str) -> str:
    """
    Create OTP storage string with timestamp.
    
    Args:
        otp: OTP string
        
    Returns:
        Storage string with timestamp
    """
    return f"{otp}|{datetime.now().isoformat()}"


def hash_hmac(data: str, secret: str) -> str:
    """
    Create HMAC signature for data.
    
    Args:
        data: Data to sign
        secret: Signing secret
        
    Returns:
        Hex-encoded HMAC signature
    """
    return hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()


def verify_hmac(data: str, signature: str, secret: str) -> bool:
    """
    Verify HMAC signature.
    
    Args:
        data: Original data
        signature: Signature to verify
        secret: Signing secret
        
    Returns:
        True if signature is valid
    """
    expected_signature = hash_hmac(data, secret)
    return hmac.compare_digest(signature, expected_signature)


class PermissionChecker:
    """
    Utility class for checking user permissions.
    """
    
    def __init__(self, required_permissions: list):
        """Initialize with required permissions."""
        self.required_permissions = required_permissions
    
    def __call__(self, user_permissions: list) -> bool:
        """
        Check if user has all required permissions.
        
        Args:
            user_permissions: List of user permissions
            
        Returns:
            True if user has all required permissions
        """
        return all(
            perm in user_permissions
            for perm in self.required_permissions
        )
