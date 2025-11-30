"""
Database Base Configuration
Similar to Prisma's datasource configuration
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.logger.logger import logger

# Get database connection parameters from environment
DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_NAME = os.environ.get('DATABASE_NAME')
DATABASE_USER = os.environ.get('DATABASE_USER')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_PORT = os.environ.get('DATABASE_PORT', '5432')

# Validate required environment variables
missing_vars = []
if not DATABASE_HOST:
    missing_vars.append('DATABASE_HOST')
if not DATABASE_NAME:
    missing_vars.append('DATABASE_NAME')
if not DATABASE_USER:
    missing_vars.append('DATABASE_USER')
if not DATABASE_PASSWORD:
    missing_vars.append('DATABASE_PASSWORD')

if missing_vars:
    error_msg = f"Missing required database environment variables: {', '.join(missing_vars)}"
    logger.error(error_msg, module="SQLAlchemy")
    # Don't raise during import, allow graceful degradation
    DATABASE_URL = None
else:
    # Build PostgreSQL connection URL
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Create engine with connection pooling
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Enable connection health checks
        pool_recycle=3600,   # Recycle connections after 1 hour
        echo=os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
    )
else:
    engine = None

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
) if engine else None

# Create declarative base for models
Base = declarative_base()


def get_db():
    """
    Dependency for FastAPI to get database session.
    Similar to Prisma's PrismaClient usage.

    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    if not SessionLocal:
        raise RuntimeError("Database not configured properly")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Similar to `prisma db push` command.
    """
    if not engine:
        raise RuntimeError("Database engine not configured")

    # Import all models to ensure they are registered
    from . import User, Permission, Group, GroupPermission, UserGroup, ActivityLog  # noqa: F401

    # Create all tables
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all database tables.
    Use with caution - this will delete all data!
    """
    if not engine:
        raise RuntimeError("Database engine not configured")

    Base.metadata.drop_all(bind=engine)
    logger.warning("All database tables dropped", module="SQLAlchemy")

