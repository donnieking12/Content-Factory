from app.core.config import settings
from app.core.database import engine
from sqlalchemy import text

print("DATABASE_URL:", settings.DATABASE_URL)
print("Testing database connection...")

try:
    # Try to connect to the database
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection successful!")
        print("Result:", result.fetchone())
except Exception as e:
    print("Database connection failed:", str(e))