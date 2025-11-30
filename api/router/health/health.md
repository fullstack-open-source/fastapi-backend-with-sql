# Health & Monitoring Router

> **Complete Documentation for Health Check and System Monitoring Endpoints**

This router provides endpoints for checking API health status, system information, and testing error tracking integration.

## 📋 Table of Contents

- [Overview](#overview)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [System Health Check](#system-health-check)
  - [Database Health Check](#database-health-check)
  - [Storage Health Check](#storage-health-check)
  - [Test Sentry](#test-sentry)
- [Workflows](#workflows)
- [Error Handling](#error-handling)
- [Client-Side Implementation](#client-side-implementation)
- [Summary](#summary)

## Overview

The Health router provides monitoring and diagnostic endpoints that help track the API's operational status. These endpoints are essential for:
- **Load Balancer Health Checks**: Verify service availability
- **System Monitoring**: Track resource usage and system metrics
- **Error Tracking Testing**: Validate Sentry integration

**Base Path:** `/{MODE}/health` or `/health` (for basic health check)

**Authentication:** Most endpoints do not require authentication (except `/test-sentry`)

## Endpoints

### Health Check

**Endpoint:** `GET /health` or `GET /{MODE}/health`

**Description:** Returns the health status of the API service with environment information. This endpoint is typically used by load balancers and monitoring systems.

**Authentication:** Not required

**Request Headers:**
```
(No authentication required)
```

**Request Example:**
```http
GET /health HTTP/1.1
Host: api.example.com
```

**Response:**
```json
{
  "success": true,
  "message": "Service is healthy",
  "data": {
    "status": "ok"
  },
  "meta": {
    "service": "fastapi-backend-with-postgresql-api",
    "status": "ok",
    "env": {
      "API_VERSION": "1.0.0",
      "API_MODE": "development",
      "MODE": "dev/v1",
      "UTC": "UTC",
      "DEBUG_MODE": "false",
      "TIMEZONE": "UTC",
      "LOG_LEVEL": "info"
    }
  }
}
```

**Workflow:**
```
1. Client Request
   │
   ├─► Extract Environment Variables
   │   ├─► API_VERSION
   │   ├─► API_MODE
   │   ├─► MODE
   │   ├─► UTC
   │   ├─► DEBUG_MODE
   │   ├─► TIMEZONE
   │   └─► LOG_LEVEL
   │
   ├─► Build Response
   │   ├─► Status: "ok"
   │   └─► Meta Information
   │
   └─► Return 200 OK
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Client prepares request
  ├─► Load balancer/monitoring system initiates health check
  ├─► No authentication required
  └─► Prepare GET request to /health or /{MODE}/health

Step 2: Client sends request
  GET /health
  Headers:
    (No special headers required)

Step 3: Client receives response
  ├─► Success (200): Service is healthy, continue routing traffic
  ├─► Error (500): Service unhealthy, remove from load balancer
  └─► Timeout: Service unavailable, mark as down

Step 4: Client processes response
  ├─► Check response.status === "ok"
  ├─► Verify response time < threshold (e.g., 100ms)
  └─► Update service status in monitoring system

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request received
  ├─► No authentication validation needed
  └─► Process request immediately

Step 2: Gather environment information
  ├─► Extract environment variables:
  │   ├─► API_VERSION
  │   ├─► API_MODE
  │   ├─► MODE
  │   ├─► UTC
  │   ├─► DEBUG_MODE
  │   ├─► TIMEZONE
  │   └─► LOG_LEVEL
  └─► Build environment info object

Step 3: Build response
  ├─► Set status: "ok"
  ├─► Include service name
  ├─► Include environment information
  └─► Return 200 OK

Step 4: Error handling
  ├─► If environment variables not accessible: Return 500
  └─► Log any errors for debugging
```

**Use Cases:**
- Load balancer health checks
- Container orchestration health probes
- Service discovery
- Monitoring dashboards

---

### System Health Check

**Endpoint:** `GET /{MODE}/health/system`

**Description:** Returns detailed system information including CPU, memory, platform details, and environment configuration. Useful for system administrators and monitoring tools.

**Authentication:** Not required

**Request Headers:**
```
(No authentication required)
```

**Request Example:**
```http
GET /dev/v1/health/system HTTP/1.1
Host: api.example.com
```

**Response:**
```json
{
  "success": true,
  "message": "System health check completed",
  "data": {
    "status": "healthy",
    "system_info": {
      "platform": "linux",
      "nodeVersion": "v18.0.0",
      "cpuCount": 4,
      "memoryTotal": 8589934592,
      "memoryFree": 4294967296,
      "memoryUsed": 4294967296,
      "uptime": 3600
    },
    "environment": {
      "API_VERSION": "1.0.0",
      "API_MODE": "development",
      "MODE": "dev/v1",
      "DEBUG_MODE": "false",
      "LOG_LEVEL": "info"
    },
    "timestamp": 1704067200000
  }
}
```

**Response Fields:**
- `system_info.platform`: Operating system platform (Linux, Windows, macOS)
- `system_info.python_version`: Python version
- `system_info.cpu_count`: Number of CPU cores
- `system_info.memory_total`: Total system memory in bytes
- `system_info.memory_available`: Available memory in bytes
- `system_info.memory_percent`: Memory usage percentage
- `system_info.disk_usage`: Disk usage percentage
- `environment`: Environment configuration variables
- `timestamp`: Unix timestamp of the check

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Client prepares request
  ├─► Monitoring system or admin dashboard initiates check
  ├─► No authentication required
  └─► Prepare GET request to /{MODE}/health/system

Step 2: Client sends request
  GET /{MODE}/health/system
  Headers:
    (No special headers required)

Step 3: Client receives response
  ├─► Success (200): Process system information
  ├─► Error (500): Log error, show error message
  └─► Timeout: Mark service as unavailable

Step 4: Client processes data
  ├─► Extract system_info from response.data
  ├─► Format memory values (bytes → MB/GB)
  ├─► Display CPU, memory, disk usage
  ├─► Update monitoring dashboard
  └─► Alert if thresholds exceeded

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request received
  ├─► No authentication validation needed
  └─► Process request immediately

Step 2: Gather system information
  ├─► Import psutil and platform modules
  ├─► Get platform information:
  │   ├─► platform.platform() - OS platform
  │   └─► platform.python_version() - Python version
  ├─► Get CPU information:
  │   └─► psutil.cpu_count() - Number of CPU cores
  ├─► Get memory information:
  │   ├─► psutil.virtual_memory().total - Total memory
  │   ├─► psutil.virtual_memory().available - Available memory
  │   └─► psutil.virtual_memory().percent - Memory usage %
  └─► Get disk information:
      └─► psutil.disk_usage('/').percent - Disk usage %

Step 3: Gather environment information
  ├─► Extract environment variables:
  │   ├─► API_VERSION
  │   ├─► API_MODE
  │   ├─► MODE
  │   ├─► DEBUG_MODE
  │   └─► LOG_LEVEL
  └─► Build environment info object

Step 4: Build response
  ├─► Set status: "healthy"
  ├─► Include system_info object
  ├─► Include environment information
  ├─► Add timestamp
  └─► Return 200 OK

Step 5: Error handling
  ├─► If psutil not available: Return error
  ├─► If system info gathering fails: Return 500
  └─► Log errors for debugging
```

**Workflow:**
```
1. Client Request
   │
   ├─► Gather System Information
   │   ├─► Platform (process.platform)
   │   ├─► Node.js Version (process.version)
   │   ├─► CPU Count (os.cpus().length)
   │   ├─► Memory Stats (os.totalmem(), os.freemem())
   │   └─► System Uptime (os.uptime())
   │
   ├─► Gather Environment Info
   │   ├─► API_VERSION
   │   ├─► API_MODE
   │   ├─► MODE
   │   ├─► DEBUG_MODE
   │   └─► LOG_LEVEL
   │
   ├─► Calculate Memory Usage
   │   └─► memoryUsed = totalmem - freemem
   │
   ├─► Build Response
   │   ├─► Status: "healthy"
   │   ├─► System Information
   │   ├─► Environment Information
   │   └─► Timestamp
   │
   └─► Return 200 OK
```

**Use Cases:**
- System resource monitoring
- Performance analysis
- Capacity planning
- Troubleshooting system issues

---

### Test Sentry

**Endpoint:** `GET /{MODE}/health/test-sentry`

**Description:** Intentionally triggers different types of errors to test Sentry error tracking integration. Useful for validating error monitoring setup.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `test_sentry`

**Query Parameters:**
- `type` (optional): Type of error to test
  - `exception` (default): Manual exception capture
  - `message`: Manual message capture
  - `unhandled`: Unhandled error (caught by error handler)
  - `async`: Async error

**Request Headers:**
```
Authorization: Bearer <access_token>
# OR
X-Session-Token: <session_token>
```

**Request Example:**
```http
GET /dev/v1/health/test-sentry?type=exception HTTP/1.1
Host: api.example.com
Authorization: Bearer <token>
```

**Response (Exception Type):**
```json
{
  "success": true,
  "message": "Test exception sent to Sentry",
  "data": {
    "type": "exception",
    "environment": "development",
    "message": "Check your Sentry dashboard for the error",
    "error": "Test Sentry Exception - This is a test error"
  }
}
```

**Response (Message Type):**
```json
{
  "success": true,
  "message": "Test message sent to Sentry",
  "data": {
    "type": "message",
    "environment": "development",
    "message": "Check your Sentry dashboard for the message"
  }
}
```

**Response (Async Type):**
```json
{
  "success": true,
  "message": "Test async error scheduled",
  "data": {
    "type": "async",
    "environment": "development",
    "message": "Async error will be sent to Sentry in 100ms"
  }
}
```

**Workflow (Exception Type):**
```
1. Client Request with Authentication
   │
   ├─► Validate JWT Token
   │
   ├─► Extract Query Parameters
   │   └─► type = "exception" (default)
   │
   ├─► Set Sentry User Context
   │   └─► If user available, set user info
   │
   ├─► Add Breadcrumb
   │   └─► Log test initiation
   │
   ├─► Create Test Error
   │   ├─► Error Name: "SentryTestError"
   │   └─► Error Message: "Test Sentry Exception..."
   │
   ├─► Capture Exception in Sentry
   │   ├─► Add Tags (test_type, environment, endpoint)
   │   └─► Add Extra Data (query, userAgent, IP)
   │
   └─► Return 200 OK with Success Message
```

**Workflow (Unhandled Type):**
```
1. Client Request with Authentication
   │
   ├─► Validate JWT Token
   │
   ├─► Extract Query Parameters
   │   └─► type = "unhandled"
   │
   ├─► Throw Error
   │   └─► "Test Unhandled Error..."
   │
   ├─► Error Handler Catches
   │   ├─► Log Error
   │   ├─► Capture in Sentry
   │   └─► Format Error Response
   │
   └─► Return 500 with Error Details
```

**Workflow (Async Type):**
```
1. Client Request with Authentication
   │
   ├─► Validate JWT Token
   │
   ├─► Extract Query Parameters
   │   └─► type = "async"
   │
   ├─► Schedule Async Error
   │   └─► setTimeout(() => {
   │       └─► Capture Exception in Sentry
   │   }, 100)
   │
   └─► Return 200 OK Immediately
       └─► Error sent to Sentry after 100ms
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Client prepares request
  ├─► Admin/developer wants to test Sentry integration
  ├─► Select error type (exception, message, unhandled, async)
  ├─► Retrieve stored access_token or session_token
  └─► Prepare GET request with query parameter

Step 2: Client sends request
  GET /{MODE}/health/test-sentry?type=exception
  Headers:
    Authorization: Bearer <token>
    # OR
    X-Session-Token: <session_token>

Step 3: Client receives response
  ├─► Success (200): Check Sentry dashboard for error
  ├─► Unauthorized (401): Redirect to login
  ├─► Forbidden (403): Show permission error
  └─► Error (500): Error was captured (for unhandled type)

Step 4: Client processes response
  ├─► Display success message
  ├─► Show link to Sentry dashboard
  └─► Verify error appears in Sentry

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token (JWT verification)
  ├─► Check token blacklist
  ├─► Extract user from token
  ├─► Extract query parameter (type)
  └─► Validate type parameter (exception, message, unhandled, async)

Step 2: Permission check
  ├─► Check if user has "test_sentry" permission
  └─► If no permission: Return 403 Forbidden

Step 3: Set Sentry context
  ├─► Set user context (user_id, email)
  ├─► Add breadcrumb with test initiation info
  └─► Set environment from API_MODE

Step 4: Execute test based on type
  ├─► If type = "exception":
  │   ├─► Create test exception
  │   ├─► Capture exception in Sentry with tags and extra data
  │   └─► Return success response
  │
  ├─► If type = "message":
  │   ├─► Capture warning message in Sentry
  │   └─► Return success response
  │
  ├─► If type = "unhandled":
  │   ├─► Throw exception (will be caught by error handler)
  │   └─► Error handler captures in Sentry and returns 500
  │
  └─► If type = "async":
      ├─► Schedule async task to capture error after 100ms
      └─► Return success response immediately

Step 5: Response preparation
  ├─► Build SUCCESS response
  ├─► Include test type and environment
  ├─► Include message to check Sentry dashboard
  └─► Return response

Step 6: Error handling
  ├─► Invalid type: Return 400
  ├─► Permission denied: Return 403
  ├─► Token invalid: Return 401
  └─► Other errors: Log and return 500
```

**Error Types:**

1. **Exception**: Manually captures an exception with context
2. **Message**: Sends a warning message to Sentry
3. **Unhandled**: Throws an error that gets caught by the global error handler
4. **Async**: Schedules an async error to test async error tracking

**Use Cases:**
- Testing Sentry integration
- Validating error tracking setup
- Debugging error monitoring
- Verifying error context capture

---

### Database Health Check

**Endpoint:** `GET /{MODE}/health/database`

**Description:** Checks database connectivity and response time. Returns database status and connection metrics.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `view_system_health`

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
  "message": "Database is healthy",
  "data": {
    "status": "healthy",
    "message": "Database connection is working",
    "response_time": 2.45,
    "database_type": "PostgreSQL"
  }
}
```

**Error Response (503 Service Unavailable):**
```json
{
  "success": false,
  "message": "Database is unhealthy",
  "error": {
    "code": "DATABASE_UNHEALTHY",
    "details": {
      "status": "error",
      "message": "Database check failed: Connection refused",
      "error": "Connection refused"
    }
  }
}
```

---

### Storage Health Check

**Endpoint:** `GET /{MODE}/health/storage`

**Description:** Checks Google Cloud Storage connectivity and status. Returns storage service metrics.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `view_system_health`

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
  "message": "Storage is healthy",
  "data": {
    "status": "healthy",
    "message": "Google Cloud Storage is working",
    "response_time": 150.23,
    "bucket_name": "my-bucket",
    "blob_count": 1,
    "storage_class": "ProfessionalMediaStorage"
  }
}
```

**Error Response (503 Service Unavailable):**
```json
{
  "success": false,
  "message": "Storage is unhealthy",
  "error": {
    "code": "STORAGE_UNHEALTHY",
    "details": {
      "status": "error",
      "message": "GCS connection failed",
      "error": "Bucket not found"
    }
  }
}
```

---

## Workflows

### Complete Health Check Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Health Check Request                     │
└────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Determine Endpoint Type                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Basic Health │  │ System Info  │  │ Test Sentry  │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Gather Env Vars │ │ Gather Sys Info │ │ Validate Auth   │
│ Return Status   │ │ Calculate Memory│ │ Test Error Type │
│                 │ │ Return Metrics  │ │ Capture Sentry  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Return Response                          │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling

### Health Check Errors

**500 Internal Server Error:**
```json
{
  "success": false,
  "message": "Health check failed",
  "error": "Error details",
  "statusCode": 500
}
```

**Common Error Scenarios:**
- Environment variables not accessible
- System information gathering fails
- Sentry configuration issues (for test-sentry endpoint)

### Error Handling Workflow

```
1. Error Occurs
   │
   ├─► Log Error
   │   └─► Winston Logger
   │
   ├─► Capture in Sentry (if applicable)
   │   └─► captureException()
   │
   ├─► Format Error Response
   │   └─► ERROR.fromMap()
   │
   └─► Return Error Response
       └─► Appropriate Status Code
```

---

## Best Practices

1. **Use Basic Health Check for Load Balancers**: The `/health` endpoint is lightweight and perfect for frequent health checks
2. **Use System Health for Monitoring**: The `/health/system` endpoint provides detailed metrics for monitoring dashboards
3. **Test Sentry Regularly**: Use `/test-sentry` to validate error tracking is working correctly
4. **Monitor Response Times**: Health checks should respond quickly (< 100ms)
5. **Cache System Info**: Consider caching system information if called frequently
6. **Secure Test Endpoint**: The test-sentry endpoint requires authentication to prevent abuse

---

## Client-Side Implementation

### Token Management

```javascript
// Get authentication token (prefer session_token)
function getAuthToken() {
  return localStorage.getItem('session_token') || 
         localStorage.getItem('access_token');
}

// API request helper for health endpoints
async function healthRequest(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  // Add token if endpoint requires authentication
  const token = getAuthToken();
  if (token && url.includes('/test-sentry') || url.includes('/database') || url.includes('/storage')) {
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
    throw new Error('You do not have permission to access this endpoint');
  }
  
  const data = await response.json();
  
  if (!data.success && response.status >= 400) {
    throw new Error(data.error?.message || 'Health check failed');
  }
  
  return data;
}
```

### Basic Health Check

```javascript
// Check basic API health (no authentication required)
async function checkHealth() {
  try {
    const response = await fetch('/health', {
      method: 'GET'
    });
    
    const data = await response.json();
    
    if (data.success && data.data.status === 'ok') {
      console.log('Service is healthy');
      return {
        healthy: true,
        status: data.data.status,
        environment: data.meta.env
      };
    } else {
      console.error('Service is unhealthy');
      return {
        healthy: false,
        status: 'error'
      };
    }
  } catch (error) {
    console.error('Health check failed:', error);
    return {
      healthy: false,
      error: error.message
    };
  }
}

// Use in load balancer or monitoring
setInterval(async () => {
  const health = await checkHealth();
  if (!health.healthy) {
    console.error('Service is down!');
    // Alert monitoring system
  }
}, 30000); // Check every 30 seconds
```

### System Health Check

```javascript
// Get detailed system information
async function getSystemHealth() {
  try {
    const response = await fetch('/api/v1/health/system', {
      method: 'GET'
    });
    
    const data = await response.json();
    
    if (data.success && data.data) {
      const systemInfo = data.data.system_info;
      
      // Format memory values
      const formatBytes = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
      };
      
      return {
        healthy: true,
        platform: systemInfo.platform,
        pythonVersion: systemInfo.python_version,
        cpuCount: systemInfo.cpu_count,
        memory: {
          total: formatBytes(systemInfo.memory_total),
          available: formatBytes(systemInfo.memory_available),
          percent: systemInfo.memory_percent
        },
        diskUsage: systemInfo.disk_usage,
        environment: data.data.environment
      };
    }
  } catch (error) {
    console.error('System health check failed:', error);
    return {
      healthy: false,
      error: error.message
    };
  }
}

// Display system health in dashboard
async function displaySystemHealth() {
  const health = await getSystemHealth();
  
  if (health.healthy) {
    document.getElementById('cpu-count').textContent = health.cpuCount;
    document.getElementById('memory-total').textContent = health.memory.total;
    document.getElementById('memory-available').textContent = health.memory.available;
    document.getElementById('memory-percent').textContent = `${health.memory.percent}%`;
    document.getElementById('disk-usage').textContent = `${health.diskUsage}%`;
    
    // Alert if memory or disk usage is high
    if (health.memory.percent > 80) {
      showWarning('Memory usage is high: ' + health.memory.percent + '%');
    }
    if (health.diskUsage > 80) {
      showWarning('Disk usage is high: ' + health.diskUsage + '%');
    }
  }
}
```

### Database Health Check

```javascript
// Check database connectivity
async function checkDatabaseHealth() {
  try {
    const response = await healthRequest('/api/v1/health/database', {
      method: 'GET'
    });
    
    if (response && response.data) {
      const dbHealth = response.data;
      
      return {
        healthy: dbHealth.status === 'healthy',
        status: dbHealth.status,
        message: dbHealth.message,
        responseTime: dbHealth.response_time,
        databaseType: dbHealth.database_type
      };
    }
  } catch (error) {
    console.error('Database health check failed:', error);
    return {
      healthy: false,
      error: error.message
    };
  }
}

// Display database health status
async function displayDatabaseHealth() {
  const health = await checkDatabaseHealth();
  
  const statusElement = document.getElementById('db-status');
  if (statusElement) {
    statusElement.textContent = health.healthy ? 'Healthy' : 'Unhealthy';
    statusElement.className = health.healthy ? 'status-healthy' : 'status-unhealthy';
    
    if (health.responseTime) {
      document.getElementById('db-response-time').textContent = 
        `${health.responseTime}ms`;
    }
  }
}
```

### Storage Health Check

```javascript
// Check storage connectivity
async function checkStorageHealth() {
  try {
    const response = await healthRequest('/api/v1/health/storage', {
      method: 'GET'
    });
    
    if (response && response.data) {
      const storageHealth = response.data;
      
      return {
        healthy: storageHealth.status === 'healthy',
        status: storageHealth.status,
        message: storageHealth.message,
        responseTime: storageHealth.response_time,
        bucketName: storageHealth.bucket_name,
        blobCount: storageHealth.blob_count
      };
    }
  } catch (error) {
    console.error('Storage health check failed:', error);
    return {
      healthy: false,
      error: error.message
    };
  }
}
```

### Test Sentry

```javascript
// Test Sentry error tracking
async function testSentry(type = 'exception') {
  try {
    const response = await healthRequest(
      `/api/v1/health/test-sentry?type=${type}`,
      {
        method: 'GET'
      }
    );
    
    if (response && response.data) {
      const testResult = response.data;
      
      showNotification(
        `Test ${testResult.type} sent to Sentry. Check your Sentry dashboard.`
      );
      
      // Open Sentry dashboard in new tab
      const sentryUrl = 'https://sentry.io/organizations/your-org/issues/';
      window.open(sentryUrl, '_blank');
      
      return testResult;
    }
  } catch (error) {
    console.error('Sentry test failed:', error);
    showError('Failed to test Sentry: ' + error.message);
    throw error;
  }
}

// Test different error types
async function testAllSentryTypes() {
  const types = ['exception', 'message', 'unhandled', 'async'];
  
  for (const type of types) {
    console.log(`Testing Sentry type: ${type}`);
    try {
      await testSentry(type);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
    } catch (error) {
      console.error(`Failed to test ${type}:`, error);
    }
  }
}
```

### Complete Health Monitor Component

```javascript
// Complete Health Monitor Class
class HealthMonitor {
  constructor() {
    this.healthStatus = {
      api: null,
      system: null,
      database: null,
      storage: null
    };
    this.monitoringInterval = null;
  }
  
  async init() {
    try {
      // Initial health check
      await this.checkAll();
      
      // Set up auto-refresh (every 60 seconds)
      this.startMonitoring(60 * 1000);
    } catch (error) {
      console.error('Failed to initialize health monitor:', error);
    }
  }
  
  async checkAll() {
    try {
      showLoading('Checking system health...');
      
      // Check all health endpoints in parallel
      const [apiHealth, systemHealth, dbHealth, storageHealth] = await Promise.allSettled([
        checkHealth(),
        getSystemHealth(),
        checkDatabaseHealth(),
        checkStorageHealth()
      ]);
      
      this.healthStatus.api = apiHealth.status === 'fulfilled' ? apiHealth.value : null;
      this.healthStatus.system = systemHealth.status === 'fulfilled' ? systemHealth.value : null;
      this.healthStatus.database = dbHealth.status === 'fulfilled' ? dbHealth.value : null;
      this.healthStatus.storage = storageHealth.status === 'fulfilled' ? storageHealth.value : null;
      
      this.renderHealthStatus();
      hideLoading();
    } catch (error) {
      hideLoading();
      console.error('Health check failed:', error);
      showError('Failed to check system health');
    }
  }
  
  renderHealthStatus() {
    // Render API health
    this.renderStatus('api-status', this.healthStatus.api);
    
    // Render system health
    if (this.healthStatus.system) {
      this.renderSystemMetrics(this.healthStatus.system);
    }
    
    // Render database health
    this.renderStatus('db-status', this.healthStatus.database);
    
    // Render storage health
    this.renderStatus('storage-status', this.healthStatus.storage);
  }
  
  renderStatus(elementId, health) {
    const element = document.getElementById(elementId);
    if (element && health) {
      element.textContent = health.healthy ? 'Healthy' : 'Unhealthy';
      element.className = health.healthy ? 'status-healthy' : 'status-unhealthy';
    }
  }
  
  renderSystemMetrics(system) {
    if (system.healthy) {
      document.getElementById('cpu-count').textContent = system.cpuCount;
      document.getElementById('memory-percent').textContent = `${system.memory.percent}%`;
      document.getElementById('disk-usage').textContent = `${system.diskUsage}%`;
      
      // Update progress bars
      this.updateProgressBar('memory-bar', system.memory.percent);
      this.updateProgressBar('disk-bar', system.diskUsage);
    }
  }
  
  updateProgressBar(elementId, percent) {
    const bar = document.getElementById(elementId);
    if (bar) {
      bar.style.width = `${percent}%`;
      bar.className = percent > 80 ? 'progress-bar-danger' : 
                     percent > 60 ? 'progress-bar-warning' : 
                     'progress-bar-success';
    }
  }
  
  startMonitoring(interval) {
    this.monitoringInterval = setInterval(() => {
      this.checkAll();
    }, interval);
  }
  
  stopMonitoring() {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }
}

// Initialize health monitor
document.addEventListener('DOMContentLoaded', () => {
  const healthMonitor = new HealthMonitor();
  healthMonitor.init();
});
```

### Error Handling

```javascript
// Enhanced error handling for health checks
async function healthCheckWithRetry(url, maxRetries = 3) {
  let lastError;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await healthRequest(url, { method: 'GET' });
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

---

## Summary

This documentation provides comprehensive coverage of all health and monitoring endpoints:

### Endpoints Covered:
1. ✅ **Health Check** - Basic API health status (public)
2. ✅ **System Health Check** - Detailed system information (public)
3. ✅ **Database Health Check** - Database connectivity check (authenticated)
4. ✅ **Storage Health Check** - Google Cloud Storage check (authenticated)
5. ✅ **Test Sentry** - Sentry error tracking test (authenticated)

### Documentation Sections:
- ✅ Overview and system architecture
- ✅ Detailed endpoint documentation with examples
- ✅ Client-server communication flows
- ✅ Complete workflows and diagrams
- ✅ Error handling guide
- ✅ Best practices
- ✅ Complete client-side implementation examples
- ✅ Health monitoring component examples

### Key Features:
- **Public endpoints** - Basic and system health checks don't require authentication
- **Authenticated endpoints** - Database, storage, and Sentry test require permissions
- **Comprehensive monitoring** - System metrics, database status, storage connectivity
- **Error tracking** - Sentry integration testing
- **Client-side examples** - Ready-to-use JavaScript code for health monitoring

All endpoints are fully documented with request/response examples, client-server communication flows, and implementation guidance.

---

**Last Updated**: January 2025

