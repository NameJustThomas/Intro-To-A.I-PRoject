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
    
    # Anti-Spoofing
    ANTI_SPOOF_THRESHOLD: float = 0.48  # Liveness detection threshold (0.0-1.0, higher = stricter)
    # Balanced threshold (0.48) - blocks most photos while allowing live video
    # Adjust based on your environment: 
    #   0.40-0.45 = lenient (may allow some photos)
    #   0.48-0.52 = balanced (recommended)
    #   0.55-0.6 = strict (may reject some live video)
    #   0.6+ = very strict
    ANTI_SPOOF_ENABLED: bool = True  # Set to False to disable anti-spoofing check
    MULTI_FACE_DETECTION_ENABLED: bool = True  # Set to False to disable multiple face/person detection
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    SNAPSHOT_DIR: str = "./snapshots"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

