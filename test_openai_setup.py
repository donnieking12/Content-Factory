"""
Quick test to verify OpenAI API key configuration
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings
from app.services.video_generation import call_ai_script_generation_api


async def test_openai_api():
    """Test the OpenAI API key configuration"""
    print("🤖 Testing OpenAI API Key Configuration...")
    print(f"API Key configured: {'✅ Yes' if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != 'your_openai_api_key_here' else '❌ No'}")
    
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
        print("❌ OpenAI API key is not properly configured!")
        return False
    
    # Test with a simple prompt
    test_prompt = """
    Create a short, engaging video script for a product called "Smart Water Bottle" 
    that tracks your daily water intake. Keep it under 100 words and make it exciting for social media.
    """
    
    try:
        print("🔄 Testing API call...")
        result = await call_ai_script_generation_api(test_prompt)
        
        if result.startswith("Error"):
            print(f"❌ API call failed: {result}")
            return False
        else:
            print("✅ API call successful!")
            print(f"📝 Generated script preview:\n{result[:200]}...")
            return True
            
    except Exception as e:
        print(f"❌ API test failed with exception: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_openai_api())
    if success:
        print("\n🎉 OpenAI API is properly configured and working!")
        print("Your AI Content Factory can now generate intelligent video scripts!")
    else:
        print("\n⚠️  Please check your OpenAI API key configuration.")