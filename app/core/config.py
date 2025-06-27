import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "SkillSync - AI Resume & Job Match Hub"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # CORS settings
    CORS_ORIGINS: list = ["*"]
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_EXTENSIONS: list = [".pdf", ".docx", ".txt"]
    
    class Config:
        env_file = ".env"


settings = Settings()