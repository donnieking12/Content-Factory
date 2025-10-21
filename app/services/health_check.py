"""
Health check service for the AI Content Factory application
"""
import asyncio
import httpx
from typing import Dict, Any, List
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine
from app.core.logging import logger


async def check_database_health(db: Session) -> Dict[str, Any]:
    """
    Check database health with fallback to Supabase REST API
    """
    try:
        # Try direct database connection first
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        return {
            "status": "healthy",
            "message": "Database connection successful (SQLAlchemy)"
        }
    except Exception as e:
        logger.warning(f"SQLAlchemy database check failed: {e}, trying Supabase REST API")
        
        # Fallback to Supabase REST API
        try:
            from supabase import create_client
            supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            result = supabase.table('products').select('*').limit(1).execute()
            return {
                "status": "healthy",
                "message": "Database connection successful (Supabase REST API)"
            }
        except Exception as rest_error:
            logger.error(f"Database health check failed: {rest_error}", exc_info=True)
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(rest_error)}"
            }


async def check_redis_health() -> Dict[str, Any]:
    """
    Check Redis health
    """
    r = None
    try:
        # For Redis health check, we would typically use redis-py
        # This is a placeholder implementation
        import redis
        r = redis.Redis.from_url(settings.REDIS_URL)
        r.ping()
        return {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }
    finally:
        try:
            if r:
                r.close()
        except:
            pass


async def check_external_api_health() -> Dict[str, Any]:
    """
    Check external API health (FakeStoreAPI as an example)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://fakestoreapi.com/products", timeout=10)
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "message": "External API connection successful"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"External API returned status code {response.status_code}"
                }
    except Exception as e:
        logger.error(f"External API health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "message": f"External API connection failed: {str(e)}"
        }


async def check_ai_services_health() -> Dict[str, Any]:
    """
    Check AI services health
    """
    # This is a placeholder implementation
    # In a real implementation, you would check the health of:
    # - OpenAI API
    # - AI Avatar service
    # - Other AI services
    
    try:
        # Check if API keys are set
        health_checks = []
        
        if settings.OPENAI_API_KEY:
            health_checks.append("OpenAI API key configured")
        else:
            health_checks.append("OpenAI API key missing")
            
        if settings.AI_AVATAR_API_URL and settings.AI_AVATAR_API_KEY:
            health_checks.append("AI Avatar service configured")
        else:
            health_checks.append("AI Avatar service not fully configured")
            
        return {
            "status": "healthy" if all("configured" in check or "key configured" in check for check in health_checks) else "degraded",
            "message": ", ".join(health_checks)
        }
    except Exception as e:
        logger.error(f"AI services health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "message": f"AI services health check failed: {str(e)}"
        }


async def check_all_services_health(db: Session) -> Dict[str, Any]:
    """
    Check health of all services
    """
    logger.info("Starting comprehensive health check")
    
    # Run all health checks concurrently
    tasks = [
        check_database_health(db),
        check_redis_health(),
        check_external_api_health(),
        check_ai_services_health()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    health_results = {}
    overall_status = "healthy"
    
    service_names = ["database", "redis", "external_api", "ai_services"]
    for i, (service_name, result) in enumerate(zip(service_names, results)):
        if isinstance(result, Exception):
            health_results[service_name] = {
                "status": "unhealthy",
                "message": f"Health check failed with exception: {str(result)}"
            }
            overall_status = "unhealthy"
        else:
            health_results[service_name] = result
            if isinstance(result, dict) and result.get("status") == "unhealthy":
                overall_status = "unhealthy"
            elif isinstance(result, dict) and result.get("status") == "degraded" and overall_status == "healthy":
                overall_status = "degraded"
    
    logger.info(f"Health check completed with overall status: {overall_status}")
    
    return {
        "status": overall_status,
        "services": health_results,
        "timestamp": asyncio.get_event_loop().time()
    }


def get_system_metrics() -> Dict[str, Any]:
    """
    Get system metrics
    """
    try:
        import psutil
        import platform
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_usage": f"{cpu_percent}%",
            "memory_total": f"{memory.total / (1024**3):.2f} GB",
            "memory_available": f"{memory.available / (1024**3):.2f} GB",
            "memory_used": f"{memory.used / (1024**3):.2f} GB",
            "memory_percent": f"{memory.percent}%",
            "disk_total": f"{disk.total / (1024**3):.2f} GB",
            "disk_used": f"{disk.used / (1024**3):.2f} GB",
            "disk_free": f"{disk.free / (1024**3):.2f} GB",
            "disk_percent": f"{(disk.used / disk.total) * 100:.2f}%",
            "platform": platform.platform(),
            "python_version": platform.python_version()
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}", exc_info=True)
        return {
            "error": f"Failed to get system metrics: {str(e)}"
        }


async def get_application_status(db: Session) -> Dict[str, Any]:
    """
    Get comprehensive application status
    """
    try:
        # Get health check results
        health_results = await check_all_services_health(db)
        
        # Get system metrics
        system_metrics = get_system_metrics()
        
        # Get database stats (example)
        try:
            product_result = db.execute(text("SELECT COUNT(*) FROM products")).fetchone()
            product_count = product_result[0] if product_result is not None else 0
            
            video_result = db.execute(text("SELECT COUNT(*) FROM videos")).fetchone()
            video_count = video_result[0] if video_result is not None else 0
            
            post_result = db.execute(text("SELECT COUNT(*) FROM social_media_posts")).fetchone()
            post_count = post_result[0] if post_result is not None else 0
        except Exception as e:
            logger.error(f"Error getting database stats: {e}", exc_info=True)
            product_count = video_count = post_count = "Error"
        
        return {
            "health": health_results,
            "system": system_metrics,
            "database_stats": {
                "products": product_count,
                "videos": video_count,
                "social_media_posts": post_count
            },
            "version": settings.PROJECT_VERSION
        }
    except Exception as e:
        logger.error(f"Error getting application status: {e}", exc_info=True)
        return {
            "error": f"Failed to get application status: {str(e)}"
        }