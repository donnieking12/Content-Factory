# YouTube OAuth Integration Guide

## Overview

The Content Factory now supports YouTube video uploads using OAuth2 authentication. This integration allows you to upload videos directly to your YouTube channel with proper authentication.

## Setup Complete ✅

The following components have been configured:

1. **Google OAuth Client Credentials** - Configured and saved
2. **YouTube OAuth Service** - Implemented in `app/services/youtube_oauth.py`
3. **API Endpoints** - Added to `app/api/routes/social_media.py`
4. **Required Dependencies** - Google API packages installed

## Configuration

### Environment Variables (`.env`)

The following YouTube OAuth settings have been added:

```env
# YouTube OAuth settings
YOUTUBE_CLIENT_ID=your_youtube_client_id_here
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret_here
YOUTUBE_CLIENT_SECRET_FILE=google_client_secret.json
```

### Google Client Secret File

Location: `google_client_secret.json`

This file contains your Google OAuth credentials and is automatically loaded by the YouTube service.

## How to Use

### Step 1: Check Authentication Status

```bash
curl http://localhost:8000/api/v1/social-media/youtube/auth-status
```

Response if not authenticated:
```json
{
  "authenticated": false,
  "message": "Not authenticated with YouTube"
}
```

### Step 2: Initiate Authentication

```bash
curl http://localhost:8000/api/v1/social-media/youtube/auth
```

Response:
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?...",
  "message": "Please visit the auth_url to authenticate with YouTube"
}
```

**Important:** Copy the `auth_url` and open it in your browser to authenticate.

### Step 3: Authenticate with Google

1. Visit the authorization URL from Step 2
2. Log in with your Google account
3. Grant permissions to the application
4. You'll be redirected to: `http://localhost:8000/api/v1/social-media/youtube/oauth2callback?code=...`
5. The callback will automatically complete the authentication

### Step 4: Verify Authentication

After authentication, check status again:

```bash
curl http://localhost:8000/api/v1/social-media/youtube/auth-status
```

Response when authenticated:
```json
{
  "authenticated": true,
  "channel": {
    "success": true,
    "channel_id": "UC...",
    "title": "Your Channel Name",
    "description": "Channel description",
    "subscriber_count": "1234",
    "video_count": "56",
    "view_count": "78900"
  }
}
```

### Step 5: Upload Videos

Once authenticated, you can upload videos:

```bash
curl -X POST http://localhost:8000/api/v1/social-media/youtube/upload \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/path/to/video.mp4",
    "title": "Amazing Product Review",
    "description": "Check out this amazing product! #viral #trending",
    "category_id": "22",
    "privacy_status": "public",
    "tags": ["product", "review", "viral"]
  }'
```

Response:
```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "message": "Video uploaded successfully to YouTube"
}
```

## API Endpoints

### Authentication Endpoints

#### `GET /api/v1/social-media/youtube/auth-status`
Check if user is authenticated with YouTube and get channel information.

**Response:**
- `authenticated`: Boolean indicating auth status
- `channel`: Channel information (if authenticated)

#### `GET /api/v1/social-media/youtube/auth`
Initiate OAuth2 authentication flow.

**Response:**
- `auth_url`: URL for user to visit for authentication
- `message`: Instructions

#### `GET /api/v1/social-media/youtube/oauth2callback`
OAuth2 callback endpoint (automatically handled by browser redirect).

**Parameters:**
- `code`: Authorization code from Google
- `error`: Error message if authentication failed

### Upload Endpoint

#### `POST /api/v1/social-media/youtube/upload`
Upload a video to YouTube.

**Request Body:**
```json
{
  "video_path": "string (required)",
  "title": "string (required)",
  "description": "string (required)",
  "category_id": "string (default: '22' - People & Blogs)",
  "privacy_status": "string (default: 'public')",
  "tags": ["array of strings (optional)"]
}
```

**Response:**
```json
{
  "success": true,
  "video_id": "string",
  "video_url": "string",
  "message": "string"
}
```

## YouTube Video Categories

Common category IDs:
- `1` - Film & Animation
- `2` - Autos & Vehicles
- `10` - Music
- `15` - Pets & Animals
- `17` - Sports
- `19` - Travel & Events
- `20` - Gaming
- `22` - People & Blogs (default)
- `23` - Comedy
- `24` - Entertainment
- `25` - News & Politics
- `26` - Howto & Style
- `27` - Education
- `28` - Science & Technology

