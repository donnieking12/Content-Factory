from app.core.database import Base, engine
from app.models import product, video, social_media

print("Creating database tables...")
try:
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
except Exception as e:
    print(f"Error creating database tables: {e}")