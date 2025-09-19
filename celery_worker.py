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
        "celery_worker.execute_full_workflow_task": "main-queue",
        "celery_worker.create_content_for_product_task": "main-queue",
    }
)


@celery_app.task
def discover_products_task():
    """
    Celery task to discover trending products
    """
    # Import here to avoid circular imports
    from app.services.product_discovery import discover_trending_products
    from app.core.database import SessionLocal
    
    try:
        db = SessionLocal()
        products = discover_trending_products(db)
        db.close()
        return {"status": "success", "products_found": len(products), "products": [p.name for p in products]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@celery_app.task
def generate_video_task(product_id: int):
    """
    Celery task to generate a video for a product using AI avatar service
    """
    # Import here to avoid circular imports
    from app.services.video_generation import generate_video_script, create_video_for_product
    from app.services.ai_avatar import create_avatar_video
    from app.core.database import SessionLocal
    
    try:
        db = SessionLocal()
        # Generate script
        script = generate_video_script(product_id, db)
        
        # Create video using AI avatar
        avatar_settings = {
            "title": f"Product Demo Video {product_id}",
            "description": "AI Generated Product Demo",
            "ratio": "16:9",
            "avatar_id": "default_avatar",
            "voice_id": "default_voice",
            "background": "default_background"
        }
        
        # Create avatar video
        import asyncio
        video_url = asyncio.run(create_avatar_video(script, avatar_settings))
        
        # Save video to database
        video = create_video_for_product(product_id, db)
        
        # Update video with the real URL
        if video:
            from app.services.video_generation import update_video
            from app.schemas.video import VideoUpdate
            update_data = VideoUpdate(
                video_url=video_url,
                status="completed"
            )
            update_video(db, int(str(video.id)), update_data)
        
        db.close()
        
        return {"status": "success", "video_id": video.id if video else None, "video_url": video_url}
    except Exception as e:
        # Update video status to failed
        try:
            db = SessionLocal()
            from app.services.video_generation import get_video_by_id, update_video
            from app.schemas.video import VideoUpdate
            video = get_video_by_id(db, product_id)  # Assuming product_id is used as video_id for simplicity
            if video:
                update_data = VideoUpdate(
                    status="failed"
                )
                update_video(db, int(str(video.id)), update_data)
            db.close()
        except Exception:
            pass  # Ignore errors in error handling
        
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
    from app.services.video_generation import get_video_by_id
    from app.core.database import SessionLocal
    
    try:
        # Get video details
        db = SessionLocal()
        video = get_video_by_id(db, video_id)
        db.close()
        
        if not video:
            return {"status": "error", "message": f"Video with ID {video_id} not found"}
        
        # Get video details, handling SQLAlchemy column objects
        video_url = str(getattr(video, 'video_url', None) or "https://example.com/sample-video.mp4")
        title = str(getattr(video, 'title', None) or "Untitled Video")
        description = str(getattr(video, 'description', None) or "Check out this amazing product!")
        
        results = []
        
        # Publish to each platform
        for platform in platforms:
            if platform == "tiktok":
                result = publish_to_tiktok(video_url, description)
                results.append(result)
            elif platform == "instagram":
                result = publish_to_instagram(video_url, description)
                results.append(result)
            elif platform == "youtube":
                result = publish_to_youtube(video_url, title, description)
                results.append(result)
        
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@celery_app.task
def execute_full_workflow_task():
    """
    Celery task to execute the full content workflow
    """
    # Import here to avoid circular imports
    from app.services.content_workflow import execute_full_content_workflow
    from app.core.database import SessionLocal
    
    try:
        db = SessionLocal()
        import asyncio
        # Run the async workflow in a new event loop
        result = asyncio.run(execute_full_content_workflow(db))
        db.close()
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


@celery_app.task
def create_content_for_product_task(product_id: int):
    """
    Celery task to create content for a specific product
    """
    # Import here to avoid circular imports
    from app.services.content_workflow import create_content_for_product
    from app.core.database import SessionLocal
    
    try:
        db = SessionLocal()
        import asyncio
        # Run the async workflow in a new event loop
        result = asyncio.run(create_content_for_product(db, product_id))
        db.close()
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


@celery_app.task
def scheduled_trend_discovery_task():
    """
    Celery task for scheduled trend discovery (to be run periodically)
    """
    from app.services.product_discovery import discover_trending_products
    from app.core.database import SessionLocal
    
    try:
        db = SessionLocal()
        products = discover_trending_products(db)
        db.close()
        return {
            "status": "success", 
            "message": f"Discovered {len(products)} trending products",
            "products": [p.name for p in products]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}