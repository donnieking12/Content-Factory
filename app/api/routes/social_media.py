"""
Social media API routes for the AI Content Factory application
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.social_media import SocialMediaPost, SocialMediaPostCreate, SocialMediaPostUpdate
from app.services.social_media_publisher import get_post_by_id, get_posts, create_post, update_post, delete_post

router = APIRouter()


@router.get("/", response_model=List[SocialMediaPost])
def read_posts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    posts = get_posts(db, skip=skip, limit=limit)
    return posts


@router.get("/{post_id}", response_model=SocialMediaPost)
def read_post(post_id: int, db: Session = Depends(get_db)):
    db_post = get_post_by_id(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Social media post not found")
    return db_post


@router.post("/", response_model=SocialMediaPost, status_code=status.HTTP_201_CREATED)
def create_new_post(post: SocialMediaPostCreate, db: Session = Depends(get_db)):
    db_post = create_post(db=db, post=post)
    return db_post


@router.put("/{post_id}", response_model=SocialMediaPost)
def update_existing_post(post_id: int, post: SocialMediaPostUpdate, db: Session = Depends(get_db)):
    db_post = update_post(db=db, post_id=post_id, post=post)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Social media post not found")
    return db_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_post(post_id: int, db: Session = Depends(get_db)):
    success = delete_post(db=db, post_id=post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Social media post not found")
    return None