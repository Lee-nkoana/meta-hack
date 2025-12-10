# Security utilities for password hashing and JWT tokens
from datetime import timedelta
from typing import Optional
from flask_jwt_extended import create_access_token as flask_create_access_token, decode_token
import bcrypt
from app.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token using Flask-JWT-Extended"""
 
    identity = data.get("sub")
    additional_claims = {k: v for k, v in data.items() if k != "sub"}
    
    if expires_delta:
        expires = expires_delta
    else:
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token = flask_create_access_token(
        identity=identity,
        additional_claims=additional_claims,
        expires_delta=expires
    )
    return token


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = decode_token(token)
        return payload
    except Exception:
        return None
