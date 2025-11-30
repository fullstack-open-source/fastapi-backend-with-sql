# Permissions & Groups Router

> **Complete Documentation for Permission and Group Management Endpoints**

This router handles all permission and group management operations including CRUD operations for permissions and groups, assigning permissions to groups, and managing user-group relationships.

## 📋 Table of Contents

- [Overview](#overview)
- [Endpoints](#endpoints)
  - [Permissions](#permissions)
  - [Groups](#groups)
  - [User Permissions & Groups](#user-permissions--groups)
- [Workflows](#workflows)
- [Error Handling](#error-handling)
- [Client-Side Implementation](#client-side-implementation)
- [Summary](#summary)

## Overview

The Permissions & Groups router provides comprehensive role-based access control (RBAC) functionality including:
- **Permission Management**: Create, read, update, and delete permissions
- **Group Management**: Create, read, update, and delete groups
- **Permission Assignment**: Assign permissions to groups
- **User-Group Assignment**: Assign groups to users
- **Permission Queries**: Get user permissions and groups

**Base Path:** `/{MODE}/permissions`, `/{MODE}/groups`, `/{MODE}/users`

**Authentication:** All endpoints require authentication

**Permissions:** Various permissions required (see each endpoint)

## Endpoints

### Permissions

#### Get All Permissions

**Endpoint:** `GET /{MODE}/permissions`

**Description:** Get list of all permissions in the system.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `view_permission`

**Request Headers:**
```
Authorization: Bearer <access_token>
# OR
X-Session-Token: <session_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Permissions retrieved successfully",
  "data": {
    "permissions": [
      {
        "permission_id": "uuid",
        "name": "View Dashboard",
        "codename": "view_dashboard",
        "description": "Permission to view dashboard",
        "category": "dashboard"
      }
    ]
  }
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Client prepares request
  ├─► Admin navigates to permissions management page
  ├─► Retrieve stored access_token or session_token
  ├─► Add token to Authorization header or X-Session-Token header
  └─► Prepare GET request to /{MODE}/permissions

Step 2: Client sends request
  GET /{MODE}/permissions
  Headers:
    Authorization: Bearer <token>
    # OR
    X-Session-Token: <session_token>

Step 3: Client receives response
  ├─► Success (200): Display permissions list in UI
  ├─► Unauthorized (401): Redirect to login
  ├─► Forbidden (403): Show permission error
  └─► Error (500): Show error message

Step 4: Client processes data
  ├─► Extract permissions array from response.data.permissions
  ├─► Render permissions table/list
  ├─► Group by category if needed
  └─► Enable edit/delete actions based on permissions

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token (JWT verification)
  ├─► Check token blacklist
  └─► Extract user from token

Step 2: Permission check
  ├─► Check if user has "view_permission" permission
  └─► If no permission: Return 403 Forbidden

Step 3: Database query
  ├─► Query all permissions from database
  ├─► Fetch permission fields (permission_id, name, codename, description, category)
  └─► Order by category or name

Step 4: Response preparation
  ├─► Build SUCCESS response
  ├─► Include permissions array in data.permissions
  └─► Return response with user's language preference

Step 5: Error handling
  ├─► Database error: Log error, return 500
  ├─► Permission denied: Return 403
  └─► Token invalid: Return 401
```

**Error Responses:**

```json
// 403 - Permission Denied
{
  "success": false,
  "id": null,
  "message": "Permission denied",
  "error": {
    "code": "PERMISSION_DENIED",
    "details": {
      "required_permission": "view_permission"
    }
  }
}

// 500 - Server Error
{
  "success": false,
  "id": null,
  "message": "Internal server error",
  "error": {
    "code": "INTERNAL_ERROR",
    "details": {
      "exception": "Error details"
    }
  }
}
```

---

#### Get Permission by ID

**Endpoint:** `GET /{MODE}/permissions/:permission_id`

**Description:** Get a specific permission by ID.

**Authentication:** Required
**Permission:** `view_permission`

**Parameters:**
- `permission_id` (path): Permission UUID

**Response:**
```json
{
  "success": true,
  "message": "Permission retrieved successfully",
  "data": {
    "permission": {
      "permission_id": "uuid",
      "name": "View Dashboard",
      "codename": "view_dashboard",
      "description": "Permission to view dashboard",
      "category": "dashboard"
    }
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (view_permission)
   │
   ├─► Get Permission by ID
   │   └─► prisma.permission.findUnique()
   │
   └─► Return Permission Data
```

---

#### Create Permission

**Endpoint:** `POST /{MODE}/permissions`

**Description:** Create a new permission.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `add_permission`

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
# OR
X-Session-Token: <session_token>
```

**Request Body:**
```json
{
  "name": "View Dashboard",
  "codename": "view_dashboard",
  "description": "Permission to view dashboard",
  "category": "dashboard"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Permission created successfully",
  "data": {
    "permission": {
      "permission_id": "uuid",
      "name": "View Dashboard",
      "codename": "view_dashboard",
      "description": "Permission to view dashboard",
      "category": "dashboard"
    }
  }
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User fills permission form
  ├─► User enters permission name
  ├─► User enters codename (lowercase with underscores)
  ├─► User enters description (optional)
  ├─► User selects category (optional)
  └─► User clicks "Create" button

Step 2: Client validates form
  ├─► Validate name is not empty
  ├─► Validate codename format (lowercase, underscores)
  ├─► Check codename uniqueness (client-side check)
  └─► Prepare request payload

Step 3: Client sends request
  POST /{MODE}/permissions
  Headers:
    Authorization: Bearer <token>
    Content-Type: application/json
  Body:
    {
      "name": "View Dashboard",
      "codename": "view_dashboard",
      "description": "Permission to view dashboard",
      "category": "dashboard"
    }

Step 4: Client receives response
  ├─► Success (200): Add permission to list, show success message
  ├─► Bad Request (400): Show validation errors
  ├─► Conflict (409): Show duplicate codename error
  ├─► Unauthorized (401): Redirect to login
  ├─► Forbidden (403): Show permission error
  └─► Error (500): Show error message

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token
  ├─► Extract user from token
  ├─► Parse request body (PermissionCreate model)
  └─► Check permission: "add_permission"

Step 2: Data validation
  ├─► Validate name is provided and not empty
  ├─► Validate codename is provided
  ├─► Validate codename format (lowercase, underscores, alphanumeric)
  ├─► Check codename uniqueness in database
  └─► If duplicate: Return 409 Conflict

Step 3: Create permission
  ├─► Insert permission into database
  ├─► Generate permission_id (UUID)
  ├─► Set created_at timestamp
  └─► Return created permission

Step 4: Response preparation
  ├─► Build SUCCESS response
  ├─► Include created permission in data.permission
  └─► Return response with user's language preference

Step 5: Error handling
  ├─► Validation error: Return 400
  ├─► Duplicate codename: Return 409
  ├─► Permission denied: Return 403
  ├─► Database error: Log error, return 500
  └─► Token invalid: Return 401
```

---

#### Update Permission

**Endpoint:** `PUT /{MODE}/permissions/:permission_id`

**Description:** Update an existing permission.

**Authentication:** Required
**Permission:** `edit_permission`

**Parameters:**
- `permission_id` (path): Permission UUID

**Request Body:**
```json
{
  "name": "View Dashboard Updated",
  "description": "Updated description"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Permission updated successfully",
  "data": {
    "permission": { ... }
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (edit_permission)
   │
   ├─► Update Permission
   │   └─► prisma.permission.update()
   │
   └─► Return Updated Permission
```

---

#### Delete Permission

**Endpoint:** `DELETE /{MODE}/permissions/:permission_id`

**Description:** Delete a permission. Removes permission from all groups.

**Authentication:** Required
**Permission:** `delete_permission`

**Parameters:**
- `permission_id` (path): Permission UUID

**Response:**
```json
{
  "success": true,
  "message": "Permission deleted successfully",
  "data": { ... }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (delete_permission)
   │
   ├─► Delete Permission
   │   └─► prisma.permission.delete()
   │       └─► Cascade deletes GroupPermission entries
   │
   └─► Return Success Response
```

---

### Groups

#### Get All Groups

**Endpoint:** `GET /{MODE}/groups`

**Description:** Get list of all groups with their permissions.

**Authentication:** Required
**Permission:** `view_group`

**Response:**
```json
{
  "success": true,
  "message": "Groups retrieved successfully",
  "data": {
    "groups": [
      {
        "group_id": "uuid",
        "name": "Admin",
        "codename": "admin",
        "description": "Administrator group",
        "is_system": true,
        "is_active": true,
        "permissions": [
          {
            "permission_id": "uuid",
            "name": "View Dashboard",
            "codename": "view_dashboard"
          }
        ]
      }
    ]
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (view_group)
   │
   ├─► Get All Groups with Permissions
   │   └─► prisma.group.findMany({ include: { permissions } })
   │
   └─► Return Groups List
```

---

#### Get Group by ID

**Endpoint:** `GET /{MODE}/groups/:group_id`

**Description:** Get a specific group with its permissions.

**Authentication:** Required
**Permission:** `view_group`

**Parameters:**
- `group_id` (path): Group UUID

**Response:**
```json
{
  "success": true,
  "message": "Group retrieved successfully",
  "data": {
    "group": {
      "group_id": "uuid",
      "name": "Admin",
      "codename": "admin",
      "permissions": [ ... ]
    }
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (view_group)
   │
   ├─► Get Group by ID with Permissions
   │   └─► prisma.group.findUnique({ include: { permissions } })
   │
   └─► Return Group Data
```

---

#### Create Group

**Endpoint:** `POST /{MODE}/groups`

**Description:** Create a new group.

**Authentication:** Required
**Permission:** `add_group`

**Request Body:**
```json
{
  "name": "Moderator",
  "codename": "moderator",
  "description": "Moderator group",
  "is_system": false,
  "is_active": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Group created successfully",
  "data": {
    "group": { ... }
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (add_group)
   │
   ├─► Validate Request Data
   │   ├─► name required
   │   ├─► codename required
   │   └─► codename must be unique
   │
   ├─► Create Group
   │   └─► prisma.group.create()
   │
   └─► Return Created Group
```

---

#### Update Group

**Endpoint:** `PUT /{MODE}/groups/:group_id`

**Description:** Update an existing group.

**Authentication:** Required
**Permission:** `edit_group`

**Parameters:**
- `group_id` (path): Group UUID

**Request Body:**
```json
{
  "name": "Moderator Updated",
  "description": "Updated description",
  "is_active": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Group updated successfully",
  "data": {
    "group": { ... }
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (edit_group)
   │
   ├─► Update Group
   │   └─► prisma.group.update()
   │
   └─► Return Updated Group
```

---

#### Delete Group

**Endpoint:** `DELETE /{MODE}/groups/:group_id`

**Description:** Delete a group. System groups cannot be deleted.

**Authentication:** Required
**Permission:** `delete_group`

**Parameters:**
- `group_id` (path): Group UUID

**Response:**
```json
{
  "success": true,
  "message": "Group deleted successfully",
  "data": {
    "group_id": "uuid"
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (delete_group)
   │
   ├─► Check if System Group
   │   └─► If is_system = true, reject deletion
   │
   ├─► Delete Group
   │   └─► prisma.group.delete()
   │       └─► Cascade deletes GroupPermission and UserGroup entries
   │
   └─► Return Success Response
```

**Note:** System groups (is_system = true) cannot be deleted.

---

#### Assign Permissions to Group

**Endpoint:** `POST /{MODE}/groups/:group_id/permissions`

**Description:** Assign permissions to a group. Replaces existing permissions.

**Authentication:** Required
**Permission:** `edit_group`

**Parameters:**
- `group_id` (path): Group UUID

**Request Body:**
```json
{
  "permission_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Permissions assigned successfully",
  "data": {
    "group": {
      "group_id": "uuid",
      "permissions": [ ... ]
    }
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (edit_group)
   │
   ├─► Validate Request
   │   └─► permission_ids must be array
   │
   ├─► Delete Existing Permissions
   │   └─► prisma.groupPermission.deleteMany()
   │
   ├─► Create New Permission Assignments
   │   └─► prisma.groupPermission.createMany()
   │
   ├─► Get Updated Group with Permissions
   │
   └─► Return Updated Group
```

---

### User Permissions & Groups

#### Get User Groups

**Endpoint:** `GET /{MODE}/users/:user_id/groups`

**Description:** Get all groups assigned to a user.

**Authentication:** Required
**Permission:** `view_user`

**Parameters:**
- `user_id` (path): User UUID

**Response:**
```json
{
  "success": true,
  "message": "User groups retrieved successfully",
  "data": {
    "user_id": "uuid",
    "groups": [
      {
        "group_id": "uuid",
        "name": "Admin",
        "codename": "admin"
      }
    ]
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (view_user)
   │
   ├─► Get User Groups
   │   └─► getUserGroups(user_id)
   │
   └─► Return User Groups
```

---

#### Get User Permissions

**Endpoint:** `GET /{MODE}/users/:user_id/permissions`

**Description:** Get all permissions for a user (from all groups).

**Authentication:** Required
**Permission:** `view_user`

**Parameters:**
- `user_id` (path): User UUID

**Response:**
```json
{
  "success": true,
  "message": "User permissions retrieved successfully",
  "data": {
    "user_id": "uuid",
    "permissions": [
      {
        "permission_id": "uuid",
        "name": "View Dashboard",
        "codename": "view_dashboard"
      }
    ]
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (view_user)
   │
   ├─► Get User Permissions
   │   └─► getUserPermissions(user_id)
   │       └─► Aggregates permissions from all user groups
   │
   └─► Return User Permissions
```

---

#### Assign Groups to User

**Endpoint:** `POST /{MODE}/users/:user_id/groups`

**Description:** Assign groups to a user. Uses group codenames. Updates user role flags.

**Authentication:** Required
**Permission:** `assign_groups`

**Parameters:**
- `user_id` (path): User UUID

**Request Body:**
```json
{
  "group_codenames": ["admin", "user"]
}
```

**Valid Codenames:** `super_admin`, `admin`, `developer`, `business`, `accountant`, `user`

**Response:**
```json
{
  "success": true,
  "message": "Groups assigned successfully (user role flags updated)",
  "data": {
    "user_id": "uuid",
    "groups": [ ... ]
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (assign_groups)
   │
   ├─► Validate Request
   │   ├─► group_codenames must be array
   │   └─► Validate codenames (must be valid)
   │
   ├─► Get Assigned By User ID
   │   └─► From JWT token
   │
   ├─► Assign Groups to User
   │   ├─► Delete existing UserGroup entries
   │   ├─► Create new UserGroup entries
   │   └─► Update user role flags (is_superuser, is_admin, etc.)
   │
   ├─► Get Updated User Groups
   │
   └─► Return User Groups
```

**Note:** This endpoint updates user role flags (is_superuser, is_admin, etc.) based on assigned groups.

---

#### Get My Groups

**Endpoint:** `GET /{MODE}/users/me/groups`

**Description:** Get all groups for the current authenticated user.

**Authentication:** Required
**Permission:** `view_profile`

**Response:**
```json
{
  "success": true,
  "message": "User groups retrieved successfully",
  "data": {
    "groups": [ ... ]
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (view_profile)
   │
   ├─► Get Current User ID
   │   └─► From JWT token
   │
   ├─► Get User Groups
   │   └─► getUserGroups(userId)
   │
   └─► Return User Groups
```

---

#### Get My Permissions

**Endpoint:** `GET /{MODE}/users/me/permissions`

**Description:** Get all permissions for the current authenticated user.

**Authentication:** Required
**Permission:** `view_profile`

**Response:**
```json
{
  "success": true,
  "message": "User permissions retrieved successfully",
  "data": {
    "permissions": [ ... ]
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (view_profile)
   │
   ├─► Get Current User ID
   │   └─► From JWT token
   │
   ├─► Get User Permissions
   │   └─► getUserPermissions(userId)
   │
   └─► Return User Permissions
```

---

## Workflows

### Complete Permission Management Flow

```
┌─────────────────────────────────────────────────────────────┐
│          Permission & Group Management Flow                 │
└────────────────────────────┬────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
        ┌───────────────┐         ┌───────────────┐
        │  Permissions  │         │    Groups     │
        └───────┬───────┘         └───────┬───────┘
                │                           │
        ┌───────┴───────┐         ┌───────┴───────┐
        │               │         │               │
        ▼               ▼         ▼               ▼
    Create/Read    Update/Delete  Create/Read  Update/Delete
        │               │         │               │
        └───────┬───────┘         └───────┬───────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Assign Permissions│
                    │   to Groups       │
                    └────────┬──────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Assign Groups   │
                    │   to Users      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ User Permissions │
                    │   (Aggregated)   │
                    └──────────────────┘
```

### User Permission Resolution Flow

```
1. User Makes Request
   │
   ├─► Extract JWT Token
   │
   ├─► Get User ID from Token
   │
   ├─► Get User Groups
   │   └─► Query UserGroup table
   │
   ├─► Get Group Permissions
   │   └─► Query GroupPermission for each group
   │
   ├─► Aggregate Permissions
   │   └─► Combine all permissions from all groups
   │
   └─► Check Required Permission
       └─► Verify permission exists in aggregated list
```

## Error Handling

### Common Error Responses

**400 Bad Request - Invalid Payload:**
```json
{
  "success": false,
  "message": "Invalid request payload",
  "error": "name and codename are required",
  "statusCode": 400
}
```

**403 Forbidden - Permission Denied:**
```json
{
  "success": false,
  "message": "Permission denied",
  "error": "Insufficient permissions",
  "statusCode": 403
}
```

**404 Not Found:**
```json
{
  "success": false,
  "message": "Group not found",
  "error": "Group with provided ID does not exist",
  "statusCode": 404
}
```

**409 Conflict - Duplicate Entry:**
```json
{
  "success": false,
  "message": "Duplicate entry",
  "error": "Group with this name or codename already exists",
  "statusCode": 409
}
```

---

## Best Practices

1. **Permission Codenames**: Use lowercase with underscores (e.g., `view_dashboard`)
2. **Group Codenames**: Use lowercase (e.g., `admin`, `user`)
3. **System Groups**: Don't delete system groups (is_system = true)
4. **Permission Assignment**: Assign permissions to groups, not directly to users
5. **Group Assignment**: Assign groups to users, not permissions directly
6. **Permission Aggregation**: User permissions are aggregated from all assigned groups
7. **Role Flags**: User role flags are automatically updated when groups are assigned
8. **Validation**: Always validate permission/group codenames before assignment

---

## Client-Side Implementation

### Token Management

```javascript
// Get authentication token (prefer session_token)
function getAuthToken() {
  return localStorage.getItem('session_token') || 
         localStorage.getItem('access_token');
}

// API request helper for permissions endpoints
async function permissionsRequest(url, options = {}) {
  const token = getAuthToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  // Prefer X-Session-Token header
  if (token) {
    headers['X-Session-Token'] = token;
    // Or use Authorization header
    // headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers
  });
  
  if (response.status === 401) {
    // Token expired, redirect to login
    window.location.href = '/login';
    return null;
  }
  
  if (response.status === 403) {
    // Permission denied
    throw new Error('You do not have permission to perform this action');
  }
  
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error?.message || 'Request failed');
  }
  
  return data;
}
```

### Permissions Management

```javascript
// Get all permissions
async function getPermissions() {
  try {
    const response = await permissionsRequest('/api/v1/permissions', {
      method: 'GET'
    });
    
    if (response && response.data) {
      return response.data.permissions;
    }
  } catch (error) {
    console.error('Error fetching permissions:', error);
    showError('Failed to load permissions');
    throw error;
  }
}

// Get permission by ID
async function getPermission(permissionId) {
  try {
    const response = await permissionsRequest(
      `/api/v1/permissions/${permissionId}`,
      { method: 'GET' }
    );
    
    if (response && response.data) {
      return response.data.permission;
    }
  } catch (error) {
    console.error('Error fetching permission:', error);
    showError('Failed to load permission');
    throw error;
  }
}

// Create permission
async function createPermission(permissionData) {
  try {
    // Validate codename format
    if (!/^[a-z][a-z0-9_]*$/.test(permissionData.codename)) {
      throw new Error('Codename must be lowercase with underscores');
    }
    
    const response = await permissionsRequest('/api/v1/permissions', {
      method: 'POST',
      body: JSON.stringify(permissionData)
    });
    
    if (response && response.data) {
      showNotification('Permission created successfully');
      return response.data.permission;
    }
  } catch (error) {
    console.error('Error creating permission:', error);
    showError(error.message || 'Failed to create permission');
    throw error;
  }
}

// Update permission
async function updatePermission(permissionId, updateData) {
  try {
    const response = await permissionsRequest(
      `/api/v1/permissions/${permissionId}`,
      {
        method: 'PUT',
        body: JSON.stringify(updateData)
      }
    );
    
    if (response && response.data) {
      showNotification('Permission updated successfully');
      return response.data.permission;
    }
  } catch (error) {
    console.error('Error updating permission:', error);
    showError('Failed to update permission');
    throw error;
  }
}

// Delete permission
async function deletePermission(permissionId) {
  try {
    const confirmed = confirm('Are you sure you want to delete this permission?');
    if (!confirmed) {
      return;
    }
    
    const response = await permissionsRequest(
      `/api/v1/permissions/${permissionId}`,
      { method: 'DELETE' }
    );
    
    if (response) {
      showNotification('Permission deleted successfully');
      return true;
    }
  } catch (error) {
    console.error('Error deleting permission:', error);
    showError('Failed to delete permission');
    throw error;
  }
}
```

### Groups Management

```javascript
// Get all groups
async function getGroups() {
  try {
    const response = await permissionsRequest('/api/v1/groups', {
      method: 'GET'
    });
    
    if (response && response.data) {
      return response.data.groups;
    }
  } catch (error) {
    console.error('Error fetching groups:', error);
    showError('Failed to load groups');
    throw error;
  }
}

// Get group by ID
async function getGroup(groupId) {
  try {
    const response = await permissionsRequest(
      `/api/v1/groups/${groupId}`,
      { method: 'GET' }
    );
    
    if (response && response.data) {
      return response.data.group;
    }
  } catch (error) {
    console.error('Error fetching group:', error);
    showError('Failed to load group');
    throw error;
  }
}

// Create group
async function createGroup(groupData) {
  try {
    // Validate codename format
    if (!/^[a-z][a-z0-9_]*$/.test(groupData.codename)) {
      throw new Error('Codename must be lowercase with underscores');
    }
    
    const response = await permissionsRequest('/api/v1/groups', {
      method: 'POST',
      body: JSON.stringify(groupData)
    });
    
    if (response && response.data) {
      showNotification('Group created successfully');
      return response.data.group;
    }
  } catch (error) {
    console.error('Error creating group:', error);
    showError(error.message || 'Failed to create group');
    throw error;
  }
}

// Update group
async function updateGroup(groupId, updateData) {
  try {
    const response = await permissionsRequest(
      `/api/v1/groups/${groupId}`,
      {
        method: 'PUT',
        body: JSON.stringify(updateData)
      }
    );
    
    if (response && response.data) {
      showNotification('Group updated successfully');
      return response.data.group;
    }
  } catch (error) {
    console.error('Error updating group:', error);
    showError('Failed to update group');
    throw error;
  }
}

// Delete group
async function deleteGroup(groupId) {
  try {
    const confirmed = confirm(
      'Are you sure you want to delete this group? This will remove all user assignments.'
    );
    if (!confirmed) {
      return;
    }
    
    const response = await permissionsRequest(
      `/api/v1/groups/${groupId}`,
      { method: 'DELETE' }
    );
    
    if (response) {
      showNotification('Group deleted successfully');
      return true;
    }
  } catch (error) {
    console.error('Error deleting group:', error);
    showError('Failed to delete group');
    throw error;
  }
}

// Assign permissions to group
async function assignPermissionsToGroup(groupId, permissionIds) {
  try {
    const response = await permissionsRequest(
      `/api/v1/groups/${groupId}/permissions`,
      {
        method: 'POST',
        body: JSON.stringify({ permission_ids: permissionIds })
      }
    );
    
    if (response && response.data) {
      showNotification('Permissions assigned successfully');
      return response.data.group;
    }
  } catch (error) {
    console.error('Error assigning permissions:', error);
    showError('Failed to assign permissions');
    throw error;
  }
}
```

### User Permissions & Groups

```javascript
// Get user groups
async function getUserGroups(userId) {
  try {
    const response = await permissionsRequest(
      `/api/v1/users/${userId}/groups`,
      { method: 'GET' }
    );
    
    if (response && response.data) {
      return response.data.groups;
    }
  } catch (error) {
    console.error('Error fetching user groups:', error);
    showError('Failed to load user groups');
    throw error;
  }
}

// Get user permissions
async function getUserPermissions(userId) {
  try {
    const response = await permissionsRequest(
      `/api/v1/users/${userId}/permissions`,
      { method: 'GET' }
    );
    
    if (response && response.data) {
      return response.data.permissions;
    }
  } catch (error) {
    console.error('Error fetching user permissions:', error);
    showError('Failed to load user permissions');
    throw error;
  }
}

// Assign groups to user
async function assignGroupsToUser(userId, groupCodenames) {
  try {
    // Validate group codenames
    const validCodenames = ['super_admin', 'admin', 'developer', 'business', 'accountant', 'user'];
    const invalid = groupCodenames.filter(c => !validCodenames.includes(c));
    if (invalid.length > 0) {
      throw new Error(`Invalid group codenames: ${invalid.join(', ')}`);
    }
    
    const response = await permissionsRequest(
      `/api/v1/users/${userId}/groups`,
      {
        method: 'POST',
        body: JSON.stringify({ group_codenames: groupCodenames })
      }
    );
    
    if (response && response.data) {
      showNotification('Groups assigned successfully');
      return response.data.groups;
    }
  } catch (error) {
    console.error('Error assigning groups:', error);
    showError(error.message || 'Failed to assign groups');
    throw error;
  }
}

// Get my groups (current user)
async function getMyGroups() {
  try {
    const response = await permissionsRequest('/api/v1/users/me/groups', {
      method: 'GET'
    });
    
    if (response && response.data) {
      return response.data.groups;
    }
  } catch (error) {
    console.error('Error fetching my groups:', error);
    showError('Failed to load groups');
    throw error;
  }
}

// Get my permissions (current user)
async function getMyPermissions() {
  try {
    const response = await permissionsRequest('/api/v1/users/me/permissions', {
      method: 'GET'
    });
    
    if (response && response.data) {
      return response.data.permissions;
    }
  } catch (error) {
    console.error('Error fetching my permissions:', error);
    showError('Failed to load permissions');
    throw error;
  }
}
```

### Complete Permissions Manager Component

```javascript
// Complete Permissions Manager Class
class PermissionsManager {
  constructor() {
    this.permissions = [];
    this.groups = [];
    this.userPermissions = null;
    this.userGroups = null;
  }
  
  async init() {
    try {
      // Load permissions and groups
      await Promise.all([
        this.loadPermissions(),
        this.loadGroups(),
        this.loadMyPermissions(),
        this.loadMyGroups()
      ]);
    } catch (error) {
      console.error('Failed to initialize permissions manager:', error);
      showError('Failed to load permissions data');
    }
  }
  
  async loadPermissions() {
    try {
      this.permissions = await getPermissions();
      this.renderPermissions();
      return this.permissions;
    } catch (error) {
      console.error('Failed to load permissions:', error);
      return [];
    }
  }
  
  async loadGroups() {
    try {
      this.groups = await getGroups();
      this.renderGroups();
      return this.groups;
    } catch (error) {
      console.error('Failed to load groups:', error);
      return [];
    }
  }
  
  async loadMyPermissions() {
    try {
      this.userPermissions = await getMyPermissions();
      this.renderMyPermissions();
      return this.userPermissions;
    } catch (error) {
      console.error('Failed to load my permissions:', error);
      return [];
    }
  }
  
  async loadMyGroups() {
    try {
      this.userGroups = await getMyGroups();
      this.renderMyGroups();
      return this.userGroups;
    } catch (error) {
      console.error('Failed to load my groups:', error);
      return [];
    }
  }
  
  renderPermissions() {
    const container = document.getElementById('permissions-list');
    if (!container) return;
    
    container.innerHTML = this.permissions.map(perm => `
      <div class="permission-item">
        <h4>${perm.name}</h4>
        <code>${perm.codename}</code>
        <p>${perm.description || ''}</p>
        <span class="category">${perm.category || 'uncategorized'}</span>
        <button onclick="permissionsManager.editPermission('${perm.permission_id}')">Edit</button>
        <button onclick="permissionsManager.deletePermission('${perm.permission_id}')">Delete</button>
      </div>
    `).join('');
  }
  
  renderGroups() {
    const container = document.getElementById('groups-list');
    if (!container) return;
    
    container.innerHTML = this.groups.map(group => `
      <div class="group-item">
        <h4>${group.name}</h4>
        <code>${group.codename}</code>
        <p>${group.description || ''}</p>
        <div class="permissions-count">
          ${group.permissions?.length || 0} permissions
        </div>
        <button onclick="permissionsManager.editGroup('${group.group_id}')">Edit</button>
        <button onclick="permissionsManager.deleteGroup('${group.group_id}')">Delete</button>
      </div>
    `).join('');
  }
  
  renderMyPermissions() {
    const container = document.getElementById('my-permissions');
    if (!container) return;
    
    if (this.userPermissions && this.userPermissions.length > 0) {
      container.innerHTML = this.userPermissions.map(perm => `
        <div class="permission-badge">${perm.name} (${perm.codename})</div>
      `).join('');
    } else {
      container.innerHTML = '<p>No permissions assigned</p>';
    }
  }
  
  renderMyGroups() {
    const container = document.getElementById('my-groups');
    if (!container) return;
    
    if (this.userGroups && this.userGroups.length > 0) {
      container.innerHTML = this.userGroups.map(group => `
        <div class="group-badge">${group.name} (${group.codename})</div>
      `).join('');
    } else {
      container.innerHTML = '<p>No groups assigned</p>';
    }
  }
  
  async createPermission(permissionData) {
    try {
      const permission = await createPermission(permissionData);
      await this.loadPermissions();
      return permission;
    } catch (error) {
      console.error('Failed to create permission:', error);
      throw error;
    }
  }
  
  async updatePermission(permissionId, updateData) {
    try {
      const permission = await updatePermission(permissionId, updateData);
      await this.loadPermissions();
      return permission;
    } catch (error) {
      console.error('Failed to update permission:', error);
      throw error;
    }
  }
  
  async deletePermission(permissionId) {
    try {
      await deletePermission(permissionId);
      await this.loadPermissions();
    } catch (error) {
      console.error('Failed to delete permission:', error);
      throw error;
    }
  }
  
  async createGroup(groupData) {
    try {
      const group = await createGroup(groupData);
      await this.loadGroups();
      return group;
    } catch (error) {
      console.error('Failed to create group:', error);
      throw error;
    }
  }
  
  async updateGroup(groupId, updateData) {
    try {
      const group = await updateGroup(groupId, updateData);
      await this.loadGroups();
      return group;
    } catch (error) {
      console.error('Failed to update group:', error);
      throw error;
    }
  }
  
  async deleteGroup(groupId) {
    try {
      await deleteGroup(groupId);
      await this.loadGroups();
    } catch (error) {
      console.error('Failed to delete group:', error);
      throw error;
    }
  }
  
  async assignPermissionsToGroup(groupId, permissionIds) {
    try {
      const group = await assignPermissionsToGroup(groupId, permissionIds);
      await this.loadGroups();
      return group;
    } catch (error) {
      console.error('Failed to assign permissions:', error);
      throw error;
    }
  }
}

// Initialize permissions manager
document.addEventListener('DOMContentLoaded', () => {
  window.permissionsManager = new PermissionsManager();
  permissionsManager.init();
});
```

### Permission Checking Utility

```javascript
// Check if user has a specific permission
async function hasPermission(codename) {
  try {
    const permissions = await getMyPermissions();
    return permissions.some(perm => perm.codename === codename);
  } catch (error) {
    console.error('Error checking permission:', error);
    return false;
  }
}

// Check if user has any of the specified permissions
async function hasAnyPermission(codenames) {
  try {
    const permissions = await getMyPermissions();
    const permissionCodenames = permissions.map(p => p.codename);
    return codenames.some(codename => permissionCodenames.includes(codename));
  } catch (error) {
    console.error('Error checking permissions:', error);
    return false;
  }
}

// Check if user has all of the specified permissions
async function hasAllPermissions(codenames) {
  try {
    const permissions = await getMyPermissions();
    const permissionCodenames = permissions.map(p => p.codename);
    return codenames.every(codename => permissionCodenames.includes(codename));
  } catch (error) {
    console.error('Error checking permissions:', error);
    return false;
  }
}

// Conditionally render UI based on permissions
async function renderPermissionBasedUI() {
  const canViewDashboard = await hasPermission('view_dashboard');
  const canEditProfile = await hasPermission('edit_profile');
  
  if (canViewDashboard) {
    document.getElementById('dashboard-link').style.display = 'block';
  }
  
  if (canEditProfile) {
    document.getElementById('edit-profile-btn').style.display = 'block';
  }
}
```

---

## Summary

This documentation provides comprehensive coverage of all permission and group management endpoints:

### Endpoints Covered:
1. ✅ **Get All Permissions** - List all permissions
2. ✅ **Get Permission by ID** - Get specific permission
3. ✅ **Create Permission** - Create new permission
4. ✅ **Update Permission** - Update existing permission
5. ✅ **Delete Permission** - Delete permission
6. ✅ **Get All Groups** - List all groups with permissions
7. ✅ **Get Group by ID** - Get specific group
8. ✅ **Create Group** - Create new group
9. ✅ **Update Group** - Update existing group
10. ✅ **Delete Group** - Delete group
11. ✅ **Assign Permissions to Group** - Assign permissions to a group
12. ✅ **Get User Groups** - Get groups for a user
13. ✅ **Get User Permissions** - Get permissions for a user
14. ✅ **Assign Groups to User** - Assign groups to a user
15. ✅ **Get My Groups** - Get current user's groups
16. ✅ **Get My Permissions** - Get current user's permissions

### Documentation Sections:
- ✅ Overview and RBAC architecture
- ✅ Detailed endpoint documentation with examples
- ✅ Client-server communication flows
- ✅ Complete workflows and diagrams
- ✅ Error handling guide
- ✅ Best practices
- ✅ Complete client-side implementation examples
- ✅ Permissions Manager component
- ✅ Permission checking utilities

### Key Features:
- **Role-Based Access Control (RBAC)** - Comprehensive permission system
- **Group Management** - Organize permissions into groups
- **User Assignment** - Assign groups to users
- **Permission Aggregation** - User permissions from all groups
- **System Groups Protection** - System groups cannot be deleted
- **Client-side examples** - Ready-to-use JavaScript code

All endpoints are fully documented with request/response examples, client-server communication flows, and implementation guidance.

---

**Last Updated**: January 2025

