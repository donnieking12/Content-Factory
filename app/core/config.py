"""
Configuration settings for the AI Content Factory application
"""
import os
from typing import List, Optional

from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    # Project information
    PROJECT_NAME: str = "AI Content Factory"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "Automated system for discovering trending products and creating viral videos"

    # API settings
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Security settings
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database settings (Supabase)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_DB_PASSWORD: str = ""

    # Redis settings for Celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # Social media API keys (to be set in environment variables)
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    INSTAGRAM_CLIENT_ID: str = ""
    INSTAGRAM_CLIENT_SECRET: str = ""
    INSTAGRAM_PAGE_ID: str = ""
    YOUTUBE_API_KEY: str = ""
    
    # YouTube OAuth settings
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    YOUTUBE_CLIENT_SECRET_FILE: str = "google_client_secret.json"

    # E-commerce API keys
    ECOMMERCE_API_KEY: str = ""
    
    # Enhanced E-commerce APIs
    AMAZON_API_KEY: str = ""
    SHOPIFY_API_KEY: str = ""
    SHOPIFY_STORE_URL: str = ""
    EBAY_API_KEY: str = ""
    ETSY_API_KEY: str = ""

    # AI Service API keys
    OPENAI_API_KEY: str = ""

    # AI Avatar service settings
    AI_AVATAR_API_URL: str = ""
    AI_AVATAR_API_KEY: str = ""

    # FFmpeg path
    FFMPEG_PATH: str = "ffmpeg"

    # Environment
    ENVIRONMENT: str = "development"

    @property
    def DATABASE_URL(self) -> str:
        """Construct DATABASE_URL from Supabase credentials"""
        if self.SUPABASE_URL and self.SUPABASE_DB_PASSWORD:
            # Extract the project-id from SUPABASE_URL
            # Supabase URL format: https://<project-id>.supabase.co
            # PostgreSQL connection format: postgresql://postgres:[PASSWORD]@db.<project-id>.supabase.co:5432/postgres
            try:
                from urllib.parse import quote_plus
                host = self.SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
                # URL encode password using quote_plus for better compatibility
                encoded_password = quote_plus(self.SUPABASE_DB_PASSWORD)
                return f"postgresql://postgres:{encoded_password}@db.{host}.supabase.co:5432/postgres?client_encoding=utf8"
            except Exception:
                return ""
        return ""

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()