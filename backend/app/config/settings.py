from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App settings
    app_name: str = "Northwestern Course AI"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./database.db"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"  # Change this!
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # OpenAI
    openai_api_key: Optional[str] = None
    
    # Google OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: Optional[str] = None  # e.g., "http://localhost:8000/auth/google/callback"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

