"""
Content Factory AI - Application Runner
This script starts the FastAPI application with proper error handling.
"""
import uvicorn
import sys
import os
from pathlib import Path

from app.main import app
from app.core.config import settings

def check_environment():
    """Check if the environment is properly configured"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Error: .env file not found")
        print("Please run setup_project.py first or create a .env file")
        return False
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected")
        print("It's recommended to activate the virtual environment first:")
        if os.name == 'nt':  # Windows
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print()
    
    return True

def main():
    """Main application runner"""
    print("🚀 Starting Content Factory AI...")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    try:
        print("✅ Application loaded successfully")
        print("📡 Starting server on http://localhost:8000")
        print("📚 API documentation available at http://localhost:8000/docs")
        print("🔍 Alternative docs at http://localhost:8000/redoc")
        print("\n⏹️  Press Ctrl+C to stop the server\n")
        
        # Start the server
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            workers=1,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("Please ensure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()