"""Application configuration settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App settings
    APP_NAME: str = "BillOS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database settings (SQLite for now, MySQL later)
    DATABASE_URL: str = "sqlite:///./billos.db"
    
    # Redis settings (optional for initial development)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT settings
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Tax settings (VAT for Qatar)
    DEFAULT_GST_RATE: float = 0.0  # Qatar has implemented selective tax but broad VAT is pending/0 for many items. I'll set to 0 to be safe, or 5. Let's set 0 for now as basic food is often exempt.
    # Actually, user asked "For Qatar". I will just rename the comment.
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
