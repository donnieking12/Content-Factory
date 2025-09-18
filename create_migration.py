import os
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext
from alembic import command
from app.core.database import Base

# Create alembic config
alembic_cfg = Config("alembic.ini")

# Generate migration
try:
    command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
    print("Migration created successfully!")
except Exception as e:
    print(f"Error creating migration: {e}")