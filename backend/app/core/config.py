"""Application configuration settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App settings
    APP_NAME: str = "BillOS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False  # Disable debug in production
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./billos.db"
    
    # Redis settings (optional for initial development)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT settings
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Tax settings
    DEFAULT_GST_RATE: float = 0.0
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def effective_database_url(self) -> str:
        """Get the effective database URL based on environment."""
        # On Vercel, use /tmp which is writable
        if os.environ.get("VERCEL"):
            return "sqlite:////tmp/billos.db"
        return self.DATABASE_URL


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