## Privacy Settings

Supported privacy statuses:
- `public` - Anyone can view
- `unlisted` - Anyone with the link can view
- `private` - Only you can view

## Authentication Token Storage

The OAuth token is automatically saved to `youtube_token.pickle` after successful authentication. This token:

- ✅ Persists across application restarts
- ✅ Automatically refreshes when expired
- ✅ Stored securely in the project directory

**Note:** Keep `youtube_token.pickle` secure and do not commit it to version control.

## Integration with Content Workflow

### Automated Publishing

The YouTube OAuth service integrates with the existing social media publisher:

```python
from app.services.youtube_oauth import youtube_oauth_service

# Check authentication
if youtube_oauth_service.is_authenticated():
    # Upload video
    result = youtube_oauth_service.upload_video(
        video_path="generated_video.mp4",
        title="Product Video Title",
        description="Product description with hashtags",
        tags=["product", "trending"]
    )
```

### Using with Video Generation Workflow

```bash
# 1. Generate video for product
curl -X POST http://localhost:8000/api/v1/videos/generate-for-product/1

# 2. Upload to YouTube
curl -X POST http://localhost:8000/api/v1/social-media/youtube/upload \
  -H "Content-Type: application/json" \
  -d '{
    "video_path": "/path/to/generated/video.mp4",
    "title": "Product Name - Review",
    "description": "Check out this amazing product!",
    "tags": ["product", "review"]
  }'
```

## Troubleshooting

### Error: "Not authenticated with YouTube"

**Solution:** Follow the authentication flow (Steps 1-3 above)

### Error: "Client secret file not found"

**Solution:** Ensure `google_client_secret.json` exists in the project root directory.

### Error: "Token has expired"

**Solution:** The service automatically refreshes expired tokens. If this fails, re-authenticate using the auth flow.

### Error: "Upload failed"

**Possible Causes:**
1. Video file doesn't exist at specified path
2. Video format not supported by YouTube
3. Network connectivity issues
4. YouTube API quota exceeded

**Solution:** Check the error details in the response and application logs.

## Quota Limits

YouTube Data API v3 has quota limits:
- **Daily quota:** 10,000 units
- **Video upload cost:** 1,600 units per upload
- **Daily upload limit:** ~6 videos (may vary)

Monitor your quota usage in the [Google Cloud Console](https://console.cloud.google.com/).

## Security Best Practices

1. ✅ **Never commit credentials** - `.gitignore` includes token files
2. ✅ **Use environment variables** - Credentials stored in `.env`
3. ✅ **Secure token storage** - Tokens encrypted and stored locally
4. ✅ **OAuth2 flow** - No password storage required
5. ✅ **Automatic token refresh** - No manual intervention needed

## Testing the Integration

### Quick Test Script

Create `test_youtube_upload.py`:

```python
import asyncio
from app.services.youtube_oauth import youtube_oauth_service

async def test_youtube():
    # Check auth status
    if not youtube_oauth_service.is_authenticated():
        print("Not authenticated. Please authenticate first.")
        auth_url = youtube_oauth_service.get_auth_url()
        print(f"Visit: {auth_url}")
        return
    
    # Get channel info
    channel_info = youtube_oauth_service.get_channel_info()
    print(f"Channel: {channel_info}")
    
    # Upload a test video
    result = youtube_oauth_service.upload_video(
        video_path="test_video.mp4",
        title="Test Upload",
        description="Test description",
        privacy_status="private"  # Use private for testing
    )
    print(f"Upload result: {result}")

if __name__ == "__main__":
    asyncio.run(test_youtube())
```

Run:
```bash
python test_youtube_upload.py
```

## Interactive API Documentation

View and test all endpoints at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Navigate to the "social-media" section to see YouTube endpoints.

## Next Steps

1. ✅ **Authenticate** - Complete the OAuth flow
2. ✅ **Test upload** - Try uploading a sample video
3. ✅ **Integrate with workflow** - Connect to automated content pipeline
4. ✅ **Monitor usage** - Track API quota in Google Cloud Console
5. ✅ **Scale up** - Request quota increase if needed

## Support

- **YouTube Data API Documentation:** https://developers.google.com/youtube/v3
- **Google OAuth2 Guide:** https://developers.google.com/identity/protocols/oauth2
- **API Reference:** http://localhost:8000/docs

---

**Status:** ✅ YouTube OAuth integration is fully configured and ready to use!
