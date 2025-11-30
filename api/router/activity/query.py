"""
Activity Router - Database Queries
All database operations for activity logs
"""
from typing import Optional, Dict, Any, List
from src.db.postgres.postgres import connection as db
from src.logger.logger import logger
import uuid
import json


def create_activity_log(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create activity log entry"""
    try:
        log_id = str(uuid.uuid4())
        with db as cursor:
            query = """
                INSERT INTO activity_log (
                    log_id, user_id, level, message, action, module,
                    ip_address, user_agent, device, browser, os, platform,
                    endpoint, method, status_code, request_id, session_id,
                    metadata, error_details, duration_ms
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING log_id, user_id, level, message, action, module,
                    ip_address, user_agent, device, browser, os, platform,
                    endpoint, method, status_code, request_id, session_id,
                    metadata, error_details, duration_ms, created_at
            """
            metadata_json = json.dumps(log_data.get("metadata")) if log_data.get("metadata") else None
            error_details_json = json.dumps(log_data.get("error_details")) if log_data.get("error_details") else None

            cursor.execute(query, (
                log_id, log_data.get("user_id"), log_data.get("level", "info"),
                log_data.get("message"), log_data.get("action"), log_data.get("module"),
                log_data.get("ip_address"), log_data.get("user_agent"),
                log_data.get("device"), log_data.get("browser"), log_data.get("os"),
                log_data.get("platform", "web"), log_data.get("endpoint"),
                log_data.get("method"), log_data.get("status_code"),
                log_data.get("request_id"), log_data.get("session_id"),
                metadata_json, error_details_json, log_data.get("duration_ms")
            ))
            row = cursor.fetchone()
            return {
                "log_id": str(row[0]),
                "user_id": str(row[1]) if row[1] else None,
                "level": row[2],
                "message": row[3],
                "action": row[4],
                "module": row[5],
                "ip_address": row[6],
                "user_agent": row[7],
                "device": row[8],
                "browser": row[9],
                "os": row[10],
                "platform": row[11],
                "endpoint": row[12],
                "method": row[13],
                "status_code": row[14],
                "request_id": row[15],
                "session_id": row[16],
                "metadata": json.loads(row[17]) if row[17] else None,
                "error_details": json.loads(row[18]) if row[18] else None,
                "duration_ms": row[19],
                "created_at": row[20].isoformat() if row[20] else None
            }
    except Exception as e:
        logger.error(f"Error creating activity log: {e}", exc_info=True, module="ActivityLog")
        raise


def get_activity_logs(filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Get activity logs with filters"""
    try:
        if filters is None:
            filters = {}
        where_clauses = []
        params = []
        if filters.get("user_id"):
            where_clauses.append("al.user_id::text = %s")
            params.append(filters["user_id"])
        if filters.get("level"):
            where_clauses.append("al.level = %s")
            params.append(filters["level"])
        if filters.get("action"):
            where_clauses.append("al.action = %s")
            params.append(filters["action"])
        if filters.get("module"):
            where_clauses.append("al.module = %s")
            params.append(filters["module"])
        if filters.get("ip_address"):
            where_clauses.append("al.ip_address = %s")
            params.append(filters["ip_address"])
        if filters.get("start_date"):
            where_clauses.append("al.created_at >= %s")
            params.append(filters["start_date"])
        if filters.get("end_date"):
            where_clauses.append("al.created_at <= %s")
            params.append(filters["end_date"])
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        order_by = filters.get("orderBy", "created_at")
        if order_by not in ["created_at", "level", "action", "module"]:
            order_by = "created_at"
        order = "DESC" if filters.get("order", "desc").upper() == "DESC" else "ASC"
        limit = filters.get("limit", 100)
        offset = filters.get("offset", 0)
        params.extend([limit, offset])
        with db as cursor:
            query = f"""
                SELECT al.log_id, al.user_id, al.level, al.message, al.action, al.module,
                    al.ip_address, al.user_agent, al.device, al.browser, al.os, al.platform,
                    al.endpoint, al.method, al.status_code, al.request_id, al.session_id,
                    al.metadata, al.error_details, al.duration_ms, al.created_at,
                    u.user_id as u_user_id, u.email, u.user_name, u.first_name, u.last_name
                FROM activity_log al
                LEFT JOIN public."user" u ON al.user_id = u.user_id
                WHERE {where_sql}
                ORDER BY al.{order_by} {order}
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, params)
            rows = cursor.fetchall()
            logs = []
            for row in rows:
                logs.append({
                    "log_id": str(row[0]),
                    "user_id": str(row[1]) if row[1] else None,
                    "level": row[2],
                    "message": row[3],
                    "action": row[4],
                    "module": row[5],
                    "ip_address": row[6],
                    "user_agent": row[7],
                    "device": row[8],
                    "browser": row[9],
                    "os": row[10],
                    "platform": row[11],
                    "endpoint": row[12],
                    "method": row[13],
                    "status_code": row[14],
                    "request_id": row[15],
                    "session_id": row[16],
                    "metadata": json.loads(row[17]) if row[17] else None,
                    "error_details": json.loads(row[18]) if row[18] else None,
                    "duration_ms": row[19],
                    "created_at": row[20].isoformat() if row[20] else None,
                    "user": {
                        "user_id": str(row[21]) if row[21] else None,
                        "email": row[22],
                        "user_name": row[23],
                        "first_name": row[24],
                        "last_name": row[25]
                    } if row[21] else None
                })
            return logs
    except Exception as e:
        logger.error(f"Error getting activity logs: {e}", exc_info=True, module="ActivityLog")
        raise


def get_activity_log_by_id(log_id: str) -> Optional[Dict[str, Any]]:
    """Get activity log by ID"""
    try:
        with db as cursor:
            query = """
                SELECT al.log_id, al.user_id, al.level, al.message, al.action, al.module,
                    al.ip_address, al.user_agent, al.device, al.browser, al.os, al.platform,
                    al.endpoint, al.method, al.status_code, al.request_id, al.session_id,
                    al.metadata, al.error_details, al.duration_ms, al.created_at,
                    u.user_id as u_user_id, u.email, u.user_name, u.first_name, u.last_name
                FROM activity_log al
                LEFT JOIN public."user" u ON al.user_id = u.user_id
                WHERE al.log_id::text = %s
            """
            cursor.execute(query, (log_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "log_id": str(row[0]),
                "user_id": str(row[1]) if row[1] else None,
                "level": row[2],
                "message": row[3],
                "action": row[4],
                "module": row[5],
                "ip_address": row[6],
                "user_agent": row[7],
                "device": row[8],
                "browser": row[9],
                "os": row[10],
                "platform": row[11],
                "endpoint": row[12],
                "method": row[13],
                "status_code": row[14],
                "request_id": row[15],
                "session_id": row[16],
                "metadata": json.loads(row[17]) if row[17] else None,
                "error_details": json.loads(row[18]) if row[18] else None,
                "duration_ms": row[19],
                "created_at": row[20].isoformat() if row[20] else None,
                "user": {
                    "user_id": str(row[21]) if row[21] else None,
                    "email": row[22],
                    "user_name": row[23],
                    "first_name": row[24],
                    "last_name": row[25]
                } if row[21] else None
            }
    except Exception as e:
        logger.error(f"Error getting activity log by ID: {e}", exc_info=True, module="ActivityLog")
        raise


def get_user_activity_logs(user_id: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """Get user activity logs"""
    try:
        if filters is None:
            filters = {}
        filters["user_id"] = user_id
        return get_activity_logs(filters)
    except Exception as e:
        logger.error(f"Error getting user activity logs: {e}", exc_info=True, module="ActivityLog")
        raise


def get_activity_statistics(filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get activity statistics"""
    try:
        if filters is None:
            filters = {}
        where_clauses = []
        params = []
        if filters.get("user_id"):
            where_clauses.append("user_id::text = %s")
            params.append(filters["user_id"])
        if filters.get("start_date"):
            where_clauses.append("created_at >= %s")
            params.append(filters["start_date"])
        if filters.get("end_date"):
            where_clauses.append("created_at <= %s")
            params.append(filters["end_date"])
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        with db as cursor:
            total_query = f"SELECT COUNT(*) FROM activity_log WHERE {where_sql}"
            cursor.execute(total_query, params)
            total = cursor.fetchone()[0]
            level_query = f"""
                SELECT level, COUNT(*) as count
                FROM activity_log
                WHERE {where_sql}
                GROUP BY level
            """
            cursor.execute(level_query, params)
            by_level = [{"level": row[0], "count": row[1]} for row in cursor.fetchall()]
            action_query = f"""
                SELECT action, COUNT(*) as count
                FROM activity_log
                WHERE {where_sql} AND action IS NOT NULL
                GROUP BY action
                ORDER BY count DESC
                LIMIT 10
            """
            cursor.execute(action_query, params)
            by_action = [{"action": row[0], "count": row[1]} for row in cursor.fetchall()]
            module_query = f"""
                SELECT module, COUNT(*) as count
                FROM activity_log
                WHERE {where_sql} AND module IS NOT NULL
                GROUP BY module
                ORDER BY count DESC
                LIMIT 10
            """
            cursor.execute(module_query, params)
            by_module = [{"module": row[0], "count": row[1]} for row in cursor.fetchall()]
        return {
            "total": total,
            "by_level": by_level,
            "by_action": by_action,
            "by_module": by_module
        }
    except Exception as e:
        logger.error(f"Error getting activity statistics: {e}", exc_info=True, module="ActivityLog")
        raise


def delete_old_activity_logs(days_old: int = 90) -> int:
    """Delete old activity logs"""
    try:
        with db as cursor:
            query = """
                DELETE FROM activity_log
                WHERE created_at < NOW() - INTERVAL '%s days'
            """
            cursor.execute(query, (days_old,))
            return cursor.rowcount
    except Exception as e:
        logger.error(f"Error deleting old activity logs: {e}", exc_info=True, module="ActivityLog")
        raise


def parse_user_agent(user_agent: str) -> Dict[str, Optional[str]]:
    """Parse user agent string (simplified)"""
    try:
        device = "unknown"
        browser = "unknown"
        os = "unknown"
        if user_agent:
            user_agent_lower = user_agent.lower()
            if "mobile" in user_agent_lower or "android" in user_agent_lower or "iphone" in user_agent_lower:
                device = "mobile"
            elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
                device = "tablet"
            else:
                device = "desktop"
            if "chrome" in user_agent_lower:
                browser = "chrome"
            elif "firefox" in user_agent_lower:
                browser = "firefox"
            elif "safari" in user_agent_lower:
                browser = "safari"
            elif "edge" in user_agent_lower:
                browser = "edge"
            if "windows" in user_agent_lower:
                os = "windows"
            elif "mac" in user_agent_lower or "darwin" in user_agent_lower:
                os = "macos"
            elif "linux" in user_agent_lower:
                os = "linux"
            elif "android" in user_agent_lower:
                os = "android"
            elif "ios" in user_agent_lower or "iphone" in user_agent_lower:
                os = "ios"
        return {"device": device, "browser": browser, "os": os}
    except Exception:
        return {"device": "unknown", "browser": "unknown", "os": "unknown"}

