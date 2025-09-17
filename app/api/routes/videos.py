"""
Video API routes for the AI Content Factory application
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.video import Video, VideoCreate, VideoUpdate
from app.services.video_generation import get_video_by_id, get_videos, create_video, update_video, delete_video

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