"""
Simple Analytics Service for Content Factory AI
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.logging import logger
from app.models.product import Product
from app.models.video import Video
from app.models.social_media import SocialMediaPost


class SimpleAnalyticsService:
    """Simple analytics service for dashboard metrics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get simple dashboard summary metrics"""
        try:
            # Time ranges
            now = datetime.now()
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)
            
            # Basic counts
            total_products = self.db.query(Product).count()
            total_videos = self.db.query(Video).count()
            total_posts = self.db.query(SocialMediaPost).count()
            
            # Recent activity
            products_24h = self.db.query(Product).filter(Product.created_at >= last_24h).count()
            videos_24h = self.db.query(Video).filter(Video.created_at >= last_24h).count()
            posts_24h = self.db.query(SocialMediaPost).filter(SocialMediaPost.created_at >= last_24h).count()
            
            # Trending products
            trending_count = self.db.query(Product).filter(Product.is_trending == True).count()
            
            # Video success rate
            completed_videos = self.db.query(Video).filter(Video.status == 'completed').count()
            success_rate = (completed_videos / total_videos * 100) if total_videos > 0 else 0
            
            return {
                "timestamp": now.isoformat(),
                "totals": {
                    "products": total_products,
                    "videos": total_videos,
                    "posts": total_posts,
                    "trending_products": trending_count
                },
                "daily_activity": {
                    "products_discovered": products_24h,
                    "videos_created": videos_24h,
                    "posts_published": posts_24h
                },
                "performance": {
                    "video_success_rate": round(success_rate, 2),
                    "discovery_rate": round(products_24h / 24, 2),
                    "publishing_rate": round(posts_24h, 2)
                },
                "status": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Analytics calculation failed: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }