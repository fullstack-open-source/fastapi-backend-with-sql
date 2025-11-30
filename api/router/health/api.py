
from fastapi import APIRouter, Depends, HTTPException
from src.middleware.permission_middleware import check_permission
from src.multilingual.multilingual import normalize_language
from src.db.postgres.postgres import connection as db
from src.authenticate.models import User
from src.response.success import SUCCESS
from src.storage import media_storage
from src.response.error import ERROR
from typing import Dict, Any
import os
import asyncio
import httpx

router = APIRouter()

# Environment Variables
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GCS_BUCKET_NAME = os.environ.get("GOOGLE_STORAGE_BUCKET_NAME")
SMTP_HOST = os.environ.get("EMAIL_HOST")
SMTP_PORT = os.environ.get("EMAIL_PORT")



async def check_google_api() -> Dict[str, Any]:
    """Check Google API connectivity and status."""
    try:
        if not GOOGLE_API_KEY:
            return {
                "status": "error",
                "message": "Google API key not configured",
                "response_time": None,
                "error": "Missing GOOGLE_API_KEY"
            }

        async with httpx.AsyncClient(timeout=10) as client:
            params = {
                "key": GOOGLE_API_KEY,
                "input": "test",
                "inputtype": "textquery"
            }

            start_time = asyncio.get_event_loop().time()
            response = await client.get("https://maps.googleapis.com/maps/api/place/textsearch/json", params=params)
            end_time = asyncio.get_event_loop().time()

            response_time = round((end_time - start_time) * 1000, 2)

            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "message": "Google API is working",
                    "response_time": response_time,
                    "status_code": response.status_code
                }
            else:
                return {
                    "status": "error",
                    "message": f"Google API returned status {response.status_code}",
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "error": response.text
                }

    except httpx.TimeoutException:
        return {
            "status": "error",
            "message": "Google API request timed out",
            "response_time": None,
            "error": "Request timeout"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Google API check failed: {str(e)}",
            "error": str(e)
        }


async def check_database() -> Dict[str, Any]:
    """Check database connectivity and status."""
    try:
        start_time = asyncio.get_event_loop().time()

        with db as cursor:
            # Test basic database connectivity
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()

        end_time = asyncio.get_event_loop().time()
        response_time = round((end_time - start_time) * 1000, 2)

        if result and result[0] == 1:
            return {
                "status": "healthy",
                "message": "Database connection is working",
                "response_time": response_time,
                "database_type": "PostgreSQL"
            }
        else:
            return {
                "status": "error",
                "message": "Database query failed",
                "response_time": response_time,
                "error": "Query returned unexpected result"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Database check failed: {str(e)}",
            "response_time": None,
            "error": str(e)
        }


async def check_storage() -> Dict[str, Any]:
    """Check Google Cloud Storage connectivity and status."""
    try:
        if not GCS_BUCKET_NAME:
            return {
                "status": "error",
                "message": "GCS bucket name not configured",
                "response_time": None,
                "error": "Missing GCS_BUCKET_NAME"
            }

        start_time = asyncio.get_event_loop().time()

        # Test GCS connection by trying to list blobs using ProfessionalMediaStorage
        try:
            # Use media_storage instance to check connectivity
            if not media_storage._bucket:
                raise RuntimeError("Google Cloud Storage bucket not initialized")

            # List blobs with limit
            blobs = list(media_storage._bucket.list_blobs(max_results=1))
            end_time = asyncio.get_event_loop().time()
            response_time = round((end_time - start_time) * 1000, 2)

            return {
                "status": "healthy",
                "message": "Google Cloud Storage is working",
                "response_time": response_time,
                "bucket_name": GCS_BUCKET_NAME,
                "blob_count": len(blobs),
                "storage_class": "ProfessionalMediaStorage"
            }
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            response_time = round((end_time - start_time) * 1000, 2)

            return {
                "status": "error",
                "message": "GCS connection failed",
                "response_time": response_time,
                "error": str(e)
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Storage check failed: {str(e)}",
            "response_time": None,
            "error": str(e)
        }


async def check_email_service() -> Dict[str, Any]:
    """Check email service connectivity and status."""
    try:
        if not SMTP_HOST or not SMTP_PORT:
            return {
                "status": "error",
                "message": "SMTP credentials not configured",
                "response_time": None,
                "error": "Missing SMTP_HOST or SMTP_PORT"
            }

        start_time = asyncio.get_event_loop().time()

        # Test email service by checking SMTP connection
        try:
            import smtplib

            # Test SMTP connection
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
            server.quit()

            end_time = asyncio.get_event_loop().time()
            response_time = round((end_time - start_time) * 1000, 2)

            return {
                "status": "healthy",
                "message": "Email service is working",
                "response_time": response_time,
                "smtp_host": SMTP_HOST,
                "smtp_port": SMTP_PORT
            }
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            response_time = round((end_time - start_time) * 1000, 2)

            return {
                "status": "error",
                "message": "Email service connection failed",
                "response_time": response_time,
                "error": str(e)
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Email service check failed: {str(e)}",
            "response_time": None,
            "error": str(e)
        }


@router.get("/health/database", response_model=Dict[str, Any])
async def health_check_database(current_user: User = Depends(check_permission("view_system_health"))) -> Dict[str, Any]:
    """
    Health check specifically for database connectivity.

    Required Permission: view_system_health
    Allows users to check database connectivity and status.
    """
    try:
        result = await check_database()

        if result["status"] == "healthy":
            return SUCCESS.response(
                message="Database is healthy",
                data=result
            )
        else:
            raise HTTPException(
                status_code=503,
                detail=ERROR.build(
                    error_key="DATABASE_UNHEALTHY",
                    details=result,
                    exception=result.get("error", "Unknown error")
                )
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                error_key="DATABASE_HEALTH_CHECK_FAILED",
                details={"user_id": current_user.uid},
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )


@router.get("/health/storage", response_model=Dict[str, Any])
async def health_check_storage(current_user: User = Depends(check_permission("view_system_health"))) -> Dict[str, Any]:
    """
    Health check specifically for Google Cloud Storage.

    Required Permission: view_system_health
    Allows users to check storage connectivity and status.
    """
    try:
        result = await check_storage()

        if result["status"] == "healthy":
            return SUCCESS.response(
                message="Storage is healthy",
                data=result
            )
        else:
            raise HTTPException(
                status_code=503,
                detail=ERROR.build(
                    error_key="STORAGE_UNHEALTHY",
                    details=result,
                    exception=result.get("error", "Unknown error")
                )
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                error_key="STORAGE_HEALTH_CHECK_FAILED",
                details={"user_id": current_user.uid},
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )


@router.get("/health/system", response_model=Dict[str, Any])
async def health_check_system() -> Dict[str, Any]:
    """
    Public system health check endpoint (no authentication required).
    """
    try:
        import psutil
        import platform

        # System information
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }

        # Environment variables (non-sensitive)
        env_info = {
            "API_VERSION": os.getenv("API_VERSION", "N/A"),
            "API_MODE": os.getenv("API_MODE", "N/A"),
            "MODE": os.getenv("MODE", "N/A"),
            "DEBUG_MODE": os.getenv("DEBUG_MODE", "N/A"),
            "LOG_LEVEL": os.getenv("LOG_LEVEL", "N/A")
        }

        return SUCCESS.response(
            message="System health check completed",
            data={
                "status": "healthy",
                "system_info": system_info,
                "environment": env_info,
                "timestamp": asyncio.get_event_loop().time()
            },
        )

    except Exception as e:
        return ERROR.response(
            message="System health check failed",
            data={"status": "error"},
            exception=str(e)
        )
