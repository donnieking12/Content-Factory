# E-commerce Integration Guide

## Overview

This guide explains how to integrate real e-commerce APIs with the content factory for product discovery.

## Supported E-commerce APIs

Currently, the system uses FakeStoreAPI as a demonstration. You can easily extend it to support other e-commerce platforms:

### 1. Amazon Product Advertising API
- Requires AWS account
- Provides extensive product data
- Rate limits apply

### 2. eBay Finding API
- Free tier available
- Good for product discovery
- Requires eBay developer account

### 3. Walmart Open API
- Free tier available
- Product search and lookup
- Requires Walmart developer account

### 4. Best Buy API
- Free tier available
- Electronics products
- Requires Best Buy developer account

## Setting up FakeStoreAPI (Default)

FakeStoreAPI is already configured and works out of the box:
- No authentication required
- Free to use
- Provides sample product data

## Adding a New E-commerce API

To add a new e-commerce API:

1. Update the [app/services/product_discovery.py](file:///c%3A/Users/Mimi/content-factory-ai/app/services/product_discovery.py) file
2. Add your API key to [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env) and [.env.example](file:///c%3A/Users/Mimi/content-factory-ai/.env.example)
3. Add the setting to [app/core/config.py](file:///c%3A/Users/Mimi/content-factory-ai/app/core/config.py)

### Example: Adding eBay API

1. Add to config.py:
```python
EBAY_API_KEY: str = ""
```

2. Add to .env files:
```env
EBAY_API_KEY=your_ebay_api_key_here
```

3. Update the discovery function in product_discovery.py:
```python
# Add eBay API call
ebay_response = await client.get(
    "https://svcs.ebay.com/services/search/FindingService/v1",
    params={
        "OPERATION-NAME": "findItemsByKeywords",
        "SERVICE-VERSION": "1.0.0",
        "SECURITY-APPNAME": settings.EBAY_API_KEY,
        "RESPONSE-DATA-FORMAT": "JSON",
        "keywords": "trending"
    }
)
ebay_response.raise_for_status()
ebay_data = ebay_response.json()
# Process eBay data...
```

## Product Data Structure

All e-commerce APIs should return products in this format:
```json
{
  "name": "Product Name",
  "description": "Product description",
  "price": "$99.99",
  "url": "https://example.com/product/123",
  "image_url": "https://example.com/images/product.jpg",
  "is_trending": true
}
```

## Rate Limiting and Error Handling

The system includes error handling for:
- Network issues
- API rate limits
- Invalid responses
- Authentication failures

## Testing

To test your e-commerce integration:
1. Update your API keys in [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env)
2. Run the product discovery endpoint:
   ```bash
   curl -X POST http://localhost:8000/api/v1/products/discover-trending
   ```
3. Check the database for imported products

## Troubleshooting

Common issues:
1. **Authentication errors**: Check your API keys
2. **Rate limiting**: Implement exponential backoff
3. **Network errors**: Check your internet connection
4. **Data format issues**: Ensure your API returns data in the expected format