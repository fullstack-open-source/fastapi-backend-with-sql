# Authentication Architecture - Instagram Pattern

> **Complete Documentation for Multi-Token Authentication System**

This document describes the authentication architecture following Instagram's multi-token pattern, providing comprehensive details on token types, flows, security features, and implementation guidelines.

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Token Types](#token-types)
- [Authentication Flows](#authentication-flows)
- [Token Validation](#token-validation)
- [Security Features](#security-features)
- [Client-Server Communication](#client-server-communication)
- [Configuration](#configuration)
- [Implementation Examples](#implementation-examples)
- [Best Practices](#best-practices)
- [Comparison with Traditional JWT](#comparison-with-traditional-jwt)

## Architecture Overview

The authentication system implements a **stateless, multi-token architecture** similar to Instagram:

### Core Principles

1. **Stateless Authentication**: No database storage of sessions - all session info embedded in JWT tokens
2. **Multi-Token System**: Three token types with different lifespans and purposes
3. **Token Blacklisting**: Cache-based blacklist for token invalidation (logout)
4. **Session Management**: Unique session_id links all tokens together
5. **Token Rotation**: Refresh tokens rotate on each refresh for security

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   CLIENT     │
│  (Browser)   │
└──────┬───────┘
       │
       │ 1. Login Request
       ▼
┌──────────────┐
│   SERVER     │
│  (FastAPI)   │
└──────┬───────┘
       │
       │ 2. Generate Tokens
       ▼
┌─────────────────────────────────────┐
│         TOKEN GENERATION            │
│  ┌──────────┐  ┌──────────┐  ┌─────┐│
│  │  Access  │  │ Session │  │Refresh│
│  │  Token   │  │  Token  │  │ Token │
│  │ (1 hour) │  │ (7 days)│  │(30d) │
│  └────┬─────┘  └────┬────┘  └──┬───┘│
│       │             │           │    │
│       └─────────────┴───────────┘    │
│              session_id               │
└─────────────────────────────────────┘
       │
       │ 3. Return Tokens
       ▼
┌──────────────┐
│   CLIENT     │
│  Store Tokens│
└──────┬───────┘
       │
       │ 4. API Requests
       ▼
┌─────────────────────────────────────┐
│      TOKEN VALIDATION               │
│  ┌──────────────────────────────┐  │
│  │ 1. Extract Token              │  │
│  │ 2. Decode JWT                 │  │
│  │ 3. Check Blacklist            │  │
│  │ 4. Validate Origin            │  │
│  │ 5. Build User Object          │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
       │
       │ 5. Validate
       ▼
┌──────────────┐
│   REDIS      │
│  Blacklist   │
└──────────────┘
```

## Token Types

### 1. Access Token
- **Lifespan**: 1 hour (configurable via `ACCESS_TOKEN_EXPIRY_MINUTES`)
- **Purpose**: Primary token for API authentication
- **Payload**: Minimal - user_id, username, email, basic permissions
- **Usage**: `Authorization: Bearer <access_token>` header
- **Storage**: Memory or secure storage
- **Validation**: Fast - lightweight payload

**Token Payload Example:**
```json
{
  "sub": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "username": "johndoe",
  "email": "john@example.com",
  "exp": 1704067200,
  "iat": 1704063600,
  "jti": "f533589d-48d3-4b67-9430-c0b4793ac13e",
  "type": "access",
  "aud": "authenticated",
  "is_active": true,
  "is_verified": true,
  "session_id": "session-uuid-here",
  "origin": "https://example.com"
}
```

### 2. Session Token (Recommended)
- **Lifespan**: 7 days (configurable via `SESSION_TOKEN_EXPIRY_MINUTES`)
- **Purpose**: Full user profile for client-side validation
- **Payload**: Complete user profile + permissions
- **Usage**: `X-Session-Token: <session_token>` or `Authorization: Bearer <session_token>`
- **Storage**: Secure storage (httpOnly cookie preferred)
- **Validation**: Fastest - no database lookup needed

**Token Payload Example:**
```json
{
  "sub": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "profile_picture_url": "https://...",
  "exp": 1704672000,
  "iat": 1704063600,
  "type": "session",
  "aud": "authenticated",
  "is_active": true,
  "is_verified": true,
  "session_id": "session-uuid-here",
  "origin": "https://example.com",
  "permissions": ["view_dashboard", "edit_profile", "view_user"],
  "groups": ["user", "admin"]
}
```

### 3. Refresh Token
- **Lifespan**: 30 days (configurable via `REFRESH_TOKEN_EXPIRY_MINUTES`)
- **Purpose**: Obtain new tokens when they expire
- **Payload**: Minimal - user_id, session_id
- **Usage**: Send to `/auth/refresh-token` endpoint
- **Storage**: Most secure storage (httpOnly cookie)
- **Validation**: Cannot be used for API authentication

**Token Payload Example:**
```json
{
  "sub": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "exp": 1706655600,
  "iat": 1704063600,
  "type": "refresh",
  "aud": "authenticated",
  "session_id": "session-uuid-here",
  "origin": "https://example.com"
}
```

### 4. Session ID
- **Purpose**: Unique identifier linking all tokens in a session
- **Embedded**: In all three token types
- **Usage**: Logout operations, session invalidation

## Authentication Flow

### Login Flow

**Complete Client-Server Communication:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User submits credentials
  ├─► User enters email/phone and password
  ├─► Client validates form (email format, password length)
  └─► User clicks "Login" button

Step 2: Client sends login request
  POST /{MODE}/auth/login-with-password
  Headers:
    Content-Type: application/x-www-form-urlencoded
  Body:
    username: user@example.com
    password: ********

Step 3: Client receives response
  ├─► Success (200): Extract tokens from response
  ├─► Unauthorized (401): Show invalid credentials error
  └─► Error (500): Show error message

Step 4: Client stores tokens
  ├─► Store access_token (memory or localStorage)
  ├─► Store session_token (preferred - localStorage or httpOnly cookie)
  ├─► Store refresh_token (httpOnly cookie - most secure)
  └─► Store session_id (for logout operations)

Step 5: Client uses tokens
  ├─► Use session_token for API calls (recommended)
  ├─► Include in X-Session-Token header
  └─► Or use Authorization: Bearer header

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract username and password from request
  ├─► Validate input format
  └─► Check if user exists

Step 2: User authentication
  ├─► Find user by email or phone
  ├─► Verify password using bcrypt
  ├─► Check user status (is_active, is_verified)
  └─► Update last_sign_in_at timestamp

Step 3: Generate session ID
  ├─► Generate UUID v4
  └─► This links all tokens together

Step 4: Generate tokens
  ├─► Access Token:
  │   ├─► Payload: user_id, username, email, is_active, is_verified
  │   ├─► Expiry: 1 hour
  │   ├─► Include session_id and origin
  │   └─► Sign with JWT_SECRET_KEY
  │
  ├─► Refresh Token:
  │   ├─► Payload: user_id, session_id
  │   ├─► Expiry: 30 days
  │   ├─► Include origin
  │   └─► Sign with JWT_SECRET_KEY
  │
  └─► Session Token:
      ├─► Payload: Complete user profile + permissions
      ├─► Expiry: 7 days
      ├─► Include session_id and origin
      └─► Sign with JWT_SECRET_KEY

Step 5: Clear user blacklist (if exists)
  ├─► Remove user from blacklist on successful login
  └─► Allows user to login after being blacklisted

Step 6: Response preparation
  ├─► Build SUCCESS response
  ├─► Include all tokens and session_id
  └─► Return response with user's language preference

Step 7: Error handling
  ├─► Invalid credentials: Return 401
  ├─► User inactive: Return 401
  ├─► User not verified: Return 401
  └─► Server error: Log and return 500
```

**Response Example:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "session_id": "f533589d-48d3-4b67-9430-c0b4793ac13e",
    "token_type": "bearer"
  }
}
```

### Token Refresh Flow

**Complete Client-Server Communication:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Token expiration detected
  ├─► API request returns 401 Unauthorized
  ├─► Client detects token expiration
  └─► Client initiates token refresh

Step 2: Client sends refresh request
  POST /{MODE}/auth/refresh-token
  Headers:
    Content-Type: application/json
  Body:
    {
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }

Step 3: Client receives response
  ├─► Success (200): Extract new tokens
  ├─► Unauthorized (401): Redirect to login
  └─► Error (500): Show error message

Step 4: Client updates tokens
  ├─► Replace old access_token with new one
  ├─► Replace old session_token with new one
  ├─► Replace old refresh_token with new one
  ├─► Update session_id
  └─► Retry original API request with new token

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract refresh_token from request body
  ├─► Validate refresh_token is provided
  └─► Parse request (RefreshTokenRequest model)

Step 2: Validate refresh token
  ├─► Decode JWT token
  ├─► Verify signature with JWT_SECRET_KEY
  ├─► Check token expiration
  ├─► Validate token type = "refresh"
  ├─► Extract user_id and session_id
  └─► Check if token is blacklisted

Step 3: Check session and user blacklist
  ├─► Check if session_id is blacklisted
  ├─► Check if user_id is blacklisted
  └─► If blacklisted: Return 401 Unauthorized

Step 4: Get user data
  ├─► Fetch user from database by user_id
  ├─► Verify user exists and is active
  └─► Get user permissions and groups

Step 5: Token rotation (blacklist old tokens)
  ├─► Blacklist old refresh_token
  ├─► Blacklist old session_id (invalidates all old tokens)
  └─► This prevents token reuse if compromised

Step 6: Generate new session
  ├─► Generate NEW session_id (UUID v4)
  └─► This creates a completely new session

Step 7: Generate new tokens
  ├─► Access Token:
  │   ├─► Payload: user_id, username, email, is_active, is_verified
  │   ├─► Expiry: 1 hour
  │   ├─► Include NEW session_id and origin
  │   └─► Sign with JWT_SECRET_KEY
  │
  ├─► Refresh Token:
  │   ├─► Payload: user_id, NEW session_id
  │   ├─► Expiry: 30 days
  │   ├─► Include origin
  │   └─► Sign with JWT_SECRET_KEY
  │
  └─► Session Token:
      ├─► Payload: Complete user profile + permissions
      ├─► Expiry: 7 days
      ├─► Include NEW session_id and origin
      └─► Sign with JWT_SECRET_KEY

Step 8: Response preparation
  ├─► Build SUCCESS response
  ├─► Include all new tokens and NEW session_id
  └─► Return response with user's language preference

Step 9: Error handling
  ├─► Invalid refresh token: Return 401
  ├─► Token blacklisted: Return 401
  ├─► Session blacklisted: Return 401
  ├─► User blacklisted: Return 401
  └─► Server error: Log and return 500
```

**Key Points:**
- **Token Rotation**: Old tokens are blacklisted to prevent reuse
- **Session Rotation**: New session_id is generated on each refresh
- **Security**: Prevents token reuse if refresh token is compromised

### Logout Flow

**Complete Client-Server Communication:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User initiates logout
  ├─► User clicks "Logout" button
  ├─► Client shows confirmation (optional)
  └─► Client prepares logout request

Step 2: Client sends logout request
  POST /{MODE}/auth/logout
  Headers:
    Authorization: Bearer <access_token>
    # OR
    X-Session-Token: <session_token>
  Body:
    {
      "logout_all_devices": false  // Optional
    }

Step 3: Client receives response
  ├─► Success (200): Clear tokens, redirect to login
  ├─► Unauthorized (401): Already logged out, clear tokens
  └─► Error (500): Show error message

Step 4: Client cleanup
  ├─► Remove tokens from storage
  ├─► Clear httpOnly cookies (if used)
  ├─► Clear localStorage/sessionStorage
  └─► Redirect to login page

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token (JWT verification)
  ├─► Extract session_id from token
  ├─► Extract token_type from token
  └─► Parse request body (logout_all_devices flag)

Step 2: Blacklist current token
  ├─► Hash token for blacklist key
  ├─► Add to Redis blacklist
  ├─► Set TTL to match token expiration
  └─► Key format: blacklist:{token_type}:{token_hash}

Step 3: Blacklist session
  ├─► Add session_id to session blacklist
  ├─► Set TTL to match refresh token expiration (longest)
  └─► Key format: blacklist:session:{session_id}
  └─► This invalidates ALL tokens in the session

Step 4: User-level blacklist (if logout_all_devices)
  ├─► Extract user_id from token
  ├─► Add user_id to user blacklist
  ├─► Set TTL to match refresh token expiration
  └─► Key format: blacklist:user:{user_id}
  └─► This invalidates ALL sessions for the user

Step 5: Response preparation
  ├─► Build SUCCESS response
  ├─► Include revocation status for each operation
  └─► Return response

Step 6: Error handling
  ├─► Invalid token: Return 401 (but still process if possible)
  ├─► Expired token: Return 401 (but still blacklist if session_id available)
  └─► Server error: Log and return 500
```

**Response Example:**
```json
{
  "success": true,
  "message": "Logout successful",
  "data": {
    "token_revoked": true,
    "session_revoked": true,
    "all_devices_logged_out": false,
    "revoked_session_id": "f533589d-48d3-4b67-9430-c0b4793ac13e"
  }
}
```

**Logout Types:**
- **Single Device**: Only current session is invalidated
- **All Devices**: All user sessions are invalidated (logout_all_devices: true)

## Token Validation Flow

### Request Authentication

**Complete Validation Process:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Client makes API request
  ├─► Client retrieves token from storage
  ├─► Prefer session_token (recommended)
  └─► Add token to request headers

Step 2: Client sends request
  GET /{MODE}/api/endpoint
  Headers:
    X-Session-Token: <session_token>
    # OR
    Authorization: Bearer <access_token>

Step 3: Client receives response
  ├─► Success (200): Process response data
  ├─► Unauthorized (401): Token expired or invalid
  │   ├─► Attempt token refresh
  │   └─► If refresh fails: Redirect to login
  └─► Forbidden (403): Permission denied

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Extract Token (Priority Order)
  ├─► 1. X-Session-Token header (preferred - fastest validation)
  ├─► 2. Authorization: Bearer header (standard OAuth2)
  ├─► 3. OAuth2 scheme (for Swagger UI compatibility)
  └─► 4. access_token query parameter (backward compatibility)

Step 2: Decode JWT Token
  ├─► Verify JWT signature with JWT_SECRET_KEY
  ├─► Check token expiration (exp claim)
  ├─► Extract payload (user_id, token_type, session_id, etc.)
  └─► Handle audience validation (aud: "authenticated")

Step 3: Validate Token Type
  ├─► Check token_type from payload
  ├─► Accept: "access" or "session"
  └─► Reject: "refresh" (cannot be used for API authentication)

Step 4: Blacklist Checks (Fastest First - Optimized Order)
  ├─► 1. Check token blacklist (most common, fastest)
  │   └─► Key: blacklist:{token_type}:{token_hash}
  │
  ├─► 2. Check session blacklist
  │   └─► Key: blacklist:session:{session_id}
  │
  └─► 3. Check user blacklist
      └─► Key: blacklist:user:{user_id}

Step 5: Origin Validation
  ├─► Extract origin from token payload
  ├─► Extract origin from request headers
  ├─► Compare token origin with request origin
  └─► Allow localhost in development mode

Step 6: Build User Object
  ├─► If session_token:
  │   ├─► Extract full user profile from token payload
  │   ├─► Extract permissions from token payload
  │   └─► No database lookup needed (fastest)
  │
  └─► If access_token:
      ├─► Extract minimal user data from token
      ├─► Optionally: Fetch full user data from database
      └─► Build User object

Step 7: Return User Object
  ├─► User object available for endpoint handlers
  └─► Includes all user data and permissions

Step 8: Error Handling
  ├─► No token: Return 401 Unauthorized
  ├─► Invalid token: Return 401 Unauthorized
  ├─► Expired token: Return 401 Unauthorized
  ├─► Token blacklisted: Return 401 Unauthorized
  ├─► Invalid token type: Return 401 Unauthorized
  └─► Origin mismatch: Return 401 Unauthorized
```

**Performance Optimization:**
- **Session Token**: Fastest validation (no database lookup)
- **Access Token**: Fast validation (minimal payload)
- **Blacklist Checks**: Ordered by frequency (token > session > user)
- **Caching**: Redis cache for blacklist checks (sub-millisecond)

## Security Features

### 1. Token Blacklisting
- **Storage**: Redis cache (or in-memory fallback)
- **Key Format**: `blacklist:{token_type}:{token_hash}`
- **TTL**: Matches token expiration time
- **Purpose**: Invalidate tokens on logout

### 2. Session Blacklisting
- **Storage**: Redis cache
- **Key Format**: `blacklist:session:{session_id}`
- **TTL**: Matches refresh token expiration (longest)
- **Purpose**: Invalidate all tokens in a session

### 3. User Blacklisting
- **Storage**: Redis cache
- **Key Format**: `blacklist:user:{user_id}`
- **TTL**: Matches refresh token expiration
- **Purpose**: Invalidate all sessions for a user

### 4. Token Rotation
- **On Refresh**: Old refresh token is blacklisted
- **New Session**: Each refresh creates a new session_id
- **Security**: Prevents token reuse if compromised

### 5. Origin Validation
- **Purpose**: Prevent token reuse across domains
- **Validation**: Token origin must match request origin
- **Flexibility**: Localhost allowed in development

## Configuration

All settings are configurable via environment variables:

```bash
# Required
JWT_SECRET_KEY=your-secret-key-here

# Optional (with defaults)
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRY_MINUTES=60
SESSION_TOKEN_EXPIRY_MINUTES=10080
REFRESH_TOKEN_EXPIRY_MINUTES=43200
BCRYPT_SALT_ROUNDS=10
```

## Key Differences from Traditional JWT

| Feature | Traditional JWT | Instagram Pattern (This Implementation) |
|---------|----------------|------------------------------------------|
| **Tokens** | Single access token | Multi-token (access, refresh, session) |
| **Session Storage** | Database or stateless | Stateless with cache blacklist |
| **Session ID** | Not used | Embedded in all tokens |
| **Token Refresh** | Same session | New session (token rotation) |
| **Logout** | Client-side only | Server-side blacklisting |
| **User Profile** | Database lookup | Embedded in session_token |

## Benefits

1. **Performance**: Session tokens eliminate database lookups
2. **Security**: Token rotation and blacklisting
3. **Scalability**: Stateless design scales horizontally
4. **Flexibility**: Multiple token types for different use cases
5. **User Experience**: Longer session tokens reduce refresh operations

## Implementation Files

- **Token Generation**: `src/authenticate/checkpoint.py`
- **Token Validation**: `src/authenticate/authenticate.py`
- **Session Management**: `src/authenticate/session_manager.py`
- **API Endpoints**: `router/authenticate/authenticate.py`
- **Configuration**: `.env` file

## Security Considerations

### Token Security

1. **JWT Secret Key**
   - Use strong, random secret key (minimum 32 characters)
   - Never commit secret key to version control
   - Rotate secret key periodically
   - Use different keys for different environments

2. **Token Storage**
   - **Session Token**: localStorage or sessionStorage (acceptable for client-side validation)
   - **Access Token**: localStorage or memory (short-lived)
   - **Refresh Token**: httpOnly cookie (most secure, prevents XSS)

3. **Token Transmission**
   - Always use HTTPS in production
   - Never send tokens in URL query parameters (except for backward compatibility)
   - Prefer headers over query parameters
   - Use X-Session-Token header for session tokens

4. **Token Expiration**
   - Access tokens: Short-lived (1 hour)
   - Session tokens: Medium-lived (7 days)
   - Refresh tokens: Long-lived (30 days)
   - Balance security with user experience

### Blacklist Security

1. **Redis Configuration**
   - Use Redis for production (fast, persistent)
   - Configure Redis authentication
   - Use Redis TLS in production
   - Set appropriate TTL for blacklist entries

2. **Blacklist Keys**
   - Use hashed tokens for keys (prevent key enumeration)
   - Include token type in key (prevent collisions)
   - Set TTL to match token expiration

3. **Fallback Strategy**
   - In-memory cache fallback if Redis unavailable
   - Consider database fallback for critical systems
   - Monitor blacklist performance

### Origin Validation

1. **Purpose**
   - Prevent token reuse across domains
   - Protect against token theft
   - Enforce domain-specific tokens

2. **Implementation**
   - Extract origin from request headers
   - Compare with token origin
   - Allow localhost in development
   - Strict validation in production

### Token Rotation

1. **Benefits**
   - Prevents token reuse if compromised
   - Limits exposure window
   - Enhances security posture

2. **Implementation**
   - Generate new session_id on refresh
   - Blacklist old tokens immediately
   - Blacklist old session_id
   - Return new tokens to client

## Performance Optimization

### Token Validation Performance

1. **Session Token Priority**
   - Fastest validation (no database lookup)
   - Full user profile in token
   - Recommended for all API calls

2. **Blacklist Check Order**
   - Check token blacklist first (most common)
   - Check session blacklist second
   - Check user blacklist last (least common)

3. **Caching Strategy**
   - Redis cache for blacklist (sub-millisecond)
   - In-memory fallback for development
   - Monitor cache hit rates

### Database Optimization

1. **Minimize Database Lookups**
   - Use session_token (no lookup needed)
   - Cache user data in session_token
   - Only lookup on access_token if needed

2. **Query Optimization**
   - Index user_id for fast lookups
   - Use connection pooling
   - Monitor query performance

## Troubleshooting

### Common Issues

1. **Token Expired**
   - **Symptom**: 401 Unauthorized
   - **Solution**: Refresh token using refresh_token endpoint
   - **Prevention**: Monitor token expiration client-side

2. **Token Blacklisted**
   - **Symptom**: 401 Unauthorized after logout
   - **Solution**: User must login again
   - **Prevention**: Don't reuse tokens after logout

3. **Origin Mismatch**
   - **Symptom**: 401 Unauthorized with origin error
   - **Solution**: Ensure token origin matches request origin
   - **Prevention**: Use same domain for token generation and usage

4. **Invalid Token Type**
   - **Symptom**: 401 Unauthorized with token type error
   - **Solution**: Use access_token or session_token, not refresh_token
   - **Prevention**: Store tokens correctly and use appropriate token type

### Debugging Tips

1. **Token Inspection**
   - Decode JWT at jwt.io to inspect payload
   - Check expiration (exp claim)
   - Verify token type (type claim)
   - Check session_id presence

2. **Blacklist Verification**
   - Check Redis for blacklist entries
   - Verify TTL on blacklist keys
   - Check session blacklist
   - Check user blacklist

3. **Logging**
   - Enable debug logging for token validation
   - Log token extraction process
   - Log blacklist check results
   - Monitor authentication errors

## Client-Server Communication

### Token Storage Best Practices

```javascript
// Recommended: Store tokens securely
class TokenManager {
  constructor() {
    this.accessToken = null;
    this.sessionToken = null;
    this.refreshToken = null;
    this.sessionId = null;
  }
  
  // Store tokens after login
  storeTokens(tokens) {
    // Session token: localStorage (preferred for API calls)
    localStorage.setItem('session_token', tokens.session_token);
    
    // Access token: localStorage (backup)
    localStorage.setItem('access_token', tokens.access_token);
    
    // Refresh token: httpOnly cookie (most secure) - set by server
    // Or localStorage if cookies not available
    localStorage.setItem('refresh_token', tokens.refresh_token);
    
    // Session ID: localStorage (for logout)
    localStorage.setItem('session_id', tokens.session_id);
    
    this.accessToken = tokens.access_token;
    this.sessionToken = tokens.session_token;
    this.refreshToken = tokens.refresh_token;
    this.sessionId = tokens.session_id;
  }
  
  // Get token for API calls (prefer session_token)
  getAuthToken() {
    return this.sessionToken || 
           localStorage.getItem('session_token') ||
           this.accessToken ||
           localStorage.getItem('access_token');
  }
  
  // Clear all tokens
  clearTokens() {
    localStorage.removeItem('session_token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('session_id');
    
    this.accessToken = null;
    this.sessionToken = null;
    this.refreshToken = null;
    this.sessionId = null;
  }
}
```

### Token Refresh Interceptor

```javascript
// Automatic token refresh on 401 errors
async function apiRequestWithRefresh(url, options = {}) {
  const tokenManager = new TokenManager();
  const token = tokenManager.getAuthToken();
  
  // Add token to request
  const headers = {
    'Content-Type': 'application/json',
    'X-Session-Token': token,
    ...options.headers
  };
  
  let response = await fetch(url, {
    ...options,
    headers
  });
  
  // If 401, try to refresh token
  if (response.status === 401) {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!refreshToken) {
        // No refresh token, redirect to login
        window.location.href = '/login';
        return null;
      }
      
      // Attempt token refresh
      const refreshResponse = await fetch('/api/v1/auth/refresh-token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh_token: refreshToken })
      });
      
      const refreshData = await refreshResponse.json();
      
      if (refreshData.success) {
        // Store new tokens
        tokenManager.storeTokens(refreshData.data);
        
        // Retry original request with new token
        headers['X-Session-Token'] = refreshData.data.session_token;
        response = await fetch(url, {
          ...options,
          headers
        });
      } else {
        // Refresh failed, redirect to login
        tokenManager.clearTokens();
        window.location.href = '/login';
        return null;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      tokenManager.clearTokens();
      window.location.href = '/login';
      return null;
    }
  }
  
  return response.json();
}
```

### Logout Implementation

```javascript
// Complete logout implementation
async function logout(logoutAllDevices = false) {
  try {
    const tokenManager = new TokenManager();
    const token = tokenManager.getAuthToken();
    
    if (!token) {
      // Already logged out
      tokenManager.clearTokens();
      window.location.href = '/login';
      return;
    }
    
    // Send logout request
    const response = await fetch('/api/v1/auth/logout', {
      method: 'POST',
      headers: {
        'X-Session-Token': token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        logout_all_devices: logoutAllDevices
      })
    });
    
    // Clear tokens regardless of response
    tokenManager.clearTokens();
    
    // Redirect to login
    window.location.href = '/login';
  } catch (error) {
    console.error('Logout error:', error);
    // Clear tokens even if request fails
    const tokenManager = new TokenManager();
    tokenManager.clearTokens();
    window.location.href = '/login';
  }
}
```

## Best Practices

1. **Use Session Token** for API calls (fastest validation)
2. **Store Refresh Token** in httpOnly cookie (most secure)
3. **Rotate Tokens** on refresh (automatic)
4. **Blacklist on Logout** (server-side invalidation)
5. **Monitor Token Expiration** (client-side refresh logic)
6. **Handle 401 Errors** - Automatically refresh tokens
7. **Secure Storage** - Use httpOnly cookies for refresh tokens
8. **Token Priority** - Prefer session_token over access_token
9. **Error Handling** - Gracefully handle token expiration
10. **Logout All Devices** - Option to invalidate all sessions

## Instagram Pattern Compliance

✅ **Multi-token system** - access, refresh, session tokens  
✅ **Stateless authentication** - no database session storage  
✅ **Session ID** - unique identifier in all tokens  
✅ **Token blacklisting** - cache-based invalidation  
✅ **Token rotation** - new session on refresh  
✅ **Origin validation** - domain-specific tokens  
✅ **Fast validation** - session token with full profile  
✅ **Secure logout** - server-side token invalidation  

This architecture matches Instagram's authentication pattern for optimal security and performance.

