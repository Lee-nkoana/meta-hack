# Flask application configuration
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = os.getenv("APP_NAME", "Medical Records Bridge API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    
    # Flask
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./medical_records.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # JWT (Flask-JWT-Extended)
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production"))
    JWT_ACCESS_TOKEN_EXPIRES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")) * 60  # Convert to seconds
    
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16MB max upload
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        origin.strip().strip('"').strip("'") 
        for origin in os.getenv(
            "BACKEND_CORS_ORIGINS", 
            "http://localhost:3000,http://localhost:8000,http://localhost:5173"
        ).strip("[]").split(",")
    ]
    
    # Meta AI Configuration
    META_AI_API_KEY: Optional[str] = os.getenv("META_AI_API_KEY")
    META_AI_MODEL: str = os.getenv("META_AI_MODEL", "llama-3.1-70b")
    META_AI_BASE_URL: str = os.getenv("META_AI_BASE_URL", "https://api.together.xyz/v1")
    META_AI_TEMPERATURE: float = float(os.getenv("META_AI_TEMPERATURE", "0.7"))
    META_AI_MAX_TOKENS: int = int(os.getenv("META_AI_MAX_TOKENS", "2000"))
    
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    HUGGINGFACE_MODEL: str = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-3.2-11B-Vision-Instruct")
    HUGGINGFACE_BASE_URL: str = os.getenv("HUGGINGFACE_BASE_URL", "https://router.huggingface.co/models")
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    # Groq Configuration
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Legacy Together/Meta AI (Optional Fallback)
    META_AI_API_KEY: Optional[str] = os.getenv("META_AI_API_KEY")


settings = Settings()
