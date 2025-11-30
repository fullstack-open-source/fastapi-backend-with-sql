"""
Permission Middleware
Checks if user has required permissions and groups
"""

from typing import Union, List
from fastapi import Depends, HTTPException, status
from src.authenticate.authenticate import validate_request
from src.authenticate.models import User
from src.permissions.permissions import (
    get_user_groups,
    user_has_permission
)
from src.response.error import ERROR
from src.logger.logger import logger


def check_permission(
    required_permissions: Union[str, List[str]],
    require_all: bool = False
):
    """
    Check if user has required permission(s).

    This function performs TWO checks:
    1. User Authentication - Validates user token via validate_request
    2. User Permissions - Checks if user has required permission(s) through their groups

    Both checks must pass for the request to proceed.

    Args:
        required_permissions: Single permission codename or list of permission codenames
        require_all: If True, user must have ALL permissions. If False, user needs ANY permission

    Returns:
        FastAPI dependency function that returns authenticated User if both checks pass

    Usage:
        @router.get("/endpoint")
        async def my_endpoint(current_user: User = Depends(check_permission("view_users"))):
            # current_user is guaranteed to be authenticated AND have "view_users" permission
            ...

        @router.post("/endpoint")
        async def my_endpoint(current_user: User = Depends(check_permission(["edit_users", "delete_users"], require_all=True))):
            # current_user is guaranteed to be authenticated AND have BOTH permissions
            ...
    """
    def permission_checker(current_user: User = Depends(validate_request)):
        """
        Permission checker that validates:
        1. User authentication (via validate_request) - CHECKED FIRST
        2. User permissions (via user_has_permission) - CHECKED AFTER AUTH

        Both checks must pass for the request to proceed.

        Flow:
        =====
        Step 1: Authentication Check (via validate_request dependency)
        - Validates token exists and is valid
        - Checks token blacklist
        - Checks session blacklist
        - Validates token signature and expiration
        - Returns authenticated User object

        Step 2: Permission Check (this function)
        - Extracts user_id from authenticated user
        - Checks if user has super_admin group (bypass)
        - Checks if user has required permission(s) through groups
        - Returns user if all checks pass
        """
        try:
            # ============================================================
            # STEP 1: AUTHENTICATION CHECK (ALREADY DONE)
            # ============================================================
            # Authentication is validated by validate_request dependency
            # If we reach here, user is authenticated (token is valid)
            # current_user is guaranteed to be a valid, authenticated User

            # Extract user_id from authenticated user
            user_id = str(current_user.uid) if hasattr(current_user, 'uid') else str(getattr(current_user, 'user_id', ''))

            # Double-check: If user_id is missing, this is an auth issue
            if not user_id:
                logger.error("Authentication check passed but user_id is missing", module="Permissions", label="PERMISSION_CHECK")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,  # Changed to 401 (auth issue, not permission)
                    detail=ERROR.build(
                        "UNAUTHORIZED",
                        details={
                            "message": "User authentication incomplete - user_id not found",
                            "check": "authentication"
                        }
                    )
                )

            # ============================================================
            # STEP 2: PERMISSION CHECK (NOW CHECKING)
            # ============================================================
            # Now that authentication is confirmed, check permissions

            # 2.1: Check superuser bypass first (super_admin group bypasses all permission checks)
            try:
                user_groups = get_user_groups(user_id)
                is_superuser = any(g.get('codename') == 'super_admin' for g in user_groups)
                if is_superuser:
                    return current_user
            except Exception as error:
                logger.warning(f"Error checking superuser status: {error}", module="Permissions", label="PERMISSION_CHECK")
                # Continue with normal permission check if superuser check fails

            # 2.2: Normalize permissions to list
            permissions = [required_permissions] if isinstance(required_permissions, str) else required_permissions

            # 2.3: Check permissions based on require_all flag
            if require_all:
                # User must have ALL permissions
                for permission in permissions:
                    has_perm = user_has_permission(user_id, permission)
                    if not has_perm:
                        logger.warning(f"Permission check FAILED: User {user_id} missing permission '{permission}'", module="Permissions", label="PERMISSION_CHECK")
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=ERROR.build(
                                "FORBIDDEN",
                                details={
                                    "message": f"Missing required permission: {permission}",
                                    "permission": permission,
                                    "required_permissions": permissions,
                                    "check": "permission",
                                    "user_id": user_id
                                }
                            )
                        )
            else:
                # User needs ANY permission
                has_any_permission = False
                found_permission = None
                for permission in permissions:
                    if user_has_permission(user_id, permission):
                        has_any_permission = True
                        found_permission = permission
                        break

                if not has_any_permission:
                    logger.warning(f"Permission check FAILED: User {user_id} missing all required permissions {permissions}", module="Permissions", label="PERMISSION_CHECK")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=ERROR.build(
                            "FORBIDDEN",
                            details={
                                "message": f"Missing required permission. Required one of: {', '.join(permissions)}",
                                "required_permissions": permissions,
                                "check": "permission",
                                "user_id": user_id
                            }
                        )
                    )

            # All checks passed - return authenticated and authorized user
            return current_user

        except HTTPException:
            raise
        except Exception as error:
            logger.error(f"Error in permission check: {error}", exc_info=True, module="Permissions", label="PERMISSION_CHECK")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR.build("AUTH_PROCESSING_ERROR", exception=error)
            )

    return permission_checker


