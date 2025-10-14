"""
Automated Content Publisher - One-Click Generate & Publish
"""
import asyncio
from typing import Dict, List, Any, Optional, cast
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.services.product_discovery import discover_trending_products_from_api
from app.services.video_generation import generate_video_script
from app.services.ai_avatar import create_avatar_video
from app.services.social_media_publisher import publish_to_multiple_platforms
from app.models.product import Product
from app.models.video import Video
from app.models.social_media import SocialMediaPost
from app.schemas.product import ProductCreate
from app.schemas.video import VideoCreate
from app.schemas.social_media import SocialMediaPostCreate


class AutomatedContentPublisher:
    """
    One-click content generation and publishing system
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def execute_full_content_pipeline(
        self, 
        target_platforms: List[str] = ["tiktok", "instagram", "youtube"],
        product_limit: int = 5
    ) -> Dict[str, Any]:
        """
        Execute the complete content pipeline:
        1. Discover trending products
        2. Generate AI scripts for each
        3. Create AI avatar videos
        4. Publish to all platforms
        """
        pipeline_results = {
            "status": "started",
            "products_discovered": 0,
            "videos_created": 0,
            "posts_published": 0,
            "platforms_reached": [],
            "total_potential_reach": 0,
            "errors": [],
            "success_rate": 0
        }
        
        try:
            logger.info("🚀 Starting automated content pipeline")
            
            # Step 1: Discover trending products
            logger.info("📦 Step 1: Discovering trending products...")
            products = await self._discover_and_save_products(product_limit)
            pipeline_results["products_discovered"] = len(products)
            
            if not products:
                pipeline_results["status"] = "failed"
                pipeline_results["errors"].append("No trending products found")
                return pipeline_results
            
            # Step 2: Generate content for each product
            logger.info("🎬 Step 2: Generating AI content...")
            content_items = []
            
            for product in products:
                try:
                    content_item = await self._create_content_for_product(product)
                    if content_item:
                        content_items.append(content_item)
                        pipeline_results["videos_created"] += 1
                except Exception as e:
                    logger.error(f"Content creation failed for product {product.id}: {e}")
                    pipeline_results["errors"].append(f"Video creation failed: {str(e)}")
            
            # Step 3: Publish to social media platforms
            logger.info("📱 Step 3: Publishing to social media...")
            publication_results = []
            
            for content_item in content_items:
                try:
                    pub_result = await self._publish_content(content_item, target_platforms)
                    publication_results.extend(pub_result)
                    pipeline_results["posts_published"] += len(pub_result)
                except Exception as e:
                    logger.error(f"Publishing failed for content {content_item['video_id']}: {e}")
                    pipeline_results["errors"].append(f"Publishing failed: {str(e)}")
            
            # Step 4: Calculate final metrics
            pipeline_results.update(self._calculate_pipeline_metrics(publication_results))
            pipeline_results["status"] = "completed"
            
            logger.info(f"✅ Pipeline completed: {pipeline_results['videos_created']} videos, {pipeline_results['posts_published']} posts")
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            pipeline_results["status"] = "failed"
            pipeline_results["errors"].append(f"Pipeline error: {str(e)}")
        
        return pipeline_results
    
    async def _discover_and_save_products(self, limit: int) -> List[Product]:
        """Discover and save trending products"""
        try:
            # Get products from API
            product_data = await discover_trending_products_from_api()
            
            saved_products = []
            for data in product_data[:limit]:
                try:
                    # Check if product already exists
                    existing = self.db.query(Product).filter(Product.url == data["url"]).first()
                    
                    if not existing:
                        # Create new product
                        from app.services.product_discovery import create_product
                        product_create = ProductCreate(**data)
                        product = create_product(self.db, product_create)
                        saved_products.append(product)
                    else:
                        saved_products.append(existing)
                        
                except Exception as e:
                    logger.error(f"Failed to save product: {e}")
                    continue
            
            return saved_products
            
        except Exception as e:
            logger.error(f"Product discovery failed: {e}")
            return []
    
    async def _create_content_for_product(self, product: Product) -> Optional[Dict[str, Any]]:
        """Create complete content (script + video) for a product"""
        try:
            # Generate AI script (use cast to fix type checking)
            product_id = cast(int, product.id)
            
            script = generate_video_script(product_id, self.db)
            
            if not script or script == "Product not found":
                return None
            
            # Create video record
            video_create = VideoCreate(
                title=f"Discover {product.name} - Trending Now!",
                description=f"Check out this amazing {product.name} that's trending everywhere!",
                script=script,
                status="processing",
                product_id=product_id
            )
            
            from app.services.video_generation import create_video
            video = create_video(self.db, video_create)
            
            # Generate AI avatar video
            avatar_settings = {
                "title": video.title,
                "description": video.description,
                "ratio": "9:16",  # Perfect for TikTok/Instagram/YouTube Shorts
                "avatar_id": "professional_presenter",
                "voice_id": "energetic_female",
                "background": "trending_gradient"
            }
            
            video_url = await create_avatar_video(script, avatar_settings)
            
            # Update video with URL (use cast to fix type checking)
            video_id = cast(int, video.id)
            from app.services.video_generation import update_video
            from app.schemas.video import VideoUpdate
            update_video(self.db, video_id, VideoUpdate(
                video_url=video_url,
                status="completed"
            ))
            
            return {
                "product_id": product_id,
                "product_name": product.name,
                "video_id": video_id,
                "video_url": video_url,
                "script": script,
                "title": video.title,
                "description": video.description
            }
            
        except Exception as e:
            logger.error(f"Content creation failed for product {product.id}: {e}")
            return None
    
    async def _publish_content(self, content_item: Dict[str, Any], platforms: List[str]) -> List[Dict[str, Any]]:
        """Publish content to specified platforms"""
        try:
            # Publish to multiple platforms
            results = await publish_to_multiple_platforms(
                video_url=content_item["video_url"],
                title=content_item["title"],
                description=content_item["description"]
            )
            
            # Save publication records
            publication_records = []
            for result in results:
                try:
                    post_create = SocialMediaPostCreate(
                        platform=result.get("platform", "unknown"),
                        content=content_item["description"],
                        status="published" if result.get("status") == "published" else "failed",
                        video_id=content_item["video_id"]
                    )
                    
                    from app.services.social_media_publisher import create_post
                    post = create_post(self.db, post_create)
                    
                    publication_records.append({
                        "platform": result.get("platform"),
                        "status": result.get("status"),
                        "post_id": result.get("post_id"),
                        "post_url": result.get("post_url"),
                        "reach_potential": self._estimate_platform_reach(result.get("platform", "unknown"))
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to save publication record: {e}")
                    continue
            
            return publication_records
            
        except Exception as e:
            logger.error(f"Publishing failed: {e}")
            return []
    
    def _estimate_platform_reach(self, platform: str) -> int:
        """Estimate potential reach per platform"""
        reach_estimates = {
            "tiktok": 10000,      # Average TikTok video reach
            "instagram": 5000,    # Average Instagram Reel reach  
            "youtube": 3000,      # Average YouTube Short reach
            "facebook": 2000,     # Average Facebook video reach
            "twitter": 1500,      # Average Twitter video reach
        }
        return reach_estimates.get(platform.lower(), 1000)
    
    def _calculate_pipeline_metrics(self, publication_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive pipeline metrics"""
        total_reach = sum(item.get("reach_potential", 0) for item in publication_results)
        successful_posts = len([item for item in publication_results if item.get("status") == "published"])
        total_posts = len(publication_results)
        
        platforms_reached = list(set(item.get("platform") for item in publication_results if item.get("status") == "published"))
        
        success_rate = (successful_posts / total_posts * 100) if total_posts > 0 else 0
        
        return {
            "platforms_reached": platforms_reached,
            "total_potential_reach": total_reach,
            "success_rate": round(success_rate, 2),
            "successful_publications": successful_posts,
            "failed_publications": total_posts - successful_posts
        }


# Utility function for quick testing
async def quick_content_generation_test(db: Session) -> Dict[str, Any]:
    """Quick test of the content generation pipeline"""
    publisher = AutomatedContentPublisher(db)
    
    # Generate content for 2 products
    result = await publisher.execute_full_content_pipeline(
        target_platforms=["tiktok", "instagram", "youtube"],
        product_limit=2
    )
    
    return {
        "test_status": "completed",
        "pipeline_result": result,
        "message": "Content generation pipeline test completed successfully!"
    }