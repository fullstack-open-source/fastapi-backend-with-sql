"""
Permissions Router
Handles permissions and groups management
"""

from fastapi import APIRouter, Depends, HTTPException
from src.middleware.permission_middleware import check_permission
from src.authenticate.models import User
from src.response.success import SUCCESS
from src.response.error import ERROR
from src.logger.logger import logger
from src.multilingual.multilingual import normalize_language
from .models import (
    PermissionCreate, PermissionUpdate,
    GroupCreate, GroupUpdate,
    AssignPermissionsRequest, AssignGroupsRequest
)
from .query import (
    get_all_permissions, get_permission_by_id, create_permission,
    update_permission, delete_permission,
    get_all_groups, get_group_by_id, create_group,
    update_group, delete_group,
    assign_permissions_to_group,
    get_user_groups as query_get_user_groups, get_user_permissions, assign_groups_to_user
)

router = APIRouter()

@router.get("/permissions")
async def get_permissions(current_user: User = Depends(check_permission("view_permission"))):
    """
    Get all permissions.

    Required Permission: view_permission
    Returns list of all permissions in the system.
    """
    try:
        perms = get_all_permissions()
        return SUCCESS.response(
            message="Permissions retrieved successfully",
            data={"permissions": perms},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error getting permissions: {e}", exc_info=True, module="Permissions", label="GET_PERMISSIONS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("INTERNAL_ERROR", exception=str(e))
        )

@router.get("/permissions/{permission_id}")
async def get_permission(permission_id: str, current_user: User = Depends(check_permission("view_permission"))):
    """
    Get permission by ID.

    Required Permission: view_permission
    Returns a specific permission by ID.
    """
    try:
        perm = get_permission_by_id(permission_id)
        if not perm:
            raise HTTPException(
                status_code=404,
                detail=ERROR.build("USER_NOT_FOUND", details={"permission_id": permission_id})
            )
        return SUCCESS.response(
            message="Permission retrieved successfully",
            data={"permission": perm},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting permission: {e}", exc_info=True, module="Permissions", label="GET_PERMISSION")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("INTERNAL_ERROR", exception=str(e))
        )

@router.post("/permissions")
async def create_permission(payload: PermissionCreate, current_user: User = Depends(check_permission("add_permission"))):
    """
    Create new permission.

    Required Permission: add_permission
    Creates a new permission in the system.
    """
    try:
        perm = create_permission(payload.dict())
        return SUCCESS.response(
            message="Permission created successfully",
            data={"permission": perm},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error creating permission: {e}", exc_info=True, module="Permissions", label="CREATE_PERMISSION")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("PERMISSION_CREATE_FAILED", exception=str(e))
        )

@router.put("/permissions/{permission_id}")
async def update_permission(permission_id: str, payload: PermissionUpdate, current_user: User = Depends(check_permission("edit_permission"))):
    """
    Update permission.

    Required Permission: edit_permission
    Updates an existing permission.
    """
    try:
        perm = update_permission(permission_id, payload.dict(exclude_unset=True))
        if not perm:
            raise HTTPException(
                status_code=404,
                detail=ERROR.build("PERMISSION_NOT_FOUND", details={"permission_id": permission_id})
            )
        return SUCCESS.response(
            message="Permission updated successfully",
            data={"permission": perm},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating permission: {e}", exc_info=True, module="Permissions", label="UPDATE_PERMISSION")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("PERMISSION_UPDATE_FAILED", exception=str(e))
        )

@router.delete("/permissions/{permission_id}")
async def delete_permission(permission_id: str, current_user: User = Depends(check_permission("delete_permission"))):
    """
    Delete permission.

    Required Permission: delete_permission
    Deletes a permission from the system.
    """
    try:
        deleted = delete_permission(permission_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=ERROR.build("PERMISSION_NOT_FOUND", details={"permission_id": permission_id})
            )
        return SUCCESS.response(
            message="Permission deleted successfully",
            data={"permission_id": permission_id},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting permission: {e}", exc_info=True, module="Permissions", label="DELETE_PERMISSION")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("PERMISSION_DELETE_FAILED", exception=str(e))
        )

@router.get("/groups")
async def get_groups(current_user: User = Depends(check_permission("view_group"))):
    """
    Get all groups.

    Required Permission: view_group
    Returns list of all groups with their permissions.
    """
    try:
        groups = get_all_groups()
        return SUCCESS.response(
            message="Groups retrieved successfully",
            data={"groups": groups},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error getting groups: {e}", exc_info=True, module="Permissions", label="GET_GROUPS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("INTERNAL_ERROR", exception=str(e))
        )

@router.get("/groups/{group_id}")
async def get_group(group_id: str, current_user: User = Depends(check_permission("view_group"))):
    """
    Get group by ID.

    Required Permission: view_group
    Returns a specific group with its permissions.
    """
    try:
        group = get_group_by_id(group_id)
        if not group:
            raise HTTPException(
                status_code=404,
                detail=ERROR.build("GROUP_NOT_FOUND", details={"group_id": group_id})
            )
        return SUCCESS.response(
            message="Group retrieved successfully",
            data={"group": group},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting group: {e}", exc_info=True, module="Permissions", label="GET_GROUP")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("INTERNAL_ERROR", exception=str(e))
        )

