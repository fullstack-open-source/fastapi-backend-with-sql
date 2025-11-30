# Authentication Router

> **Complete Documentation for User Authentication Endpoints**

This router handles all user authentication operations including login, registration, password management, OTP verification, and user availability checks.

## 📋 Table of Contents

- [Overview](#overview)
  - [Token System](#token-system)
- [Endpoints](#endpoints)
  - [Login with Password](#login-with-password)
  - [Login with OTP](#login-with-otp)
  - [Send OTP](#send-otp)
  - [Verify OTP](#verify-otp)
  - [Signup/Register](#signupregister)
  - [Set Password](#set-password)
  - [Change Password](#change-password)
  - [Forget Password](#forget-password)
  - [Refresh Token](#refresh-token)
  - [Logout](#logout)
  - [Check User Availability](#check-user-availability)
  - [Verify Email and Phone](#verify-email-and-phone)
  - [Change Email/Phone Workflow](#change-emailphone-workflow-recommended)
- [Token Management](#token-management)
  - [Frontend Token Usage](#frontend-token-usage)
  - [Token Expiration Handling](#token-expiration-handling)
  - [Security Best Practices](#security-best-practices)
- [Workflows](#workflows)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Environment Variables](#environment-variables)
- [Architecture](#architecture)

## Overview

The Authentication router provides comprehensive user authentication functionality including:
- **Password-based Authentication**: Traditional email/phone + password login
- **OTP-based Authentication**: One-time password via email, SMS, or WhatsApp
- **User Registration**: Account creation with OTP verification
- **Password Management**: Set, change, and reset passwords
- **User Verification**: Email and phone number verification
- **Multi-Token System**: Access, refresh, and session tokens for secure authentication
- **Session Management**: Stateless session management with token blacklisting

**Base Path:** `/{MODE}/auth` or `/{MODE}/auth/logout`

**Authentication:** Most endpoints do not require authentication (except password change, logout, and token-info)

### Token System

The authentication system uses a multi-token approach for optimal security and performance:

1. **Session Token** (Recommended for Frontend - Fastest & Most Secure)
   - **Lifespan**: 7 days (configurable via `SESSION_TOKEN_EXPIRY_MINUTES`)
   - **Purpose**: **Preferred token for API authentication** - contains full user profile
   - **Payload**: Complete user profile and permissions (no database lookup needed)
   - **Storage**: Store securely (httpOnly cookie or secure storage)
   - **Usage**: Include in `X-Session-Token` header or `Authorization: Bearer` header
   - **Benefits**: 
     - Fastest validation (no database queries)
     - Contains full user data
     - Longer lifespan (7 days vs 1 hour)
     - Optimized for client-side validation

2. **Access Token** (Alternative for API Calls)
   - **Lifespan**: 1 hour (60 minutes, configurable via `ACCESS_TOKEN_EXPIRY_MINUTES`)
   - **Purpose**: Lightweight token for API requests
   - **Payload**: Minimal - contains user_id, username, email, is_active, is_verified, jti (JWT ID)
   - **Storage**: Store in memory or secure storage
   - **Usage**: Include in `Authorization: Bearer <access_token>` header
   - **Note**: Requires database lookup if full user data needed
   - **Features**: Includes JTI (JWT ID) for efficient blacklisting

3. **Refresh Token**
   - **Lifespan**: 30 days (configurable via `REFRESH_TOKEN_EXPIRY_MINUTES`)
   - **Purpose**: Use to obtain new tokens when they expire
   - **Payload**: Minimal - contains only user_id and session_id
   - **Storage**: Store securely (httpOnly cookie or secure storage)
   - **Usage**: Send to `/auth/refresh-token` endpoint when tokens expire
   - **Note**: Cannot be used for API authentication

4. **Session ID**
   - **Purpose**: Unique identifier for the session, used for logout operations
   - **Storage**: Store with tokens for logout functionality
   - **Usage**: Include in logout requests to revoke specific sessions

**Frontend Token Usage (Recommended - Session Token):**
```javascript
// Store tokens after login
const { access_token, refresh_token, session_token, session_id } = loginResponse.data;

// RECOMMENDED: Use session_token for API calls (fastest and most secure)
// Option 1: X-Session-Token header (preferred method)
fetch('/api/protected-endpoint', {
  headers: {
    'X-Session-Token': session_token
  }
});

// Option 2: Authorization Bearer header (session_token works here too!)
fetch('/api/protected-endpoint', {
  headers: {
    'Authorization': `Bearer ${session_token}`  // session_token in Bearer header
  }
});

// Alternative: Use access_token with Bearer header (still supported)
fetch('/api/protected-endpoint', {
  headers: {
    'Authorization': `Bearer ${access_token}`  // access_token in Bearer header
  }
});

// When tokens expire, use refresh_token
fetch('/api/auth/refresh-token', {
  method: 'POST',
  body: JSON.stringify({ refresh_token })
});
```

**Token Validation Priority:**
The server accepts tokens in this order (first match wins):
1. `X-Session-Token` header (preferred - fastest validation)
2. `Authorization: Bearer <token>` header (accepts both session_token and access_token)
3. OAuth2 scheme (for Swagger UI)
4. `access_token` query parameter (backward compatibility)

**Important Notes:**
- ✅ **Bearer header accepts both**: You can use `session_token` OR `access_token` in `Authorization: Bearer` header
- ✅ **X-Session-Token is preferred**: Fastest validation path when using `X-Session-Token` header
- ✅ **Flexible usage**: Use whichever method fits your frontend architecture

**Why Session Token is Recommended:**
- ✅ **Fastest**: No database lookup needed (full user data in token)
- ✅ **Secure**: Same security as access token with blacklist checking
- ✅ **Longer lifespan**: 7 days vs 1 hour (fewer refresh operations)
- ✅ **Complete data**: Full user profile embedded in token
- ✅ **Optimized**: Server-side validation optimized for session tokens
- ✅ **Flexible**: Works with both `X-Session-Token` header and `Authorization: Bearer` header

## Endpoints

### Login with Password

**Endpoint:** `POST /{MODE}/auth/login-with-password`

**Description:** Authenticate user with email/phone and password. Returns all tokens (access, refresh, session) upon successful authentication.

**Note:** This is the single unified login endpoint for password-based authentication.

**Authentication:** Not required

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "your-password"
}
```

**Response:**
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
  },
  "meta": {
    "type": "dict"
  },
  "timestamp": "2025-01-28T15:51:55.980680Z"
}
```

**Token Details:**
- `access_token`: Use this for API authentication (60 minutes expiry, configurable)
- `refresh_token`: Use to refresh all tokens (30 days expiry, configurable)
- `session_token`: Contains full user profile (7 days expiry, configurable) - **RECOMMENDED**
- `session_id`: Unique session identifier for logout and session management

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User submits login form
  ├─► User enters email/phone and password
  └─► Client validates form (email format, password length)

Step 2: Client sends login request
  POST /{MODE}/auth/login-with-password
  Content-Type: application/x-www-form-urlencoded
  Body: username=user@example.com&password=secret123
  
  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Step 3: Server validates request
    ├─► Check username exists → ❌ 400 if missing
    └─► Check password exists → ❌ 400 if missing
  
  Step 4: Server authenticates user
    ├─► Query database: Get user by email/phone
    │   └─► ❌ 401 if user not found
    ├─► Verify password (bcrypt/PBKDF2)
    │   └─► ❌ 401 if password incorrect
    ├─► Check user status
    │   ├─► is_active = true → ❌ 401 if false
    │   └─► is_verified = true → ❌ 401 if false
    └─► Update last_sign_in_at timestamp
  
  Step 5: Server clears user blacklist (if exists)
    ├─► Clear user-level session blacklist
    └─► Clear user refresh token blacklist
    (Allows re-login after previous logout)
  
  Step 6: Server generates tokens
    ├─► Generate session_id (UUID)
    ├─► Generate access_token (60 min, includes JTI)
    ├─► Generate session_token (7 days, includes full user profile)
    └─► Generate refresh_token (30 days, includes session_id)
  
  Step 7: Server returns response
    HTTP 200 OK
    {
      "success": true,
      "data": {
        "access_token": "...",
        "refresh_token": "...",
        "session_token": "...",
        "session_id": "...",
        "token_type": "bearer"
      }
    }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 8: Client receives response
  ├─► Check response.success === true
  └─► Extract tokens from response.data

Step 9: Client stores tokens securely
  ├─► Store session_token (RECOMMENDED for API calls)
  │   └─► localStorage.setItem('session_token', token)
  │   OR httpOnly cookie (more secure)
  ├─► Store refresh_token (for token renewal)
  │   └─► localStorage.setItem('refresh_token', token)
  │   OR httpOnly cookie (preferred)
  ├─► Store session_id (for logout)
  │   └─► localStorage.setItem('session_id', id)
  └─► Store access_token (optional, if not using session_token)
      └─► localStorage.setItem('access_token', token)

Step 10: Client updates UI
  ├─► Redirect to dashboard/home
  ├─► Update user state/context
  └─► Show success message

Step 11: Client uses tokens for API calls
  ├─► Add to request headers:
  │   ├─► X-Session-Token: <session_token> (RECOMMENDED)
  │   OR
  │   └─► Authorization: Bearer <session_token>
  └─► All subsequent API requests include token
```

**Error Handling:**

```
Client receives error response:
  ├─► 400 Bad Request
  │   └─► Show: "Username and password are required"
  │
  ├─► 401 Unauthorized
  │   ├─► "Invalid username or password" → Show error, clear password field
  │   ├─► "User account is not active" → Show: "Account is disabled"
  │   └─► "User account is not verified" → Show: "Please verify your email/phone"
  │
  └─► 500 Internal Server Error
      └─► Show: "Login failed. Please try again."
```

**Use Cases:**
- User login
- Session establishment
- API access token generation

---

### Send OTP

**Endpoint:** `POST /{MODE}/auth/send-one-time-password`

**Description:** Send one-time password via email, SMS, or WhatsApp. OTP is valid for 10 minutes.

**Authentication:** Not required

**Request Body:**
```json
{
  "user_id": "user@example.com",
  "channel": "email"
}
```

**Channel Options:**
- `email`: Send OTP via email
- `sms`: Send OTP via SMS
- `whatsapp`: Send OTP via WhatsApp

**Response:**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "data": {
    "message": "OTP sent successfully"
  }
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User requests OTP
  ├─► User enters email/phone on login/signup form
  └─► User clicks "Send OTP" button

Step 2: Client sends OTP request
  POST /{MODE}/auth/send-one-time-password
  Content-Type: application/json
  {
    "user_id": "user@example.com",
    "channel": "email"
  }
  
  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Step 3: Server validates request
    ├─► Check user_id exists → ❌ 400 if missing
    ├─► Check channel exists → ❌ 400 if missing
    └─► Validate channel value → ❌ 400 if not email/sms/whatsapp
  
  Step 4: Server generates OTP
    ├─► Generate 6-digit random code (e.g., "123456")
    └─► Store in cache (Redis or in-memory)
        ├─► Key: "otp:{channel}:{user_id}"
        ├─► Value: OTP code
        └─► TTL: 600 seconds (10 minutes)
  
  Step 5: Server sends OTP via channel
    ├─► channel = "email"
    │   └─► Send email with OTP code
    │       └─► Subject: "Your OTP Code"
    │
    ├─► channel = "sms"
    │   └─► Send SMS via Twilio
    │       └─► Message: "Your OTP is: 123456"
    │
    └─► channel = "whatsapp"
        └─► Send WhatsApp message via Twilio
            └─► Message: "Your OTP is: 123456"
  
  Step 6: Server returns success response
    HTTP 200 OK
    {
      "success": true,
      "message": "OTP sent successfully",
      "data": {
        "message": "OTP sent successfully"
      }
    }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 7: Client receives response
  ├─► Check response.success === true
  └─► Show success message to user

Step 8: Client shows OTP input form
  ├─► Display: "OTP sent to your email/phone"
  ├─► Show OTP input field
  ├─► Start countdown timer (10 minutes)
  └─► Enable "Resend OTP" button (after 60 seconds)

Step 9: User enters OTP
  └─► User types 6-digit code from email/SMS

Step 10: Client validates OTP format
  ├─► Check: OTP is 6 digits
  └─► ❌ Show error if invalid format

Step 11: Client sends OTP for verification
  └─► Proceed to verify-otp or login-with-otp endpoint
```

**Error Handling:**

```
Client receives error response:
  ├─► 400 Bad Request
  │   ├─► "user_id is required" → Show: "Please enter email/phone"
  │   └─► "channel is required" → Show: "Please select channel"
  │
  ├─► 500 Internal Server Error
  │   └─► "Failed to send OTP" → Show: "Unable to send OTP. Please try again."
  │
  └─► Network Error
      └─► Show: "Connection error. Check your internet."
```

**Use Cases:**
- Password reset
- Email/phone verification
- Two-factor authentication
- Account recovery

---

### Verify OTP

**Endpoint:** `POST /{MODE}/auth/verify-one-time-password`

**Description:** Verify one-time password without logging in. Used for verification purposes.

**Authentication:** Not required

**Request Body:**
```json
{
  "user_id": "user@example.com",
  "channel": "email",
  "otp": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Verify Successfully",
  "data": {
    "user_id": "user@example.com"
  }
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User enters OTP
  ├─► User receives OTP via email/SMS/WhatsApp
  └─► User types OTP into input field

Step 2: Client validates OTP format
  ├─► Check: OTP is 6 digits
  └─► ❌ Show error if invalid format

Step 3: Client sends verification request
  POST /{MODE}/auth/verify-one-time-password
  Content-Type: application/json
  {
    "user_id": "user@example.com",
    "channel": "email",
    "otp": "123456"
  }
  
  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Step 4: Server validates request
    ├─► Check user_id exists → ❌ 400 if missing
    ├─► Check channel exists → ❌ 400 if missing
    └─► Check otp exists → ❌ 400 if missing
  
  Step 5: Server retrieves stored OTP
    ├─► Build cache key: "otp:{channel}:{user_id}"
    ├─► Get OTP from cache (Redis or in-memory)
    └─► ❌ 401 if OTP not found (expired or never sent)
  
  Step 6: Server compares OTPs
    ├─► Compare stored OTP with provided OTP
    └─► ❌ 401 if OTPs don't match
  
  Step 7: Server checks expiration
    ├─► Check if OTP is still valid (within 10 minutes)
    └─► ❌ 401 if expired
  
  Step 8: Server returns verification result
    ├─► OTP is NOT deleted (can be reused)
    └─► HTTP 200 OK
        {
          "success": true,
          "message": "Verify Successfully",
          "data": {
            "user_id": "user@example.com"
          }
        }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 9: Client receives response
  ├─► Check response.success === true
  └─► Proceed to next step (e.g., signup, password reset)

Step 10: Client updates UI
  ├─► Show success message: "OTP verified successfully"
  ├─► Enable next step button (e.g., "Create Account")
  └─► Hide OTP input field
```

**Error Handling:**

```
Client receives error response:
  ├─► 400 Bad Request
  │   └─► Show: "Please enter all required fields"
  │
  ├─► 401 Unauthorized
  │   ├─► "Invalid OTP" → Show: "Incorrect OTP. Please try again."
  │   ├─► "OTP expired" → Show: "OTP has expired. Please request a new one."
  │   └─► "OTP not found" → Show: "OTP not found. Please request a new OTP."
  │
  └─► 500 Internal Server Error
      └─► Show: "Verification failed. Please try again."
```

**Use Cases:**
- Email verification
- Phone verification
- Pre-login verification

---

### Login with OTP

**Endpoint:** `POST /{MODE}/auth/login-with-otp`

**Description:** Verify OTP and login user. Returns access token upon successful verification. OTP is deleted after successful login.

**Authentication:** Not required

**Request Body:**
```json
{
  "user_id": "user@example.com",
  "channel": "email",
  "otp": "123456"
}
```

**Response:**
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
    "token_type": "bearer",
    "user": {
      "user_id": "uuid",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  },
  "meta": {
    "type": "dict"
  },
  "timestamp": "2025-01-28T15:51:55.980680Z"
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User has received OTP
  ├─► User received OTP via email/SMS/WhatsApp (from send-otp)
  └─► User enters OTP in login form

Step 2: Client sends login request
  POST /{MODE}/auth/login-with-otp
  Content-Type: application/json
  {
    "user_id": "user@example.com",
    "channel": "email",
    "otp": "123456"
  }
  
  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Step 3: Server validates request
    ├─► Check user_id exists → ❌ 400 if missing
    ├─► Check channel exists → ❌ 400 if missing
    ├─► Check otp exists → ❌ 400 if missing
    └─► Validate email/phone format → ❌ 400 if invalid
  
  Step 4: Server gets user from database
    ├─► Query: getUserByEmailOrPhone(user_id)
    └─► ❌ 404 if user not found
  
  Step 5: Server checks user status
    ├─► Check is_active = true → ❌ 401 if false
    └─► Check is_verified = true → ❌ 401 if false
  
  Step 6: Server verifies OTP
    ├─► Get stored OTP from cache: "otp:{channel}:{user_id}"
    ├─► Compare stored OTP with provided OTP
    ├─► Check expiration (10 minutes)
    └─► ❌ 401 if invalid/expired
  
  Step 7: Server deletes OTP (consume)
    └─► Delete OTP from cache (one-time use)
  
  Step 8: Server updates last sign-in
    └─► Update last_sign_in_at = current timestamp
  
  Step 9: Server clears user blacklist
    ├─► Clear user-level session blacklist
    └─► Clear user refresh token blacklist
  
  Step 10: Server generates all tokens
    ├─► Generate session_id (UUID)
    ├─► Generate access_token (60 min)
    ├─► Generate session_token (7 days, with full profile)
    └─► Generate refresh_token (30 days)
  
  Step 11: Server returns tokens and user data
    HTTP 200 OK
    {
      "success": true,
      "data": {
        "access_token": "...",
        "refresh_token": "...",
        "session_token": "...",
        "session_id": "...",
        "token_type": "bearer",
        "user": { ... }
      }
    }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 12: Client stores tokens
  ├─► Store session_token (RECOMMENDED)
  ├─► Store refresh_token
  ├─► Store session_id
  └─► Store user data in app state

Step 13: Client updates UI
  ├─► Redirect to dashboard
  ├─► Show welcome message
  └─► Update user context/state
```

**Error Handling:**

```
Client receives error response:
  ├─► 400 Bad Request
  │   └─► Show: "Please enter all required fields"
  │
  ├─► 401 Unauthorized
  │   ├─► "Invalid OTP" → Show: "Incorrect OTP"
  │   ├─► "OTP expired" → Show: "OTP expired. Request new one."
  │   ├─► "User account is not active" → Show: "Account disabled"
  │   └─► "User account is not verified" → Show: "Please verify account"
  │
  ├─► 404 Not Found
  │   └─► "User not found" → Show: "User does not exist"
  │
  └─► 500 Internal Server Error
      └─► Show: "Login failed. Please try again."
```

**Use Cases:**
- Passwordless login
- Quick authentication
- Mobile app login

---

### Signup/Register

**Endpoint:** `POST /{MODE}/auth/verify`

**Description:** Verify OTP and create new user account. Supports master OTP for admin account creation.

**Authentication:** Not required

**Request Body:**
```json
{
  "user_id": "user@example.com",
  "channel": "email",
  "otp": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "Signup successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "session_id": "f533589d-48d3-4b67-9430-c0b4793ac13e",
    "token_type": "bearer",
    "user": { ... }
  },
  "meta": {
    "type": "dict"
  },
  "timestamp": "2025-01-28T15:51:55.980680Z"
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User completes signup form
  ├─► User enters email/phone
  ├─► User requests OTP (via send-otp endpoint)
  └─► User receives and enters OTP

Step 2: Client sends signup request
  POST /{MODE}/auth/verify
  Content-Type: application/json
  {
    "user_id": "newuser@example.com",
    "channel": "email",
    "otp": "123456"
  }
  
  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Step 3: Server validates request
    ├─► Check user_id exists → ❌ 400 if missing
    ├─► Check channel exists → ❌ 400 if missing
    └─► Check otp exists → ❌ 400 if missing
  
  Step 4: Server checks master OTP (optional)
    ├─► Compare OTP with MASTER_OTP env variable
    └─► If matches → Skip OTP verification, assign admin group
  
  Step 5: Server verifies OTP (if not master OTP)
    ├─► Get stored OTP from cache
    ├─► Compare with provided OTP
    ├─► Check expiration
    └─► ❌ 401 if invalid/expired
    (Note: OTP not deleted yet - will be deleted after signup)
  
  Step 6: Server validates email/phone format
    ├─► If channel = "email" → validateEmail()
    └─► If channel = "sms/whatsapp" → validatePhone()
    └─► ❌ 400 if invalid format
  
  Step 7: Server checks if user already exists
    ├─► Query: getUserByEmailOrPhone(user_id)
    └─► ❌ 409 if user already exists
  
  Step 8: Server creates new user account
    ├─► Generate user_id (UUID)
    ├─► Set default values:
    │   ├─► is_active: true
    │   ├─► is_verified: true
    │   ├─► profile_accessibility: "public"
    │   ├─► theme: "light"
    │   ├─► user_type: "customer"
    │   ├─► language: "en"
    │   └─► status: "ACTIVE"
    ├─► Set auth_type based on channel
    ├─► Set verification status:
    │   ├─► is_email_verified: true (if channel=email)
    │   └─► is_phone_verified: true (if channel=sms/whatsapp)
    └─► Insert user into database
  
  Step 9: Server assigns groups (if master OTP)
    └─► Assign admin group to user
  
  Step 10: Server clears user blacklist
    ├─► Clear user-level session blacklist
    └─► Clear user refresh token blacklist
  
  Step 11: Server generates all tokens
    ├─► Generate session_id
    ├─► Generate access_token (60 min)
    ├─► Generate session_token (7 days)
    └─► Generate refresh_token (30 days)
  
  Step 12: Server deletes OTP (if not master OTP)
    └─► Delete OTP from cache (consume=true)
  
  Step 13: Server returns tokens and user data
    HTTP 200 OK
    {
      "success": true,
      "data": {
        "access_token": "...",
        "refresh_token": "...",
        "session_token": "...",
        "session_id": "...",
        "token_type": "bearer",
        "user": { ... }
      }
    }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 14: Client stores tokens
  ├─► Store session_token (RECOMMENDED)
  ├─► Store refresh_token
  ├─► Store session_id
  └─► Store user data

Step 15: Client updates UI
  ├─► Redirect to onboarding/dashboard
  ├─► Show welcome message
  └─► Update user context/state
```

**Error Handling:**

```
Client receives error response:
  ├─► 400 Bad Request
  │   ├─► "Invalid email format" → Show: "Please enter valid email"
  │   └─► "Invalid phone format" → Show: "Please enter valid phone"
  │
  ├─► 401 Unauthorized
  │   └─► "Invalid OTP" → Show: "Incorrect OTP. Please try again."
  │
  ├─► 409 Conflict
  │   └─► "User already exists" → Show: "Account already exists. Please login."
  │
  └─► 500 Internal Server Error
      └─► Show: "Signup failed. Please try again."
```

**Special Features:**
- **Master OTP**: If `MASTER_OTP` environment variable matches, user is assigned admin group
- **Auto-verification**: Email/phone is automatically verified during signup
- **Default Settings**: New users get sensible defaults

**Use Cases:**
- New user registration
- Account creation
- Onboarding flow

---

### Set Password

**Endpoint:** `POST /{MODE}/auth/set-password`

**Description:** Set password for authenticated user (for users who signed up with OTP).

**Authentication:** Required
**Permission:** `edit_profile`

**Request Body:**
```json
{
  "password": "new-password",
  "confirm_password": "new-password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password set successfully",
  "data": {
    "message": "Password set successfully"
  }
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User wants to set password
  ├─► User is logged in (has valid token)
  └─► User navigates to "Set Password" page

Step 2: User enters password
  ├─► User enters new password
  ├─► User confirms password
  └─► Client validates: passwords match

Step 3: Client sends set password request
  POST /{MODE}/auth/set-password
  Authorization: Bearer <session_token>
  Content-Type: application/json
  {
    "password": "newSecurePassword123",
    "confirm_password": "newSecurePassword123"
  }
  
  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Step 4: Server validates authentication
    ├─► Extract token from Authorization header
    ├─► Validate token (decode, check expiration, blacklist)
    └─► ❌ 401 if invalid/expired
  
  Step 5: Server validates request
    ├─► Check password exists → ❌ 400 if missing
    ├─► Check confirm_password exists → ❌ 400 if missing
    └─► Check password === confirm_password → ❌ 400 if mismatch
  
  Step 6: Server hashes password
    ├─► Use bcrypt with 10 salt rounds
    └─► Generate secure hash
  
  Step 7: Server updates user password
    ├─► Get user_id from token
    ├─► Update password in database
    └─► Update last_updated timestamp
  
  Step 8: Server returns success response
    HTTP 200 OK
    {
      "success": true,
      "message": "Password set successfully",
      "data": {
        "message": "Password set successfully"
      }
    }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 9: Client receives response
  ├─► Check response.success === true
  └─► Show success message

Step 10: Client updates UI
  ├─► Show: "Password set successfully"
  ├─► Redirect to profile/settings
  └─► Clear password fields
```

**Error Handling:**

```
Client receives error response:
  ├─► 400 Bad Request
  │   ├─► "Password is required" → Show: "Please enter password"
  │   └─► "Passwords do not match" → Show: "Passwords don't match"
  │
  ├─► 401 Unauthorized
  │   └─► "Invalid token" → Redirect to login
  │
  └─► 500 Internal Server Error
      └─► Show: "Failed to set password. Please try again."
```

**Use Cases:**
- Initial password setup
- Passwordless signup completion

---

### Change Password

**Endpoint:** `POST /{MODE}/auth/change-password`

**Description:** Change user's existing password. Requires old password verification.

**Authentication:** Required
**Permission:** `edit_profile`

**Request Body:**
```json
{
  "user_id": "user@example.com",
  "channel": "email",
  "old_password": "current-password",
  "password": "new-password",
  "confirm_password": "new-password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password updated successfully",
  "data": {
    "message": "Password updated successfully"
  }
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User wants to change password
  ├─► User is logged in (has valid token)
  └─► User navigates to "Change Password" page

Step 2: User enters password information
  ├─► User enters current password
  ├─► User enters new password
  └─► User confirms new password

Step 3: Client validates passwords
  ├─► Check: new password !== old password
  ├─► Check: new password === confirm password
  └─► ❌ Show error if validation fails

Step 4: Client sends change password request
  POST /{MODE}/auth/change-password
  Authorization: Bearer <session_token>
  Content-Type: application/json
  {
    "user_id": "user@example.com",
    "channel": "email",
    "old_password": "currentPassword123",
    "password": "newSecurePassword123",
    "confirm_password": "newSecurePassword123"
  }
  
  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Step 5: Server validates authentication
    ├─► Extract token from Authorization header
    ├─► Validate token (decode, check expiration, blacklist)
    └─► ❌ 401 if invalid/expired
  
  Step 6: Server validates request
    ├─► Check user_id exists → ❌ 400 if missing
    ├─► Check old_password exists → ❌ 400 if missing
    ├─► Check password exists → ❌ 400 if missing
    └─► Check confirm_password exists → ❌ 400 if missing
  
  Step 7: Server validates passwords match
    └─► Check password === confirm_password
    └─► ❌ 400 if mismatch
  
  Step 8: Server verifies old password
    ├─► Get user from database (by user_id from token)
    ├─► Authenticate user with old_password
    │   ├─► Get user by email/phone
    │   ├─► Verify password (bcrypt/PBKDF2)
    │   └─► Check user status (is_active, is_verified)
    └─► ❌ 401 if old password incorrect
  
  Step 9: Server hashes new password
    ├─► Use bcrypt with 10 salt rounds
    └─► Generate secure hash
  
  Step 10: Server updates user password
    ├─► Get user_id from authenticated token
    ├─► Update password in database
    └─► Update last_updated timestamp
  
  Step 11: Server returns success response
    HTTP 200 OK
    {
      "success": true,
      "message": "Password updated successfully",
      "data": {
        "message": "Password updated successfully"
      }
    }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 12: Client receives response
  ├─► Check response.success === true
  └─► Show success message

Step 13: Client updates UI
  ├─► Show: "Password changed successfully"
  ├─► Clear password fields
  └─► Optionally: Force re-login for security
```

**Error Handling:**

```
Client receives error response:
  ├─► 400 Bad Request
  │   ├─► "Passwords do not match" → Show: "New passwords don't match"
  │   └─► "Missing required fields" → Show: "Please fill all fields"
  │
  ├─► 401 Unauthorized
  │   ├─► "Invalid token" → Redirect to login
  │   └─► "Invalid old password" → Show: "Current password is incorrect"
  │
  └─► 500 Internal Server Error
      └─► Show: "Failed to change password. Please try again."
```

**Use Cases:**
- Password change
- Security updates
- Account security

---

### Forget Password

**Endpoint:** `POST /{MODE}/auth/forget-password`

**Description:** Reset password after verifying OTP. Used for password recovery.

**Authentication:** Not required

**Request Body:**
```json
{
  "user_id": "user@example.com",
  "otp": "123456",
  "password": "new-password",
  "confirm_password": "new-password"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Password updated successfully",
  "data": {
    "message": "Password updated successfully"
  }
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User forgot password
  ├─► User clicks "Forgot Password" link
  └─► User enters email/phone

Step 2: Client requests OTP
  POST /{MODE}/auth/send-one-time-password
  {
    "user_id": "user@example.com",
    "channel": "email"
  }
  └─► User receives OTP via email/SMS

Step 3: User enters OTP and new password
  ├─► User enters OTP from email/SMS
  ├─► User enters new password
  └─► User confirms new password

Step 4: Client validates passwords match
  └─► ❌ Show error if passwords don't match

Step 5: Client sends password reset request
  POST /{MODE}/auth/forget-password
  Content-Type: application/json
  {
    "user_id": "user@example.com",
    "otp": "123456",
    "password": "newSecurePassword123",
    "confirm_password": "newSecurePassword123"
  }
  
  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Step 6: Server validates request
    ├─► Check user_id exists → ❌ 400 if missing
    ├─► Check otp exists → ❌ 400 if missing
    ├─► Check password exists → ❌ 400 if missing
    └─► Check confirm_password exists → ❌ 400 if missing
  
  Step 7: Server verifies OTP
    ├─► Get stored OTP from cache
    ├─► Compare with provided OTP
    ├─► Check expiration (10 minutes)
    └─► ❌ 401 if invalid/expired
  
  Step 8: Server validates email/phone format
    ├─► Validate email format (if contains @)
    └─► Validate phone format (if doesn't contain @)
    └─► ❌ 400 if invalid format
  
  Step 9: Server gets user from database
    ├─► Query: getUserByEmailOrPhone(user_id)
    └─► ❌ 404 if user not found
  
  Step 10: Server validates passwords match
    └─► Check password === confirm_password
    └─► ❌ 400 if mismatch
  
  Step 11: Server hashes new password
    ├─► Use bcrypt with 10 salt rounds
    └─► Generate secure hash
  
  Step 12: Server updates user password
    ├─► Update password in database
    └─► Update last_updated timestamp
  
  Step 13: Server deletes OTP (consume)
    └─► Delete OTP from cache (one-time use)
  
  Step 14: Server returns success response
    HTTP 200 OK
    {
      "success": true,
      "message": "Password updated successfully",
      "data": {
        "message": "Password updated successfully"
      }
    }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 15: Client receives response
  ├─► Check response.success === true
  └─► Show success message

Step 16: Client updates UI
  ├─► Show: "Password reset successfully"
  ├─► Redirect to login page
  └─► Clear form fields
```

**Error Handling:**

```
Client receives error response:
  ├─► 400 Bad Request
  │   ├─► "Passwords do not match" → Show: "Passwords don't match"
  │   └─► "Invalid email/phone format" → Show: "Invalid format"
  │
  ├─► 401 Unauthorized
  │   └─► "Invalid OTP" → Show: "Incorrect or expired OTP"
  │
  ├─► 404 Not Found
  │   └─► "User not found" → Show: "User does not exist"
  │
  └─► 500 Internal Server Error
      └─► Show: "Password reset failed. Please try again."
```

**Use Cases:**
- Password recovery
- Account reset
- Security recovery

---

### Refresh Token

**Endpoint:** `POST /{MODE}/auth/refresh-token`

**Description:** Refresh access token using refresh token. Returns new tokens with a new session.

**Authentication:** Not required (uses refresh token)

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "session_id": "f533589d-48d3-4b67-9430-c0b4793ac13e",
    "token_type": "bearer"
  },
  "meta": {
    "type": "dict"
  },
  "timestamp": "2025-01-28T15:51:55.980680Z"
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Token expires or about to expire
  ├─► Client makes API request with expired token
  └─► Server returns 401 Unauthorized

Step 2: Client detects token expiration
  ├─► Intercept 401 response
  └─► Check if refresh_token exists

Step 3: Client sends refresh token request
  POST /{MODE}/auth/refresh-token
  Content-Type: application/json
  {
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  
  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Step 4: Server validates refresh token
    ├─► Check refresh_token exists → ❌ 400 if missing
    └─► Decode JWT token
        ├─► Try with audience="authenticated"
        └─► Fallback: decode without audience
        └─► ❌ 401 if invalid/expired
  
  Step 5: Server validates token type
    ├─► Check token.type === "refresh"
    └─► ❌ 401 if not refresh token
  
  Step 6: Server checks blacklist status
    ├─► Check if token is blacklisted → ❌ 401 if blacklisted
    ├─► Check if user refresh tokens revoked → ❌ 401 if revoked
    └─► Check if session is blacklisted → ❌ 401 if blacklisted
  
  Step 7: Server extracts user info
    ├─► Get user_id from token.sub
    └─► Get session_id from token (if exists)
  
  Step 8: Server gets user from database
    ├─► Query: getUserById(user_id)
    └─► ❌ 404 if user not found
  
  Step 9: Server blacklists old tokens
    ├─► Blacklist old refresh token
    └─► Blacklist old session (if session_id exists)
  
  Step 10: Server generates new tokens
    ├─► Generate new session_id (UUID)
    ├─► Generate new access_token (60 min, new JTI)
    ├─► Generate new session_token (7 days, full profile)
    └─► Generate new refresh_token (30 days, rotated)
  
  Step 11: Server returns new tokens
    HTTP 200 OK
    {
      "success": true,
      "data": {
        "access_token": "...",
        "refresh_token": "...",
        "session_token": "...",
        "session_id": "...",
        "token_type": "bearer"
      }
    }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 12: Client receives new tokens
  ├─► Check response.success === true
  └─► Extract new tokens from response.data

Step 13: Client updates stored tokens
  ├─► Update session_token (RECOMMENDED)
  ├─► Update refresh_token (rotated)
  ├─► Update session_id (new)
  └─► Update access_token (optional)

Step 14: Client retries original request
  ├─► Use new session_token in request header
  └─► Original API call succeeds
```

**Error Handling:**

```
Client receives error response:
  ├─► 400 Bad Request
  │   └─► "refresh_token is required" → Show: "Please login again"
  │
  ├─► 401 Unauthorized
  │   ├─► "Refresh token expired" → Redirect to login
  │   ├─► "Refresh token revoked" → Redirect to login
  │   └─► "Invalid refresh token" → Redirect to login
  │
  ├─► 404 Not Found
  │   └─► "User not found" → Redirect to login
  │
  └─► 500 Internal Server Error
      └─► Show: "Token refresh failed. Please login again."
```

**Client-Side Implementation Example:**

```javascript
// Axios interceptor for automatic token refresh
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If 401 and not already retrying
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Get refresh token
        const refreshToken = localStorage.getItem('refresh_token');
        
        // Request new tokens
        const response = await axios.post('/api/auth/refresh-token', {
          refresh_token: refreshToken
        });
        
        // Update stored tokens
        localStorage.setItem('session_token', response.data.data.session_token);
        localStorage.setItem('refresh_token', response.data.data.refresh_token);
        localStorage.setItem('session_id', response.data.data.session_id);
        
        // Retry original request with new token
        originalRequest.headers['X-Session-Token'] = response.data.data.session_token;
        return axios(originalRequest);
        
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
```

**Token Rotation:**
- All tokens are rotated (new tokens generated)
- Old refresh token is blacklisted
- Old session is blacklisted (if session_id exists)
- New session_id is created for all new tokens
- Complete token rotation for security

**Use Cases:**
- Access token expiration
- Token rotation for security
- Session renewal

**Error Responses:**
- `400`: Refresh token not provided
- `401`: Invalid or expired refresh token
- `401`: Refresh token has been revoked (user-level blacklist)
- `401`: Session has been revoked
- `401`: Invalid token type (not a refresh token)
- `404`: User not found
- `500`: JWT configuration error

---

### Logout

**Endpoint:** `POST /{MODE}/auth/logout`

**Description:** Logout user and revoke all tokens and sessions from all devices. Returns detailed revocation status.

**Authentication:** Required (permission: `view_profile`)

**Request Body:** None

**Headers:**
```
Authorization: Bearer <access_token>
```
or
```
X-Session-Token: <session_token>
```

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "Logged out successfully. All tokens and sessions have been revoked.",
  "data": {
    "message": "Logged out successfully",
    "access_token_revoked": true,
    "refresh_tokens_revoked": true,
    "sessions_revoked": true,
    "tokens_revoked": true
  },
  "meta": {
    "type": "dict"
  },
  "timestamp": "2025-01-28T15:51:55.980680Z"
}
```

**Response Fields:**
- `access_token_revoked`: Whether the current access token was blacklisted (by JTI)
- `refresh_tokens_revoked`: Whether all refresh tokens for the user were revoked
- `sessions_revoked`: Whether all sessions for the user were blacklisted (complete logout from all devices)
- `tokens_revoked`: Overall status - true if all operations succeeded

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User clicks logout
  ├─► User clicks "Logout" button
  └─► Client shows confirmation (optional)

Step 2: Client sends logout request
  POST /{MODE}/auth/logout
  Authorization: Bearer <session_token>
  OR
  X-Session-Token: <session_token>
  
  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Step 3: Server validates authentication
    ├─► Extract token from Authorization header or X-Session-Token
    ├─► Validate token (decode, check signature)
    └─► ❌ 401 if invalid (but continues with logout if expired)
  
  Step 4: Server decodes token (even if expired)
    ├─► Decode with verify_exp: false (allows expired tokens)
    ├─► Extract JTI (JWT ID) from token
    ├─► Extract user_id from token.sub
    └─► Extract session_id from token (if available)
  
  Step 5: Server blacklists access token
    ├─► Blacklist by JTI: "blacklist:access:jti:{jti}"
    └─► TTL: 45 days (3888000 seconds)
  
  Step 6: Server revokes all refresh tokens
    ├─► Set user-level blacklist: "blacklist:refresh:user:{user_id}"
    └─► TTL: 30 days (all refresh tokens for user invalidated)
  
  Step 7: Server blacklists all user sessions
    ├─► Set user-level blacklist: "blacklist:user:{user_id}"
    └─► TTL: 30 days (all sessions for user invalidated)
    └─► Complete logout from all devices
  
  Step 8: Server tracks revocation status
    ├─► access_token_revoked: true/false
    ├─► refresh_tokens_revoked: true/false
    ├─► sessions_revoked: true/false
    └─► tokens_revoked: overall status
  
  Step 9: Server returns logout status
    HTTP 200 OK
    {
      "success": true,
      "message": "Logged out successfully. All tokens and sessions have been revoked.",
      "data": {
        "message": "Logged out successfully",
        "access_token_revoked": true,
        "refresh_tokens_revoked": true,
        "sessions_revoked": true,
        "tokens_revoked": true
      }
    }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 10: Client receives logout response
  ├─► Check response.success === true
  └─► Check tokens_revoked status

Step 11: Client clears local storage
  ├─► Remove session_token
  ├─► Remove refresh_token
  ├─► Remove access_token
  ├─► Remove session_id
  └─► Clear user data from app state

Step 12: Client updates UI
  ├─► Redirect to login page
  ├─► Clear user context/state
  └─► Show logout success message (optional)
```

**Error Handling:**

```
Client receives error response:
  ├─► 401 Unauthorized
  │   └─► Token invalid/expired → Still proceed with logout
  │       └─► Clear local storage and redirect to login
  │
  └─► 500 Internal Server Error
      └─► Logout may have partially succeeded
      └─► Still clear local storage and redirect to login
```

**Important Notes:**
- Logout works even with expired tokens (server decodes without expiration check)
- All tokens are invalidated (access, refresh, session)
- All sessions are revoked (complete logout from all devices)
- Client should always clear local storage regardless of response

**Token Blacklisting:**
- Access tokens are blacklisted by JTI (JWT ID) for efficiency
- All refresh tokens for the user are revoked (user-level blacklist)
- All sessions for the user are blacklisted (complete logout from all devices)
- Blacklist entries expire automatically based on token expiration times
- Works even with expired tokens (decodes without expiration check)

**Security Features:**
- Complete logout from all devices (all sessions revoked)
- All refresh tokens invalidated (prevents token refresh)
- Access token blacklisted (prevents reuse)
- Works with expired tokens (for cleanup)

**Use Cases:**
- User logout
- Complete session termination (all devices)
- Security logout
- Account security
- Force logout from all devices

---

### Check User Availability

**Endpoint:** `POST /{MODE}/auth/check-user-availability`

**Description:** Check if email or phone number is available for registration.

**Authentication:** Not required

**Request Body:**
```json
{
  "user_id": "user@example.com"
}
```

**Alternative:**
```json
{
  "email": "user@example.com"
}
```

or

```json
{
  "phone": "+1234567890"
}
```

**Response (Available):**
```json
{
  "success": true,
  "message": "User is not available",
  "data": {
    "available": false,
    "first_name": null,
    "last_name": null
  }
}
```

**Response (Not Available):**
```json
{
  "success": true,
  "message": "User is available",
  "data": {
    "available": true,
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User enters email/phone in registration form
  ├─► User types email or phone number
  └─► Client may validate format client-side (optional)

Step 2: Client sends availability check (on blur or debounced)
  POST /{MODE}/auth/check-user-availability
  Content-Type: application/json
  {
    "user_id": "user@example.com"
  }
  OR
  {
    "email": "user@example.com"
  }
  OR
  {
    "phone": "+1234567890"
  }
  
  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Step 3: Server validates request
    ├─► Check: user_id OR email OR phone exists
    └─► ❌ 400 if none provided
  
  Step 4: Server determines identifier
    ├─► Use user_id if provided
    ├─► Use email if provided
    └─► Use phone if provided
  
  Step 5: Server validates format
    ├─► If email format → validateEmail()
    └─► If phone format → validatePhone()
    └─► ❌ 400 if invalid format
  
  Step 6: Server queries database
    ├─► Query: getUserByEmailOrPhone(identifier)
    └─► Returns user if exists, None if not exists
  
  Step 7: Server determines availability
    ├─► If user exists:
    │   ├─► available: false
    │   ├─► first_name: user.first_name (if exists)
    │   └─► last_name: user.last_name (if exists)
    └─► If user not exists:
        ├─► available: true
        ├─► first_name: null
        └─► last_name: null
  
  Step 8: Server returns availability status
    HTTP 200 OK
    {
      "success": true,
      "message": "User is not available",  // or "User is available"
      "data": {
        "available": false,  // or true
        "first_name": "John",  // or null
        "last_name": "Doe"  // or null
      }
    }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 9: Client receives response
  ├─► Check response.data.available
  └─► Update UI based on availability

Step 10: Client updates UI
  ├─► If available === false:
  │   ├─► Show: "Email/phone already registered"
  │   ├─► Show user name if provided: "This email belongs to John Doe"
  │   └─► Disable submit button or show error
  └─► If available === true:
      ├─► Show: "Email/phone is available" (optional)
      └─► Enable submit button
```

**Error Handling:**

```
Client receives error response:
  ├─► 400 Bad Request
  │   ├─► "user_id, email, or phone is required" → Show: "Please enter email/phone"
  │   └─► "Invalid email/phone format" → Show: "Invalid format"
  │
  └─► 500 Internal Server Error
      └─► Show: "Unable to check availability. Please try again."
```

**Client-Side Implementation Example:**

```javascript
// Debounced availability check
let checkTimeout;
const emailInput = document.getElementById('email');

emailInput.addEventListener('input', (e) => {
  clearTimeout(checkTimeout);
  const email = e.target.value;
  
  // Wait 500ms after user stops typing
  checkTimeout = setTimeout(async () => {
    if (email && validateEmail(email)) {
      try {
        const response = await fetch('/api/auth/check-user-availability', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        
        if (!data.data.available) {
          // Email already registered
          showError('Email already registered');
          if (data.data.first_name) {
            showInfo(`This email belongs to ${data.data.first_name} ${data.data.last_name}`);
          }
        } else {
          // Email available
          clearError();
        }
      } catch (error) {
        console.error('Availability check failed:', error);
      }
    }
  }, 500);
});
```

**Use Cases:**
- Registration form validation
- Username/email availability check
- Phone number availability check

---

### Verify Email and Phone

**Endpoint:** `POST /{MODE}/auth/verify-email-and-phone`

**Description:** Verify email or phone number with OTP.

**Authentication:** Not required

**Request Body:**
```json
{
  "user_id": "user@example.com",
  "channel": "email",
  "otp": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email/Phone verified successfully",
  "data": { ... }
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User wants to verify email/phone
  ├─► User is on verification page
  └─► User has received OTP (from send-otp endpoint)

Step 2: User enters OTP
  ├─► User enters OTP from email/SMS
  └─► User clicks "Verify" button

Step 3: Client sends verification request
  POST /{MODE}/auth/verify-email-and-phone
  Content-Type: application/json
  {
    "user_id": "user@example.com",
    "channel": "email",
    "otp": "123456"
  }
  
  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Step 4: Server validates request
    ├─► Check user_id exists → ❌ 400 if missing
    ├─► Check channel exists → ❌ 400 if missing
    └─► Check otp exists → ❌ 400 if missing
  
  Step 5: Server validates channel
    ├─► Check channel is "email" or "sms"
    └─► ❌ 400 if invalid channel
  
  Step 6: Server validates format
    ├─► If channel = "email" → validateEmail(user_id)
    └─► If channel = "sms" → validatePhone(user_id)
    └─► ❌ 400 if invalid format
  
  Step 7: Server verifies OTP
    ├─► Get stored OTP from cache: "otp:{channel}:{user_id}"
    ├─► Compare stored OTP with provided OTP
    ├─► Check expiration (10 minutes)
    └─► ❌ 401 if invalid/expired
    └─► OTP is NOT deleted (consume=false, can be reused)
  
  Step 8: Server returns success response
    HTTP 200 OK
    {
      "success": true,
      "message": "Email/Phone verified successfully",
      "data": {
        "user_id": "user@example.com",
        "channel": "email",
        "verified": true
      }
    }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 9: Client receives response
  ├─► Check response.success === true
  └─► Check response.data.verified === true

Step 10: Client updates UI
  ├─► Show: "Email/Phone verified successfully"
  ├─► Mark verification status as complete
  ├─► Enable next step (e.g., complete profile)
  └─► Hide OTP input field
```

**Error Handling:**

```
Client receives error response:
  ├─► 400 Bad Request
  │   ├─► "Invalid channel" → Show: "Channel must be email or sms"
  │   ├─► "Invalid email format" → Show: "Please enter valid email"
  │   └─► "Invalid phone format" → Show: "Please enter valid phone"
  │
  ├─► 401 Unauthorized
  │   ├─► "Invalid OTP" → Show: "Incorrect OTP. Please try again."
  │   └─► "OTP expired" → Show: "OTP expired. Please request a new one."
  │
  └─► 500 Internal Server Error
      └─► Show: "Verification failed. Please try again."
```

**Note:** This endpoint does NOT delete the OTP after verification (consume=false), allowing the OTP to be reused for other verification steps if needed.

**Use Cases:**
- Email verification
- Phone verification
- Account verification

---

### Change Email/Phone Workflow (Recommended)

**Description:** Secure two-step verification process for changing email or phone number. This workflow ensures both the current and new contact information are verified before making changes.

**Recommended Workflow Steps:**

1. **Step 1: Verify Primary Email/Phone** (Optional but Recommended)
   - Verify user owns the current email/phone before allowing changes
   - Provides additional security layer

2. **Step 2: Request OTP for New Email/Phone**
   - Request OTP to be sent to the new email/phone address
   - Ensures user has access to the new contact information

3. **Step 3: Change Email/Phone**
   - Call the change email/phone API with the OTP
   - Server verifies OTP and updates the contact information

**Complete Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User initiates email/phone change
  ├─► User is logged in (has valid token)
  ├─► User navigates to "Change Email" or "Change Phone" page
  └─► User enters new email/phone address

Step 2: (OPTIONAL) Verify Primary Email/Phone
  ├─► Client requests OTP for current email/phone
  │   POST /{MODE}/auth/send-one-time-password
  │   {
  │     "user_id": "current@example.com",  // Current email/phone
  │     "channel": "email"
  │   }
  │
  └─► User receives OTP on current email/phone
      └─► User enters OTP to verify ownership

Step 3: Client verifies primary email/phone (OPTIONAL)
  ├─► POST /{MODE}/auth/verify-one-time-password
  │   {
  │     "user_id": "current@example.com",
  │     "channel": "email",
  │     "otp": "123456"
  │   }
  │
  └─► Server verifies OTP (does NOT delete it)
      └─► Response: { "success": true, "message": "Verify Successfully" }

Step 4: Client requests OTP for NEW email/phone
  ├─► POST /{MODE}/auth/send-one-time-password
  │   {
  │     "user_id": "newemail@example.com",  // NEW email/phone
  │     "channel": "email"
  │   }
  │
  └─► User receives OTP on NEW email/phone
      └─► This proves user has access to new contact info

  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Server → Generates OTP, stores in cache (10 min TTL)
  Server → Sends OTP via email/SMS/WhatsApp to NEW address
  Server → Response: { "success": true, "message": "OTP sent successfully" }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 5: User receives OTP on new email/phone
  └─► User checks new email/SMS, gets 6-digit code

Step 6: Client calls change email/phone API
  ├─► POST /{MODE}/settings/change-email
  │   Authorization: Bearer <session_token>
  │   {
  │     "new_email": "newemail@example.com",
  │     "otp": "123456"  // OTP received on new email
  │   }
  │
  OR
  │
  ├─► POST /{MODE}/settings/change-phone
  │   Authorization: Bearer <session_token>
  │   {
  │     "new_phone": "+1234567890",
  │     "otp": "123456"  // OTP received on new phone
  │   }

  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Step 7: Server validates authentication
    ├─► Extract token from Authorization header
    ├─► Validate token (decode, check expiration, blacklist)
    └─► ❌ 401 if invalid/expired
  
  Step 8: Server verifies OTP for NEW email/phone
    ├─► Get stored OTP from cache: "otp:{channel}:{new_email/phone}"
    ├─► Compare stored OTP with provided OTP
    ├─► Check expiration (10 minutes)
    └─► ❌ 400 if invalid/expired
  
  Step 9: Server checks email/phone availability
    ├─► Check if new email/phone already exists for another user
    └─► ❌ 400 if already exists
  
  Step 10: Server updates email/phone
    ├─► Update user.email or user.phone_number
    ├─► Set is_email_verified = TRUE or is_phone_verified = TRUE
    ├─► Set email_verified_at or phone_number_verified_at = NOW()
    └─► Update last_updated = NOW()
  
  Step 11: Server deletes OTP (consume)
    └─► Delete OTP from cache (one-time use)
  
  Step 12: Server returns success response
    HTTP 200 OK
    {
      "success": true,
      "message": "Email/Phone updated and verified successfully",
      "data": {
        "user": {
          "id": "uuid",
          "email": "newemail@example.com",
          "is_email_verified": true,
          "email_verified_at": "2025-01-28T15:51:55Z"
        }
      }
    }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 13: Client receives response
  ├─► Check response.success === true
  └─► Extract updated user data

Step 14: Client updates UI
  ├─► Show: "Email/Phone updated successfully"
  ├─► Update user profile display
  ├─► Clear form fields
  └─► Redirect to profile/settings page
```

**Why This Workflow is Recommended:**

1. **Security**: Verifies ownership of both current and new contact information
2. **Prevents Unauthorized Changes**: Requires access to both email/phone addresses
3. **Two-Step Verification**: Adds an extra layer of security
4. **User Experience**: Clear step-by-step process
5. **Error Prevention**: Catches issues before making changes

**Alternative Simplified Workflow (Less Secure):**

If you skip Step 2-3 (primary verification), you can directly:
1. Request OTP for new email/phone
2. Call change email/phone API

**However, the recommended workflow provides better security.**

**Client-Side Implementation Example:**

```javascript
// Complete email change workflow
async function changeEmailWithVerification(currentEmail, newEmail) {
  try {
    // Step 1: (Optional) Verify current email
    // Request OTP for current email
    await fetch('/api/v1/auth/send-one-time-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: currentEmail,
        channel: 'email'
      })
    });
    
    // User enters OTP for current email
    const currentOtp = prompt('Enter OTP sent to your current email:');
    
    // Verify current email
    const verifyResponse = await fetch('/api/v1/auth/verify-one-time-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: currentEmail,
        channel: 'email',
        otp: currentOtp
      })
    });
    
    const verifyData = await verifyResponse.json();
    if (!verifyData.success) {
      throw new Error('Current email verification failed');
    }
    
    // Step 2: Request OTP for new email
    await fetch('/api/v1/auth/send-one-time-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: newEmail,
        channel: 'email'
      })
    });
    
    // User enters OTP for new email
    const newOtp = prompt('Enter OTP sent to your new email:');
    
    // Step 3: Change email
    const token = localStorage.getItem('session_token');
    const changeResponse = await fetch('/api/v1/settings/change-email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        new_email: newEmail,
        otp: newOtp
      })
    });
    
    const changeData = await changeResponse.json();
    if (changeData.success) {
      console.log('Email changed successfully:', changeData.data.user.email);
      return changeData.data;
    } else {
      throw new Error(changeData.error?.message || 'Failed to change email');
    }
    
  } catch (error) {
    console.error('Email change error:', error);
    throw error;
  }
}

// Simplified workflow (without primary verification)
async function changeEmailSimple(newEmail) {
  try {
    // Step 1: Request OTP for new email
    await fetch('/api/v1/auth/send-one-time-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: newEmail,
        channel: 'email'
      })
    });
    
    // User enters OTP
    const otp = prompt('Enter OTP sent to your new email:');
    
    // Step 2: Change email
    const token = localStorage.getItem('session_token');
    const response = await fetch('/api/v1/settings/change-email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        new_email: newEmail,
        otp: otp
      })
    });
    
    const data = await response.json();
    return data;
    
  } catch (error) {
    console.error('Email change error:', error);
    throw error;
  }
}
```

**Error Handling:**

```
Client receives error response:
  ├─► 400 Bad Request
  │   ├─► "Invalid OTP" → Show: "Incorrect OTP. Please try again."
  │   ├─► "Email already exists" → Show: "This email is already registered"
  │   └─► "Invalid email format" → Show: "Please enter valid email"
  │
  ├─► 401 Unauthorized
  │   ├─► "Invalid token" → Redirect to login
  │   └─► "OTP expired" → Show: "OTP expired. Please request a new one."
  │
  ├─► 403 Forbidden
  │   └─► "Permission denied" → Show: "You don't have permission to change email"
  │
  └─► 500 Internal Server Error
      └─► Show: "Failed to change email. Please try again."
```

**Use Cases:**
- Secure email change with two-step verification
- Secure phone change with two-step verification
- Account security updates
- Contact information updates

**Related Endpoints:**
- `POST /{MODE}/auth/send-one-time-password` - Request OTP
- `POST /{MODE}/auth/verify-one-time-password` - Verify OTP (doesn't delete)
- `POST /{MODE}/settings/change-email` - Change email (requires OTP to new email)
- `POST /{MODE}/settings/change-phone` - Change phone (requires OTP to new phone)

---

### Token Info

**Endpoint:** `GET /{MODE}/auth/token-info` or `POST /{MODE}/auth/token-info`

**Description:** Get information about the current authentication token. Useful for debugging and understanding token configuration.

**Authentication:** Required

**Request Body (POST only, optional):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Headers:**
```
Authorization: Bearer <access_token>
```
or
```
X-Session-Token: <session_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Token information retrieved successfully",
  "data": {
    "current_token": {
      "type": "session",
      "user_id": "f533589d-48d3-4b67-9430-c0b4793ac13e",
      "expires_at": "2025-02-04T15:51:55Z",
      "expires_in": "7 days",
      "issued_at": "2025-01-28T15:51:55Z",
      "session_id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd"
    },
    "token_config": {
      "access_token": {
        "expiry_minutes": 60,
        "expires_in": "1 hour"
      },
      "session_token": {
        "expiry_minutes": 10080,
        "expires_in": "7 days"
      },
      "refresh_token": {
        "expiry_minutes": 43200,
        "expires_in": "30 days"
      }
    },
    "extension_info": {
      "access_token_extension": "1 hour",
      "session_token_extension": "7 days",
      "refresh_token_extension": "30 days"
    }
  }
}
```

**Response Fields:**
- `current_token`: Information about the token used for authentication
  - `type`: Token type (access, session, or refresh)
  - `user_id`: User ID from token
  - `expires_at`: Token expiration timestamp
  - `expires_in`: Human-readable expiration time
  - `issued_at`: Token issuance timestamp
  - `session_id`: Session identifier (if available)
- `token_config`: Configuration for all token types
- `extension_info`: How long tokens are extended when refreshed

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Extract Token from Headers
   │   ├─► Authorization Bearer header
   │   └─► X-Session-Token header (fallback)
   │
   ├─► Decode Token
   │   ├─► Extract token type
   │   ├─► Extract user_id
   │   ├─► Extract expiration time
   │   └─► Extract session_id
   │
   ├─► Get Token Configuration
   │   └─► Read from environment variables
   │
   └─► Return Token Information
```

**Use Cases:**
- Debug authentication issues
- Check token expiration
- Understand token configuration
- Verify token type and payload
- Client-side token validation

**Note:** This endpoint is excluded from API schema (`include_in_schema=False`) but is available for use.

---

## Workflows

### Complete Authentication Flow (High-Level Overview)

```
┌─────────────────────────────────────────────────────────────┐
│              User Authentication Flow                       │
└────────────────────────────┬────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Registration?  │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        ┌───────────────┐         ┌───────────────┐
        │   Signup      │         │    Login      │
        └───────┬───────┘         └───────┬───────┘
                │                         │
                ▼                         ▼
        ┌───────────────┐         ┌───────────────┐
        │  Send OTP     │         │ Password/OTP  │
        └───────┬───────┘         └───────┬───────┘
                │                         │
                ▼                         ▼
        ┌───────────────┐         ┌───────────────┐
        │  Verify OTP   │         │ Authenticate  │
        └───────┬───────┘         └───────┬───────┘
                │                         │
                └────────────┬────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Generate Token  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Return Token   │
                    └─────────────────┘
```

**Flow Explanation:**
1. **User Decision**: User chooses between Registration (Signup) or Login
2. **Signup Path**: Send OTP → Verify OTP → Generate Token
3. **Login Path**: Password/OTP → Authenticate → Generate Token
4. **Token Generation**: Server generates all tokens (access, refresh, session)
5. **Token Return**: Client receives tokens and stores them securely

### Enhanced Authentication Flow Diagram (Client ↔ Server)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ User Action: Login or Signup?
                              ▼
                    ┌─────────────────────┐
                    │  Registration?      │
                    └─────────┬─────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
        ┌───────────────┐               ┌───────────────┐
        │   SIGNUP     │               │    LOGIN      │
        └───────┬───────┘               └───────┬───────┘
                │                               │
                │                               │
                ▼                               │
        ┌───────────────┐                       │
        │  Send OTP     │                       │
        │  (Client)     │                       │
        └───────┬───────┘                       │
                │                               │
                │ POST /auth/send-otp           │
                ▼                               │
        ┌───────────────┐                       │
        │  SERVER       │                       │
        │  - Generate   │                       │
        │  - Store OTP  │                       │
        │  - Send Email │                       │
        └───────┬───────┘                       │
                │                               │
                │ Response: OTP Sent            │
                ▼                               │
        ┌───────────────┐                       │
        │  User Receives│                       │
        │  OTP via Email│                       │
        └───────┬───────┘                       │
                │                               │
                │ POST /auth/verify             │
                │ (Signup)                      │
                ▼                               │
        ┌───────────────┐                       │
        │  SERVER       │                       │
        │  - Verify OTP │                       │
        │  - Create User│                       │
        │  - Generate   │                       │
        │    Tokens     │                       │
        └───────┬───────┘                       │
                │                               │
                │ Response: Tokens + User       │
                ▼                               │
        ┌───────────────┐                       │
        │  CLIENT       │                       │
        │  - Store      │                       │
        │    Tokens     │                       │
        │  - Redirect   │                       │
        └───────────────┘                       │
                                                │
                                                │
                                                ▼
                                        ┌───────────────┐
                                        │  Password/   │
                                        │  OTP Login   │
                                        └───────┬───────┘
                                                │
                        ┌───────────────────────┴───────────────────────┐
                        │                                               │
                        ▼                                               ▼
                ┌───────────────┐                               ┌───────────────┐
                │ Password      │                               │ OTP Login     │
                │ Login         │                               │               │
                └───────┬───────┘                               └───────┬───────┘
                        │                                               │
                        │ POST /auth/login-with-password                │ POST /auth/send-otp
                        ▼                                               ▼
                ┌───────────────┐                               ┌───────────────┐
                │  SERVER       │                               │  SERVER       │
                │  - Validate   │                               │  - Generate   │
                │  - Authenticate│                              │  - Send OTP   │
                │  - Generate   │                               └───────┬───────┘
                │    Tokens     │                                       │
                └───────┬───────┘                                       │
                        │                                               │ User Receives OTP
                        │                                               ▼
                        │                                       ┌───────────────┐
                        │                                       │ POST /auth/   │
                        │                                       │ login-with-otp│
                        │                                       └───────┬───────┘
                        │                                               │
                        │                                               ▼
                        │                                       ┌───────────────┐
                        │                                       │  SERVER       │
                        │                                       │  - Verify OTP │
                        │                                       │  - Generate   │
                        │                                       │    Tokens     │
                        │                                       └───────┬───────┘
                        │                                               │
                        └───────────────────────┬───────────────────────┘
                                                │
                                                │ Response: Tokens + User
                                                ▼
                                        ┌───────────────┐
                                        │  CLIENT       │
                                        │  - Store      │
                                        │    Tokens     │
                                        │  - Use for API│
                                        │    Requests   │
                                        └───────────────┘
```

**Key Points:**
- **Blue boxes**: Client-side actions
- **Green boxes**: Server-side processing
- **Arrows**: Request/response flow direction
- **Multiple paths**: Shows different authentication methods
- **Token storage**: Final step shows token usage for API requests

---

### Complete Authentication Flow (Detailed Client-Server Communication)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

User Action: Wants to login or signup
  │
  ├─► Decision: New User (Signup) or Existing User (Login)?
  │
  └─► User enters email/phone

─────────────────────────────────────────────────────────────────

SCENARIO 1: NEW USER (SIGNUP)
─────────────────────────────────────────────────────────────────

Step 1: Check Availability (Optional)
  Client → POST /auth/check-user-availability
  Body: { "email": "user@example.com" }
  
  Server → Response: { "available": true }
  
  Client: If available, proceed to signup

Step 2: Request OTP
  Client → POST /auth/send-one-time-password
  Body: { "user_id": "user@example.com", "channel": "email" }
  
  Server → Generates OTP, stores in cache, sends email
  Server → Response: { "success": true, "message": "OTP sent" }
  
  Client: Shows "OTP sent to your email"

Step 3: User receives OTP
  User: Checks email, gets 6-digit code

Step 4: Verify OTP and Signup
  Client → POST /auth/verify
  Body: { "user_id": "user@example.com", "channel": "email", "otp": "123456" }
  
  Server → Verifies OTP, creates user account, generates tokens
  Server → Response: { "success": true, "data": { tokens, user } }
  
  Client: Stores tokens, redirects to dashboard

─────────────────────────────────────────────────────────────────

SCENARIO 2: EXISTING USER (LOGIN)
─────────────────────────────────────────────────────────────────

OPTION A: Password Login
─────────────────────────────────────────────────────────────────

Step 1: User enters credentials
  Client: User enters email/phone and password

Step 2: Login Request
  Client → POST /auth/login-with-password
  Body: username=user@example.com&password=secret123
  
  Server → Validates credentials, checks user status, generates tokens
  Server → Response: { "success": true, "data": { tokens, user } }
  
  Client: Stores tokens, redirects to dashboard

─────────────────────────────────────────────────────────────────

OPTION B: OTP Login
─────────────────────────────────────────────────────────────────

Step 1: Request OTP
  Client → POST /auth/send-one-time-password
  Body: { "user_id": "user@example.com", "channel": "email" }
  
  Server → Generates OTP, sends email
  Server → Response: { "success": true }
  
  Client: Shows "OTP sent to your email"

Step 2: User receives OTP
  User: Checks email, gets 6-digit code

Step 3: Login with OTP
  Client → POST /auth/login-with-otp
  Body: { "user_id": "user@example.com", "channel": "email", "otp": "123456" }
  
  Server → Verifies OTP, checks user status, generates tokens
  Server → Response: { "success": true, "data": { tokens, user } }
  
  Client: Stores tokens, redirects to dashboard

─────────────────────────────────────────────────────────────────

ONGOING: TOKEN USAGE
─────────────────────────────────────────────────────────────────

Step 1: Client makes API requests
  Client → GET /api/protected-endpoint
  Headers: X-Session-Token: <session_token>
  
  Server → Validates token, processes request
  Server → Response: { "success": true, "data": {...} }

Step 2: Token expires
  Client → GET /api/protected-endpoint
  Headers: X-Session-Token: <expired_token>
  
  Server → Response: 401 Unauthorized
  
  Client: Detects 401, triggers token refresh

Step 3: Refresh tokens
  Client → POST /auth/refresh-token
  Body: { "refresh_token": "..." }
  
  Server → Validates refresh token, generates new tokens
  Server → Response: { "success": true, "data": { new_tokens } }
  
  Client: Updates stored tokens, retries original request

─────────────────────────────────────────────────────────────────

LOGOUT FLOW
─────────────────────────────────────────────────────────────────

Step 1: User clicks logout
  Client → POST /auth/logout
  Headers: Authorization: Bearer <session_token>
  
  Server → Blacklists tokens, revokes all sessions
  Server → Response: { "success": true, "data": { revocation_status } }
  
  Client: Clears local storage, redirects to login
```

### Password Reset Flow (Client-Server Communication)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User clicks "Forgot Password"
  └─► User navigates to password reset page

Step 2: User enters email/phone
  └─► Client validates format

Step 3: Request OTP
  Client → POST /auth/send-one-time-password
  Body: { "user_id": "user@example.com", "channel": "email" }
  
  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Server → Generates OTP, stores in cache (10 min TTL)
  Server → Sends OTP via email/SMS
  Server → Response: { "success": true, "message": "OTP sent" }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 4: User receives OTP
  └─► User checks email/SMS, gets 6-digit code

Step 5: User enters OTP and new password
  ├─► User enters OTP
  ├─► User enters new password
  └─► User confirms new password

Step 6: Reset password
  Client → POST /auth/forget-password
  Body: {
    "user_id": "user@example.com",
    "otp": "123456",
    "password": "newPassword123",
    "confirm_password": "newPassword123"
  }
  
  ┌─────────────────────────────────────────────────────────────┐
  │                    SERVER SIDE                              │
  └─────────────────────────────────────────────────────────────┘
  
  Server → Verifies OTP
  Server → Validates passwords match
  Server → Hashes new password (bcrypt)
  Server → Updates user password in database
  Server → Deletes OTP (consume=true)
  Server → Response: { "success": true, "message": "Password updated" }

┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 7: Password reset complete
  ├─► Show: "Password reset successfully"
  └─► Redirect to login page
```

### Token Lifecycle Flow (Client-Server Communication)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

LOGIN → Token Generation
  ├─► POST /auth/login-with-password
  └─► Receive: access_token, refresh_token, session_token, session_id
  └─► Store tokens securely

API REQUESTS → Token Usage
  ├─► Include token in request header
  │   ├─► X-Session-Token: <session_token> (RECOMMENDED)
  │   OR
  │   └─► Authorization: Bearer <session_token>
  └─► Server validates token, processes request

TOKEN EXPIRATION → Automatic Refresh
  ├─► API request returns 401
  ├─► Client intercepts 401 error
  ├─► POST /auth/refresh-token
  │   └─► Body: { "refresh_token": "..." }
  ├─► Receive new tokens
  ├─► Update stored tokens
  └─► Retry original request with new token

LOGOUT → Token Revocation
  ├─► POST /auth/logout
  ├─► Server blacklists all tokens
  ├─► Server revokes all sessions
  └─► Client clears local storage
```

## Error Handling

### Common Error Responses

**400 Bad Request - Invalid Payload:**
```json
{
  "success": false,
  "message": "Invalid request payload",
  "error": "Validation error details",
  "statusCode": 400
}
```

**401 Unauthorized - Invalid Credentials:**
```json
{
  "success": false,
  "message": "Invalid credentials",
  "error": "Email/phone or password is incorrect",
  "statusCode": 401
}
```

**401 Unauthorized - Invalid OTP:**
```json
{
  "success": false,
  "message": "Invalid OTP",
  "error": "OTP is incorrect or expired",
  "statusCode": 401
}
```

**404 Not Found - User Not Found:**
```json
{
  "success": false,
  "message": "User not found",
  "error": "User with provided email/phone does not exist",
  "statusCode": 404
}
```

**409 Conflict - User Already Exists:**
```json
{
  "success": false,
  "message": "User already exists",
  "error": "User with this email/phone already registered",
  "statusCode": 409
}
```

---

## Token Management

### Frontend Token Usage

**Recommended Approach (Session Token - Fastest & Most Secure):**
1. **Session Token**: Use for all API requests (RECOMMENDED)
   ```javascript
   // Store after login
   localStorage.setItem('session_token', response.data.session_token);
   localStorage.setItem('refresh_token', response.data.refresh_token);
   localStorage.setItem('session_id', response.data.session_id);
   
   // Use session_token for API calls (fastest validation)
   // Option 1: X-Session-Token header (preferred)
   const headers = {
     'X-Session-Token': localStorage.getItem('session_token')
   };
   
   // Option 2: Authorization Bearer header (session_token works here too!)
   const headers = {
     'Authorization': `Bearer ${localStorage.getItem('session_token')}`
   };
   
   // Decode session token for client-side user info (no API call needed)
   import jwtDecode from 'jwt-decode';
   const userInfo = jwtDecode(localStorage.getItem('session_token'));
   console.log(userInfo.user_profile);  // Full user profile available
   ```

2. **Alternative: Access Token** (Still supported)
   ```javascript
   // Store after login
   localStorage.setItem('access_token', response.data.access_token);
   
   // Use in API calls
   const headers = {
     'Authorization': `Bearer ${localStorage.getItem('access_token')}`
   };
   ```

3. **Refresh Token**: Store securely and use when tokens expire
   ```javascript
   // Store securely (prefer httpOnly cookie if possible)
   localStorage.setItem('refresh_token', response.data.refresh_token);
   
   // Refresh when session/access token expires
   async function refreshTokens() {
     const refreshToken = localStorage.getItem('refresh_token');
     const response = await fetch('/api/auth/refresh-token', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify({ refresh_token: refreshToken })
     });
     const data = await response.json();
     // Update all tokens
     localStorage.setItem('session_token', data.data.session_token);
     localStorage.setItem('access_token', data.data.access_token);
     localStorage.setItem('refresh_token', data.data.refresh_token);
     localStorage.setItem('session_id', data.data.session_id);
     return data.data;
   }
   ```

4. **Session ID**: Store for logout operations
   ```javascript
   localStorage.setItem('session_id', response.data.session_id);
   ```

### Token Expiration Handling

**Using Session Token (Recommended):**
```javascript
// Intercept API responses to handle token expiration
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Session token expired, try to refresh
      try {
        const newTokens = await refreshTokens();
        // Retry original request with new session token
        // You can use either method:
        error.config.headers['X-Session-Token'] = newTokens.session_token;
        // OR
        // error.config.headers['Authorization'] = `Bearer ${newTokens.session_token}`;
        return axios.request(error.config);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Request interceptor to add session token
axios.interceptors.request.use(
  (config) => {
    const sessionToken = localStorage.getItem('session_token');
    if (sessionToken) {
      // Option 1: X-Session-Token header (preferred)
      config.headers['X-Session-Token'] = sessionToken;
      // OR
      // Option 2: Authorization Bearer header (session_token works here too!)
      // config.headers['Authorization'] = `Bearer ${sessionToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);
```

**Using Access Token (Alternative):**
```javascript
// Intercept API responses to handle token expiration
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Access token expired, try to refresh
      try {
        const newTokens = await refreshTokens();
        // Retry original request with new access token
        error.config.headers.Authorization = `Bearer ${newTokens.access_token}`;
        return axios.request(error.config);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
```

### Security Best Practices

1. **Token Storage**:
   - **Session Token**: httpOnly cookie (preferred) or secure storage - **RECOMMENDED for API calls**
   - Access Token: Memory or secure storage (avoid localStorage for sensitive apps)
   - Refresh Token: httpOnly cookie (preferred) or secure storage
   - Session ID: Store with tokens

2. **Token Usage Priority**:
   - **Primary**: Use `session_token` with `X-Session-Token` header (fastest, most secure)
   - **Alternative 1**: Use `session_token` with `Authorization: Bearer` header (also works!)
   - **Alternative 2**: Use `access_token` with `Authorization: Bearer` header (still supported)
   - **Never**: Use `refresh_token` for API authentication (only for token refresh)
   
   **Note**: The `Authorization: Bearer` header accepts both `session_token` and `access_token`. 
   The server automatically detects the token type and validates accordingly.

3. **Token Rotation**: Refresh tokens are rotated on each refresh for security

4. **Token Blacklisting**: Tokens are blacklisted on logout and cannot be reused

5. **Session Management**: Each login creates a new session with unique session_id

6. **Client-Side Validation**: Session tokens can be decoded client-side for user info display without API calls

## Best Practices

1. **Use Strong Passwords**: Enforce password complexity requirements
2. **OTP Expiration**: OTPs expire after 10 minutes for security
3. **Rate Limiting**: Implement rate limiting on authentication endpoints
4. **Token Storage**: 
   - Access tokens: Store in memory when possible
   - Refresh tokens: Use httpOnly cookies for web apps
   - Never store tokens in localStorage for sensitive applications
5. **Password Hashing**: Always use bcrypt with appropriate salt rounds (10 rounds)
6. **Email/Phone Validation**: Validate format before processing
7. **Error Messages**: Don't reveal if email/phone exists in system
8. **Token Refresh**: Implement automatic token refresh before expiration
9. **Session Management**: Track active sessions and allow users to revoke them
10. **Token Blacklisting**: Tokens are automatically blacklisted on logout

## Environment Variables

Configure token expiration times:

```bash
# Token Expiration Times (in minutes)
ACCESS_TOKEN_EXPIRY_MINUTES=60      # Access token lifetime (default: 60 minutes = 1 hour)
SESSION_TOKEN_EXPIRY_MINUTES=10080  # Session token lifetime (default: 10080 minutes = 7 days)
REFRESH_TOKEN_EXPIRY_MINUTES=43200  # Refresh token lifetime (default: 43200 minutes = 30 days)

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here  # Required: Secret key for JWT signing
JWT_ALGORITHM=HS256                  # Optional: JWT algorithm (default: HS256)

# Password Hashing
BCRYPT_SALT_ROUNDS=10                # Optional: Bcrypt salt rounds (default: 10)
```

## Architecture

### Stateless Authentication
- No database storage for sessions
- All session info embedded in JWT tokens
- Token blacklisting via cache (Redis or in-memory)
- Fast and scalable

### Token Blacklisting
- Tokens blacklisted in cache with TTL matching token expiration
- Automatic cleanup when tokens expire
- Supports Redis for distributed systems
- Falls back to in-memory cache if Redis unavailable

### Performance Optimizations
- Lightweight access tokens (minimal payload - only essential fields)
- Session tokens with full user profile (no database lookup needed)
- Non-blocking sign-in updates
- Optimized blacklist check order
- Fast token generation and validation
- JTI-based access token blacklisting (efficient)
- User-level blacklist for refresh tokens and sessions
- Token validation priority: X-Session-Token > Authorization Bearer > OAuth2 > query param

### Token Blacklisting Strategy
- **Access Tokens**: Blacklisted by JTI (JWT ID) for efficiency
- **Refresh Tokens**: User-level blacklist (revokes all refresh tokens for user)
- **Sessions**: User-level blacklist (revokes all sessions for user - complete logout)
- **Automatic Expiration**: Blacklist entries expire with token expiration times
- **Cache Storage**: Uses Redis (if available) or in-memory cache
- **Logout Behavior**: Complete logout from all devices (all sessions revoked)

---

**Last Updated**: January 2025

## Recent Updates

### Token System Improvements
- ✅ Access token expiration updated to 60 minutes (1 hour)
- ✅ Session token contains full user profile (no database lookup needed)
- ✅ JTI-based access token blacklisting for efficiency
- ✅ Complete logout from all devices (all sessions revoked)
- ✅ User-level blacklist for refresh tokens and sessions
- ✅ Token rotation on refresh (all tokens regenerated)

### New Endpoints
- ✅ `GET/POST /auth/token-info` - Get token information and configuration

### Security Enhancements
- ✅ Complete logout from all devices
- ✅ All refresh tokens revoked on logout
- ✅ Access token blacklisted by JTI
- ✅ Token rotation on refresh for security
- ✅ User-level blacklist clearing on login (allows re-login after logout)

