"""
Analytics API routes for the AI Content Factory application
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.analytics_simple import SimpleAnalyticsService

router = APIRouter()


@router.get("/dashboard", response_model=Dict[str, Any])
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Get comprehensive dashboard metrics for the admin panel
    
    Returns:
    - Total counts of products, videos, posts
    - Daily activity metrics
    - Performance indicators
    - System health status
    """
    try:
        analytics_service = SimpleAnalyticsService(db)
        metrics = analytics_service.get_dashboard_summary()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics calculation failed: {str(e)}")


@router.get("/products/trends")
def get_product_trends(db: Session = Depends(get_db)):
    """Get product trending analysis"""
    try:
        from app.models.product import Product
        from sqlalchemy import func
        
        # Top categories
        categories = db.query(
            Product.category,
            func.count(Product.id).label('count')
        ).group_by(Product.category).order_by(func.count(Product.id).desc()).limit(10).all()
        
        # Trending products
        trending = db.query(Product).filter(Product.is_trending == True).limit(10).all()
        
        # Price analysis
        products = db.query(Product).all()
        avg_price = 0
        if products:
            prices = []
            for p in products:
                try:
                    price_str = str(p.price).replace('$', '') if p.price is not None else '0'
                    prices.append(float(price_str))
                except:
                    continue
            avg_price = sum(prices) / len(prices) if prices else 0
        
        return {
            "top_categories": [{"name": cat, "count": count} for cat, count in categories],
            "trending_products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "category": p.category
                } for p in trending
            ],
            "average_price": round(avg_price, 2),
            "total_trending": len(trending)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/videos/performance")
def get_video_performance(db: Session = Depends(get_db)):
    """Get video generation performance metrics"""
    try:
        from app.models.video import Video
        from sqlalchemy import func
        
        # Status distribution
        status_dist = db.query(
            Video.status,
            func.count(Video.id).label('count')
        ).group_by(Video.status).all()
        
        # Recent videos
        from datetime import datetime, timedelta
        last_7d = datetime.now() - timedelta(days=7)
        recent_videos = db.query(Video).filter(Video.created_at >= last_7d).count()
        
        # Average script length
        videos_with_scripts = db.query(Video).filter(Video.script.isnot(None)).all()
        avg_script_length = 0
        if videos_with_scripts:
            lengths = [len(str(v.script)) for v in videos_with_scripts if v.script is not None]
            avg_script_length = sum(lengths) / len(lengths) if lengths else 0
        
        return {
            "status_distribution": [{"status": status, "count": count} for status, count in status_dist],
            "recent_videos_7d": recent_videos,
            "avg_script_length": round(avg_script_length, 0),
            "total_videos": db.query(Video).count()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/social-media/stats")
def get_social_media_stats(db: Session = Depends(get_db)):
    """Get social media publishing statistics"""
    try:
        from app.models.social_media import SocialMediaPost
        from sqlalchemy import func
        
        # Platform distribution
        platforms = db.query(
            SocialMediaPost.platform,
            func.count(SocialMediaPost.id).label('count')
        ).group_by(SocialMediaPost.platform).all()
        
        # Status distribution
        statuses = db.query(
            SocialMediaPost.status,
            func.count(SocialMediaPost.id).label('count')
        ).group_by(SocialMediaPost.status).all()
        
        # Mock engagement data (would be real in production)
        import random
        engagement_data = {
            "total_views": random.randint(10000, 100000),
            "total_likes": random.randint(1000, 10000),
            "total_shares": random.randint(100, 1000),
            "engagement_rate": round(random.uniform(2.0, 8.0), 2)
        }
        
        return {
            "platforms": [{"name": platform, "posts": count} for platform, count in platforms],
            "status_distribution": [{"status": status, "count": count} for status, count in statuses],
            "engagement": engagement_data,
            "total_posts": db.query(SocialMediaPost).count()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/health")
def get_system_health():
    """Get system health metrics"""
    try:
        import psutil
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Calculate health score
        health_score = 100
        if cpu_percent > 80:
            health_score -= 20
        elif cpu_percent > 60:
            health_score -= 10
        
        if memory.percent > 85:
            health_score -= 25
        elif memory.percent > 70:
            health_score -= 15
        
        status = "healthy"
        if health_score < 60:
            status = "warning"
        elif health_score < 40:
            status = "critical"
        
        return {
            "cpu_usage": cpu_percent,
            "memory_usage": memory.percent,
            "disk_usage": round((disk.used / disk.total) * 100, 2),
            "available_memory_gb": round(memory.available / (1024**3), 2),
            "health_score": max(health_score, 0),
            "status": status,
            "uptime": "24h 15m"  # Mock uptime
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "health_score": 0
        }