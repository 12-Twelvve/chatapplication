"""
Configuration settings for the JWT Authentication system.
"""
import os

class Settings:
    """Application settings and configuration."""
    
    # Security
    SECRET_KEY: str = "thisissecretkey123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./test.db"
    )
    
    # Application
    APP_NAME: str = "JWT Authentication & RBAC API"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # API
    API_V1_STR: str = "/api/v1"
    
    class Config:
        case_sensitive = True

settings = Settings()