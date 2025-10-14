"""
Main application entry point for the AI Content Factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import products, videos, social_media, monitoring, analytics

# Set up logging
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(products.router, prefix=settings.API_V1_STR + "/products", tags=["products"])
app.include_router(videos.router, prefix=settings.API_V1_STR + "/videos", tags=["videos"])
app.include_router(social_media.router, prefix=settings.API_V1_STR + "/social-media", tags=["social-media"])
app.include_router(monitoring.router, prefix=settings.API_V1_STR + "/monitoring", tags=["monitoring"])
app.include_router(analytics.router, prefix=settings.API_V1_STR + "/analytics", tags=["analytics"])

# Add middleware for monitoring
@app.middleware("http")
async def monitoring_middleware(request, call_next):
    from app.services.monitoring import monitoring_service
    import time
    
    # Record start time
    start_time = time.time()
    monitoring_service.increment_request_count()
    
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        monitoring_service.increment_error_count()
        raise
    finally:
        # Record response time
        response_time = time.time() - start_time
        monitoring_service.update_response_time(response_time)

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Content Factory API"}

@app.get("/health")
async def health_check():
    from app.core.database import SessionLocal
    from app.services.health_check import check_all_services_health
    
    db = SessionLocal()
    try:
        result = await check_all_services_health(db)
        return result
    finally:
        db.close()

@app.get("/status")
async def status_check():
    from app.core.database import SessionLocal
    from app.services.health_check import get_application_status
    
    db = SessionLocal()
    try:
        result = await get_application_status(db)
        return result
    finally:
        db.close()