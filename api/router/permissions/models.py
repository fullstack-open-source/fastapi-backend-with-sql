"""
Permissions Router - Models
Pydantic models for request/response validation
"""
from pydantic import BaseModel
from typing import List, Optional


class PermissionCreate(BaseModel):
    name: str
    codename: str
    description: Optional[str] = None
    category: Optional[str] = None


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    codename: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class GroupCreate(BaseModel):
    name: str
    codename: str
    description: Optional[str] = None
    is_system: Optional[bool] = False
    is_active: Optional[bool] = True


class GroupUpdate(BaseModel):
    name: Optional[str] = None
    codename: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AssignPermissionsRequest(BaseModel):
    permission_ids: List[str]


class AssignGroupsRequest(BaseModel):
    group_codenames: List[str]

