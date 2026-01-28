"""Application configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/social_hub.db"

    # Security
    encryption_key: str

    # Application
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Facebook
    facebook_api_version: str = "v24.0"
    facebook_base_url: str = "https://graph.facebook.com"
    facebook_app_id: Optional[str] = None
    facebook_app_secret: Optional[str] = None
    fb_page_id: Optional[str] = None
    fb_page_access_token: Optional[str] = None

    # LinkedIn
    linkedin_api_version: str = "202601"
    linkedin_base_url: str = "https://api.linkedin.com/rest"
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    linkedin_organization_urn: Optional[str] = None
    linkedin_access_token: Optional[str] = None

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
