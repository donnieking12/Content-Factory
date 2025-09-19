# Error Handling and Logging Guide

## Overview

This guide explains the error handling and logging implementation in the content factory application.

## Logging Configuration

The application uses Python's built-in logging module with a custom configuration.

### Log Levels

- **DEBUG**: Detailed information, typically of interest only when diagnosing problems
- **INFO**: Confirmation that things are working as expected
- **WARNING**: An indication that something unexpected happened
- **ERROR**: Due to a more serious problem, the software has not been able to perform some function
- **CRITICAL**: A serious error, indicating that the program itself may be unable to continue running

### Log Handlers

1. **Console Handler**: Outputs logs to stdout
2. **File Handler**: Writes logs to `logs/app.log`
3. **Error File Handler**: Writes error-level logs to `logs/error.log`

### Log Rotation

Log files are automatically rotated when they reach 10MB, with up to 5 backup files kept.

## Error Handling Strategy

### Database Operations

All database operations include proper error handling:

```python
try:
    # Database operation
    db.commit()
except Exception as e:
    db.rollback()
    logger.error(f"Error message: {e}", exc_info=True)
    raise  # Re-raise the exception if needed
```

### API Calls

External API calls include error handling for network issues and HTTP errors:

```python
try:
    response = await client.get("https://api.example.com")
    response.raise_for_status()
except httpx.HTTPError as e:
    logger.error(f"HTTP error: {e}", exc_info=True)
except Exception as e:
    logger.error(f"General error: {e}", exc_info=True)
```

### Async Operations

Async operations are wrapped in try/except blocks:

```python
try:
    result = asyncio.run(async_function())
except Exception as e:
    logger.error(f"Async operation failed: {e}", exc_info=True)
```

## Custom Exception Classes

For better error categorization, consider creating custom exception classes:

```python
class ProductDiscoveryError(Exception):
    """Exception raised for errors in product discovery."""
    pass

class VideoGenerationError(Exception):
    """Exception raised for errors in video generation."""
    pass

class SocialMediaPublishingError(Exception):
    """Exception raised for errors in social media publishing."""
    pass
```

## Error Response Format

API endpoints return consistent error responses:

```json
{
    "status": "error",
    "message": "Descriptive error message",
    "error_code": "OPTIONAL_ERROR_CODE"
}
```

## Monitoring Error Patterns

The logging system helps identify common error patterns:

1. **Rate limiting errors** from external APIs
2. **Database connection issues**
3. **Invalid data errors**
4. **Network timeouts**

## Best Practices

### 1. Log Context Information

Include relevant context in log messages:

```python
logger.info(f"Processing product {product_id} for user {user_id}")
```

### 2. Use Structured Logging

For complex applications, consider structured logging:

```python
logger.info("Product processed", extra={
    "product_id": product_id,
    "user_id": user_id,
    "processing_time": processing_time
})
```

### 3. Don't Log Sensitive Information

Never log passwords, API keys, or personal information:

```python
# DON'T DO THIS
logger.info(f"User {username} logged in with password {password}")

# DO THIS INSTEAD
logger.info(f"User {username} logged in successfully")
```

### 4. Use Appropriate Log Levels

- Use DEBUG for detailed diagnostic information
- Use INFO for general operational messages
- Use WARNING for handled errors
- Use ERROR for unhandled errors
- Use CRITICAL for system-level failures

## Error Handling in Different Components

### 1. Services Layer

Services should handle their own errors and log appropriately:

```python
def create_product(db: Session, product: ProductCreate) -> Product:
    try:
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        logger.info(f"Created new product with ID {db_product.id}")
        return db_product
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating product: {e}", exc_info=True)
        raise
```

### 2. API Routes

API routes should catch exceptions and return appropriate HTTP responses:

```python
@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_new_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        db_product = create_product(db=db, product=product)
        return db_product
    except Exception as e:
        logger.error(f"Failed to create product: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create product")
```

### 3. Background Tasks

Celery tasks should handle errors gracefully:

```python
@celery_app.task
def discover_products_task():
    try:
        # Task implementation
        logger.info("Product discovery task completed successfully")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Product discovery task failed: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
```

## Testing Error Handling

### 1. Unit Tests

Test error conditions in unit tests:

```python
def test_create_product_database_error(self, mock_db):
    mock_db.commit.side_effect = Exception("Database error")
    with pytest.raises(Exception):
        create_product(mock_db, product_data)
```

### 2. Integration Tests

Test end-to-end error scenarios:

```python
def test_api_error_response(self):
    response = client.post("/products/", json=invalid_product_data)
    assert response.status_code == 422
```

## Log Analysis

Regularly analyze logs to:

1. Identify recurring errors
2. Monitor system performance
3. Detect security issues
4. Track feature usage

### Common Log Analysis Patterns

1. **Error frequency**: Count errors by type
2. **Response times**: Track API response times
3. **Resource usage**: Monitor memory and CPU usage
4. **User behavior**: Analyze feature usage patterns

## Security Considerations

1. **Log Sanitization**: Remove sensitive data from logs
2. **Access Control**: Restrict access to log files
3. **Log Retention**: Implement appropriate log retention policies
4. **Audit Trails**: Maintain audit trails for security-relevant events

## Performance Considerations

1. **Asynchronous Logging**: Use async logging for high-throughput applications
2. **Log Sampling**: Sample logs in high-volume scenarios
3. **Efficient Formatting**: Use efficient log formatting
4. **External Logging Services**: Consider external logging services for production

## Troubleshooting

### Common Issues

1. **Missing Logs**: Check log level configuration
2. **Large Log Files**: Verify log rotation settings
3. **Permission Errors**: Ensure proper file permissions
4. **Disk Space**: Monitor disk space for log storage

### Debugging Tips

1. Increase log level to DEBUG for detailed information
2. Use structured logging for easier parsing
3. Correlate logs across services using request IDs
4. Use log aggregation tools for distributed systems