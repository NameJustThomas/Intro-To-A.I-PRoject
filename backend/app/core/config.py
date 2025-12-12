from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://app:changeme@localhost:5432/ai_attendance"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "changeme-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Attendance API"
    
    # AI Models
    FACE_RECOGNITION_MODEL: Optional[str] = None
    PEOPLE_COUNT_MODEL: Optional[str] = None
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    SNAPSHOT_DIR: str = "./snapshots"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

