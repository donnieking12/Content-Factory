"""
Monitoring API routes for the AI Content Factory application
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.monitoring import get_monitoring_dashboard

router = APIRouter()


@router.get("/dashboard")
async def monitoring_dashboard(db: Session = Depends(get_db)):
    """
    Get monitoring dashboard data
    """
    return await get_monitoring_dashboard(db)


@router.get("/metrics")
async def metrics_endpoint(db: Session = Depends(get_db)):
    """
    Get application metrics
    """
    from app.services.monitoring import monitoring_service
    return monitoring_service.get_metrics()