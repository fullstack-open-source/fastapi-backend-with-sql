# Dashboard Router

> **Complete Documentation for Dashboard Analytics and Statistics Endpoints**

This router provides comprehensive dashboard statistics and analytics for user management, including user counts, growth metrics, role statistics, and sign-in analytics.

## 📋 Table of Contents

- [Overview](#overview)
- [Endpoints](#endpoints)
  - [Dashboard Overview](#dashboard-overview)
  - [Users by Status](#users-by-status)
  - [Users by Type](#users-by-type)
  - [Users by Auth Type](#users-by-auth-type)
  - [Users by Country](#users-by-country)
  - [Users by Language](#users-by-language)
  - [User Growth](#user-growth)
  - [Role Statistics](#role-statistics)
  - [Recent Sign-ins](#recent-sign-ins)
  - [All Statistics](#all-statistics)
- [Workflows](#workflows)
- [Error Handling](#error-handling)

## Overview

The Dashboard router provides analytics and statistics endpoints for monitoring user data, growth metrics, and system health. These endpoints are essential for:
- **Administrative Dashboards**: Display key metrics and KPIs
- **User Analytics**: Track user growth and demographics
- **System Monitoring**: Monitor user activity and engagement
- **Reporting**: Generate reports for stakeholders

**Base Path:** `/{MODE}/dashboard`

**Authentication:** All endpoints require authentication

**Permissions:** All endpoints require `view_dashboard` permission

## Endpoints

### Dashboard Overview

**Endpoint:** `GET /{MODE}/dashboard/overview`

**Description:** Returns comprehensive dashboard overview statistics including total users, active users, verified users, and new user counts.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `view_dashboard`

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
  "message": "Dashboard overview retrieved successfully",
  "data": {
    "overview": {
      "total_users": 1000,
      "active_users": 850,
      "verified_users": 800,
      "email_verified": 750,
      "phone_verified": 700,
      "new_users": {
        "today": 10,
        "this_week": 50,
        "this_month": 200
      },
      "users_with_sign_in": 600
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
   ├─► Check Permission (view_dashboard)
   │
   ├─► Calculate Date Boundaries
   │   ├─► Today (00:00:00)
   │   ├─► Tomorrow (00:00:00)
   │   ├─► Week Ago (7 days)
   │   └─► Month Start (1st of month)
   │
   ├─► Execute Parallel Queries
   │   ├─► Total Users Count
   │   ├─► Active Users Count (is_active = true)
   │   ├─► Verified Users Count (is_verified = true)
   │   ├─► Email Verified Count
   │   ├─► Phone Verified Count
   │   ├─► New Users Today
   │   ├─► New Users This Week
   │   ├─► New Users This Month
   │   └─► Users With Sign-in (last_sign_in_at not null)
   │
   └─► Return Aggregated Statistics
```

**Metrics Explained:**
- `total_users`: Total number of registered users
- `active_users`: Users with `is_active = true`
- `verified_users`: Users with `is_verified = true`
- `email_verified`: Users with verified email addresses
- `phone_verified`: Users with verified phone numbers
- `new_users.today`: Users created today
- `new_users.this_week`: Users created in last 7 days
- `new_users.this_month`: Users created this month
- `users_with_sign_in`: Users who have signed in at least once

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Client prepares request
  ├─► User navigates to dashboard page
  ├─► Retrieve stored access_token or session_token
  ├─► Add token to Authorization header or X-Session-Token header
  └─► Prepare GET request to /{MODE}/dashboard/overview

Step 2: Client sends request
  GET /{MODE}/dashboard/overview
  Headers:
    Authorization: Bearer <token>
    # OR
    X-Session-Token: <session_token>

Step 3: Client receives response
  ├─► Success (200): Display dashboard metrics in UI
  ├─► Unauthorized (401): Redirect to login
  ├─► Forbidden (403): Show permission error
  └─► Error (500): Show error message, log error

Step 4: Client processes data
  ├─► Extract overview statistics from response.data.overview
  ├─► Update dashboard cards/widgets with metrics
  ├─► Format numbers (e.g., 1000 → "1,000")
  └─► Display charts/graphs if applicable

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token (JWT verification)
  ├─► Check token blacklist
  └─► Extract user from token

Step 2: Permission check
  ├─► Check if user has "view_dashboard" permission
  └─► If no permission: Return 403 Forbidden

Step 3: Calculate date boundaries
  ├─► today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
  ├─► tomorrow = today + timedelta(days=1)
  ├─► week_ago = datetime.now() - timedelta(days=7)
  └─► month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

Step 4: Execute database queries
  ├─► Total Users: SELECT COUNT(*) FROM public."user"
  ├─► Active Users: SELECT COUNT(*) WHERE is_active = TRUE
  ├─► Verified Users: SELECT COUNT(*) WHERE is_verified = TRUE
  ├─► Email Verified: SELECT COUNT(*) WHERE is_email_verified = TRUE
  ├─► Phone Verified: SELECT COUNT(*) WHERE is_phone_verified = TRUE
  ├─► New Users Today: SELECT COUNT(*) WHERE created_at >= today AND created_at < tomorrow
  ├─► New Users Week: SELECT COUNT(*) WHERE created_at >= week_ago
  ├─► New Users Month: SELECT COUNT(*) WHERE created_at >= month_start
  └─► Users With Sign-in: SELECT COUNT(*) WHERE last_sign_in_at IS NOT NULL

Step 5: Aggregate results
  ├─► Combine all query results
  ├─► Structure data into overview object
  └─► Format new_users as nested object

Step 6: Response preparation
  ├─► Build SUCCESS response
  ├─► Include overview statistics in data.overview
  └─► Return response with user's language preference

Step 7: Error handling
  ├─► Database error: Log error, return 500
  ├─► Permission denied: Return 403
  └─► Token invalid: Return 401
```

**Error Responses:**

```json
// 401 - Unauthorized
{
  "success": false,
  "id": null,
  "message": "Authentication required",
  "error": {
    "code": "UNAUTHORIZED",
    "details": {
      "message": "Invalid or missing token"
    }
  }
}

// 403 - Forbidden
{
  "success": false,
  "id": null,
  "message": "Permission denied",
  "error": {
    "code": "PERMISSION_DENIED",
    "details": {
      "required_permission": "view_dashboard"
    }
  }
}

// 500 - Server Error
{
  "success": false,
  "id": null,
  "message": "Dashboard error",
  "error": {
    "code": "DASHBOARD_ERROR",
    "details": {
      "exception": "Error details"
    }
  }
}
```

---

### Users by Status

**Endpoint:** `GET /{MODE}/dashboard/users-by-status`

**Description:** Returns count of users grouped by status (ACTIVE, INACTIVE, etc.).

**Authentication:** Required
**Permission:** `view_dashboard`

**Response:**
```json
{
  "success": true,
  "message": "User statistics by status retrieved successfully",
  "data": {
    "users_by_status": [
      { "status": "ACTIVE", "count": 850 },
      { "status": "INACTIVE", "count": 150 }
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
   ├─► Check Permission (view_dashboard)
   │
   ├─► Group Users by Status
   │   └─► prisma.user.groupBy({ by: ['status'] })
   │
   ├─► Count Users per Status
   │   └─► Order by count (descending)
   │
   └─► Return Status Statistics
```

**Status Values:**
- `ACTIVE`: Active users
- `INACTIVE`: Inactive users
- Other custom statuses as defined in the system

---

### Users by Type

**Endpoint:** `GET /{MODE}/dashboard/users-by-type`

**Description:** Returns count of users grouped by user_type (customer, business, etc.).

**Authentication:** Required
**Permission:** `view_dashboard`

**Response:**
```json
{
  "success": true,
  "message": "User statistics by type retrieved successfully",
  "data": {
    "users_by_type": [
      { "user_type": "customer", "count": 800 },
      { "user_type": "business", "count": 200 }
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
   ├─► Check Permission (view_dashboard)
   │
   ├─► Group Users by Type
   │   └─► prisma.user.groupBy({ by: ['user_type'] })
   │
   ├─► Count Users per Type
   │   └─► Order by count (descending)
   │
   └─► Return Type Statistics
```

**User Types:**
- `customer`: Regular customers
- `business`: Business accounts
- Other custom types as defined in the system

---

### Users by Auth Type

**Endpoint:** `GET /{MODE}/dashboard/users-by-auth-type`

**Description:** Returns count of users grouped by authentication type (email, phone, etc.).

**Authentication:** Required
**Permission:** `view_dashboard`

**Response:**
```json
{
  "success": true,
  "message": "User statistics by auth type retrieved successfully",
  "data": {
    "users_by_auth_type": [
      { "auth_type": "email", "count": 600 },
      { "auth_type": "phone", "count": 400 }
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
   ├─► Check Permission (view_dashboard)
   │
   ├─► Group Users by Auth Type
   │   └─► prisma.user.groupBy({ by: ['auth_type'] })
   │
   ├─► Count Users per Auth Type
   │   └─► Order by count (descending)
   │
   └─► Return Auth Type Statistics
```

**Auth Types:**
- `email`: Email-based authentication
- `phone`: Phone-based authentication

---

### Users by Country

**Endpoint:** `GET /{MODE}/dashboard/users-by-country`

**Description:** Returns count of users grouped by country (top 20 countries).

**Authentication:** Required
**Permission:** `view_dashboard`

**Response:**
```json
{
  "success": true,
  "message": "User statistics by country retrieved successfully",
  "data": {
    "users_by_country": [
      { "country": "US", "count": 300 },
      { "country": "UK", "count": 200 },
      { "country": "CA", "count": 150 }
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
   ├─► Check Permission (view_dashboard)
   │
   ├─► Group Users by Country
   │   └─► prisma.user.groupBy({ by: ['country'], take: 20 })
   │
   ├─► Count Users per Country
   │   └─► Order by count (descending)
   │
   └─► Return Top 20 Countries
```

**Note:** Returns top 20 countries by user count.

---

### Users by Language

**Endpoint:** `GET /{MODE}/dashboard/users-by-language`

**Description:** Returns count of users grouped by language preference.

**Authentication:** Required
**Permission:** `view_dashboard`

**Response:**
```json
{
  "success": true,
  "message": "User statistics by language retrieved successfully",
  "data": {
    "users_by_language": [
      { "language": "en", "count": 700 },
      { "language": "ar", "count": 300 }
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
   ├─► Check Permission (view_dashboard)
   │
   ├─► Group Users by Language
   │   └─► prisma.user.groupBy({ by: ['language'] })
   │
   ├─► Count Users per Language
   │   └─► Order by count (descending)
   │
   └─► Return Language Statistics
```

**Language Codes:** ISO 639-1 codes (en, ar, etc.)

---

### User Growth

**Endpoint:** `GET /{MODE}/dashboard/user-growth`

**Description:** Returns user sign-up statistics over time (daily, weekly, monthly).

**Authentication:** Required (access_token or session_token)

**Required Permission:** `view_dashboard`

**Query Parameters:**
- `period` (optional): Time period for growth statistics
  - `daily` (default): Daily growth
  - `weekly`: Weekly growth
  - `monthly`: Monthly growth
- `days` (optional): Number of days to look back (for daily period, default: 30, max: 365)

**Request Headers:**
```
Authorization: Bearer <access_token>
# OR
X-Session-Token: <session_token>
```

**Request Example:**
```http
GET /dev/v1/dashboard/user-growth?period=daily&days=30 HTTP/1.1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "User growth statistics retrieved successfully",
  "data": {
    "period": "daily",
    "growth": [
      { "period": "2025-01-01", "count": 10 },
      { "period": "2025-01-02", "count": 15 },
      { "period": "2025-01-03", "count": 12 }
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
   ├─► Check Permission (view_dashboard)
   │
   ├─► Extract Query Parameters
   │   ├─► period: daily/weekly/monthly (default: daily)
   │   └─► days: number (default: 30, max: 365)
   │
   ├─► Execute Raw SQL Query
   │   ├─► Daily: DATE(created_at) with last N days
   │   ├─► Weekly: DATE_TRUNC('week', created_at) with last 12 weeks
   │   └─► Monthly: DATE_TRUNC('month', created_at) with last 12 months
   │
   ├─► Format Results
   │   └─► Map to period and count
   │
   └─► Return Growth Statistics
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Client prepares request
  ├─► User selects time period (daily/weekly/monthly)
  ├─► User selects number of days (for daily period)
  ├─► Retrieve stored access_token or session_token
  ├─► Build query string with parameters
  └─► Prepare GET request to /{MODE}/dashboard/user-growth

Step 2: Client sends request
  GET /{MODE}/dashboard/user-growth?period=daily&days=30
  Headers:
    Authorization: Bearer <token>
    # OR
    X-Session-Token: <session_token>

Step 3: Client receives response
  ├─► Success (200): Process growth data
  ├─► Unauthorized (401): Redirect to login
  ├─► Forbidden (403): Show permission error
  └─► Error (500): Show error message

Step 4: Client processes data
  ├─► Extract growth array from response.data.growth
  ├─► Format dates for display
  ├─► Render line chart or bar chart
  └─► Update UI with growth statistics

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token (JWT verification)
  ├─► Check token blacklist
  ├─► Extract user from token
  ├─► Extract query parameters (period, days)
  └─► Validate parameters (period: daily/weekly/monthly, days: 1-365)

Step 2: Permission check
  ├─► Check if user has "view_dashboard" permission
  └─► If no permission: Return 403 Forbidden

Step 3: Build SQL query based on period
  ├─► If period = "daily":
  │   ├─► Limit days to 1-365 range
  │   └─► Query: SELECT DATE(created_at) as date, COUNT(*) 
  │       WHERE created_at >= CURRENT_DATE - INTERVAL '{days} days'
  │       GROUP BY DATE(created_at) ORDER BY date ASC
  │
  ├─► If period = "weekly":
  │   └─► Query: SELECT DATE_TRUNC('week', created_at) as week, COUNT(*)
  │       WHERE created_at >= CURRENT_DATE - INTERVAL '12 weeks'
  │       GROUP BY DATE_TRUNC('week', created_at) ORDER BY week ASC
  │
  └─► If period = "monthly":
      └─► Query: SELECT DATE_TRUNC('month', created_at) as month, COUNT(*)
          WHERE created_at >= CURRENT_DATE - INTERVAL '12 months'
          GROUP BY DATE_TRUNC('month', created_at) ORDER BY month ASC

Step 4: Execute database query
  ├─► Execute SQL query
  ├─► Fetch all rows
  └─► Process results

Step 5: Format results
  ├─► Convert dates to ISO format
  ├─► Structure as array of {period, count} objects
  └─► Ensure count is integer

Step 6: Response preparation
  ├─► Build SUCCESS response
  ├─► Include period type and growth array
  └─► Return response with user's language preference

Step 7: Error handling
  ├─► Invalid parameters: Return 400
  ├─► Database error: Log error, return 500
  ├─► Permission denied: Return 403
  └─► Token invalid: Return 401
```

**Use Cases:**
- Growth trend analysis
- User acquisition metrics
- Time-series visualization
- Reporting

---

### Role Statistics

**Endpoint:** `GET /{MODE}/dashboard/role-statistics`

**Description:** Returns count of users by role (admin, business, developer, etc.).

**Authentication:** Required
**Permission:** `view_dashboard`

**Response:**
```json
{
  "success": true,
  "message": "Role statistics retrieved successfully",
  "data": {
    "role_statistics": {
      "superusers": 5,
      "admins": 10,
      "business": 50,
      "developers": 20,
      "accountants": 15,
      "regular_users": 900
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
   ├─► Check Permission (view_dashboard)
   │
   ├─► Get All Users
   │   └─► prisma.user.findMany({ select: { user_id: true } })
   │
   ├─► For Each User
   │   ├─► Get User Groups
   │   │   └─► getUserGroups(user_id)
   │   │
   │   └─► Count by Group Codename
   │       ├─► super_admin
   │       ├─► admin
   │       ├─► business
   │       ├─► developer
   │       ├─► accountant
   │       └─► user
   │
   └─► Return Role Statistics
```

**Note:** This endpoint iterates through all users to count roles. For large user bases, consider caching or optimization.

**Roles:**
- `superusers`: Users with super_admin group
- `admins`: Users with admin group
- `business`: Users with business group
- `developers`: Users with developer group
- `accountants`: Users with accountant group
- `regular_users`: Users with user group

---

### Recent Sign-ins

**Endpoint:** `GET /{MODE}/dashboard/recent-sign-ins`

**Description:** Returns users who signed in recently within specified hours.

**Authentication:** Required
**Permission:** `view_dashboard`

**Query Parameters:**
- `hours` (optional): Number of hours to look back (default: 24, max: 168)

**Request:**
```http
GET /dev/v1/dashboard/recent-sign-ins?hours=24 HTTP/1.1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Recent sign-in statistics retrieved successfully",
  "data": {
    "recent_sign_ins": {
      "total_with_sign_in": 600,
      "last_hour": 10,
      "last_24_hours": 100,
      "today": 150
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
   ├─► Check Permission (view_dashboard)
   │
   ├─► Extract Query Parameters
   │   └─► hours: number (default: 24, max: 168)
   │
   ├─► Calculate Date Boundaries
   │   ├─► One Hour Ago
   │   ├─► N Hours Ago (from query)
   │   └─► Today (00:00:00)
   │
   ├─► Execute Parallel Queries
   │   ├─► Total Users With Sign-in (last_sign_in_at not null)
   │   ├─► Sign-ins Last Hour
   │   ├─► Sign-ins Last N Hours
   │   └─► Sign-ins Today
   │
   └─► Return Sign-in Statistics
```

**Metrics:**
- `total_with_sign_in`: Total users who have signed in at least once
- `last_hour`: Users who signed in within last hour
- `last_{N}_hours`: Users who signed in within last N hours
- `today`: Users who signed in today

---

### All Statistics

**Endpoint:** `GET /{MODE}/dashboard/all-statistics`

**Description:** Returns comprehensive dashboard statistics including all metrics from other endpoints.

**Authentication:** Required
**Permission:** `view_dashboard`

**Response:**
```json
{
  "success": true,
  "message": "All dashboard statistics retrieved successfully",
  "data": {
    "overview": {
      "total_users": 1000,
      "active_users": 850,
      "verified_users": 800,
      "email_verified": 750,
      "phone_verified": 700,
      "new_users": {
        "today": 10,
        "this_week": 50,
        "this_month": 200
      }
    },
    "by_status": [
      { "status": "ACTIVE", "count": 850 },
      { "status": "INACTIVE", "count": 150 }
    ],
    "by_type": [
      { "user_type": "customer", "count": 800 },
      { "user_type": "business", "count": 200 }
    ],
    "by_auth_type": [
      { "auth_type": "email", "count": 600 },
      { "auth_type": "phone", "count": 400 }
    ],
    "roles": {
      "superusers": 5,
      "admins": 10,
      "business": 50,
      "developers": 20,
      "accountants": 15,
      "regular_users": 900
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
   ├─► Check Permission (view_dashboard)
   │
   ├─► Calculate Date Boundaries
   │   ├─► Today, Tomorrow, Week Ago, Month Start
   │
   ├─► Execute All Queries in Parallel
   │   ├─► Overview Statistics (9 queries)
   │   ├─► Users by Status (groupBy)
   │   ├─► Users by Type (groupBy)
   │   ├─► Users by Auth Type (groupBy)
   │   └─► Role Statistics (iterate users)
   │
   ├─► Aggregate All Results
   │
   └─► Return Comprehensive Statistics
```

**Use Cases:**
- Dashboard initialization
- Comprehensive reporting
- Single API call for all metrics
- Admin panel data loading

---

## Workflows

### Complete Dashboard Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│              Dashboard Statistics Request                   │
└────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Validate Auth  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Check Permission │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        ┌───────────────┐         ┌───────────────┐
        │ Single Metric │         │ All Metrics   │
        └───────┬───────┘         └───────┬───────┘
                │                         │
                ▼                         ▼
        ┌───────────────┐         ┌───────────────┐
        │ Execute Query │         │ Parallel Queries│
        └───────┬───────┘         └───────┬───────┘
                │                         │
                └────────────┬────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Format Results  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Return Response │
                    └─────────────────┘
```

## Error Handling

### Common Error Responses

**401 Unauthorized:**
```json
{
  "success": false,
  "message": "Authentication required",
  "error": "Invalid or missing token",
  "statusCode": 401
}
```

**403 Forbidden:**
```json
{
  "success": false,
  "message": "Permission denied",
  "error": "Insufficient permissions. Requires view_dashboard permission",
  "statusCode": 403
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "message": "Dashboard error",
  "error": "Error details",
  "statusCode": 500
}
```

### Error Handling Workflow

```
1. Error Occurs
   │
   ├─► Log Error
   │   └─► Winston Logger with module: 'Dashboard'
   │
   ├─► Format Error Response
   │   └─► ERROR.fromMap('DASHBOARD_ERROR')
   │
   └─► Return Error Response
       └─► Appropriate Status Code
```

---

## Best Practices

1. **Caching**: Consider caching dashboard statistics for better performance
2. **Pagination**: For large datasets, implement pagination
3. **Optimization**: Role statistics endpoint may be slow for large user bases - consider optimization
4. **Rate Limiting**: Implement rate limiting for dashboard endpoints
5. **Data Aggregation**: Use database aggregation functions for better performance
6. **Date Boundaries**: Always use proper date boundaries for time-based queries
7. **Parallel Queries**: Use Promise.all() for parallel queries when possible
8. **Error Handling**: Handle database errors gracefully

---

## Performance Considerations

1. **Role Statistics**: This endpoint iterates through all users - consider caching or background jobs
2. **User Growth**: Raw SQL queries are used for date aggregations - ensure proper indexing
3. **All Statistics**: Combines multiple queries - may be slower, consider caching
4. **Database Indexing**: Ensure proper indexes on:
   - `created_at` (for growth queries)
   - `last_sign_in_at` (for sign-in queries)
   - `status`, `user_type`, `auth_type`, `country`, `language` (for groupBy queries)

---

## Client-Side Implementation

### Token Management

```javascript
// Get authentication token (prefer session_token)
function getAuthToken() {
  return localStorage.getItem('session_token') || 
         localStorage.getItem('access_token');
}

// API request helper for dashboard endpoints
async function dashboardRequest(url, options = {}) {
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
    throw new Error('You do not have permission to view dashboard');
  }
  
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error?.message || 'Dashboard request failed');
  }
  
  return data;
}
```

### Dashboard Overview

```javascript
// Get dashboard overview statistics
async function getDashboardOverview() {
  try {
    const response = await dashboardRequest('/api/v1/dashboard/overview', {
      method: 'GET'
    });
    
    if (response && response.data) {
      const overview = response.data.overview;
      
      // Update UI with metrics
      updateMetricCard('total-users', overview.total_users);
      updateMetricCard('active-users', overview.active_users);
      updateMetricCard('verified-users', overview.verified_users);
      updateMetricCard('email-verified', overview.email_verified);
      updateMetricCard('phone-verified', overview.phone_verified);
      updateMetricCard('new-users-today', overview.new_users.today);
      updateMetricCard('new-users-week', overview.new_users.this_week);
      updateMetricCard('new-users-month', overview.new_users.this_month);
      updateMetricCard('users-with-signin', overview.users_with_sign_in);
      
      return overview;
    }
  } catch (error) {
    console.error('Error fetching dashboard overview:', error);
    showError('Failed to load dashboard overview');
    throw error;
  }
}

// Helper function to update metric cards
function updateMetricCard(elementId, value) {
  const element = document.getElementById(elementId);
  if (element) {
    element.textContent = formatNumber(value);
  }
}

// Format numbers with commas
function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}
```

### Users by Status

```javascript
// Get users grouped by status
async function getUsersByStatus() {
  try {
    const response = await dashboardRequest('/api/v1/dashboard/users-by-status', {
      method: 'GET'
    });
    
    if (response && response.data) {
      const stats = response.data.users_by_status;
      
      // Update chart or table
      renderStatusChart(stats);
      
      return stats;
    }
  } catch (error) {
    console.error('Error fetching users by status:', error);
    showError('Failed to load user status statistics');
    throw error;
  }
}

// Render status chart (example using Chart.js)
function renderStatusChart(stats) {
  const ctx = document.getElementById('status-chart').getContext('2d');
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: stats.map(s => s.status),
      datasets: [{
        data: stats.map(s => s.count),
        backgroundColor: ['#4CAF50', '#F44336', '#FF9800', '#2196F3']
      }]
    }
  });
}
```

### User Growth

```javascript
// Get user growth statistics
async function getUserGrowth(period = 'daily', days = 30) {
  try {
    const url = `/api/v1/dashboard/user-growth?period=${period}&days=${days}`;
    const response = await dashboardRequest(url, {
      method: 'GET'
    });
    
    if (response && response.data) {
      const growth = response.data.growth;
      
      // Render growth chart
      renderGrowthChart(growth, period);
      
      return growth;
    }
  } catch (error) {
    console.error('Error fetching user growth:', error);
    showError('Failed to load user growth statistics');
    throw error;
  }
}

// Render growth line chart
function renderGrowthChart(growth, period) {
  const ctx = document.getElementById('growth-chart').getContext('2d');
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: growth.map(g => formatPeriod(g.period, period)),
      datasets: [{
        label: 'New Users',
        data: growth.map(g => g.count),
        borderColor: '#2196F3',
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

// Format period label based on type
function formatPeriod(period, type) {
  const date = new Date(period);
  if (type === 'daily') {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  } else if (type === 'weekly') {
    return `Week of ${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
  } else {
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  }
}
```

### All Statistics

```javascript
// Get all dashboard statistics at once
async function getAllDashboardStatistics() {
  try {
    const response = await dashboardRequest('/api/v1/dashboard/all-statistics', {
      method: 'GET'
    });
    
    if (response && response.data) {
      const stats = response.data;
      
      // Update all dashboard sections
      updateOverviewSection(stats.overview);
      updateStatusSection(stats.by_status);
      updateTypeSection(stats.by_type);
      updateAuthTypeSection(stats.by_auth_type);
      updateRolesSection(stats.roles);
      
      return stats;
    }
  } catch (error) {
    console.error('Error fetching all statistics:', error);
    showError('Failed to load dashboard statistics');
    throw error;
  }
}
```

### Complete Dashboard Component

```javascript
// Complete Dashboard Manager Class
class DashboardManager {
  constructor() {
    this.stats = null;
    this.refreshInterval = null;
  }
  
  async init() {
    try {
      // Load all statistics on initialization
      await this.loadAllStatistics();
      
      // Set up auto-refresh (every 5 minutes)
      this.startAutoRefresh(5 * 60 * 1000);
      
      // Set up manual refresh button
      document.getElementById('refresh-dashboard').addEventListener('click', () => {
        this.loadAllStatistics();
      });
    } catch (error) {
      console.error('Failed to initialize dashboard:', error);
      showError('Failed to load dashboard');
    }
  }
  
  async loadAllStatistics() {
    try {
      showLoading('Loading dashboard...');
      
      const stats = await getAllDashboardStatistics();
      this.stats = stats;
      
      this.renderDashboard();
      hideLoading();
    } catch (error) {
      hideLoading();
      showError('Failed to load dashboard statistics');
    }
  }
  
  renderDashboard() {
    if (!this.stats) return;
    
    // Render overview cards
    this.renderOverviewCards();
    
    // Render charts
    this.renderCharts();
    
    // Render tables
    this.renderTables();
  }
  
  renderOverviewCards() {
    const overview = this.stats.overview;
    
    // Update metric cards
    document.getElementById('total-users').textContent = formatNumber(overview.total_users);
    document.getElementById('active-users').textContent = formatNumber(overview.active_users);
    document.getElementById('verified-users').textContent = formatNumber(overview.verified_users);
    document.getElementById('new-users-today').textContent = formatNumber(overview.new_users.today);
  }
  
  renderCharts() {
    // Render status pie chart
    renderStatusChart(this.stats.by_status);
    
    // Render type bar chart
    renderTypeChart(this.stats.by_type);
    
    // Render growth line chart
    getUserGrowth('daily', 30).then(growth => {
      renderGrowthChart(growth, 'daily');
    });
  }
  
  renderTables() {
    // Render status table
    renderTable('status-table', this.stats.by_status, ['status', 'count']);
    
    // Render type table
    renderTable('type-table', this.stats.by_type, ['user_type', 'count']);
  }
  
  startAutoRefresh(interval) {
    this.refreshInterval = setInterval(() => {
      this.loadAllStatistics();
    }, interval);
  }
  
  stopAutoRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
  }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
  const dashboard = new DashboardManager();
  dashboard.init();
});
```

### Error Handling

```javascript
// Enhanced error handling for dashboard requests
async function dashboardRequestWithRetry(url, options = {}, maxRetries = 3) {
  let lastError;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await dashboardRequest(url, options);
    } catch (error) {
      lastError = error;
      
      // Don't retry on 401 or 403 errors
      if (error.message.includes('401') || error.message.includes('403')) {
        throw error;
      }
      
      // Wait before retry (exponential backoff)
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
    }
  }
  
  throw lastError;
}
```

### Loading States

```javascript
// Show loading indicator
function showLoading(message = 'Loading...') {
  const loader = document.getElementById('dashboard-loader');
  if (loader) {
    loader.textContent = message;
    loader.style.display = 'block';
  }
}

// Hide loading indicator
function hideLoading() {
  const loader = document.getElementById('dashboard-loader');
  if (loader) {
    loader.style.display = 'none';
  }
}

// Show error message
function showError(message) {
  const errorDiv = document.getElementById('dashboard-error');
  if (errorDiv) {
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
      errorDiv.style.display = 'none';
    }, 5000);
  }
}
```

---

## Summary

This documentation provides comprehensive coverage of all dashboard analytics endpoints:

### Endpoints Covered:
1. ✅ **Dashboard Overview** - Comprehensive user statistics
2. ✅ **Users by Status** - Group users by account status
3. ✅ **Users by Type** - Group users by user type
4. ✅ **Users by Auth Type** - Group users by authentication method
5. ✅ **Users by Country** - Geographic distribution (top 20)
6. ✅ **Users by Language** - Language preference distribution
7. ✅ **User Growth** - Time-series growth statistics
8. ✅ **Recent Sign-ins** - Sign-in activity metrics
9. ✅ **All Statistics** - Comprehensive dashboard data

### Documentation Sections:
- ✅ Overview and system architecture
- ✅ Detailed endpoint documentation with examples
- ✅ Client-server communication flows
- ✅ Complete workflows and diagrams
- ✅ Error handling guide
- ✅ Best practices and performance considerations
- ✅ Complete client-side implementation examples
- ✅ Dashboard component examples

### Key Features:
- **Permission-based access** - All endpoints require `view_dashboard` permission
- **Comprehensive metrics** - User counts, growth, demographics, and activity
- **Flexible queries** - Support for different time periods and filters
- **Performance optimized** - Efficient database queries with proper indexing
- **Client-side examples** - Ready-to-use JavaScript code for dashboard implementation

All endpoints are fully documented with request/response examples, client-server communication flows, and implementation guidance.

---

**Last Updated**: January 2025

