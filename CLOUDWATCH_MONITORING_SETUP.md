# AWS CloudWatch Monitoring Setup - Content Factory

## 📊 Complete Monitoring Solution

Set up comprehensive monitoring for your Content Factory application using AWS CloudWatch.

---

## 🎯 What We'll Monitor

- ✅ Application health and uptime
- ✅ API response times
- ✅ Error rates and exceptions
- ✅ Database connections
- ✅ YouTube OAuth status
- ✅ Video uploads and processing
- ✅ System resources (CPU, memory, disk)
- ✅ Docker container metrics

---

## 📋 Prerequisites

- ✅ EC2 instance running Content Factory
- ✅ AWS CLI configured
- ✅ IAM role with CloudWatch permissions

---

## 🔧 Step 1: Install CloudWatch Agent on EC2

**SSH to EC2:**

```bash
ssh -i "your-key.pem" ubuntu@ec2-13-36-168-66.eu-west-3.compute.amazonaws.com
```

**Download and install CloudWatch agent:**

```bash
# Download CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb

# Install
sudo dpkg -i amazon-cloudwatch-agent.deb

# Verify installation
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a query -m ec2 -c default -s
```

---

## 🔐 Step 2: Configure IAM Role

**Create IAM policy for CloudWatch (in AWS Console):**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData",
        "ec2:DescribeVolumes",
        "ec2:DescribeTags",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams",
        "logs:DescribeLogGroups",
        "logs:CreateLogStream",
        "logs:CreateLogGroup"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter"
      ],
      "Resource": "arn:aws:ssm:*:*:parameter/AmazonCloudWatch-*"
    }
  ]
}
```

**Attach IAM role to EC2 instance:**
1. Go to EC2 Console
2. Select your instance
3. Actions → Security → Modify IAM role
4. Attach the CloudWatch role

---

## 📝 Step 3: Configure CloudWatch Agent

**Create configuration file:**

```bash
sudo nano /opt/aws/amazon-cloudwatch-agent/etc/config.json
```

**Add this configuration:**

```json
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/home/ubuntu/content-factory/logs/app.log",
            "log_group_name": "/content-factory/app",
            "log_stream_name": "{instance_id}/app.log",
            "retention_in_days": 7
          },
          {
            "file_path": "/home/ubuntu/content-factory/logs/error.log",
            "log_group_name": "/content-factory/errors",
            "log_stream_name": "{instance_id}/error.log",
            "retention_in_days": 30
          },
          {
            "file_path": "/var/log/nginx/access.log",
            "log_group_name": "/content-factory/nginx-access",
            "log_stream_name": "{instance_id}/access.log",
            "retention_in_days": 7
          },
          {
            "file_path": "/var/log/nginx/error.log",
            "log_group_name": "/content-factory/nginx-error",
            "log_stream_name": "{instance_id}/error.log",
            "retention_in_days": 30
          }
        ]
      }
    }
  },
  "metrics": {
    "namespace": "ContentFactory",
    "metrics_collected": {
      "cpu": {
        "measurement": [
          {
            "name": "cpu_usage_idle",
            "rename": "CPU_IDLE",
            "unit": "Percent"
          },
          {
            "name": "cpu_usage_iowait",
            "rename": "CPU_IOWAIT",
            "unit": "Percent"
          },
          "cpu_time_guest"
        ],
        "metrics_collection_interval": 60,
        "totalcpu": false
      },
      "disk": {
        "measurement": [
          {
            "name": "used_percent",
            "rename": "DISK_USED",
            "unit": "Percent"
          },
          "disk_free",
          "disk_used"
        ],
        "metrics_collection_interval": 60,
        "resources": [
          "*"
        ]
      },
      "diskio": {
        "measurement": [
          "io_time"
        ],
        "metrics_collection_interval": 60,
        "resources": [
          "*"
        ]
      },
      "mem": {
        "measurement": [
          {
            "name": "mem_used_percent",
            "rename": "MEMORY_USED",
            "unit": "Percent"
          },
          "mem_available",
          "mem_used"
        ],
        "metrics_collection_interval": 60
      },
      "netstat": {
        "measurement": [
          "tcp_established",
          "tcp_time_wait"
        ],
        "metrics_collection_interval": 60
      },
      "swap": {
        "measurement": [
          {
            "name": "swap_used_percent",
            "rename": "SWAP_USED",
            "unit": "Percent"
          }
        ],
        "metrics_collection_interval": 60
      }
    }
  }
}
```

**Start CloudWatch agent:**

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/config.json
```

