# AI Services Integration Guide

## Overview

This guide explains how to integrate real AI services for video script generation and other AI-powered features in the content factory.

## Supported AI Services

### 1. OpenAI (GPT-3.5-turbo, GPT-4)
- Industry-leading language models
- Excellent for script generation
- Requires API key from OpenAI

### 2. Anthropic (Claude)
- Strong reasoning capabilities
- Good alternative to OpenAI
- Requires API key from Anthropic

### 3. Google AI (Gemini)
- Google's latest AI models
- Multimodal capabilities
- Requires API key from Google AI

## Setting up OpenAI (Default)

1. Get an API key from https://platform.openai.com/
2. Add it to your [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env) file:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Uncomment the production line in [app/services/video_generation.py](file:///c%3A/Users/Mimi/content-factory-ai/app/services/video_generation.py) to use the real AI service:
   ```python
   # In production, uncomment the line below to use the real AI service:
   import asyncio
   return asyncio.run(call_ai_script_generation_api(prompt))
   ```

## Adding a New AI Service

To add a new AI service:

1. Add your API key to [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env) and [.env.example](file:///c%3A/Users/Mimi/content-factory-ai/.env.example)
2. Add the setting to [app/core/config.py](file:///c%3A/Users/Mimi/content-factory-ai/app/core/config.py)
3. Create a new function in [app/services/video_generation.py](file:///c%3A/Users/Mimi/content-factory-ai/app/services/video_generation.py)

### Example: Adding Anthropic Claude

1. Add to config.py:
```python
ANTHROPIC_API_KEY: str = ""
```

2. Add to .env files:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

3. Add a new function in video_generation.py:
```python
async def call_anthropic_script_generation_api(prompt: str) -> str:
    """
    Call Anthropic's Claude API to generate a video script
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "content-type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"].strip()
    except Exception as e:
        print(f"Error calling Anthropic API: {e}")
        return "Error generating script. Please try again later."
```

## Script Generation Prompt Engineering

The system uses carefully crafted prompts to generate effective video scripts. The prompt includes:

1. Product details (name, description, price)
2. Script structure requirements
3. Engagement guidelines
4. Formatting instructions

You can customize the prompt in the [generate_video_script](file:///c%3A/Users/Mimi/content-factory-ai/app/services/video_generation.py#L16-L42) function.

## Rate Limiting and Error Handling

The system includes error handling for:
- API rate limits
- Network issues
- Invalid responses
- Authentication failures

## Testing

To test your AI integration:
1. Update your API key in [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env)
2. Uncomment the production line in [app/services/video_generation.py](file:///c%3A/Users/Mimi/content-factory-ai/app/services/video_generation.py)
3. Generate a video script through the API:
   ```bash
   curl -X POST http://localhost:8000/api/v1/videos/generate-for-product/1
   ```

## Cost Management

AI API usage can incur costs. Consider:
- Setting usage limits
- Caching generated scripts
- Using cheaper models for development
- Monitoring usage through provider dashboards

## Troubleshooting

Common issues:
1. **Authentication errors**: Check your API keys
2. **Rate limiting**: Implement exponential backoff
3. **Network errors**: Check your internet connection
4. **Content policy violations**: Review your prompts