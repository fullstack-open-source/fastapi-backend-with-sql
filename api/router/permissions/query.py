"""
Permissions Router - Database Queries
All database operations for permissions and groups
"""
from typing import Optional, Dict, Any, List
from src.db.postgres.postgres import connection as db
from src.logger.logger import logger
import uuid


def get_all_permissions() -> List[Dict[str, Any]]:
    """Get all permissions"""
    try:
        with db as cursor:
            query = """
                SELECT permission_id, name, codename, description, category, created_at, last_updated
                FROM permission
                ORDER BY category ASC, name ASC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            return [
                {
                    "permission_id": str(row[0]),
                    "name": row[1],
                    "codename": row[2],
                    "description": row[3],
                    "category": row[4],
                    "created_at": row[5].isoformat() if row[5] else None,
                    "last_updated": row[6].isoformat() if row[6] else None
                }
                for row in rows
            ]
    except Exception as e:
        logger.error(f"Error getting all permissions: {e}", exc_info=True, module="Permissions")
        raise


def get_permission_by_id(permission_id: str) -> Optional[Dict[str, Any]]:
    """Get permission by ID"""
    try:
        with db as cursor:
            query = """
                SELECT permission_id, name, codename, description, category, created_at, last_updated
                FROM permission
                WHERE permission_id::text = %s
            """
            cursor.execute(query, (permission_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "permission_id": str(row[0]),
                "name": row[1],
                "codename": row[2],
                "description": row[3],
                "category": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "last_updated": row[6].isoformat() if row[6] else None
            }
    except Exception as e:
        logger.error(f"Error getting permission by ID: {e}", exc_info=True, module="Permissions")
        raise


def create_permission(permission_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new permission"""
    try:
        permission_id = str(uuid.uuid4())
        with db as cursor:
            query = """
                INSERT INTO permission (permission_id, name, codename, description, category)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING permission_id, name, codename, description, category, created_at, last_updated
            """
            cursor.execute(query, (
                permission_id,
                permission_data.get("name"),
                permission_data.get("codename"),
                permission_data.get("description"),
                permission_data.get("category")
            ))
            row = cursor.fetchone()
            return {
                "permission_id": str(row[0]),
                "name": row[1],
                "codename": row[2],
                "description": row[3],
                "category": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "last_updated": row[6].isoformat() if row[6] else None
            }
    except Exception as e:
        logger.error(f"Error creating permission: {e}", exc_info=True, module="Permissions")
        raise


