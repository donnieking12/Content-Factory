"""
CloudWatch metrics utility for Content Factory
"""
import boto3
import logging
from datetime import datetime
from typing import Optional, List, Dict
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class CloudWatchMetrics:
    """Send custom metrics to CloudWatch"""
    
    def __init__(self, namespace: str = "ContentFactory", region: str = "eu-west-3"):
        self.namespace = namespace
        self.region = region
        try:
            self.cloudwatch = boto3.client('cloudwatch', region_name=region)
            self.enabled = True
            logger.info(f"CloudWatch metrics initialized for namespace: {namespace}")
        except Exception as e:
            logger.warning(f"CloudWatch not available: {e}")
            self.enabled = False
    
    def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = 'Count',
        dimensions: Optional[List[Dict[str, str]]] = None
    ) -> bool:
        """
        Send a metric to CloudWatch
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit (Count, Seconds, Milliseconds, Percent, etc.)
            dimensions: List of dimension dicts [{'Name': 'key', 'Value': 'val'}]
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow()
            }
            
            if dimensions:
                metric_data['Dimensions'] = dimensions
            
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data]
            )
            
            return True
            
        except ClientError as e:
            logger.error(f"Failed to send metric {metric_name}: {e}")
            return False
    
    def track_api_request(self, endpoint: str, status_code: int, response_time: float) -> None:
        """
        Track API request metrics
        
        Args:
            endpoint: API endpoint path
            status_code: HTTP status code
            response_time: Response time in milliseconds
        """
        # Track total requests
        self.put_metric('APIRequests', 1, 'Count', [
            {'Name': 'Endpoint', 'Value': endpoint},
            {'Name': 'StatusCode', 'Value': str(status_code)}
        ])
        
        # Track response time
        self.put_metric('APIResponseTime', response_time, 'Milliseconds', [
            {'Name': 'Endpoint', 'Value': endpoint}
        ])
        
        # Track errors separately
        if status_code >= 400:
            self.put_metric('APIErrors', 1, 'Count', [
                {'Name': 'Endpoint', 'Value': endpoint},
                {'Name': 'StatusCode', 'Value': str(status_code)}
            ])
    
    def track_error(self, error_type: str, error_message: str = "") -> None:
        """
        Track application errors
        
        Args:
            error_type: Type of error (e.g., ValueError, HTTPError)
            error_message: Error message
        """
        self.put_metric('Errors', 1, 'Count', [
            {'Name': 'ErrorType', 'Value': error_type}
        ])
        
        logger.error(f"Error tracked in CloudWatch: {error_type} - {error_message}")
    
    def track_video_upload(self, platform: str, success: bool, duration: float = 0) -> None:
        """
        Track video upload metrics
        
        Args:
            platform: Platform name (YouTube, TikTok, Instagram)
            success: Whether upload was successful
            duration: Upload duration in seconds
        """
        status = 'Success' if success else 'Failed'
        
        # Track upload attempts
        self.put_metric('VideoUploads', 1, 'Count', [
            {'Name': 'Platform', 'Value': platform},
            {'Name': 'Status', 'Value': status}
        ])
        
        # Track duration for successful uploads
        if success and duration > 0:
            self.put_metric('VideoUploadDuration', duration, 'Seconds', [
                {'Name': 'Platform', 'Value': platform}
            ])
    
    def track_youtube_oauth_status(self, is_authenticated: bool) -> None:
        """
        Track YouTube OAuth status
        
        Args:
            is_authenticated: Whether user is authenticated
        """
        value = 1 if is_authenticated else 0
        self.put_metric('YouTubeOAuthStatus', value, 'Count')
    
    def track_database_connection(self, is_connected: bool, response_time: float = 0) -> None:
        """
        Track database health
        
        Args:
            is_connected: Whether database is connected
            response_time: Query response time in milliseconds
        """
        value = 1 if is_connected else 0
        self.put_metric('DatabaseConnected', value, 'Count')
        
        if is_connected and response_time > 0:
            self.put_metric('DatabaseResponseTime', response_time, 'Milliseconds')
    
    def track_product_discovery(self, product_count: int, success: bool) -> None:
        """
        Track product discovery metrics
        
        Args:
            product_count: Number of products discovered
            success: Whether discovery was successful
        """
        status = 'Success' if success else 'Failed'
        
        self.put_metric('ProductDiscovery', product_count, 'Count', [
            {'Name': 'Status', 'Value': status}
        ])
    
    def track_ai_script_generation(self, success: bool, response_time: float = 0) -> None:
        """
        Track AI script generation metrics
        
        Args:
            success: Whether generation was successful
            response_time: Generation time in seconds
        """
        status = 'Success' if success else 'Failed'
        
        self.put_metric('AIScriptGeneration', 1, 'Count', [
            {'Name': 'Status', 'Value': status}
        ])
        
        if success and response_time > 0:
            self.put_metric('AIScriptGenerationTime', response_time, 'Seconds')
    
    def track_celery_task(self, task_name: str, status: str, duration: float = 0) -> None:
        """
        Track Celery background task metrics
        
        Args:
            task_name: Name of the task
            status: Task status (started, success, failure)
            duration: Task duration in seconds
        """
        self.put_metric('CeleryTasks', 1, 'Count', [
            {'Name': 'TaskName', 'Value': task_name},
            {'Name': 'Status', 'Value': status}
        ])
        
        if duration > 0:
            self.put_metric('CeleryTaskDuration', duration, 'Seconds', [
                {'Name': 'TaskName', 'Value': task_name}
            ])
    
    def track_system_health(self, cpu_percent: float, memory_percent: float, disk_percent: float) -> None:
        """
        Track system resource usage
        
        Args:
            cpu_percent: CPU usage percentage
            memory_percent: Memory usage percentage
            disk_percent: Disk usage percentage
        """
        self.put_metric('SystemCPU', cpu_percent, 'Percent')
        self.put_metric('SystemMemory', memory_percent, 'Percent')
        self.put_metric('SystemDisk', disk_percent, 'Percent')


# Global instance
cloudwatch_metrics = CloudWatchMetrics()