---

## 📊 Step 4: Add Custom Application Metrics

**Update your application to send custom metrics:**

Create `app/utils/cloudwatch_metrics.py`:

```python
"""
CloudWatch metrics utility for Content Factory
"""
import boto3
import logging
from datetime import datetime
from typing import Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class CloudWatchMetrics:
    """Send custom metrics to CloudWatch"""
    
    def __init__(self, namespace: str = "ContentFactory"):
        self.namespace = namespace
        try:
            self.cloudwatch = boto3.client('cloudwatch', region_name='eu-west-3')
            self.enabled = True
        except Exception as e:
            logger.warning(f"CloudWatch not available: {e}")
            self.enabled = False
    
    def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = 'Count',
        dimensions: Optional[list] = None
    ):
        """
        Send a metric to CloudWatch
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit (Count, Seconds, Percent, etc.)
            dimensions: List of dimension dicts
        """
        if not self.enabled:
            return
        
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
            
        except ClientError as e:
            logger.error(f"Failed to send metric {metric_name}: {e}")
    
    def track_api_request(self, endpoint: str, status_code: int, response_time: float):
        """Track API request metrics"""
        self.put_metric('APIRequests', 1, 'Count', [
            {'Name': 'Endpoint', 'Value': endpoint},
            {'Name': 'StatusCode', 'Value': str(status_code)}
        ])
        
        self.put_metric('APIResponseTime', response_time, 'Milliseconds', [
            {'Name': 'Endpoint', 'Value': endpoint}
        ])
    
    def track_error(self, error_type: str, error_message: str):
        """Track application errors"""
        self.put_metric('Errors', 1, 'Count', [
            {'Name': 'ErrorType', 'Value': error_type}
        ])
    
    def track_video_upload(self, platform: str, success: bool, duration: float):
        """Track video upload metrics"""
        status = 'Success' if success else 'Failed'
        
        self.put_metric('VideoUploads', 1, 'Count', [
            {'Name': 'Platform', 'Value': platform},
            {'Name': 'Status', 'Value': status}
        ])
        
        if success:
            self.put_metric('VideoUploadDuration', duration, 'Seconds', [
                {'Name': 'Platform', 'Value': platform}
            ])
    
    def track_youtube_oauth_status(self, is_authenticated: bool):
        """Track YouTube OAuth status"""
        value = 1 if is_authenticated else 0
        self.put_metric('YouTubeOAuthStatus', value, 'Count')
    
    def track_database_connection(self, is_connected: bool, response_time: float):
        """Track database health"""
        value = 1 if is_connected else 0
        self.put_metric('DatabaseConnected', value, 'Count')
        
        if is_connected:
            self.put_metric('DatabaseResponseTime', response_time, 'Milliseconds')


# Global instance
cloudwatch_metrics = CloudWatchMetrics()
```

**Integrate metrics into your application:**

Update `app/main.py`:

```python
from app.utils.cloudwatch_metrics import cloudwatch_metrics
import time

@app.middleware("http")
async def monitoring_middleware(request, call_next):
    from app.services.monitoring import monitoring_service
    
    # Record start time
    start_time = time.time()
    monitoring_service.increment_request_count()
    
    try:
        response = await call_next(request)
        
        # Calculate response time
        response_time = (time.time() - start_time) * 1000  # ms
        monitoring_service.update_response_time(response_time / 1000)
        
        # Send to CloudWatch
        cloudwatch_metrics.track_api_request(
            endpoint=request.url.path,
            status_code=response.status_code,
            response_time=response_time
        )
        
        return response
        
    except Exception as e:
        monitoring_service.increment_error_count()
        
        # Track error in CloudWatch
        cloudwatch_metrics.track_error(
            error_type=type(e).__name__,
            error_message=str(e)
        )
        
        raise
```

