#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database setup script for Content Factory AI
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app.core.database import Base, engine
    from app.models import product, video, social_media
    
    print("Creating database tables...")
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # Test the connection
    from app.core.database import SessionLocal
    db = SessionLocal()
    try:
        # Try a simple query to test connection
        result = db.execute("SELECT 1")
        print("✅ Database connection verified!")
    except Exception as e:
        print(f"⚠️  Database connection test failed: {e}")
    finally:
        db.close()
        
except Exception as e:
    print(f"❌ Error setting up database: {e}")
    print("\nTroubleshooting tips:")
    print("1. Check your Supabase credentials in .env file")
    print("2. Verify your Supabase project is active")
    print("3. Ensure your internet connection is working")
    sys.exit(1)