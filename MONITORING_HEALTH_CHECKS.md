# Monitoring and Health Checks Guide

## Overview

This guide explains the monitoring and health check implementation in the content factory application.

## Health Check Endpoints

### 1. Basic Health Check
- **Endpoint**: `/health`
- **Method**: GET
- **Purpose**: Quick health check of all services
- **Response**:
```json
{
  "status": "healthy",
  "services": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection successful"
    },
    "external_api": {
      "status": "healthy",
      "message": "External API connection successful"
    },
    "ai_services": {
      "status": "healthy",
      "message": "OpenAI API key configured, AI Avatar service configured"
    }
  }
}
```

### 2. Detailed Status Check
- **Endpoint**: `/status`
- **Method**: GET
- **Purpose**: Comprehensive application status including system metrics
- **Response**:
```json
{
  "health": {
    "status": "healthy",
    "services": { /* ... */ }
  },
  "system": {
    "cpu_usage": "15.2%",
    "memory_total": "16.00 GB",
    "memory_available": "8.23 GB",
    "memory_used": "7.77 GB",
    "memory_percent": "48.5%",
    "disk_total": "512.00 GB",
    "disk_used": "128.45 GB",
    "disk_free": "383.55 GB",
    "disk_percent": "25.09%"
  },
  "database_stats": {
    "products": 42,
    "videos": 18,
    "social_media_posts": 56
  }
}
```

### 3. Monitoring Dashboard
- **Endpoint**: `/api/v1/monitoring/dashboard`
- **Method**: GET
- **Purpose**: Real-time monitoring dashboard data
- **Response**:
```json
{
  "health": { /* ... */ },
  "metrics": {
    "request_count": 1250,
    "error_count": 3,
    "average_response_time": 0.245,
    "active_tasks": 2,
    "uptime_seconds": 3600.5,
    "requests_per_second": 0.347
  },
  "activity": {
    "timestamp": 1640995200,
    "active_tasks": 2,
    "recent_requests": 100
  },
  "status": "operational"
}
```

## Monitoring Components

