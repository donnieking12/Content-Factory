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

    # Database settings (Supabase)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # Redis settings for Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Social media API keys (to be set in environment variables)
    TIKTOK_CLIENT_KEY: str = os.getenv("TIKTOK_CLIENT_KEY", "")
    TIKTOK_CLIENT_SECRET: str = os.getenv("TIKTOK_CLIENT_SECRET", "")
    INSTAGRAM_CLIENT_ID: str = os.getenv("INSTAGRAM_CLIENT_ID", "")
    INSTAGRAM_CLIENT_SECRET: str = os.getenv("INSTAGRAM_CLIENT_SECRET", "")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")

    # AI Avatar service settings
    AI_AVATAR_API_URL: str = os.getenv("AI_AVATAR_API_URL", "")
    AI_AVATAR_API_KEY: str = os.getenv("AI_AVATAR_API_KEY", "")

    # FFmpeg path
    FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "ffmpeg")

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()