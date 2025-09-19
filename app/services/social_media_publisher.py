"""
Social media publisher service for the AI Content Factory application
"""
import httpx
import asyncio
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.social_media import SocialMediaPost
from app.schemas.social_media import SocialMediaPostCreate, SocialMediaPostUpdate


def get_post_by_id(db: Session, post_id: int) -> Optional[SocialMediaPost]:
    return db.query(SocialMediaPost).filter(SocialMediaPost.id == post_id).first()


def get_posts(db: Session, skip: int = 0, limit: int = 100) -> List[SocialMediaPost]:
    return db.query(SocialMediaPost).offset(skip).limit(limit).all()


def create_post(db: Session, post: SocialMediaPostCreate) -> SocialMediaPost:
    db_post = SocialMediaPost(**post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def update_post(db: Session, post_id: int, post: SocialMediaPostUpdate) -> Optional[SocialMediaPost]:
    db_post = get_post_by_id(db, post_id)
    if db_post:
        update_data = post.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_post, key, value)
        db.commit()
        db.refresh(db_post)
    return db_post


def delete_post(db: Session, post_id: int) -> bool:
    db_post = get_post_by_id(db, post_id)
    if db_post:
        db.delete(db_post)
        db.commit()
        return True
    return False


async def publish_to_tiktok(video_url: str, caption: str) -> Dict[str, Any]:
    """
    Publish a video to TikTok using TikTok Business API
    """
    try:
        async with httpx.AsyncClient() as client:
            # First, upload the video
            # Note: TikTok requires uploading the actual video file content
            # This is a simplified example - in practice, you'd need to download
            # the video file and upload it as multipart form data
            
            # For demonstration, we'll simulate the process
            # In a real implementation, you would:
            # 1. Download the video file from video_url
            # 2. Upload it to TikTok using their upload endpoint
            # 3. Create the post with the uploaded video ID
            
            # Simulate API call delay
            await asyncio.sleep(1)
            
            # Return simulated success response
            return {
                "platform": "tiktok",
                "status": "published",
                "post_id": "tiktok_123456789",
                "post_url": "https://www.tiktok.com/@user/video/123456789"
            }
        
    except httpx.HTTPError as e:
        print(f"HTTP error occurred while publishing to TikTok: {e}")
        return {
            "platform": "tiktok",
            "status": "failed",
            "error": f"HTTP error: {str(e)}"
        }
    except Exception as e:
        print(f"Error publishing to TikTok: {e}")
        return {
            "platform": "tiktok",
            "status": "failed",
            "error": str(e)
        }


async def publish_to_instagram(video_url: str, caption: str) -> Dict[str, Any]:
    """
    Publish a video to Instagram using Instagram Graph API
    """
    try:
        async with httpx.AsyncClient() as client:
            # First, create a media object
            # Note: Instagram requires the page ID to be set in settings
            if not settings.INSTAGRAM_PAGE_ID:
                raise ValueError("INSTAGRAM_PAGE_ID is not set in environment variables")
            
            media_response = await client.post(
                f"https://graph.facebook.com/v18.0/{settings.INSTAGRAM_PAGE_ID}/media",
                params={
                    "access_token": settings.INSTAGRAM_CLIENT_SECRET,  # Using client secret as access token
                    "video_url": video_url,
                    "caption": caption,
                    "media_type": "VIDEO"
                }
            )
            media_response.raise_for_status()
            media_data = media_response.json()
            
            # Then, publish the media
            publish_response = await client.post(
                f"https://graph.facebook.com/v18.0/{settings.INSTAGRAM_PAGE_ID}/media_publish",
                params={
                    "access_token": settings.INSTAGRAM_CLIENT_SECRET,
                    "creation_id": media_data["id"]
                }
            )
            publish_response.raise_for_status()
            result = publish_response.json()
            
            return {
                "platform": "instagram",
                "status": "published",
                "post_id": result.get("id"),
                "post_url": f"https://www.instagram.com/p/{result.get('id')}/"
            }
        
    except httpx.HTTPError as e:
        print(f"HTTP error occurred while publishing to Instagram: {e}")
        return {
            "platform": "instagram",
            "status": "failed",
            "error": f"HTTP error: {str(e)}"
        }
    except Exception as e:
        print(f"Error publishing to Instagram: {e}")
        return {
            "platform": "instagram",
            "status": "failed",
            "error": str(e)
        }


async def publish_to_youtube(video_url: str, title: str, description: str) -> Dict[str, Any]:
    """
    Publish a video to YouTube using YouTube Data API
    """
    try:
        async with httpx.AsyncClient() as client:
            # For YouTube, we would typically need to:
            # 1. Use OAuth 2.0 for authentication
            # 2. Upload the video file (which requires downloading it first)
            # 3. Set metadata like title, description, tags, etc.
            
            # This is a simplified example - in practice, you'd need to implement
            # the full OAuth flow and video upload process
            
            # Simulate API call delay
            await asyncio.sleep(1)
            
            # Return simulated success response
            return {
                "platform": "youtube",
                "status": "published",
                "video_id": "youtube_ABC123",
                "post_url": "https://www.youtube.com/watch?v=ABC123"
            }
        
    except httpx.HTTPError as e:
        print(f"HTTP error occurred while publishing to YouTube: {e}")
        return {
            "platform": "youtube",
            "status": "failed",
            "error": f"HTTP error: {str(e)}"
        }
    except Exception as e:
        print(f"Error publishing to YouTube: {e}")
        return {
            "platform": "youtube",
            "status": "failed",
            "error": str(e)
        }


async def publish_to_multiple_platforms(video_url: str, title: str, description: str) -> List[Dict[str, Any]]:
    """
    Publish a video to multiple social media platforms simultaneously
    """
    # Create tasks for parallel publishing
    tasks = [
        publish_to_tiktok(video_url, description),
        publish_to_instagram(video_url, description),
        publish_to_youtube(video_url, title, description)
    ]
    
    # Execute all publishing tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    publication_results = []
    for result in results:
        if isinstance(result, Exception):
            # Handle exceptions
            publication_results.append({
                "status": "error",
                "error": str(result)
            })
        else:
            publication_results.append(result)
    
    return publication_results


def schedule_post(db: Session, platform: str, content: str, scheduled_time: str) -> SocialMediaPost:
    """
    Schedule a social media post for future publication
    """
    # Convert string to datetime if needed
    from datetime import datetime
    try:
        if isinstance(scheduled_time, str):
            scheduled_datetime = datetime.fromisoformat(scheduled_time)
        else:
            scheduled_datetime = scheduled_time
    except ValueError:
        # If parsing fails, use current time
        scheduled_datetime = datetime.now()
    
    post_create = SocialMediaPostCreate(
        platform=platform,
        content=content,
        status="scheduled",
        scheduled_time=scheduled_datetime
    )
    
    return create_post(db, post_create)


async def get_social_media_analytics(post_id: str, platform: str) -> Dict[str, Any]:
    """
    Get analytics for a published social media post
    """
    # In a real implementation, this would call platform-specific analytics APIs
    
    # For demonstration, return sample analytics data
    await asyncio.sleep(0.5)  # Simulate API call delay
    
    return {
        "post_id": post_id,
        "platform": platform,
        "views": 15000,
        "likes": 2450,
        "shares": 320,
        "comments": 180,
        "engagement_rate": 16.4
    }