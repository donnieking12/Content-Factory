# Celery Worker Setup and Configuration Guide

## Overview

This guide explains how to set up and configure Celery workers for background task processing in the content factory.

## Prerequisites

1. Redis server installed and running
2. Python dependencies installed (included in requirements.txt)
3. Environment variables configured

## Redis Setup

### Installing Redis

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

#### On macOS (using Homebrew):
```bash
brew install redis
brew services start redis
```

#### On Windows:
Download Redis from https://github.com/microsoftarchive/redis/releases

### Verifying Redis Installation

```bash
redis-cli ping
```

Should return "PONG" if Redis is running correctly.

## Environment Configuration

Ensure your [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env) file has the correct Redis URL:
```env
REDIS_URL=redis://localhost:6379/0
```

## Starting Celery Workers

### 1. Start the Main Worker

```bash
celery -A celery_worker.celery_app worker --loglevel=info
```

### 2. Start the Beat Scheduler (for periodic tasks)

```bash
celery -A celery_worker.celery_app beat --loglevel=info
```

### 3. Start with Docker (Recommended)

Using the provided docker-compose.yml:
```bash
docker-compose up -d worker beat
```

## Worker Configuration

The Celery workers are configured with task routing:

- `main-queue`: For general tasks like product discovery and content creation
- `video-queue`: For video generation tasks
- `publish-queue`: For social media publishing tasks

## Available Tasks

### 1. discover_products_task
Discovers trending products from e-commerce APIs

### 2. generate_video_task(product_id)
Generates a video for a specific product

### 3. publish_video_task(video_id, platforms)
Publishes a video to specified social media platforms

### 4. execute_full_workflow_task
Executes the complete content workflow

### 5. create_content_for_product_task(product_id)
Creates content for a specific product

### 6. scheduled_trend_discovery_task
Periodic task for trend discovery

## Monitoring Workers

### Using Flower (Optional)

Flower is a web-based tool for monitoring and administrating Celery clusters.

1. Install Flower:
```bash
pip install flower
```

2. Start Flower:
```bash
celery -A celery_worker.celery_app flower
```

3. Access the dashboard at http://localhost:5555

### Using Celery Commands

Check active workers:
```bash
celery -A celery_worker.celery_app inspect active
```

Check registered tasks:
```bash
celery -A celery_worker.celery_app inspect registered
```

Check worker statistics:
```bash
celery -A celery_worker.celery_app inspect stats
```

## Scaling Workers

### Increasing Concurrency

Start a worker with multiple processes:
```bash
celery -A celery_worker.celery_app worker --loglevel=info --concurrency=4
```

### Starting Multiple Workers

Start workers for specific queues:
```bash
# Worker for main tasks
celery -A celery_worker.celery_app worker --loglevel=info -Q main-queue

# Worker for video generation
celery -A celery_worker.celery_app worker --loglevel=info -Q video-queue

# Worker for publishing
celery -A celery_worker.celery_app worker --loglevel=info -Q publish-queue
```

## Task Scheduling

### Periodic Tasks Configuration

Periodic tasks are configured in the Celery Beat scheduler. The default configuration includes:

- `scheduled_trend_discovery_task`: Runs every hour to discover new trending products

To customize the schedule, modify the Celery configuration in [celery_worker.py](file:///c%3A/Users/Mimi/content-factory-ai/celery_worker.py).

### Adding New Periodic Tasks

1. Create a new task function in [celery_worker.py](file:///c%3A/Users/Mimi/content-factory-ai/celery_worker.py)
2. Add it to the Celery Beat schedule
3. Restart the Beat scheduler

## Error Handling and Retries

The Celery workers include error handling for:

- Database connection issues
- API call failures
- Network problems
- Invalid data

Tasks will automatically retry on failure according to Celery's retry policy.

## Logging

Workers log to stdout by default. For production deployments, configure logging to write to files:

```bash
celery -A celery_worker.celery_app worker --loglevel=info --logfile=/var/log/celery/worker.log
```

## Troubleshooting

### Common Issues

1. **Redis Connection Errors**: Check that Redis is running and the URL is correct
2. **Import Errors**: Ensure all dependencies are installed
3. **Database Connection Errors**: Verify database credentials
4. **Task Not Executing**: Check that workers are running and listening to the correct queues

### Debugging Tasks

1. Start a worker with debug logging:
```bash
celery -A celery_worker.celery_app worker --loglevel=debug
```

2. Use the Celery shell for testing:
```bash
celery -A celery_worker.celery_app shell
```

### Checking Task Results

```python
from celery_worker import discover_products_task
result = discover_products_task.delay()
print(result.get())  # This will block until the task is complete
```

## Performance Optimization

1. **Use appropriate queue routing** to distribute load
2. **Configure concurrency** based on your system resources
3. **Monitor memory usage** to prevent leaks
4. **Use result backend** (Redis) to store task results
5. **Implement proper error handling** to prevent task loss

## Security Considerations

1. **Secure Redis**: Use password authentication and bind to localhost
2. **Protect API keys**: Store in environment variables, not in code
3. **Validate input**: Sanitize all data before processing
4. **Limit worker permissions**: Run workers with minimal required privileges