"""
Social media model for the AI Content Factory application
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func

from app.core.database import Base


class SocialMediaPost(Base):
    __tablename__ = "social_media_posts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)  # tiktok, instagram, youtube, etc.
    post_id = Column(String)  # ID returned by the platform
    video_id = Column(Integer)  # Reference to the video
    content = Column(Text)  # Caption or description
    status = Column(String, default="pending")  # pending, scheduled, published, failed
    post_url = Column(String)
    scheduled_time = Column(DateTime(timezone=True))  # For scheduled posts
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<SocialMediaPost(platform='{self.platform}', status='{self.status}')>"