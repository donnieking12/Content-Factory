"""
Main application entry point for the AI Content Factory
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import products, videos, social_media

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

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Content Factory API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}