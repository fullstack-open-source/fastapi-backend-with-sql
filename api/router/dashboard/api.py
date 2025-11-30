"""
Dashboard Router
Provides comprehensive dashboard statistics and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from src.authenticate.models import User
from src.middleware.permission_middleware import check_permission
from src.response.success import SUCCESS
from src.response.error import ERROR
from src.logger.logger import logger
from src.multilingual.multilingual import normalize_language
from src.db.postgres.postgres import connection as db
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard/overview")
async def dashboard_overview(current_user: User = Depends(check_permission("view_dashboard"))):
    """
    Get dashboard overview statistics.

    Required Permission: view_dashboard
    Returns comprehensive user statistics including totals, active users, verified users, and more.
    """
    try:
        # Get today's date boundaries
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        week_ago = datetime.now() - timedelta(days=7)
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        with db as cursor:
            # Get all statistics
            queries = {
                "total_users": "SELECT COUNT(*) as count FROM public.\"user\"",
                "active_users": "SELECT COUNT(*) as count FROM public.\"user\" WHERE is_active = TRUE",
                "verified_users": "SELECT COUNT(*) as count FROM public.\"user\" WHERE is_verified = TRUE",
                "email_verified": "SELECT COUNT(*) as count FROM public.\"user\" WHERE is_email_verified = TRUE",
                "phone_verified": "SELECT COUNT(*) as count FROM public.\"user\" WHERE is_phone_verified = TRUE",
                "new_users_today": "SELECT COUNT(*) as count FROM public.\"user\" WHERE created_at >= %s AND created_at < %s",
                "new_users_week": "SELECT COUNT(*) as count FROM public.\"user\" WHERE created_at >= %s",
                "new_users_month": "SELECT COUNT(*) as count FROM public.\"user\" WHERE created_at >= %s",
                "users_with_sign_in": "SELECT COUNT(*) as count FROM public.\"user\" WHERE last_sign_in_at IS NOT NULL"
            }

            results = {}
            for key, query in queries.items():
                if key in ["new_users_today"]:
                    cursor.execute(query, (today, tomorrow))
                elif key in ["new_users_week"]:
                    cursor.execute(query, (week_ago,))
                elif key in ["new_users_month"]:
                    cursor.execute(query, (month_start,))
                else:
                    cursor.execute(query)
                row = cursor.fetchone()
                results[key] = row[0] if row else 0

        overview = {
            "total_users": results["total_users"],
            "active_users": results["active_users"],
            "verified_users": results["verified_users"],
            "email_verified": results["email_verified"],
            "phone_verified": results["phone_verified"],
            "new_users": {
                "today": results["new_users_today"],
                "this_week": results["new_users_week"],
                "this_month": results["new_users_month"]
            },
            "users_with_sign_in": results["users_with_sign_in"]
        }

        return SUCCESS.response(
            message="Dashboard overview retrieved successfully",
            data={"overview": overview},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except Exception as e:
        logger.error(f"Error in dashboard overview: {e}", exc_info=True, module="Dashboard", label="OVERVIEW")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "DASHBOARD_ERROR",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.get("/dashboard/users-by-status")
async def users_by_status(current_user: User = Depends(check_permission("view_dashboard"))):
    """
    Get user statistics by status.

    Required Permission: view_dashboard
    Returns count of users grouped by status (ACTIVE, INACTIVE, etc.).
    """
    try:
        with db as cursor:
            query = """
                SELECT status, COUNT(*) as count
                FROM public."user"
                GROUP BY status
                ORDER BY count DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            stats = [{"status": row[0], "count": row[1]} for row in rows]

        return SUCCESS.response(
            message="User statistics by status retrieved successfully",
            data={"users_by_status": stats},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except Exception as e:
        logger.error(f"Error in users by status: {e}", exc_info=True, module="Dashboard", label="USERS_BY_STATUS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "DASHBOARD_ERROR",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.get("/dashboard/users-by-type")
async def users_by_type(current_user: User = Depends(check_permission("view_dashboard"))):
    """
    Get user statistics by user type.

    Required Permission: view_dashboard
    Returns count of users grouped by user_type (customer, business, etc.).
    """
    try:
        with db as cursor:
            query = """
                SELECT COALESCE(user_type, 'unknown') as user_type, COUNT(*) as count
                FROM public."user"
                GROUP BY user_type
                ORDER BY count DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            stats = [{"user_type": row[0], "count": row[1]} for row in rows]

        return SUCCESS.response(
            message="User statistics by type retrieved successfully",
            data={"users_by_type": stats},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except Exception as e:
        logger.error(f"Error in users by type: {e}", exc_info=True, module="Dashboard", label="USERS_BY_TYPE")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "DASHBOARD_ERROR",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.get("/dashboard/users-by-auth-type")
async def users_by_auth_type(current_user: User = Depends(check_permission("view_dashboard"))):
    """
    Get user statistics by authentication type.

    Required Permission: view_dashboard
    Returns count of users grouped by auth_type (email, phone, etc.).
    """
    try:
        with db as cursor:
            query = """
                SELECT COALESCE(auth_type, 'unknown') as auth_type, COUNT(*) as count
                FROM public."user"
                GROUP BY auth_type
                ORDER BY count DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            stats = [{"auth_type": row[0], "count": row[1]} for row in rows]

        return SUCCESS.response(
            message="User statistics by auth type retrieved successfully",
            data={"users_by_auth_type": stats},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except Exception as e:
        logger.error(f"Error in users by auth type: {e}", exc_info=True, module="Dashboard", label="USERS_BY_AUTH_TYPE")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "DASHBOARD_ERROR",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.get("/dashboard/users-by-country")
async def users_by_country(current_user: User = Depends(check_permission("view_dashboard"))):
    """
    Get user statistics by country.

    Required Permission: view_dashboard
    Returns count of users grouped by country.
    """
    try:
        with db as cursor:
            query = """
                SELECT COALESCE(country, 'unknown') as country, COUNT(*) as count
                FROM public."user"
                GROUP BY country
                ORDER BY count DESC
                LIMIT 20
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            stats = [{"country": row[0], "count": row[1]} for row in rows]

        return SUCCESS.response(
            message="User statistics by country retrieved successfully",
            data={"users_by_country": stats},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except Exception as e:
        logger.error(f"Error in users by country: {e}", exc_info=True, module="Dashboard", label="USERS_BY_COUNTRY")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "DASHBOARD_ERROR",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.get("/dashboard/users-by-language")
async def users_by_language(current_user: User = Depends(check_permission("view_dashboard"))):
    """
    Get user statistics by language.

    Required Permission: view_dashboard
    Returns count of users grouped by language preference.
    """
    try:
        with db as cursor:
            query = """
                SELECT COALESCE(language, 'unknown') as language, COUNT(*) as count
                FROM public."user"
                GROUP BY language
                ORDER BY count DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            stats = [{"language": row[0], "count": row[1]} for row in rows]

        return SUCCESS.response(
            message="User statistics by language retrieved successfully",
            data={"users_by_language": stats},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except Exception as e:
        logger.error(f"Error in users by language: {e}", exc_info=True, module="Dashboard", label="USERS_BY_LANGUAGE")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "DASHBOARD_ERROR",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.get("/dashboard/user-growth")
async def user_growth(
    period: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(check_permission("view_dashboard"))
):
    """
    Get user growth statistics.

    Required Permission: view_dashboard
    Returns user sign-up statistics over time (daily, weekly, monthly).
    """
    try:
        with db as cursor:
            if period == "daily":
                days_limit = min(max(1, days), 365)
                query = f"""
                    SELECT DATE(created_at) as date, COUNT(*)::int as count
                    FROM public."user"
                    WHERE created_at >= CURRENT_DATE - INTERVAL '{days_limit} days'
                    GROUP BY DATE(created_at)
                    ORDER BY date ASC
                """
            elif period == "weekly":
                query = """
                    SELECT DATE_TRUNC('week', created_at) as week, COUNT(*)::int as count
                    FROM public."user"
                    WHERE created_at >= CURRENT_DATE - INTERVAL '12 weeks'
                    GROUP BY DATE_TRUNC('week', created_at)
                    ORDER BY week ASC
                """
            else:  # monthly
                query = """
                    SELECT DATE_TRUNC('month', created_at) as month, COUNT(*)::int as count
                    FROM public."user"
                    WHERE created_at >= CURRENT_DATE - INTERVAL '12 months'
                    GROUP BY DATE_TRUNC('month', created_at)
                    ORDER BY month ASC
                """

            cursor.execute(query)
            rows = cursor.fetchall()

            growth = []
            for row in rows:
                period_value = row[0]
                if isinstance(period_value, datetime):
                    period_value = period_value.isoformat()
                growth.append({
                    "period": period_value,
                    "count": row[1] if row[1] else 0
                })

        return SUCCESS.response(
            message="User growth statistics retrieved successfully",
            data={
                "period": period,
                "growth": growth
            },
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except Exception as e:
        logger.error(f"Error in user growth: {e}", exc_info=True, module="Dashboard", label="USER_GROWTH")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "DASHBOARD_ERROR",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.get("/dashboard/recent-sign-ins")
async def recent_sign_ins(
    hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(check_permission("view_dashboard"))
):
    """
    Get recent sign-in statistics.

    Required Permission: view_dashboard
    Returns users who signed in recently.
    """
    try:
        hours_limit = min(max(1, hours), 168)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        hours_ago = datetime.now() - timedelta(hours=hours_limit)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        with db as cursor:
            queries = {
                "total": "SELECT COUNT(*) as count FROM public.\"user\" WHERE last_sign_in_at IS NOT NULL",
                "last_hour": "SELECT COUNT(*) as count FROM public.\"user\" WHERE last_sign_in_at >= %s",
                "last_period": "SELECT COUNT(*) as count FROM public.\"user\" WHERE last_sign_in_at >= %s",
                "today": "SELECT COUNT(*) as count FROM public.\"user\" WHERE last_sign_in_at >= %s"
            }

            results = {}
            cursor.execute(queries["total"])
            results["total"] = cursor.fetchone()[0]

            cursor.execute(queries["last_hour"], (one_hour_ago,))
            results["last_hour"] = cursor.fetchone()[0]

            cursor.execute(queries["last_period"], (hours_ago,))
            results[f"last_{hours_limit}_hours"] = cursor.fetchone()[0]

            cursor.execute(queries["today"], (today,))
            results["today"] = cursor.fetchone()[0]

        stats = {
            "total_with_sign_in": results["total"],
            "last_hour": results["last_hour"],
            f"last_{hours_limit}_hours": results[f"last_{hours_limit}_hours"],
            "today": results["today"]
        }

        return SUCCESS.response(
            message="Recent sign-in statistics retrieved successfully",
            data={"recent_sign_ins": stats},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except Exception as e:
        logger.error(f"Error in recent sign-ins: {e}", exc_info=True, module="Dashboard", label="RECENT_SIGN_INS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "DASHBOARD_ERROR",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.get("/dashboard/all-statistics")
async def all_statistics(current_user: User = Depends(check_permission("view_dashboard"))):
    """
    Get all dashboard statistics.

    Required Permission: view_dashboard
    Returns comprehensive dashboard statistics including all metrics.
    """
    try:
        # Get date boundaries
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        week_ago = datetime.now() - timedelta(days=7)
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        with db as cursor:
            # Get overview statistics
            overview_queries = {
                "total_users": "SELECT COUNT(*) FROM public.\"user\"",
                "active_users": "SELECT COUNT(*) FROM public.\"user\" WHERE is_active = TRUE",
                "verified_users": "SELECT COUNT(*) FROM public.\"user\" WHERE is_verified = TRUE",
                "email_verified": "SELECT COUNT(*) FROM public.\"user\" WHERE is_email_verified = TRUE",
                "phone_verified": "SELECT COUNT(*) FROM public.\"user\" WHERE is_phone_verified = TRUE",
                "new_today": "SELECT COUNT(*) FROM public.\"user\" WHERE created_at >= %s AND created_at < %s",
                "new_week": "SELECT COUNT(*) FROM public.\"user\" WHERE created_at >= %s",
                "new_month": "SELECT COUNT(*) FROM public.\"user\" WHERE created_at >= %s"
            }

            overview_results = {}
            for key, query in overview_queries.items():
                if key == "new_today":
                    cursor.execute(query, (today, tomorrow))
                elif key == "new_week":
                    cursor.execute(query, (week_ago,))
                elif key == "new_month":
                    cursor.execute(query, (month_start,))
                else:
                    cursor.execute(query)
                overview_results[key] = cursor.fetchone()[0]

            # Get grouped statistics
            cursor.execute("SELECT status, COUNT(*) as count FROM public.\"user\" GROUP BY status")
            by_status = [{"status": row[0], "count": row[1]} for row in cursor.fetchall()]

            cursor.execute("SELECT COALESCE(user_type, 'unknown') as user_type, COUNT(*) as count FROM public.\"user\" GROUP BY user_type")
            by_type = [{"user_type": row[0], "count": row[1]} for row in cursor.fetchall()]

            cursor.execute("SELECT COALESCE(auth_type, 'unknown') as auth_type, COUNT(*) as count FROM public.\"user\" GROUP BY auth_type")
            by_auth_type = [{"auth_type": row[0], "count": row[1]} for row in cursor.fetchall()]

            # Get role statistics (simplified - would need permissions module for full implementation)
            # For now, return empty roles
            roles = {
                "superusers": 0,
                "admins": 0,
                "business": 0,
                "developers": 0,
                "accountants": 0,
                "regular_users": 0
            }

        stats = {
            "overview": {
                "total_users": overview_results["total_users"],
                "active_users": overview_results["active_users"],
                "verified_users": overview_results["verified_users"],
                "email_verified": overview_results["email_verified"],
                "phone_verified": overview_results["phone_verified"],
                "new_users": {
                    "today": overview_results["new_today"],
                    "this_week": overview_results["new_week"],
                    "this_month": overview_results["new_month"]
                }
            },
            "by_status": by_status,
            "by_type": by_type,
            "by_auth_type": by_auth_type,
            "roles": roles
        }

        return SUCCESS.response(
            message="All dashboard statistics retrieved successfully",
            data=stats,
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except Exception as e:
        logger.error(f"Error in all statistics: {e}", exc_info=True, module="Dashboard", label="ALL_STATISTICS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                "DASHBOARD_ERROR",
                exception=str(e),
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