---

## 🔔 Step 5: Create CloudWatch Alarms

**Using AWS CLI:**

```bash
# High CPU usage alarm
aws cloudwatch put-metric-alarm \
  --alarm-name content-factory-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=InstanceId,Value=<your-instance-id>

# High memory usage alarm
aws cloudwatch put-metric-alarm \
  --alarm-name content-factory-high-memory \
  --alarm-description "Alert when memory exceeds 85%" \
  --metric-name MEMORY_USED \
  --namespace ContentFactory \
  --statistic Average \
  --period 300 \
  --threshold 85 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2

# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name content-factory-high-errors \
  --alarm-description "Alert when errors exceed 10 per 5 minutes" \
  --metric-name Errors \
  --namespace ContentFactory \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1

# Application health alarm
aws cloudwatch put-metric-alarm \
  --alarm-name content-factory-health-check-failed \
  --alarm-description "Alert when health check fails" \
  --metric-name DatabaseConnected \
  --namespace ContentFactory \
  --statistic Average \
  --period 60 \
  --threshold 1 \
  --comparison-operator LessThanThreshold \
  --evaluation-periods 2

# Disk space alarm
aws cloudwatch put-metric-alarm \
  --alarm-name content-factory-low-disk-space \
  --alarm-description "Alert when disk usage exceeds 85%" \
  --metric-name DISK_USED \
  --namespace ContentFactory \
  --statistic Average \
  --period 300 \
  --threshold 85 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

---

## 📧 Step 6: Set Up SNS for Alarm Notifications

**Create SNS topic:**

```bash
aws sns create-topic --name content-factory-alerts
```

**Subscribe your email:**

```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:eu-west-3:YOUR_ACCOUNT_ID:content-factory-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com
```

**Confirm subscription** via email.

**Update alarms to use SNS:**

```bash
# Example: Update CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name content-factory-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=InstanceId,Value=<your-instance-id> \
  --alarm-actions arn:aws:sns:eu-west-3:YOUR_ACCOUNT_ID:content-factory-alerts
```

---

## 📊 Step 7: Create CloudWatch Dashboard

**Create dashboard JSON:**

Save as `cloudwatch-dashboard.json`:

```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/EC2", "CPUUtilization", {"stat": "Average"}],
          ["ContentFactory", "MEMORY_USED", {"stat": "Average"}],
          [".", "DISK_USED", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "eu-west-3",
        "title": "System Resources",
        "yAxis": {
          "left": {
            "min": 0,
            "max": 100
          }
        }
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["ContentFactory", "APIRequests", {"stat": "Sum"}],
          [".", "Errors", {"stat": "Sum"}]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "eu-west-3",
        "title": "API Metrics"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["ContentFactory", "APIResponseTime", {"stat": "Average"}],
          [".", "DatabaseResponseTime", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "eu-west-3",
        "title": "Response Times (ms)",
        "yAxis": {
          "left": {
            "min": 0
          }
        }
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["ContentFactory", "VideoUploads", {"stat": "Sum"}]
        ],
        "period": 3600,
        "stat": "Sum",
        "region": "eu-west-3",
        "title": "Video Uploads (Last Hour)"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["ContentFactory", "YouTubeOAuthStatus", {"stat": "Average"}],
          [".", "DatabaseConnected", {"stat": "Average"}]
        ],
        "period": 300,
        "stat": "Average",
        "region": "eu-west-3",
        "title": "Service Health (1=healthy, 0=unhealthy)"
      }
    },
    {
      "type": "log",
      "properties": {
        "query": "SOURCE '/content-factory/errors'\n| fields @timestamp, @message\n| sort @timestamp desc\n| limit 20",
        "region": "eu-west-3",
        "title": "Recent Errors"
      }
    }
  ]
}
```

**Create dashboard:**

```bash
aws cloudwatch put-dashboard \
  --dashboard-name ContentFactory \
  --dashboard-body file://cloudwatch-dashboard.json
