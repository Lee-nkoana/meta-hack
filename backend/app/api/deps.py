# Flask dependencies for database and authentication
from functools import wraps
from flask import abort
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.database import get_db
from app.models import User


def require_auth(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        return f(*args, **kwargs)
    return decorated_function


def get_current_user() -> User:
    """Get current authenticated user from JWT token"""
    verify_jwt_in_request()
    username = get_jwt_identity()
    
    if username is None:
        abort(401, description="Could not validate credentials")
    
    # Get user from database
    db = get_db()
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        abort(401, description="Could not validate credentials")
    
    return user


def get_current_active_user() -> User:
    """Get current active user (can add is_active check here if needed)"""
    return get_current_user()
