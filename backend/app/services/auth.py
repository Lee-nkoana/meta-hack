# Authentication service for user registration and login
from datetime import timedelta
from sqlalchemy.orm import Session
from app.models import User
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.config import settings


def get_user_by_username(db: Session, username: str) -> User | None:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """Authenticate user with username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(db: Session, user_data: dict) -> User:
    """Create a new user"""
    # Check if username already exists
    if get_user_by_username(db, user_data['username']):
        raise ValueError("Username already registered")
    
    # Check if email already exists
    if get_user_by_email(db, user_data['email']):
        raise ValueError("Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data['password'])
    db_user = User(
        email=user_data['email'],
        username=user_data['username'],
        hashed_password=hashed_password,
        full_name=user_data.get('full_name')
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def login_user(db: Session, username: str, password: str) -> dict:
    """Login user and return JWT token"""
    user = authenticate_user(db, username, password)
    if not user:
        raise ValueError("Incorrect username or password")
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
