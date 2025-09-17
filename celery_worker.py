"""
Celery worker configuration for the AI Content Factory application
"""
from celery import Celery

from app.core.config import settings

# Create the Celery app
celery_app = Celery(
    "ai_content_factory",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "celery_worker.discover_products_task": "main-queue",
        "celery_worker.generate_video_task": "video-queue",
        "celery_worker.publish_video_task": "publish-queue",
    }
)


@celery_app.task
def discover_products_task():
    """
    Celery task to discover trending products
    """
    # Import here to avoid circular imports
    from app.services.product_discovery import discover_trending_products
    
    try:
        products = discover_trending_products()
        return {"status": "success", "products_found": len(products)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@celery_app.task
def generate_video_task(product_id: int):
    """
    Celery task to generate a video for a product
    """
    # Import here to avoid circular imports
    from app.services.video_generation import generate_video_script
    from app.services.ai_avatar import create_avatar_video
    
    try:
        # Generate script
        script = generate_video_script(product_id)
        
        # Create video using AI avatar
        # This is a placeholder - you would pass actual avatar settings
        avatar_settings = {
            "avatar_id": "default",
            "voice": "en-US-Wavenet-D",
            "style": "casual"
        }
        
        video_url = create_avatar_video(script, avatar_settings)
        
        return {"status": "success", "video_url": video_url}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@celery_app.task
def publish_video_task(video_id: int, platforms: list):
    """
    Celery task to publish a video to social media platforms
    """
    # Import here to avoid circular imports
    from app.services.social_media_publisher import (
        publish_to_tiktok,
        publish_to_instagram,
        publish_to_youtube
    )
    
    try:
        results = []
        
        # Publish to each platform
        for platform in platforms:
            if platform == "tiktok":
                result = publish_to_tiktok("video_url", "Check this out! #trending")
                results.append(result)
            elif platform == "instagram":
                result = publish_to_instagram("video_url", "Check this out! #trending")
                results.append(result)
            elif platform == "youtube":
                result = publish_to_youtube("video_url", "Awesome Product", "Check this out!")
                results.append(result)
        
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}