### 1. Health Check Service
Located in [app/services/health_check.py](file:///c%3A/Users/Mimi/content-factory-ai/app/services/health_check.py), this service provides:
- Database connectivity checks
- Redis connectivity checks
- External API availability checks
- AI service configuration checks

### 2. Monitoring Service
Located in [app/services/monitoring.py](file:///c%3A/Users/Mimi/content-factory-ai/app/services/monitoring.py), this service provides:
- Request counting
- Error tracking
- Response time monitoring
- Active task tracking

### 3. Task Monitoring
The TaskMonitor context manager helps track individual tasks:
```python
async with TaskMonitor("video_generation") as monitor:
    # Task implementation
    pass
```

## Setting up External Monitoring

### 1. Prometheus Integration
To integrate with Prometheus, you can expose metrics at `/api/v1/monitoring/metrics`:
```json
{
  "request_count": 1250,
  "error_count": 3,
  "average_response_time": 0.245,
  "active_tasks": 2,
  "uptime_seconds": 3600.5,
  "requests_per_second": 0.347
}
```

### 2. Grafana Dashboard
Create a Grafana dashboard with panels for:
- Request rate
- Error rate
- Response time
- System resource usage
- Database statistics
- Task queue depth

### 3. Health Check Alerts
Set up alerts for:
- Service health status changes
- High error rates
- Slow response times
- Resource exhaustion

## Custom Health Checks

To add custom health checks:

1. Create a new function in [app/services/health_check.py](file:///c%3A/Users/Mimi/content-factory-ai/app/services/health_check.py):
```python
async def check_custom_service_health() -> Dict[str, Any]:
    try:
        # Health check implementation
        return {
            "status": "healthy",
            "message": "Custom service is running"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Custom service check failed: {str(e)}"
        }
```

2. Add it to the [check_all_services_health](file:///c%3A/Users/Mimi/content-factory-ai/app/services/health_check.py#L144-L177) function:
```python
tasks = [
    check_database_health(db),
    check_redis_health(),
    check_external_api_health(),
    check_ai_services_health(),
    check_custom_service_health()  # Add this line
]
```

## Performance Monitoring

### 1. Response Time Tracking
The middleware in [app/main.py](file:///c%3A/Users/Mimi/content-factory-ai/app/main.py) automatically tracks response times:
- Records start time before request processing
- Calculates duration after response
- Updates average response time metrics

### 2. Task Performance
Use the TaskMonitor context manager to track task performance:
```python
async with TaskMonitor("content_workflow") as monitor:
    result = await execute_full_content_workflow(db)
```

### 3. Database Query Monitoring
For database performance monitoring:
- Track slow queries
- Monitor connection pool usage
- Log query execution times

## Alerting Strategy

### 1. Health Status Alerts
- Trigger when overall health status changes to "unhealthy"
- Trigger when individual services become unhealthy

### 2. Performance Alerts
- Response time exceeds threshold (e.g., >1s)
- Error rate exceeds threshold (e.g., >5%)
- High resource usage (e.g., >90% CPU or memory)

### 3. Business Metrics Alerts
- No new products discovered in 24 hours
- No videos generated in 12 hours
- Failed social media publishes >10% rate

## Log-Based Monitoring

### 1. Error Pattern Detection
Monitor logs for:
- Repeated error messages
- New error types
- Spike in error frequency

### 2. Performance Degradation
Monitor logs for:
- Slow query warnings
- Timeout errors
- Resource exhaustion warnings

### 3. Security Events
Monitor logs for:
- Authentication failures
- Unauthorized access attempts
- Suspicious activity patterns

## Third-Party Monitoring Integration

### 1. Sentry
For error tracking and performance monitoring:
1. Install Sentry SDK: `pip install sentry-sdk`
2. Initialize in [app/main.py](file:///c%3A/Users/Mimi/content-factory-ai/app/main.py):
```python
import sentry_sdk
sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    traces_sample_rate=1.0
)
```

### 2. New Relic
For application performance monitoring:
1. Install New Relic agent: `pip install newrelic`
2. Configure with newrelic.ini
3. Wrap application with New Relic middleware

### 3. Datadog
For infrastructure and application monitoring:
1. Install Datadog agent
2. Use ddtrace library: `pip install ddtrace`
3. Instrument application code

## Testing Monitoring

### 1. Health Check Tests
Test health check endpoints:
```python
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### 2. Metrics Tests
Test metrics endpoints:
```python
def test_metrics_endpoint(client):
    response = client.get("/api/v1/monitoring/metrics")
    assert response.status_code == 200
    assert "request_count" in response.json()
```

### 3. Monitoring Service Tests
Test monitoring service functionality:
```python
def test_monitoring_service():
    from app.services.monitoring import monitoring_service
    
    initial_count = monitoring_service.metrics["request_count"]
    monitoring_service.increment_request_count()
    
    assert monitoring_service.metrics["request_count"] == initial_count + 1
```

## Troubleshooting Monitoring Issues

### 1. Health Check Failures
- Check service connectivity
- Verify credentials and configuration
- Review service logs for errors

### 2. Missing Metrics
- Verify middleware is properly configured
- Check metric collection intervals
- Ensure sufficient permissions for metric collection

### 3. Performance Impact
- Monitor monitoring overhead
- Optimize metric collection frequency
- Use sampling for high-volume metrics

## Best Practices

### 1. Proactive Monitoring
- Monitor before problems occur
- Set appropriate thresholds
- Regularly review and adjust alerts

### 2. Meaningful Metrics
- Focus on business-critical metrics
- Avoid metric overload
- Correlate metrics with user impact

### 3. Alert Fatigue Prevention
- Use appropriate alert severity levels
- Implement alert deduplication
- Regularly review and refine alerts

### 4. Dashboard Design
- Keep dashboards focused and actionable
- Use appropriate visualization types
- Regularly update dashboards based on needs

## Security Considerations

### 1. Health Check Security
- Restrict access to health check endpoints
- Don't expose sensitive system information
- Implement rate limiting for health checks

### 2. Metric Security
- Protect metric endpoints from unauthorized access
- Sanitize sensitive information in metrics
- Encrypt metric data in transit

### 3. Monitoring Data Retention
- Implement appropriate data retention policies
- Securely delete old monitoring data
- Comply with data protection regulations