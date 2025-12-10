# Database setup and session management
from flask import g
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Create session factory with scoped session for Flask
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(session_factory)

# Base class for database models
Base = declarative_base()


def get_db():
    """Get database session for Flask routes"""
    if 'db' not in g:
        g.db = SessionLocal()
    return g.db


def close_db(error=None):
    """Close database session at the end of request"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
