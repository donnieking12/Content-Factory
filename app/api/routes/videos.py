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