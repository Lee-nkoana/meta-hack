# FastAPI application configuration
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Medical Records Bridge API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./medical_records.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000", "http://localhost:5173"]
    
    # Meta AI Configuration
    META_AI_API_KEY: Optional[str] = None
    META_AI_MODEL: str = "llama-3.1-70b"
    META_AI_BASE_URL: str = "https://api.together.xyz/v1"  # Using Together AI as it supports Llama models
    META_AI_TEMPERATURE: float = 0.7
    META_AI_MAX_TOKENS: int = 2000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