def check_group(required_groups: Union[str, List[str]]):
    """
    Check if user has any of the specified groups.

    This function performs TWO checks:
    1. User Authentication - Validates user token via validate_request
    2. User Groups - Checks if user belongs to any of the required groups

    Both checks must pass for the request to proceed.

    Args:
        required_groups: Single group codename or list of group codenames

    Returns:
        FastAPI dependency function that returns authenticated User if both checks pass

    Usage:
        @router.get("/endpoint")
        async def my_endpoint(current_user: User = Depends(check_group("admin"))):
            # current_user is guaranteed to be authenticated AND have "admin" group
            ...

        @router.post("/endpoint")
        async def my_endpoint(current_user: User = Depends(check_group(["admin", "moderator"]))):
            # current_user is guaranteed to be authenticated AND have one of the groups
            ...
    """
    def group_checker(current_user: User = Depends(validate_request)):
        """
        Group checker that validates:
        1. User authentication (via validate_request) - CHECKED FIRST
        2. User groups (via get_user_groups) - CHECKED AFTER AUTH

        Both checks must pass for the request to proceed.

        Flow:
        =====
        Step 1: Authentication Check (via validate_request dependency)
        - Validates token exists and is valid
        - Checks token blacklist
        - Checks session blacklist
        - Validates token signature and expiration
        - Returns authenticated User object

        Step 2: Group Check (this function)
        - Extracts user_id from authenticated user
        - Checks if user has super_admin group (bypass)
        - Checks if user belongs to any of the required groups
        - Returns user if all checks pass
        """
        try:
            # ============================================================
            # STEP 1: AUTHENTICATION CHECK (ALREADY DONE)
            # ============================================================
            # Authentication is validated by validate_request dependency
            # If we reach here, user is authenticated (token is valid)
            # current_user is guaranteed to be a valid, authenticated User

            # Extract user_id from authenticated user
            user_id = str(current_user.uid) if hasattr(current_user, 'uid') else str(getattr(current_user, 'user_id', ''))

            # Double-check: If user_id is missing, this is an auth issue
            if not user_id:
                logger.error("Authentication check passed but user_id is missing", module="Permissions", label="GROUP_CHECK")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,  # Changed to 401 (auth issue, not permission)
                    detail=ERROR.build(
                        "UNAUTHORIZED",
                        details={
                            "message": "User authentication incomplete - user_id not found",
                            "check": "authentication"
                        }
                    )
                )

            # ============================================================
            # STEP 2: GROUP CHECK (NOW CHECKING)
            # ============================================================
            # Now that authentication is confirmed, check groups

            # 2.1: Check superuser bypass first (super_admin group bypasses all group checks)
            try:
                user_groups = get_user_groups(user_id)
                is_superuser = any(g.get('codename') == 'super_admin' for g in user_groups)
                if is_superuser:
                    return current_user
            except Exception as error:
                logger.warning(f"Error checking superuser status: {error}", module="Permissions", label="GROUP_CHECK")
                # Continue with normal group check if superuser check fails

            # 2.2: Get user groups
            user_groups = get_user_groups(user_id)
            user_group_codenames = [g.get('codename') for g in user_groups]

            # 2.3: Normalize groups to list
            groups = [required_groups] if isinstance(required_groups, str) else required_groups

            # 2.4: Check if user has any of the required groups
            has_group = any(group in user_group_codenames for group in groups)

            if not has_group:
                logger.warning(f"Group check FAILED: User {user_id} missing required groups {groups} (has: {user_group_codenames})", module="Permissions", label="GROUP_CHECK")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=ERROR.build(
                        "FORBIDDEN",
                        details={
                            "message": f"Missing required group. Required one of: {', '.join(groups)}",
                            "required_groups": groups,
                            "user_groups": user_group_codenames,
                            "check": "group",
                            "user_id": user_id
                        }
                    )
                )

            # All checks passed - return authenticated and authorized user
            return current_user

        except HTTPException:
            raise
        except Exception as error:
            logger.error(f"Error in group check: {error}", exc_info=True, module="Permissions", label="GROUP_CHECK")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR.build("AUTH_PROCESSING_ERROR", exception=error)
            )

    return group_checker


# Example usage:
"""
from fastapi import APIRouter
from src.middleware.permission_middleware import check_permission, check_group
from src.authenticate.models import User

router = APIRouter()

# Single permission check
@router.get("/users")
async def get_users(current_user: User = Depends(check_permission("view_users"))):
    return {"message": "Users list"}

# Multiple permissions - ANY permission required
@router.post("/users")
async def create_user(current_user: User = Depends(check_permission(["add_users", "create_users"]))):
    return {"message": "User created"}

# Multiple permissions - ALL permissions required
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(check_permission(["delete_users", "manage_users"], require_all=True))
):
    return {"message": "User deleted"}

# Group check
@router.get("/admin/dashboard")
async def admin_dashboard(current_user: User = Depends(check_group("admin"))):
    return {"message": "Admin dashboard"}

# Multiple groups - user needs ANY of these groups
@router.get("/moderator/content")
async def moderator_content(current_user: User = Depends(check_group(["admin", "moderator"]))):
    return {"message": "Moderator content"}
"""