@router.post("/groups")
async def create_group_endpoint(payload: GroupCreate, current_user: User = Depends(check_permission("add_group"))):
    """
    Create new group.

    Required Permission: add_group
    Creates a new group in the system.
    """
    try:
        group = create_group(payload.dict())
        return SUCCESS.response(
            message="Group created successfully",
            data={"group": group},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error creating group: {e}", exc_info=True, module="Permissions", label="CREATE_GROUP")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("GROUP_CREATE_FAILED", exception=str(e))
        )

@router.put("/groups/{group_id}")
async def update_group_endpoint(group_id: str, payload: GroupUpdate, current_user: User = Depends(check_permission("edit_group"))):
    """
    Update group.

    Required Permission: edit_group
    Updates an existing group.
    """
    try:
        group = update_group(group_id, payload.dict(exclude_unset=True))
        if not group:
            raise HTTPException(
                status_code=404,
                detail=ERROR.build("GROUP_NOT_FOUND", details={"group_id": group_id})
            )
        return SUCCESS.response(
            message="Group updated successfully",
            data={"group": group},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating group: {e}", exc_info=True, module="Permissions", label="UPDATE_GROUP")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("GROUP_UPDATE_FAILED", exception=str(e))
        )

@router.delete("/groups/{group_id}")
async def delete_group(group_id: str, current_user: User = Depends(check_permission("delete_group"))):
    """
    Delete group.

    Required Permission: delete_group
    Deletes a group from the system.
    """
    try:
        deleted = delete_group(group_id)
        if not deleted:
            raise HTTPException(
                status_code=400,
                detail=ERROR.build("GROUP_DELETE_FAILED", details={"message": "Group not found or is a system group"})
            )
        return SUCCESS.response(
            message="Group deleted successfully",
            data={"group_id": group_id},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting group: {e}", exc_info=True, module="Permissions", label="DELETE_GROUP")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("GROUP_DELETE_FAILED", exception=str(e))
        )

@router.post("/groups/{group_id}/permissions")
async def assign_permissions_to_group(group_id: str, payload: AssignPermissionsRequest, current_user: User = Depends(check_permission("edit_group"))):
    """
    Assign permissions to group.

    Required Permission: edit_group
    Assigns permissions to a group.
    """
    try:
        assign_permissions_to_group(group_id, payload.permission_ids)
        group = get_group_by_id(group_id)
        return SUCCESS.response(
            message="Permissions assigned successfully",
            data={"group": group},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error assigning permissions to group: {e}", exc_info=True, module="Permissions", label="ASSIGN_PERMISSIONS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("GROUP_ASSIGN_PERMISSIONS_FAILED", exception=str(e))
        )

@router.get("/users/{user_id}/groups")
async def get_user_groups(user_id: str, current_user: User = Depends(check_permission("view_user"))):
    """
    Get user groups.

    Required Permission: view_user
    Returns all groups assigned to a user.
    """
    try:
        groups = query_get_user_groups(user_id)
        return SUCCESS.response(
            message="User groups retrieved successfully",
            data={"user_id": user_id, "groups": groups},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error getting user groups: {e}", exc_info=True, module="Permissions", label="GET_USER_GROUPS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("INTERNAL_ERROR", exception=str(e))
        )

@router.get("/users/{user_id}/permissions")
async def get_user_permissions(user_id: str, current_user: User = Depends(check_permission("view_user"))):
    """
    Get user permissions.

    Required Permission: view_user
    Returns all permissions for a user (from all groups).
    """
    try:
        perms = get_user_permissions(user_id)
        return SUCCESS.response(
            message="User permissions retrieved successfully",
            data={"user_id": user_id, "permissions": perms},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error getting user permissions: {e}", exc_info=True, module="Permissions", label="GET_USER_PERMISSIONS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("INTERNAL_ERROR", exception=str(e))
        )

@router.post("/users/{user_id}/groups")
async def assign_groups_to_user(user_id: str, payload: AssignGroupsRequest, current_user: User = Depends(check_permission("assign_groups"))):
    """
    Assign groups to user.

    Required Permission: assign_groups
    Assigns groups to a user (replaces existing groups).
    """
    try:
        assigned_by = current_user.uid if current_user else None
        assign_groups_to_user(user_id, payload.group_codenames, assigned_by)
        groups = get_user_groups(user_id)
        return SUCCESS.response(
            message="Groups assigned successfully (user role flags updated)",
            data={"user_id": user_id, "groups": groups},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error assigning groups to user: {e}", exc_info=True, module="Permissions", label="ASSIGN_GROUPS_TO_USER")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("GROUP_ASSIGN_USERS_FAILED", exception=str(e))
        )

@router.get("/users/me/groups")
async def get_my_groups(current_user: User = Depends(check_permission("view_profile"))):
    """
    Get current user groups.

    Required Permission: view_profile
    Returns all groups assigned to the current user.
    """
    try:
        groups = get_user_groups(str(current_user.uid))
        return SUCCESS.response(
            message="User groups retrieved successfully",
            data={"groups": groups},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error getting current user groups: {e}", exc_info=True, module="Permissions", label="GET_MY_GROUPS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("INTERNAL_ERROR", exception=str(e))
        )

@router.get("/users/me/permissions")
async def get_my_permissions(current_user: User = Depends(check_permission("view_profile"))):
    """
    Get current user permissions.

    Required Permission: view_profile
    Returns all permissions for the current user.
    """
    try:
        perms = get_user_permissions(str(current_user.uid))
        return SUCCESS.response(
            message="User permissions retrieved successfully",
            data={"permissions": perms},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error getting current user permissions: {e}", exc_info=True, module="Permissions", label="GET_MY_PERMISSIONS")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build("INTERNAL_ERROR", exception=str(e))
        )

