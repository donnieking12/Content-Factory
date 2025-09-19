# Social Media Integration Guide

## Overview

This guide explains how to integrate real social media platforms for content publishing in the content factory.

## Supported Social Media Platforms

### 1. TikTok (Default Implementation)
- Large, engaged audience
- Short-form video focus
- Good for viral content

### 2. Instagram
- Visual platform with Stories and Reels
- Business account required for API access
- Good for lifestyle and product content

### 3. YouTube
- Long-form video platform
- Best for detailed product demos
- Largest video platform

### 4. Twitter (X)
- Real-time updates
- Good for engagement
- Character limit constraints

### 5. Facebook
- Largest social network
- Good for broad reach
- Multiple content formats

## Setting up TikTok Integration

1. Create a TikTok for Business account at https://www.tiktok.com/business/
2. Apply for API access through the developer portal
3. Get your API credentials
4. Add them to your [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env) file:
   ```env
   TIKTOK_CLIENT_KEY=your_tiktok_client_key
   TIKTOK_CLIENT_SECRET=your_tiktok_client_secret
   ```

## Setting up Instagram Integration

1. Create a Facebook Developer account at https://developers.facebook.com/
2. Create a new app and add the Instagram Basic Display product
3. Get your Instagram credentials
4. Create a Facebook Page (required for Instagram API)
5. Get your Page ID
6. Add credentials to your [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env) file:
   ```env
   INSTAGRAM_CLIENT_ID=your_instagram_client_id
   INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
   INSTAGRAM_PAGE_ID=your_instagram_page_id
   ```

## Setting up YouTube Integration

1. Create a Google Developer account at https://console.developers.google.com/
2. Create a new project and enable the YouTube Data API v3
3. Create credentials (API key or OAuth 2.0 client)
4. Add your API key to your [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env) file:
   ```env
   YOUTUBE_API_KEY=your_youtube_api_key
   ```

## Publishing Process

The publishing process for each platform includes:

1. **Authentication**: Obtain necessary access tokens
2. **Video Upload**: Upload the video file to the platform
3. **Metadata Setting**: Add title, description, tags, etc.
4. **Publish**: Make the content publicly available

## Rate Limiting and Error Handling

The system includes error handling for:
- API rate limits
- Network issues
- Invalid responses
- Authentication failures
- Content policy violations

## Testing

To test your social media integration:
1. Update your API keys in [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env)
2. Publish a video through the API:
   ```bash
   curl -X POST http://localhost:8000/api/v1/social-media/publish-video/1
   ```

## Content Optimization

Tips for successful social media publishing:

1. **TikTok**:
   - Keep videos under 60 seconds
   - Use trending sounds and hashtags
   - Focus on the first few seconds

2. **Instagram**:
   - Use high-quality visuals
   - Include relevant hashtags
   - Post consistently

3. **YouTube**:
   - Create engaging thumbnails
   - Write detailed descriptions
   - Use relevant tags

## Compliance and Best Practices

1. Follow each platform's terms of service
2. Respect rate limits and quotas
3. Monitor for content policy violations
4. Handle user comments and feedback
5. Track performance metrics

## Troubleshooting

Common issues:
1. **Authentication errors**: Check your API keys and tokens
2. **Rate limiting**: Implement exponential backoff
3. **Network errors**: Check your internet connection
4. **Content policy violations**: Review platform guidelines
5. **Upload failures**: Check file size and format requirements