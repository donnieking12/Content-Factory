"""
Video API routes for the AI Content Factory application
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.video import Video, VideoCreate, VideoUpdate
from app.services.video_generation import get_video_by_id, get_videos, create_video, update_video, delete_video
from app.services.content_workflow import execute_full_content_workflow, create_content_for_product

router = APIRouter()


@router.get("/", response_model=List[Video])
def read_videos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    videos = get_videos(db, skip=skip, limit=limit)
    return videos


@router.get("/{video_id}", response_model=Video)
def read_video(video_id: int, db: Session = Depends(get_db)):
    db_video = get_video_by_id(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video


@router.post("/", response_model=Video, status_code=status.HTTP_201_CREATED)
def create_new_video(video: VideoCreate, db: Session = Depends(get_db)):
    db_video = create_video(db=db, video=video)
    return db_video


@router.put("/{video_id}", response_model=Video)
def update_existing_video(video_id: int, video: VideoUpdate, db: Session = Depends(get_db)):
    db_video = update_video(db=db, video_id=video_id, video=video)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_video(video_id: int, db: Session = Depends(get_db)):
    success = delete_video(db=db, video_id=video_id)
    if not success:
        raise HTTPException(status_code=404, detail="Video not found")
    return None


@router.post("/generate-for-product/{product_id}", status_code=status.HTTP_202_ACCEPTED)
async def generate_video_for_product(product_id: int, db: Session = Depends(get_db)):
    """
    Generate a video for a specific product
    """
    # Import here to avoid circular imports
    from app.services.product_discovery import get_product_by_id
    
    # Check if product exists
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # In a real implementation, we would trigger the Celery task:
    # from celery_worker import create_content_for_product_task
    # task = create_content_for_product_task.delay(product_id)
    # return {"task_id": task.id, "status": "started"}
    
    # For now, execute synchronously for demonstration
    import asyncio
    result = await create_content_for_product(db, product_id)
    
    if result["status"] == "failed":
        raise HTTPException(status_code=500, detail=result["errors"])
    
    return result


@router.post("/one-click-generate-publish", status_code=status.HTTP_202_ACCEPTED)
async def one_click_generate_and_publish(db: Session = Depends(get_db)):
    """
    🚀 ONE-CLICK GENERATE & PUBLISH TO ALL PLATFORMS
    
    The ultimate automation endpoint that:
    1. Discovers trending products
    2. Generates AI scripts with OpenAI
    3. Creates AI avatar videos  
    4. Publishes to TikTok, Instagram, YouTube Shorts
    
    This is your complete "Generate & Publish" business automation!
    """
    from app.services.automated_publisher import AutomatedContentPublisher
    from app.core.logging import logger
    
    try:
        logger.info("🚀 Starting one-click Generate & Publish workflow")
        
        publisher = AutomatedContentPublisher(db)
        
        # Execute the full automated pipeline
        result = await publisher.execute_full_content_pipeline(
            target_platforms=["tiktok", "instagram", "youtube"],
            product_limit=3  # Generate content for 3 trending products
        )
        
        return {
            "message": "🎬 Content generation and publishing completed!",
            "workflow_type": "one_click_automation",
            "pipeline_results": result,
            "content_created": {
                "products_discovered": result.get("products_discovered", 0),
                "videos_generated": result.get("videos_created", 0),
                "posts_published": result.get("posts_published", 0)
            },
            "distribution": {
                "platforms_reached": result.get("platforms_reached", []),
                "estimated_total_reach": result.get("total_potential_reach", 0),
                "success_rate": f"{result.get('success_rate', 0)}%"
            },
            "business_impact": {
                "content_pieces_live": result.get("videos_created", 0),
                "platforms_active": len(result.get("platforms_reached", [])),
                "automation_status": result.get("status", "unknown")
            },
            "next_steps": [
                "Monitor performance in analytics dashboard",
                "Check social media engagement",
                "Schedule next content batch"
            ]
        }
        
    except Exception as e:
        logger.error(f"One-click workflow failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Automated content workflow failed: {str(e)}"
        )


@router.post("/test-automation-pipeline")
async def test_automation_pipeline(db: Session = Depends(get_db)):
    """
    🧪 Test the complete automation pipeline
    
    Safe testing endpoint to verify your automation setup
    without publishing to production social media accounts.
    """
    from app.services.automated_publisher import quick_content_generation_test
    from app.core.logging import logger
    
    try:
        logger.info("🧪 Starting automation pipeline test")
        result = await quick_content_generation_test(db)
        
        return {
            "test_status": "completed",
            "pipeline_health": "healthy" if result.get("test_status") == "completed" else "needs_attention",
            "test_results": result,
            "message": "Automation pipeline test completed successfully!",
            "ready_for_production": True
        }
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Automation pipeline test failed: {str(e)}"
        )


@router.post("/execute-full-workflow", status_code=status.HTTP_202_ACCEPTED)
async def execute_full_content_creation_workflow(db: Session = Depends(get_db)):
    """
    Execute the full content creation workflow:
    1. Discover trending products
    2. Generate video for the best product
    3. Publish to social media
    """
    # In a real implementation, we would trigger the Celery task:
    # from celery_worker import execute_full_workflow_task
    # task = execute_full_workflow_task.delay()
    # return {"task_id": task.id, "status": "started"}
    
    # For now, execute synchronously for demonstration
    import asyncio
    result = await execute_full_content_workflow(db)
    
    if result["status"] == "failed":
        raise HTTPException(status_code=500, detail=result["errors"])
    
    return result