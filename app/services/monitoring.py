"""
Monitoring service for the AI Content Factory application
"""
import asyncio
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.services.health_check import check_all_services_health


class MonitoringService:
    """
    Service for monitoring application performance and health
    """
    
    def __init__(self):
        self.metrics = {
            "request_count": 0,
            "error_count": 0,
            "average_response_time": 0.0,  # Changed to float
            "active_tasks": 0
        }
        self.start_time = time.time()
    
    def increment_request_count(self):
        """Increment the request counter"""
        self.metrics["request_count"] += 1
    
    def increment_error_count(self):
        """Increment the error counter"""
        self.metrics["error_count"] += 1
    
    def update_response_time(self, response_time: float):
        """Update average response time"""
        current_avg = self.metrics["average_response_time"]
        request_count = self.metrics["request_count"]
        if request_count > 1:
            self.metrics["average_response_time"] = (current_avg * (request_count - 1) + response_time) / request_count
        else:
            self.metrics["average_response_time"] = response_time
    
    def increment_active_tasks(self):
        """Increment active tasks counter"""
        self.metrics["active_tasks"] += 1
    
    def decrement_active_tasks(self):
        """Decrement active tasks counter"""
        self.metrics["active_tasks"] = max(0, self.metrics["active_tasks"] - 1)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        uptime = time.time() - self.start_time
        return {
            **self.metrics,
            "uptime_seconds": uptime,
            "requests_per_second": self.metrics["request_count"] / max(uptime, 1)
        }


# Global monitoring service instance
monitoring_service = MonitoringService()


async def get_monitoring_dashboard(db: Session) -> Dict[str, Any]:
    """
    Get monitoring dashboard data
    """
    try:
        # Get health check results
        health_results = await check_all_services_health(db)
        
        # Get application metrics
        metrics = monitoring_service.get_metrics()
        
        # Get recent activity (simplified)
        recent_activity = {
            "timestamp": time.time(),
            "active_tasks": metrics["active_tasks"],
            "recent_requests": min(metrics["request_count"], 100)  # Limit for display
        }
        
        return {
            "health": health_results,
            "metrics": metrics,
            "activity": recent_activity,
            "status": "operational" if health_results["status"] == "healthy" else "degraded"
        }
    except Exception as e:
        logger.error(f"Error getting monitoring dashboard: {e}", exc_info=True)
        return {
            "error": f"Failed to get monitoring dashboard: {str(e)}",
            "status": "error"
        }


def log_task_start(task_name: str) -> str:
    """
    Log the start of a task and return a task ID
    """
    task_id = f"{task_name}_{int(time.time() * 1000)}"
    logger.info(f"Task {task_name} started with ID {task_id}")
    monitoring_service.increment_active_tasks()
    return task_id


def log_task_completion(task_id: str, task_name: str, duration: Optional[float] = None):
    """
    Log the completion of a task
    """
    logger.info(f"Task {task_name} (ID: {task_id}) completed successfully" + 
                (f" in {duration:.2f} seconds" if duration else ""))
    monitoring_service.decrement_active_tasks()


def log_task_error(task_id: str, task_name: str, error: Exception):
    """
    Log an error in a task
    """
    logger.error(f"Task {task_name} (ID: {task_id}) failed with error: {str(error)}", exc_info=True)
    monitoring_service.decrement_active_tasks()
    monitoring_service.increment_error_count()


class TaskMonitor:
    """
    Context manager for monitoring tasks
    """
    
    def __init__(self, task_name: str):
        self.task_name = task_name
        self.task_id: Optional[str] = None
        self.start_time: Optional[float] = None
    
    async def __aenter__(self):
        self.task_id = log_task_start(self.task_name)
        self.start_time = time.time()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time if self.start_time else None
        if self.task_id is None:
            # Handle case where task_id was not set
            logger.warning(f"Task {self.task_name} completed but task_id was not set")
            return
            
        if exc_type is None:
            log_task_completion(self.task_id, self.task_name, duration)
        else:
            log_task_error(self.task_id, self.task_name, exc_val)