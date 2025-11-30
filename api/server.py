"""
FastAPI Server - Matching fastapi Backend Structure
Only includes routers that exist in fastapi backend
"""
from router.authenticate.authenticate import router as authenticate_router
from router.authenticate.profile import router as profile_router
from router.health.api import router as health_router
from router.health.test_sentry import router as test_sentry_router
from router.upload.api import router as upload_router
from router.dashboard.api import router as dashboard_router
from router.permissions.api import router as permissions_router
from router.activity.api import router as activity_router
from fastapi.middleware.cors import CORSMiddleware
from src.response.success import SUCCESS
from fastapi import FastAPI
from src.logger.logger import logger
import os
import sentry_sdk

# Initialize Sentry (optional - only if DSN is provided)
sentry_dsn = os.environ.get('SENTRY_DSN')
if sentry_dsn:
    try:
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '1.0')),
            profiles_sample_rate=float(os.environ.get('SENTRY_PROFILES_SAMPLE_RATE', '1.0')),
            environment=os.environ.get('API_MODE', 'development')
        )
    except Exception as e:
        logger.warning(f"Sentry initialization failed: {e}", module="Server")

app = FastAPI(
    title="FastApi - Backend",
    version=os.environ.get('API_VERSION'),
    root_path=f"/{os.environ.get('MODE')}",
    docs_url=None if os.environ.get('API_MODE') == "production" else f"/docs",
    redoc_url=None if os.environ.get('API_MODE') == "production" else f"/redoc"
)

# CORS Configuration
origins = (
    r"https?://(.*\.)?winsta\.(ai|pro)$|"  # Base domain and all subdomains
    r"https?://(127\.0\.0\.1|localhost):(8000|3000)$"  # localhost development
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# ROUTERS - Matching fastapi Backend
# ============================================================

# Authentication Routes
app.include_router(
    authenticate_router,
    tags=["Authentication"]
)

# Profile & Settings Routes
app.include_router(
    profile_router,
    tags=["Profile & Settings"]
)

# Health & Monitoring Routes
app.include_router(
    health_router,
    tags=["Health & Monitoring"]
)

app.include_router(
    test_sentry_router,
    tags=["Health & Monitoring"]
)

# Upload Routes
app.include_router(
    upload_router,
    tags=["Upload Media"]
)

# Dashboard Routes
app.include_router(
    dashboard_router,
    tags=["Dashboard"]
)

# Permissions & Groups Routes
app.include_router(
    permissions_router,
    tags=["Permissions & Groups"]
)

# Activity Logs Routes
app.include_router(
    activity_router,
    prefix="/activity",
    tags=["Activity Logs"]
)


# ============================================================
# STARTUP EVENT
# ============================================================

@app.on_event("startup")
async def startup_event():
    """
    Initialize database on application startup
    """
    # Try to initialize database triggers (non-blocking)
    try:
        from src.db.postgres.init_triggers import init_all_triggers

        # Initialize all triggers
        results = init_all_triggers()
        if results.get("failed"):
            logger.warning(f"⚠️  Some triggers failed to initialize: {results['failed']}", module="Server")
    except Exception as e:
        logger.warning(f"Trigger initialization skipped (will retry later): {e}", module="Server")

    # Test database connection (non-blocking)
    try:
        from src.db.postgres.postgres import get_db_connection
        conn = get_db_connection()
        if not conn:
            logger.warning("⚠️  Database connection not available yet (will retry on first use)", module="Server")
    except Exception as e:
        logger.warning(f"Database connection check failed (will retry on first use): {e}", module="Server")

    # Initialize cache (for token blacklisting)
    try:
        from src.cache.cache import cache
        await cache.init()
    except Exception as e:
        logger.warning(f"Cache initialization failed (will use in-memory fallback): {e}", module="Server")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():
    """
    Public health check endpoint with environment info
    Does not require database connection to return success
    """
    try:
        # Check database connection status (non-blocking)
        db_status = "unknown"
        try:
            from src.db.postgres.postgres import get_db_connection
            conn = get_db_connection()
            if conn and conn.connection and not conn.connection.closed:
                db_status = "connected"
            else:
                db_status = "disconnected"
        except Exception as e:
            db_status = f"error: {str(e)[:50]}"

        env_info = {
            "API_VERSION": os.getenv("API_VERSION", "N/A"),
            "API_MODE": os.getenv("API_MODE", "N/A"),
            "MODE": os.getenv("MODE", "N/A"),
            "UTC": os.getenv("UTC", "N/A"),
            "DEBUG_MODE": os.getenv("DEBUG_MODE", "N/A"),
            "TIMEZONE": os.getenv("TIMEZONE", "N/A"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "N/A")
        }

        meta = {
            "service": "fastapi-backend",
            "status": "ok",
            "database": db_status,
            "env": env_info
        }
        return SUCCESS.response(
            message="Service is healthy",
            data={"status": "ok", "database": db_status},
            meta=meta
        )

    except Exception as e:
        # Even on error, return a  (not an exception)
        return {
            "success": False,
            "message": "Health check failed",
            "data": {"status": "error"},
            "error": str(e)
        }