```

**Access dashboard:**
Go to: https://console.aws.amazon.com/cloudwatch/home?region=eu-west-3#dashboards:name=ContentFactory

---

## 🔍 Step 8: Set Up Log Insights Queries

**Useful CloudWatch Insights queries:**

### Find Errors
```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 50
```

### API Performance
```
fields @timestamp, endpoint, response_time
| filter endpoint like /api/
| stats avg(response_time), max(response_time), count() by endpoint
```

### Failed Video Uploads
```
fields @timestamp, platform, error
| filter status = "failed"
| sort @timestamp desc
```

### Top API Endpoints
```
fields endpoint
| stats count() as requests by endpoint
| sort requests desc
```

---

## 📈 Step 9: Monitor Docker Containers

**Install Container Insights (optional):**

```bash
# Deploy CloudWatch agent with container insights
curl https://raw.githubusercontent.com/aws-samples/amazon-cloudwatch-container-insights/latest/k8s-deployment-manifest-templates/deployment-mode/daemonset/container-insights-monitoring/quickstart/cwagent-fluentd-quickstart.yaml | sed "s/{{cluster_name}}/content-factory/;s/{{region_name}}/eu-west-3/" | kubectl apply -f -
```

**Or monitor with Docker stats:**

Create monitoring script `monitor-containers.sh`:

```bash
#!/bin/bash
# Monitor Docker containers and send to CloudWatch

while true; do
  # Get container stats
  docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemPerc}}" | while IFS=',' read name cpu mem; do
    # Remove % sign
    cpu=${cpu%%%}
    mem=${mem%%%}
    
    # Send to CloudWatch
    aws cloudwatch put-metric-data \
      --namespace ContentFactory/Docker \
      --metric-name CPUUsage \
      --value "$cpu" \
      --dimensions Container="$name"
    
    aws cloudwatch put-metric-data \
      --namespace ContentFactory/Docker \
      --metric-name MemoryUsage \
      --value "$mem" \
      --dimensions Container="$name"
  done
  
  sleep 60
done
```

Run as a service or in background.

---

## ✅ Verification Checklist

- [ ] CloudWatch agent running
- [ ] Metrics appearing in CloudWatch
- [ ] Logs streaming to CloudWatch Logs
- [ ] Alarms configured
- [ ] SNS notifications working
- [ ] Dashboard displaying data
- [ ] Custom application metrics working

---

## 🚨 Common Monitoring Scenarios

### High CPU Alert
**Action:** Scale up instance or optimize code

### High Memory Usage
**Action:** Check for memory leaks, restart services

### Disk Space Low
**Action:** Clean up old logs, increase EBS volume

### High Error Rate
**Action:** Check error logs, investigate recent deployments

### Database Connection Failed
**Action:** Verify Supabase credentials, check network

---

## 📞 View Metrics and Logs

**CloudWatch Console:**
- Metrics: https://console.aws.amazon.com/cloudwatch/home?region=eu-west-3#metricsV2:
- Logs: https://console.aws.amazon.com/cloudwatch/home?region=eu-west-3#logsV2:log-groups
- Alarms: https://console.aws.amazon.com/cloudwatch/home?region=eu-west-3#alarmsV2:

**AWS CLI:**

```bash
# List metrics
aws cloudwatch list-metrics --namespace ContentFactory

# Get metric statistics
aws cloudwatch get-metric-statistics \
  --namespace ContentFactory \
  --metric-name APIRequests \
  --start-time 2025-10-20T00:00:00Z \
  --end-time 2025-10-21T00:00:00Z \
  --period 3600 \
  --statistics Sum

# View recent logs
aws logs tail /content-factory/app --follow
```

---

## 💰 Cost Optimization

**CloudWatch costs:**
- Metrics: $0.30 per metric per month (first 10k metrics free)
- Logs: $0.50 per GB ingested, $0.03 per GB stored
- Alarms: $0.10 per alarm per month (first 10 alarms free)
- Dashboard: $3 per dashboard per month (first 3 free)

**Tips to reduce costs:**
- Increase metrics collection interval
- Reduce log retention period
- Use metric filters instead of storing all logs
- Archive old logs to S3

---

## ✅ Success!

Your Content Factory now has comprehensive CloudWatch monitoring! 📊

**Next:** Configure auto-scaling to automatically handle traffic spikes.
