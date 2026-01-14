"""Application configuration settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App settings
    APP_NAME: str = "BillOS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database settings
    # For Vercel, we need to use /tmp for sqlite as the file system is read-only
    DATABASE_URL: str = "sqlite:///./billos.db"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        import os
        import shutil
        
        # Check if running in Vercel (env var or directory structure hint)
        # Vercel file system is read-only except for /tmp
        if os.environ.get("VERCEL") or os.access('.', os.W_OK) is False:
            self.DATABASE_URL = "sqlite:////tmp/billos.db"
            
            # If original db exists, copy it to tmp (to preserve seeded data)
            # Use absolute path resolution
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # backend/app/core -> backend
            original_db = os.path.join(base_dir, "billos.db")
            target_db = "/tmp/billos.db"
            
            # Fallback if moving folders around
            if not os.path.exists(original_db):
                # Try looking in current working directory
                if os.path.exists("billos.db"):
                    original_db = "billos.db"
                elif os.path.exists("backend/billos.db"):
                    original_db = "backend/billos.db"

            if os.path.exists(original_db) and not os.path.exists(target_db):
                try:
                    shutil.copy2(original_db, target_db)
                    print(f"Copied database from {original_db} to {target_db}")
                except Exception as e:
                    print(f"Failed to copy DB from {original_db}: {e}") 
    
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
