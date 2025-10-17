#!/usr/bin/env python3
"""
Test that the complete setup is working
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all main modules can be imported"""
    print("Testing imports...")
    try:
        from app.main import app
        print("✅ Main app imports successfully")
        
        from app.core.config import settings
        print("✅ Config imports successfully")
        
        from app.models import product, video, social_media
        print("✅ Models import successfully")
        
        from app.services import product_discovery, video_generation
        print("✅ Services import successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test that configuration is properly set up"""
    print("\nTesting configuration...")
    try:
        from app.core.config import settings
        
        checks = {
            "OpenAI API Key": settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith('your_'),
            "Supabase URL": settings.SUPABASE_URL and not settings.SUPABASE_URL.startswith('your_'),
            "Supabase Key": settings.SUPABASE_KEY and not settings.SUPABASE_KEY.startswith('your_'),
        }
        
        for name, status in checks.items():
            if status:
                print(f"✅ {name}: Configured")
            else:
                print(f"⚠️  {name}: Not configured")
        
        return all(checks.values())
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_supabase_connection():
    """Test Supabase connection and tables"""
    print("\nTesting Supabase connection...")
    try:
        from supabase import create_client
        from app.core.config import settings
        
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        print("✅ Supabase client connected")
        
        # Test each table
        tables = ['products', 'videos', 'social_media_posts']
        for table_name in tables:
            try:
                result = client.table(table_name).select("*").limit(1).execute()
                print(f"✅ Table '{table_name}' exists and is accessible")
            except Exception as e:
                print(f"❌ Table '{table_name}' error: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Supabase connection error: {e}")
        return False

def main():
    print("="*60)
    print("🚀 CONTENT FACTORY - SETUP VERIFICATION")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Database Connection", test_supabase_connection()))
    
    # Summary
    print("\n" + "="*60)
    print("SETUP SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYour Content Factory is ready to use!")
        print("\nNext steps:")
        print("1. Start the application: python run.py")
        print("2. Open your browser: http://localhost:8000")
        print("3. Check the API docs: http://localhost:8000/docs")
        print("\n✨ You can now start generating AI content!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
