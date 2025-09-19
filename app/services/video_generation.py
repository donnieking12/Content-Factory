"""
Video generation service for the AI Content Factory application
"""
import asyncio
import httpx
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.video import Video
from app.models.product import Product
from app.schemas.video import VideoCreate, VideoUpdate
from app.services.product_discovery import get_product_by_id


def get_video_by_id(db: Session, video_id: int) -> Optional[Video]:
    return db.query(Video).filter(Video.id == video_id).first()


def get_videos(db: Session, skip: int = 0, limit: int = 100) -> List[Video]:
    return db.query(Video).offset(skip).limit(limit).all()


def create_video(db: Session, video: VideoCreate) -> Video:
    db_video = Video(**video.dict())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video


def update_video(db: Session, video_id: int, video: VideoUpdate) -> Optional[Video]:
    db_video = get_video_by_id(db, video_id)
    if db_video:
        update_data = video.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_video, key, value)
        db.commit()
        db.refresh(db_video)
    return db_video


def delete_video(db: Session, video_id: int) -> bool:
    db_video = get_video_by_id(db, video_id)
    if db_video:
        db.delete(db_video)
        db.commit()
        return True
    return False


def generate_video_script(product_id: int, db: Session) -> str:
    """
    Generate a video script for a product using AI
    """
    # Get the product details
    product = get_product_by_id(db, product_id)
    if not product:
        return "Product not found"
    
    # Create a prompt for the AI to generate a script
    prompt = f"""
    Create a short, engaging video script for a product with these details:
    Product Name: {product.name}
    Description: {product.description}
    Price: {product.price}
    
    The script should be structured with:
    1. An attention-grabbing opening
    2. Product introduction and key features
    3. Benefits and value proposition
    4. Clear call-to-action
    5. Closing
    
    Keep it concise and engaging for social media. Format it with scene descriptions in brackets.
    """
    
    # In a real implementation, this would call an AI service to generate a script
    # For now in development, we'll use a template-based approach
    # In production, uncomment the line below to use the real AI service:
    # import asyncio
    # return asyncio.run(call_ai_script_generation_api(prompt))
    
    # Template-based script for development
    script_template = f"""
    [Opening Scene]
    Hey everyone! Today I'm excited to show you {product.name}.
    
    [Product Introduction]
    {product.description}
    This amazing product is priced at just {product.price}.
    
    [Key Features]
    Here are the key features that make this product stand out:
    1. High quality construction
    2. Easy to use
    3. Great value for money
    
    [Call to Action]
    If you're interested in {product.name}, check out the link in the description!
    
    [Closing]
    Thanks for watching, and don't forget to like and subscribe for more great products!
    """
    
    return script_template.strip()


async def call_ai_script_generation_api(prompt: str) -> str:
    """
    Call an external AI API to generate a video script
    Using OpenAI GPT-3.5-turbo as an example
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
    except httpx.HTTPError as e:
        print(f"HTTP error occurred while calling OpenAI API: {e}")
        return "Error generating script. Please try again later."
    except Exception as e:
        print(f"Error calling AI script generation API: {e}")
        return "Error generating script. Please try again later."


def clone_viral_video_format(template_video_id: int, db: Session) -> str:
    """
    Clone a viral video format to create a new video
    """
    template_video = get_video_by_id(db, template_video_id)
    if not template_video:
        return "Template video not found"
    
    # In a real implementation, this would analyze the template video structure
    # and adapt it for a new product
    
    cloned_format = f"""
    [Cloned from Video #{template_video_id}]
    {template_video.script}
    
    [Customized for new product]
    But wait, there's more! This new product takes everything you love and improves it!
    """
    
    return cloned_format.strip()


async def generate_avatar_video(script: str, product_id: int) -> str:
    """
    Generate a video using AI avatar service
    """
    # In a real implementation, this would call the AI avatar service
    # For now, we'll simulate the process
    
    # Simulate video generation time
    await asyncio.sleep(2)
    
    # Return a sample video URL
    return f"https://example.com/videos/generated_video_for_product_{product_id}.mp4"


def create_video_for_product(product_id: int, db: Session) -> Optional[Video]:
    """
    Create a complete video for a product, including script generation and video creation
    """
    # Get the product
    product = get_product_by_id(db, product_id)
    if not product:
        return None
    
    # Generate script
    script = generate_video_script(product_id, db)
    
    # Create video record
    video_create = VideoCreate(
        title=f"How to use {product.name}",
        description=f"Learn how to use {product.name} with this helpful video guide",
        script=script,
        status="processing",
        product_id=product_id
    )
    
    video = create_video(db, video_create)
    
    # In a real implementation, we would:
    # 1. Call the AI avatar service to generate the video
    # 2. Update the video record with the generated video URL
    # 3. Update the status to "completed"
    
    # For now, we'll simulate the completion
    update_data = VideoUpdate(
        video_url=f"https://example.com/videos/product_{product_id}_video.mp4",
        status="completed"
    )
    update_video(db, int(str(video.id)), update_data)
    
    return get_video_by_id(db, int(str(video.id)))