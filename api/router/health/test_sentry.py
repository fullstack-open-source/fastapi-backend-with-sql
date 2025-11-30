"""
Sentry Test Endpoint
Tests Sentry error tracking in different environments
"""

import os
from fastapi import APIRouter, Depends, HTTPException, Query
from src.middleware.permission_middleware import check_permission
from src.authenticate.models import User
from src.response.success import SUCCESS
from src.response.error import ERROR
from src.logger.logger import logger
import sentry_sdk

router = APIRouter()

@router.get("/health/test-sentry")
async def test_sentry(
    type: str = Query("exception", regex="^(exception|message|unhandled|async)$"),
    current_user: User = Depends(check_permission("test_sentry"))
):
    """
    Test Sentry error tracking.

    Required Permission: test_sentry
    Intentionally triggers an error to test Sentry integration.
    """
    try:
        NODE_ENV = os.environ.get("API_MODE", "development")

        # Set user context if available
        if current_user:
            sentry_sdk.set_user({"id": str(current_user.uid), "email": getattr(current_user, 'email', None)})

        # Add breadcrumb
        sentry_sdk.add_breadcrumb(
            message="Sentry test initiated",
            category="test",
            level="info",
            data={"type": type, "nodeEnv": NODE_ENV}
        )

        if type == "exception":
            # Test manual exception capture
            test_error = Exception("Test Sentry Exception - This is a test error")
            sentry_sdk.capture_exception(
                test_error,
                tags={
                    "test_type": "manual_exception",
                    "environment": NODE_ENV,
                    "endpoint": "/health/test-sentry"
                },
                extra={
                    "type": type,
                    "userAgent": "test",
                    "ip": "test"
                }
            )

            return SUCCESS.response(
                message="Test exception sent to Sentry",
                data={
                    "type": "exception",
                    "environment": NODE_ENV,
                    "message": "Check your Sentry dashboard for the error",
                    "error": str(test_error)
                }
            )

        elif type == "message":
            # Test manual message capture
            sentry_sdk.capture_message(
                "Test Sentry Message - This is a test message",
                level="warning",
                tags={
                    "test_type": "manual_message",
                    "environment": NODE_ENV
                },
                extra={
                    "type": type,
                    "timestamp": "test"
                }
            )

            return SUCCESS.response(
                message="Test message sent to Sentry",
                data={
                    "type": "message",
                    "environment": NODE_ENV,
                    "message": "Check your Sentry dashboard for the message"
                }
            )

        elif type == "unhandled":
            # Test unhandled error (will be caught by error handler)
            raise Exception("Test Unhandled Error - This error should be caught by error handler and sent to Sentry")

        elif type == "async":
            # Test async error
            import asyncio
            async def send_async_error():
                await asyncio.sleep(0.1)
                async_error = Exception("Test Async Error - This is an async error")
                sentry_sdk.capture_exception(
                    async_error,
                    tags={
                        "test_type": "async_error",
                        "environment": NODE_ENV
                    }
                )

            asyncio.create_task(send_async_error())

            return SUCCESS.response(
                message="Test async error scheduled",
                data={
                    "type": "async",
                    "environment": NODE_ENV,
                    "message": "Async error will be sent to Sentry in 100ms"
                }
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=ERROR.build(
                    "INVALID_REQUEST",
                    details={"message": "Invalid test type. Use: exception, message, unhandled, or async"}
                )
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in Sentry test endpoint: {e}", exc_info=True, module="Health", label="SENTRY_TEST")
        # This error will be caught by Sentry error handler
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "SENTRY_TEST_ERROR",
                details={"type": type},
                exception=str(e)
            )
        )

