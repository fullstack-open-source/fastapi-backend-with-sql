# Activity Logging Router

> **Complete Documentation for Activity Logging and Audit Trail Endpoints**

This router handles all activity logging operations including creating log entries, retrieving logs with filters, getting statistics, and managing log cleanup.

## 📋 Table of Contents

- [Overview](#overview)
- [Endpoints](#endpoints)
  - [Create Activity Log](#create-activity-log)
  - [Get Activity Logs](#get-activity-logs)
  - [Get Activity Log by ID](#get-activity-log-by-id)
  - [Get User Activity Logs](#get-user-activity-logs)
  - [Get My Activity Logs](#get-my-activity-logs)
  - [Get Activity Statistics](#get-activity-statistics)
  - [Delete Old Activity Logs](#delete-old-activity-logs)
- [Workflows](#workflows)
- [Error Handling](#error-handling)

## Overview

The Activity Logging router provides comprehensive audit trail and activity tracking functionality including:
- **Activity Logging**: Create detailed activity log entries
- **Log Retrieval**: Query logs with advanced filters
- **User Activity Tracking**: Track user-specific activities
- **Statistics**: Get activity statistics and analytics
- **Log Management**: Clean up old logs

**Base Path:** `/{MODE}/activity`

**Authentication:** All endpoints require authentication

**Permissions:** Various permissions required (see each endpoint)

## Endpoints

### Create Activity Log

**Endpoint:** `POST /{MODE}/activity/logs`

**Description:** Create a new activity log entry with comprehensive metadata.

**Authentication:** Required
**Permission:** `edit_profile`

**Request Body:**
```json
{
  "level": "info",
  "message": "User performed action",
  "action": "login",
  "module": "authentication",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "endpoint": "/api/token",
  "method": "POST",
  "status_code": 200,
  "metadata": {
    "key": "value"
  }
}
```

**Level Options:** `info`, `warn`, `error`, `debug`, `audit`

**Response:**
```json
{
  "success": true,
  "message": "Activity log created successfully",
  "data": {
    "activity_log": {
      "log_id": "uuid",
      "user_id": "uuid",
      "level": "info",
      "message": "User performed action",
      "action": "login",
      "module": "authentication",
      "ip_address": "192.168.1.1",
      "created_at": "2025-01-01T00:00:00.000Z"
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
   ├─► Check Permission (edit_profile)
   │
   ├─► Extract Request Metadata
   │   ├─► IP Address (req.ip or req.connection.remoteAddress)
   │   ├─► User Agent (req.get('user-agent'))
   │   └─► Parse User Agent (device, browser, OS)
   │
   ├─► Build Log Data
   │   ├─► user_id (from token or request body)
   │   ├─► level (default: 'info')
   │   ├─► message (required)
   │   ├─► action, module, endpoint, method
   │   ├─► ip_address, user_agent, device, browser, os
   │   ├─► request_id, session_id
   │   ├─► metadata (JSONB)
   │   └─► error_details (JSONB, if error)
   │
   ├─► Create Activity Log
   │   └─► createActivityLog(logData)
   │
   └─► Return Created Log Entry
```

**Auto-Extracted Fields:**
- `user_id`: From JWT token if not provided
- `ip_address`: From request if not provided
- `user_agent`: From request headers if not provided
- `device`, `browser`, `os`: Parsed from user agent
- `endpoint`: From request URL if not provided
- `method`: From request method if not provided

---

### Get Activity Logs

**Endpoint:** `GET /{MODE}/activity/logs`

**Description:** Retrieve activity logs with advanced filtering options.

**Authentication:** Required
**Permission:** `view_activity_log`

**Query Parameters:**
- `user_id` (optional): Filter by user ID
- `level` (optional): Filter by log level (`info`, `warn`, `error`, `debug`, `audit`)
- `action` (optional): Filter by action
- `module` (optional): Filter by module
- `ip_address` (optional): Filter by IP address
- `start_date` (optional): Start date (ISO format)
- `end_date` (optional): End date (ISO format)
- `limit` (optional): Number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)
- `order_by` (optional): Sort field (default: `created_at`)
- `order` (optional): Sort order (`asc`, `desc`, default: `desc`)

**Request:**
```http
GET /dev/v1/activity/logs?user_id=uuid&level=error&limit=50&offset=0 HTTP/1.1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Activity logs retrieved successfully",
  "data": {
    "activity_logs": [
      {
        "log_id": "uuid",
        "user_id": "uuid",
        "level": "error",
        "message": "Error occurred",
        "action": "api_call",
        "module": "api",
        "ip_address": "192.168.1.1",
        "created_at": "2025-01-01T00:00:00.000Z"
      }
    ],
    "count": 50
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (view_activity_log)
   │
   ├─► Extract Query Parameters
   │   ├─► Filters (user_id, level, action, module, ip_address)
   │   ├─► Date Range (start_date, end_date)
   │   ├─► Pagination (limit, offset)
   │   └─► Sorting (order_by, order)
   │
   ├─► Build Query Filters
   │   └─► Construct Prisma where clause
   │
   ├─► Execute Query
   │   └─► getActivityLogs(filters)
   │
   └─► Return Filtered Logs
```

---

### Get Activity Log by ID

**Endpoint:** `GET /{MODE}/activity/logs/:log_id`

**Description:** Get a specific activity log by ID.

**Authentication:** Required
**Permission:** `view_activity_log`

**Parameters:**
- `log_id` (path): Log UUID

**Response:**
```json
{
  "success": true,
  "message": "Activity log retrieved successfully",
  "data": {
    "activity_log": {
      "log_id": "uuid",
      "user_id": "uuid",
      "level": "info",
      "message": "User performed action",
      "action": "login",
      "module": "authentication",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "device": "Desktop",
      "browser": "Chrome",
      "os": "Windows",
      "endpoint": "/api/token",
      "method": "POST",
      "status_code": 200,
      "metadata": { ... },
      "created_at": "2025-01-01T00:00:00.000Z"
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
   ├─► Check Permission (view_activity_log)
   │
   ├─► Get Activity Log by ID
   │   └─► getActivityLogById(log_id)
   │
   ├─► Check if Log Exists
   │   └─► Return 404 if not found
   │
   └─► Return Activity Log
```

---

### Get User Activity Logs

**Endpoint:** `GET /{MODE}/activity/users/:user_id/logs`

**Description:** Get activity logs for a specific user.

**Authentication:** Required
**Permission:** `view_activity_log`

**Parameters:**
- `user_id` (path): User UUID

**Query Parameters:**
- `start_date` (optional): Start date (ISO format)
- `end_date` (optional): End date (ISO format)
- `limit` (optional): Number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "success": true,
  "message": "User activity logs retrieved successfully",
  "data": {
    "user_id": "uuid",
    "activity_logs": [ ... ],
    "count": 25
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (view_activity_log)
   │
   ├─► Extract Query Parameters
   │   ├─► Date Range (start_date, end_date)
   │   └─► Pagination (limit, offset)
   │
   ├─► Get User Activity Logs
   │   └─► getUserActivityLogs(user_id, filters)
   │
   └─► Return User Activity Logs
```

---

### Get My Activity Logs

**Endpoint:** `GET /{MODE}/activity/me/logs`

**Description:** Get activity logs for the current authenticated user.

**Authentication:** Required
**Permission:** `view_profile`

**Query Parameters:**
- `start_date` (optional): Start date (ISO format)
- `end_date` (optional): End date (ISO format)
- `limit` (optional): Number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "success": true,
  "message": "Your activity logs retrieved successfully",
  "data": {
    "activity_logs": [ ... ],
    "count": 10
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
   ├─► Extract Query Parameters
   │   └─► Date range and pagination
   │
   ├─► Get User Activity Logs
   │   └─► getUserActivityLogs(userId, filters)
   │
   └─► Return Activity Logs
```

---

### Get Activity Statistics

**Endpoint:** `GET /{MODE}/activity/statistics`

**Description:** Get activity log statistics including counts by level, action, and module.

**Authentication:** Required
**Permission:** `view_activity_log`

**Query Parameters:**
- `user_id` (optional): Filter by user ID
- `start_date` (optional): Start date (ISO format)
- `end_date` (optional): End date (ISO format)

**Response:**
```json
{
  "success": true,
  "message": "Activity statistics retrieved successfully",
  "data": {
    "statistics": {
      "total_logs": 1000,
      "by_level": {
        "info": 800,
        "warn": 100,
        "error": 80,
        "debug": 15,
        "audit": 5
      },
      "by_action": {
        "login": 200,
        "logout": 150,
        "api_call": 500
      },
      "by_module": {
        "authentication": 350,
        "api": 500,
        "profile": 150
      }
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
   ├─► Check Permission (view_activity_log)
   │
   ├─► Extract Query Parameters
   │   ├─► user_id (optional)
   │   └─► Date range (optional)
   │
   ├─► Build Query Filters
   │
   ├─► Calculate Statistics
   │   ├─► Total logs count
   │   ├─► Count by level (groupBy)
   │   ├─► Count by action (groupBy)
   │   └─► Count by module (groupBy)
   │
   └─► Return Statistics
```

---

### Delete Old Activity Logs

**Endpoint:** `DELETE /{MODE}/activity/logs/cleanup`

**Description:** Delete activity logs older than specified days.

**Authentication:** Required
**Permission:** `delete_activity_log`

**Query Parameters:**
- `days` (optional): Days old (default: 90)

**Request:**
```http
DELETE /dev/v1/activity/logs/cleanup?days=90 HTTP/1.1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Old activity logs deleted successfully",
  "data": {
    "deleted_count": 500,
    "days_old": 90
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (delete_activity_log)
   │
   ├─► Extract Query Parameters
   │   └─► days (default: 90)
   │
   ├─► Calculate Cutoff Date
   │   └─► Current date - days
   │
   ├─► Delete Old Logs
   │   └─► deleteOldActivityLogs(daysOld)
   │       └─► prisma.activityLog.deleteMany()
   │
   └─► Return Deletion Count
```

**Use Cases:**
- Database maintenance
- Storage optimization
- Compliance (GDPR data retention)
- Performance optimization

---

## Workflows

### Complete Activity Logging Flow

```
┌─────────────────────────────────────────────────────────────┐
│              Activity Logging Flow                          │
└────────────────────────────┬────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
        ┌───────────────┐         ┌───────────────┐
        │  Create Log   │         │  Query Logs   │
        └───────┬───────┘         └───────┬───────┘
                │                           │
                ▼                           ▼
        ┌───────────────┐         ┌───────────────┐
        │ Extract Meta  │         │ Apply Filters │
        │   Data        │         │   & Pagination│
        └───────┬───────┘         └───────┬───────┘
                │                           │
                ▼                           ▼
        ┌───────────────┐         ┌───────────────┐
        │ Parse User    │         │ Execute Query │
        │   Agent       │         └───────┬───────┘
        └───────┬───────┘                 │
                │                         │
                ▼                         ▼
        ┌───────────────┐         ┌───────────────┐
        │ Store in DB   │         │ Return Results│
        └───────────────┘         └───────────────┘
```

### Activity Log Creation Flow

```
1. User Action Occurs
   │
   ├─► Extract Request Context
   │   ├─► IP Address
   │   ├─► User Agent
   │   ├─► Endpoint
   │   └─► Method
   │
   ├─► Parse User Agent
   │   ├─► Device Type
   │   ├─► Browser
   │   └─► Operating System
   │
   ├─► Build Log Entry
   │   ├─► User ID
   │   ├─► Level
   │   ├─► Message
   │   ├─► Action & Module
   │   ├─► Request Metadata
   │   └─► Custom Metadata
   │
   ├─► Store in Database
   │   └─► ActivityLog table
   │
   └─► Return Log Entry
```

## Error Handling

### Common Error Responses

**400 Bad Request - Invalid Payload:**
```json
{
  "success": false,
  "message": "Invalid request payload",
  "error": "message is required",
  "statusCode": 400
}
```

**403 Forbidden - Permission Denied:**
```json
{
  "success": false,
  "message": "Permission denied",
  "error": "Insufficient permissions. Requires view_activity_log permission",
  "statusCode": 403
}
```

**404 Not Found - Log Not Found:**
```json
{
  "success": false,
  "message": "Activity log not found",
  "error": "Log with provided ID does not exist",
  "statusCode": 404
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "message": "Activity log creation failed",
  "error": "Error details",
  "statusCode": 500
}
```

---

## Best Practices

1. **Log Levels**: Use appropriate log levels (info, warn, error, debug, audit)
2. **Metadata**: Include relevant metadata for debugging and auditing
3. **User Agent Parsing**: Automatically parse user agent for device/browser/OS info
4. **Pagination**: Always use pagination for log queries to avoid performance issues
5. **Date Filtering**: Use date filters to limit query scope
6. **Log Cleanup**: Regularly clean up old logs to maintain database performance
7. **Sensitive Data**: Don't log sensitive information (passwords, tokens, etc.)
8. **Performance**: Index frequently queried fields (user_id, level, action, created_at)

---

## Log Levels

- **info**: General informational messages
- **warn**: Warning messages for potential issues
- **error**: Error messages for failures
- **debug**: Debug messages for development
- **audit**: Audit trail messages for compliance

---

## Database Schema

**ActivityLog Model:**
- `log_id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key, nullable)
- `level`: String (info, warn, error, debug, audit)
- `message`: String
- `action`: String (nullable)
- `module`: String (nullable)
- `ip_address`: String
- `user_agent`: String
- `device`: String (nullable)
- `browser`: String (nullable)
- `os`: String (nullable)
- `platform`: String (default: 'web')
- `endpoint`: String (nullable)
- `method`: String (nullable)
- `status_code`: Integer (nullable)
- `request_id`: String (nullable)
- `session_id`: String (nullable)
- `metadata`: JSONB (nullable)
- `error_details`: JSONB (nullable)
- `duration_ms`: Integer (nullable)
- `created_at`: Timestamp

---

**Last Updated**: January 2025

