from pydantic_settings import BaseSettings
from typing import List, Union


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://lms_user:lms_pass@postgres:5432/lms_db"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:5173"]
    ALLOWED_HOSTS: Union[List[str], str] = ["*"]
    
    # Cloud Storage
    GCS_BUCKET_NAME: str = "lms-content-bucket"
    USE_LOCAL_STORAGE: bool = True  # For development, use local files instead of GCS
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

