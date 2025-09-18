"""
Video tests for the AI Content Factory application
"""
import pytest
from sqlalchemy.orm import Session
from typing import Any

from app.models.video import Video
from app.schemas.video import VideoCreate
from app.services.video_generation import create_video, get_video_by_id


def test_create_video(db: Session):
    """Test creating a video"""
    video_data = VideoCreate(
        title="Test Video",
        description="A test video",
        script="This is a test script",
        status="pending"
    )
    
    video = create_video(db, video_data)
    
    # Convert to string to satisfy type checker
    assert str(video.title) == "Test Video"
    assert str(video.description) == "A test video"
    assert str(video.script) == "This is a test script"
    assert str(video.status) == "pending"


def test_get_video_by_id(db: Session):
    """Test retrieving a video by ID"""
    # First create a video
    video_data = VideoCreate(
        title="Test Video 2",
        description="Another test video",
        script="This is another test script"
    )
    
    created_video = create_video(db, video_data)
    
    # Extract the ID value and convert to int to satisfy type checker
    video_id: int = int(str(created_video.id))
    
    # Then retrieve it
    retrieved_video = get_video_by_id(db, video_id)
    
    assert retrieved_video is not None
    assert int(str(retrieved_video.id)) == video_id
    assert str(retrieved_video.title) == "Test Video 2"