"""
Activity Router
Handles activity logging endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from src.authenticate.models import User
from src.middleware.permission_middleware import check_permission
from src.response.success import SUCCESS
from src.response.error import ERROR
from src.logger.logger import logger
from src.multilingual.multilingual import normalize_language
from .models import ActivityLogCreate
from .query import (
    create_activity_log, get_activity_logs, get_activity_log_by_id,
    get_user_activity_logs, get_activity_statistics,
    delete_old_activity_logs, parse_user_agent
)
from typing import Optional

router = APIRouter()

@router.post("/activity/logs")
async def create_activity_log(
    payload: ActivityLogCreate,
    request: Request,
    current_user: User = Depends(check_permission("create_activity_log"))
):
    """
    Create activity log entry.

    Required Permission: create_activity_log
    Allows users to create new activity log entries.
    """
    try:
        user_id = current_user.uid if current_user else None
        user_agent = request.headers.get("user-agent") or payload.user_agent
        ip_address = request.client.host if request.client else payload.ip_address

        # Parse user agent
        parsed_ua = parse_user_agent(user_agent)

        log_data = {
            "user_id": user_id,
            "level": payload.level,
            "message": payload.message,
            "action": payload.action,
            "module": payload.module,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "device": payload.device or parsed_ua.get("device"),
            "browser": payload.browser or parsed_ua.get("browser"),
            "os": payload.os or parsed_ua.get("os"),
            "platform": payload.platform,
            "endpoint": payload.endpoint or str(request.url.path),
            "method": payload.method or request.method,
            "status_code": payload.status_code,
            "request_id": payload.request_id,
            "session_id": payload.session_id,
            "metadata": payload.metadata,
            "error_details": payload.error_details,
            "duration_ms": payload.duration_ms
        }

        activity_log = create_activity_log(log_data)

        return SUCCESS.response(
            message="Activity log created successfully",
            data={"activity_log": activity_log},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error creating activity log: {e}", exc_info=True, module="ActivityLog", label="CREATE_ACTIVITY_LOG")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "ACTIVITY_LOG_CREATE_FAILED",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.get("/activity/logs")
async def get_activity_logs(
    user_id: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    module: Optional[str] = Query(None),
    ip_address: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    order_by: str = Query("created_at"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(check_permission("view_activity_log"))
):
    """
    Get activity logs with filters.

    Required Permission: view_activity_log
    Allows users to view all activity logs with filtering options.
    """
    try:
        filters = {
            "user_id": user_id,
            "level": level,
            "action": action,
            "module": module,
            "ip_address": ip_address,
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
            "offset": offset,
            "orderBy": order_by,
            "order": order
        }

        logs = get_activity_logs(filters)

        return SUCCESS.response(
            message="Activity logs retrieved successfully",
            data={
                "activity_logs": logs,
                "count": len(logs)
            },
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error getting activity logs: {e}", exc_info=True, module="ActivityLog", label="GET_ACTIVITY_LOGS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "ACTIVITY_LOG_QUERY_FAILED",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.get("/activity/logs/{log_id}")
async def get_activity_log_by_id(
    log_id: str,
    current_user: User = Depends(check_permission("view_activity_log"))
):
    """
    Get activity log by ID.

    Required Permission: view_activity_log
    Allows users to view a specific activity log by its ID.
    """
    try:
        log = get_activity_log_by_id(log_id)
        if not log:
            raise HTTPException(
                status_code=404,
                detail=ERROR.build("ACTIVITY_LOG_NOT_FOUND", details={"log_id": log_id})
            )

        return SUCCESS.response(
            message="Activity log retrieved successfully",
            data={"activity_log": log},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting activity log by ID: {e}", exc_info=True, module="ActivityLog", label="GET_ACTIVITY_LOG_BY_ID")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("INTERNAL_ERROR", exception=str(e))
        )

@router.get("/activity/users/{user_id}/logs")
async def get_user_activity_logs(
    user_id: str,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(check_permission("view_activity_log"))
):
    """
    Get activity logs for a specific user.

    Required Permission: view_activity_log
    Allows users to view activity logs for any user (admin/moderator access).
    """
    try:
        filters = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
            "offset": offset
        }

        logs = get_user_activity_logs(user_id, filters)

        return SUCCESS.response(
            message="User activity logs retrieved successfully",
            data={
                "user_id": user_id,
                "activity_logs": logs,
                "count": len(logs)
            },
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error getting user activity logs: {e}", exc_info=True, module="ActivityLog", label="GET_USER_ACTIVITY_LOGS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "ACTIVITY_LOG_QUERY_FAILED",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.get("/activity/me/logs")
async def get_my_activity_logs(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(check_permission("view_own_activity_log"))
):
    """
    Get current user's own activity logs.

    Required Permission: view_own_activity_log
    Allows users to view their own activity logs (self-access only).
    """
    try:
        filters = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
            "offset": offset
        }

        logs = get_user_activity_logs(str(current_user.uid), filters)

        return SUCCESS.response(
            message="Your activity logs retrieved successfully",
            data={
                "activity_logs": logs,
                "count": len(logs)
            },
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error getting current user activity logs: {e}", exc_info=True, module="ActivityLog", label="GET_MY_ACTIVITY_LOGS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "ACTIVITY_LOG_QUERY_FAILED",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.get("/activity/statistics")
async def get_activity_statistics(
    user_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(check_permission("view_activity_statistics"))
):
    """
    Get activity statistics.

    Required Permission: view_activity_statistics
    Allows users to view activity log statistics and analytics.
    """
    try:
        filters = {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date
        }

        stats = get_activity_statistics(filters)

        return SUCCESS.response(
            message="Activity statistics retrieved successfully",
            data={"statistics": stats},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error getting activity statistics: {e}", exc_info=True, module="ActivityLog", label="GET_ACTIVITY_STATISTICS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "ACTIVITY_LOG_QUERY_FAILED",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.delete("/activity/logs/cleanup")
async def delete_old_activity_logs(
    days: int = Query(90, ge=1, le=365),
    current_user: User = Depends(check_permission("delete_activity_log"))
):
    """
    Delete old activity logs.

    Required Permission: delete_activity_log
    Allows users to delete old activity logs (cleanup/maintenance operation).
    """
    try:
        deleted_count = delete_old_activity_logs(days)

        return SUCCESS.response(
            message="Old activity logs deleted successfully",
            data={
                "deleted_count": deleted_count,
                "days_old": days
            },
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error deleting old activity logs: {e}", exc_info=True, module="ActivityLog", label="DELETE_OLD_ACTIVITY_LOGS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "ACTIVITY_LOG_DELETE_FAILED",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

