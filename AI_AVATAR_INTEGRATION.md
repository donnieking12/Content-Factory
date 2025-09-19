# AI Avatar Service Integration Guide

## Overview

This guide explains how to integrate real AI avatar services for video creation in the content factory.

## Supported AI Avatar Services

### 1. HeyGen (Default Implementation)
- Easy-to-use API
- Wide variety of avatars
- Good documentation
- Competitive pricing

### 2. Synthesia
- Industry leader in AI avatars
- Professional quality
- Enterprise features
- Higher cost

### 3. Elai.io
- Good balance of features and cost
- Multiple avatar options
- Custom avatar creation

### 4. DeepBrain
- Asian-focused avatars
- Good for specific markets
- Competitive pricing

## Setting up HeyGen (Default)

1. Create an account at https://www.heygen.com/
2. Get your API key from the dashboard
3. Add it to your [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env) file:
   ```env
   AI_AVATAR_API_URL=https://api.heygen.com
   AI_AVATAR_API_KEY=your_heygen_api_key_here
   ```

## Avatar Settings

The system supports various avatar settings:

```python
avatar_settings = {
    "title": "Product Demo Video",
    "description": "Demo of our latest product",
    "ratio": "16:9",  # or "1:1", "9:16"
    "avatar_id": "default_avatar",
    "voice_id": "default_voice",
    "background": "default_background"
}
```

## Adding a New AI Avatar Service

To add a new AI avatar service:

1. Update the API URL in [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env)
2. Add your API key to [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env)
3. Modify the functions in [app/services/ai_avatar.py](file:///c%3A/Users/Mimi/content-factory-ai/app/services/ai_avatar.py)

### Example: Adding Synthesia

1. Update .env:
```env
AI_AVATAR_API_URL=https://api.synthesia.io
AI_AVATAR_API_KEY=your_synthesia_api_key_here
```

2. Update the create_avatar_video function:
```python
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{settings.AI_AVATAR_API_URL}/v1/videos",
        json={
            "test": False,
            "input": [{
                "avatar": avatar_settings.get("avatar_id", "default_avatar"),
                "avatarSettings": {
                    "voice": avatar_settings.get("voice_id", "default_voice")
                },
                "script": script
            }],
            "output": {
                "format": "mp4",
                "resolution": "1080p"
            }
        },
        headers={
            "Authorization": f"Bearer {settings.AI_AVATAR_API_KEY}",
            "Content-Type": "application/json"
        }
    )
    # ... rest of implementation
```

## Video Generation Process

The video generation process includes:

1. **Video Creation Request**: Send script and avatar settings to the API
2. **Video ID Retrieval**: Get the video ID from the response
3. **Polling**: Continuously check the video status until completion
4. **Download URL**: Retrieve the final video download URL

## Rate Limiting and Error Handling

The system includes error handling for:
- API rate limits
- Network issues
- Invalid responses
- Authentication failures
- Video generation failures

## Testing

To test your AI avatar integration:
1. Update your API key in [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env)
2. Generate a video through the API:
   ```bash
   curl -X POST http://localhost:8000/api/v1/videos/generate-for-product/1
   ```

## Cost Management

AI avatar services can incur costs. Consider:
- Setting usage limits
- Using test mode during development
- Monitoring usage through provider dashboards
- Choosing appropriate video quality settings

## Troubleshooting

Common issues:
1. **Authentication errors**: Check your API keys
2. **Rate limiting**: Implement exponential backoff
3. **Network errors**: Check your internet connection
4. **Video generation failures**: Check script length and content
5. **Avatar/voice not found**: Verify avatar and voice IDs