def update_permission(permission_id: str, permission_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update permission"""
    try:
        set_clauses = []
        values = []
        if "name" in permission_data:
            set_clauses.append("name = %s")
            values.append(permission_data["name"])
        if "codename" in permission_data:
            set_clauses.append("codename = %s")
            values.append(permission_data["codename"])
        if "description" in permission_data:
            set_clauses.append("description = %s")
            values.append(permission_data["description"])
        if "category" in permission_data:
            set_clauses.append("category = %s")
            values.append(permission_data["category"])
        if not set_clauses:
            return get_permission_by_id(permission_id)
        set_clauses.append("last_updated = NOW()")
        values.append(permission_id)
        with db as cursor:
            query = f"""
                UPDATE permission
                SET {', '.join(set_clauses)}
                WHERE permission_id::text = %s
                RETURNING permission_id, name, codename, description, category, created_at, last_updated
            """
            cursor.execute(query, values)
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "permission_id": str(row[0]),
                "name": row[1],
                "codename": row[2],
                "description": row[3],
                "category": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "last_updated": row[6].isoformat() if row[6] else None
            }
    except Exception as e:
        logger.error(f"Error updating permission: {e}", exc_info=True, module="Permissions")
        raise


def delete_permission(permission_id: str) -> bool:
    """Delete permission"""
    try:
        with db as cursor:
            query = "DELETE FROM permission WHERE permission_id::text = %s"
            cursor.execute(query, (permission_id,))
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error deleting permission: {e}", exc_info=True, module="Permissions")
        raise


def get_all_groups() -> List[Dict[str, Any]]:
    """Get all groups with their permissions"""
    try:
        with db as cursor:
            query = """
                SELECT g.group_id, g.name, g.codename, g.description, g.is_system, g.is_active, g.created_at, g.last_updated
                FROM "group" g
                WHERE g.is_active = TRUE
                ORDER BY g.name ASC
            """
            cursor.execute(query)
            groups = cursor.fetchall()
            result = []
            for group in groups:
                group_id = str(group[0])
                perm_query = """
                    SELECT p.permission_id, p.name, p.codename, p.description, p.category
                    FROM permission p
                    INNER JOIN group_permission gp ON p.permission_id = gp.permission_id
                    WHERE gp.group_id::text = %s
                """
                cursor.execute(perm_query, (group_id,))
                permissions = cursor.fetchall()
                result.append({
                    "group_id": group_id,
                    "name": group[1],
                    "codename": group[2],
                    "description": group[3],
                    "is_system": group[4],
                    "is_active": group[5],
                    "permissions": [
                        {
                            "permission_id": str(p[0]),
                            "name": p[1],
                            "codename": p[2],
                            "description": p[3],
                            "category": p[4]
                        }
                        for p in permissions
                    ],
                    "created_at": group[6].isoformat() if group[6] else None,
                    "last_updated": group[7].isoformat() if group[7] else None
                })
            return result
    except Exception as e:
        logger.error(f"Error getting all groups: {e}", exc_info=True, module="Permissions")
        raise


def get_group_by_id(group_id: str) -> Optional[Dict[str, Any]]:
    """Get group by ID with permissions"""
    try:
        with db as cursor:
            query = """
                SELECT group_id, name, codename, description, is_system, is_active, created_at, last_updated
                FROM "group"
                WHERE group_id::text = %s
            """
            cursor.execute(query, (group_id,))
            group = cursor.fetchone()
            if not group:
                return None
            perm_query = """
                SELECT p.permission_id, p.name, p.codename, p.description, p.category
                FROM permission p
                INNER JOIN group_permission gp ON p.permission_id = gp.permission_id
                WHERE gp.group_id::text = %s
            """
            cursor.execute(perm_query, (group_id,))
            permissions = cursor.fetchall()
            return {
                "group_id": str(group[0]),
                "name": group[1],
                "codename": group[2],
                "description": group[3],
                "is_system": group[4],
                "is_active": group[5],
                "permissions": [
                    {
                        "permission_id": str(p[0]),
                        "name": p[1],
                        "codename": p[2],
                        "description": p[3],
                        "category": p[4]
                    }
                    for p in permissions
                ],
                "created_at": group[6].isoformat() if group[6] else None,
                "last_updated": group[7].isoformat() if group[7] else None
            }
    except Exception as e:
        logger.error(f"Error getting group by ID: {e}", exc_info=True, module="Permissions")
        raise


def create_group(group_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new group"""
    try:
        group_id = str(uuid.uuid4())
        with db as cursor:
            query = """
                INSERT INTO "group" (group_id, name, codename, description, is_system, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING group_id, name, codename, description, is_system, is_active, created_at, last_updated
            """
            cursor.execute(query, (
                group_id,
                group_data.get("name"),
                group_data.get("codename"),
                group_data.get("description"),
                group_data.get("is_system", False),
                group_data.get("is_active", True)
            ))
            row = cursor.fetchone()
            return {
                "group_id": str(row[0]),
                "name": row[1],
                "codename": row[2],
                "description": row[3],
                "is_system": row[4],
                "is_active": row[5],
                "permissions": [],
                "created_at": row[6].isoformat() if row[6] else None,
                "last_updated": row[7].isoformat() if row[7] else None
            }
    except Exception as e:
        logger.error(f"Error creating group: {e}", exc_info=True, module="Permissions")
        raise


def update_group(group_id: str, group_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update group"""
    try:
        set_clauses = []
        values = []
        if "name" in group_data:
            set_clauses.append("name = %s")
            values.append(group_data["name"])
        if "codename" in group_data:
            set_clauses.append("codename = %s")
            values.append(group_data["codename"])
        if "description" in group_data:
            set_clauses.append("description = %s")
            values.append(group_data["description"])
        if "is_active" in group_data:
            set_clauses.append("is_active = %s")
            values.append(group_data["is_active"])
        if not set_clauses:
            return get_group_by_id(group_id)
        set_clauses.append("last_updated = NOW()")
        values.append(group_id)
        with db as cursor:
            query = f"""
                UPDATE "group"
                SET {', '.join(set_clauses)}
                WHERE group_id::text = %s
                RETURNING group_id, name, codename, description, is_system, is_active, created_at, last_updated
            """
            cursor.execute(query, values)
            row = cursor.fetchone()
            if not row:
                return None
            return get_group_by_id(group_id)
    except Exception as e:
        logger.error(f"Error updating group: {e}", exc_info=True, module="Permissions")
        raise


def delete_group(group_id: str) -> bool:
    """Delete group (system groups cannot be deleted)"""
    try:
        with db as cursor:
            check_query = "SELECT is_system FROM \"group\" WHERE group_id::text = %s"
            cursor.execute(check_query, (group_id,))
            row = cursor.fetchone()
            if not row or row[0]:
                return False
            query = "DELETE FROM \"group\" WHERE group_id::text = %s"
            cursor.execute(query, (group_id,))
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error deleting group: {e}", exc_info=True, module="Permissions")
        raise


def assign_permissions_to_group(group_id: str, permission_ids: List[str]) -> None:
    """Assign permissions to group (replaces existing permissions)"""
    try:
        with db as cursor:
            delete_query = "DELETE FROM group_permission WHERE group_id::text = %s"
            cursor.execute(delete_query, (group_id,))
            if permission_ids:
                insert_query = """
                    INSERT INTO group_permission (group_id, permission_id)
                    VALUES (%s, %s)
                """
                for perm_id in permission_ids:
                    cursor.execute(insert_query, (group_id, perm_id))
    except Exception as e:
        logger.error(f"Error assigning permissions to group: {e}", exc_info=True, module="Permissions")
        raise


def get_user_groups(user_id: str) -> List[Dict[str, Any]]:
    """Get all groups assigned to a user"""
    try:
        with db as cursor:
            query = """
                SELECT g.group_id, g.name, g.codename, g.description, g.is_system, g.is_active
                FROM "group" g
                INNER JOIN user_group ug ON g.group_id = ug.group_id
                WHERE ug.user_id::text = %s AND g.is_active = TRUE
            """
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            return [
                {
                    "group_id": str(row[0]),
                    "name": row[1],
                    "codename": row[2],
                    "description": row[3],
                    "is_system": row[4],
                    "is_active": row[5]
                }
                for row in rows
            ]
    except Exception as e:
        logger.error(f"Error getting user groups: {e}", exc_info=True, module="Permissions")
        raise


def get_user_permissions(user_id: str) -> List[Dict[str, Any]]:
    """Get all permissions for a user (from all groups)"""
    try:
        with db as cursor:
            query = """
                SELECT DISTINCT p.permission_id, p.name, p.codename, p.description, p.category
                FROM permission p
                INNER JOIN group_permission gp ON p.permission_id = gp.permission_id
                INNER JOIN user_group ug ON gp.group_id = ug.group_id
                WHERE ug.user_id::text = %s
            """
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            return [
                {
                    "permission_id": str(row[0]),
                    "name": row[1],
                    "codename": row[2],
                    "description": row[3],
                    "category": row[4]
                }
                for row in rows
            ]
    except Exception as e:
        logger.error(f"Error getting user permissions: {e}", exc_info=True, module="Permissions")
        raise


def assign_groups_to_user(user_id: str, group_codenames: List[str], assigned_by_user_id: Optional[str] = None) -> None:
    """Assign groups to user (replaces existing groups)"""
    try:
        with db as cursor:
            delete_query = "DELETE FROM user_group WHERE user_id::text = %s"
            cursor.execute(delete_query, (user_id,))
            if group_codenames:
                placeholders = ','.join(['%s'] * len(group_codenames))
                group_query = f"""
                    SELECT group_id FROM "group"
                    WHERE codename IN ({placeholders})
                """
                cursor.execute(group_query, tuple(group_codenames))
                group_rows = cursor.fetchall()
                group_ids = [str(row[0]) for row in group_rows]
                if group_ids:
                    insert_query = """
                        INSERT INTO user_group (user_id, group_id, assigned_by_user_id)
                        VALUES (%s, %s, %s)
                    """
                    for group_id in group_ids:
                        cursor.execute(insert_query, (user_id, group_id, assigned_by_user_id))
    except Exception as e:
        logger.error(f"Error assigning groups to user: {e}", exc_info=True, module="Permissions")
        raise

