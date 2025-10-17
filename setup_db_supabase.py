#!/usr/bin/env python3
"""
Database setup using Supabase client - bypasses SQLAlchemy encoding issues
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from supabase import create_client
    from app.core.config import settings
    
    print("Connecting to Supabase...")
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    print("✅ Connected to Supabase successfully!")
    
    # SQL to create tables
    create_tables_sql = """
    -- Create products table
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL,
        description TEXT,
        price DECIMAL(10, 2),
        url VARCHAR,
        image_url VARCHAR,
        category VARCHAR,
        trending_score INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create videos table
    CREATE TABLE IF NOT EXISTS videos (
        id SERIAL PRIMARY KEY,
        title VARCHAR NOT NULL,
        description TEXT,
        script TEXT,
        video_url VARCHAR,
        thumbnail_url VARCHAR,
        duration INTEGER,
        status VARCHAR DEFAULT 'pending',
        product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create social_media_posts table
    CREATE TABLE IF NOT EXISTS social_media_posts (
        id SERIAL PRIMARY KEY,
        platform VARCHAR NOT NULL,
        post_id VARCHAR,
        post_url VARCHAR,
        content TEXT,
        status VARCHAR DEFAULT 'pending',
        published_at TIMESTAMP,
        video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create indexes for better performance
    CREATE INDEX IF NOT EXISTS idx_products_trending ON products(trending_score DESC);
    CREATE INDEX IF NOT EXISTS idx_videos_product ON videos(product_id);
    CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
    CREATE INDEX IF NOT EXISTS idx_social_posts_video ON social_media_posts(video_id);
    CREATE INDEX IF NOT EXISTS idx_social_posts_platform ON social_media_posts(platform);
    """
    
    print("\n" + "="*60)
    print("📋 SUPABASE SQL SETUP INSTRUCTIONS")
    print("="*60)
    print("\nSince we're experiencing encoding issues with direct connection,")
    print("please follow these steps to create your database tables:\n")
    print("1. Go to: https://supabase.com/dashboard/project/qcmmqmqerjyfvftdlttv/sql")
    print("2. Click 'New Query'")
    print("3. Copy the SQL below and paste it into the editor")
    print("4. Click 'Run'\n")
    print("="*60)
    print("SQL TO RUN:")
    print("="*60)
    print(create_tables_sql)
    print("="*60)
    print("\nAfter running the SQL, press Enter to continue...")
    input()
    
    # Test if tables were created
    print("\nTesting database tables...")
    try:
        result = client.table('products').select("*").limit(1).execute()
        print("✅ Products table exists!")
    except Exception as e:
        print(f"⚠️ Products table not found: {e}")
    
    try:
        result = client.table('videos').select("*").limit(1).execute()
        print("✅ Videos table exists!")
    except Exception as e:
        print(f"⚠️ Videos table not found: {e}")
        
    try:
        result = client.table('social_media_posts').select("*").limit(1).execute()
        print("✅ Social media posts table exists!")
    except Exception as e:
        print(f"⚠️ Social media posts table not found: {e}")
    
    print("\n✅ Database setup complete!")
    print("You can now run the application with: python run.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
