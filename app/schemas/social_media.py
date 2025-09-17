"""
Social media schemas for the AI Content Factory application
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SocialMediaPostBase(BaseModel):
    platform: str
    post_id: Optional[str] = None
    video_id: Optional[int] = None
    status: str = "pending"
    post_url: Optional[str] = None


class SocialMediaPostCreate(SocialMediaPostBase):
    pass


class SocialMediaPostUpdate(BaseModel):
    platform: Optional[str] = None
    post_id: Optional[str] = None
    video_id: Optional[int] = None
    status: Optional[str] = None
    post_url: Optional[str] = None


class SocialMediaPostInDBBase(SocialMediaPostBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SocialMediaPost(SocialMediaPostInDBBase):
    pass


class SocialMediaPostInDB(SocialMediaPostInDBBase):
    pass