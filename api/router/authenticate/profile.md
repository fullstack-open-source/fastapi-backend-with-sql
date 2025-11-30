# Profile Router

> **Complete Documentation for User Profile Management Endpoints**

This router handles all user profile operations including viewing, updating profile information, managing profile pictures, changing email/phone, updating settings, and account management.

## 📋 Table of Contents

- [Overview](#overview)
  - [Profile System](#profile-system)
  - [Permissions](#permissions)
- [Endpoints](#endpoints)
  - [Get User Profile](#get-user-profile)
  - [Get User Profile by ID](#get-user-profile-by-id)
  - [Update Profile Picture](#update-profile-picture)
  - [Update Profile](#update-profile)
  - [Profile Accessibility](#profile-accessibility)
  - [Profile Language](#profile-language)
  - [Change Email](#change-email)
  - [Change Phone](#change-phone)
  - [Send Phone OTP](#send-phone-otp)
  - [Update Theme](#update-theme)
  - [Update Timezone](#update-timezone)
  - [Get Settings](#get-settings)
  - [Deactivate Account](#deactivate-account)
  - [Delete Account](#delete-account)
- [User Model](#user-model)
- [Workflows](#workflows)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Client-Side Implementation](#client-side-implementation)

## Overview

The Profile router provides comprehensive user profile management functionality including:
- **Profile Viewing**: Get current user profile or view other users' profiles
- **Profile Updates**: Update personal information, bio, and preferences
- **Profile Picture**: Upload and update profile pictures via Google Cloud Storage
- **Contact Management**: Change email and phone numbers with OTP verification
- **Settings Management**: Update theme, language, timezone, and accessibility settings
- **Account Management**: Deactivate or delete user accounts

**Base Path:** `/{MODE}/settings`

**Authentication:** All endpoints require authentication via token (access_token or session_token)

### Profile System

The profile system provides a comprehensive user management interface:

1. **Profile Data**
   - Personal information (name, email, phone, bio, etc.)
   - Profile picture URL (stored in Google Cloud Storage)
   - User preferences (theme, language, timezone)
   - Verification status (email, phone)
   - Account status (active, verified, protected)

2. **Profile Updates**
   - Partial updates supported (only provided fields are updated)
   - Protected fields (user_id, email/phone) cannot be changed directly
   - Email/phone changes require OTP verification
   - Automatic timestamp updates (`last_updated`)

3. **File Uploads**
   - Profile pictures uploaded to Google Cloud Storage
   - Automatic file naming with user_id and UUID
   - Support for various image formats
   - Public URL returned for frontend use

### Permissions

Profile endpoints use permission-based access control:

- **`view_profile`**: Required for viewing own profile
- **`view_user`**: Required for viewing other users' profiles
- **`edit_profile`**: Required for all profile update operations

**Permission Middleware:**
All endpoints use `check_permission()` middleware to validate user permissions before processing requests.

## Endpoints

### Get User Profile

**Endpoint:** `GET /{MODE}/settings/profile`

**Description:** Get the current authenticated user's profile information.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `view_profile`

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
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "User profile fetched successfully",
  "data": {
    "user_id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": {
      "phone": "+1234567890"
    },
    "profile_picture_url": "https://storage.googleapis.com/...",
    "bio": "Software developer",
    "country": "US",
    "gender": "male",
    "theme": "light",
    "language": "en",
    "profile_accessibility": "public",
    "timezone": "America/New_York",
    "is_email_verified": true,
    "is_phone_verified": true,
    "is_active": true,
    "is_verified": true,
    "status": "ACTIVE",
    "created_at": "2025-01-15T10:30:00Z",
    "last_updated": "2025-01-28T15:51:55Z"
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

Step 1: Client prepares request
  ├─► Retrieve stored access_token or session_token
  ├─► Add token to Authorization header or X-Session-Token header
  └─► Prepare GET request to /{MODE}/settings/profile

Step 2: Client sends request
  GET /{MODE}/settings/profile
  Headers:
    Authorization: Bearer <token>
    # OR
    X-Session-Token: <session_token>

Step 3: Client receives response
  ├─► Success (200): Display profile data
  ├─► Unauthorized (401): Redirect to login
  ├─► Forbidden (403): Show permission error
  └─► Not Found (404): Show profile not found error

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token (JWT verification)
  ├─► Check token blacklist
  └─► Extract user from token

Step 2: Permission check
  ├─► Check if user has "view_profile" permission
  └─► If no permission: Return 403 Forbidden

Step 3: Database query
  ├─► Query user profile by user_id from token
  ├─► Fetch all user fields from database
  └─► Serialize datetime fields to ISO format

Step 4: Response preparation
  ├─► Build User model from database result
  ├─► Serialize data (convert datetime objects)
  └─► Return SUCCESS response with profile data

Step 5: Error handling
  ├─► Profile not found: Return 404 with error details
  ├─► Database error: Log error, return 500
  └─► Permission error: Return 403 with error details
```

**Error Responses:**

```json
// 404 - Profile Not Found
{
  "success": false,
  "id": null,
  "message": "Profile not found",
  "error": {
    "code": "PROFILE_NOT_FOUND",
    "details": {
      "user_id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd"
    }
  }
}

// 403 - Permission Denied
{
  "success": false,
  "id": null,
  "message": "Permission denied",
  "error": {
    "code": "PERMISSION_DENIED",
    "details": {
      "required_permission": "view_profile"
    }
  }
}

// 500 - Server Error
{
  "success": false,
  "id": null,
  "message": "Error processing profile request",
  "error": {
    "code": "PROFILE_PROCESSING_ERROR",
    "details": {
      "user_id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd"
    }
  }
}
```

---

### Get User Profile by ID

**Endpoint:** `GET /{MODE}/settings/profile/{user_id}`

**Description:** Get a specific user's profile by user_id. Requires `view_user` permission.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `view_user`

**Path Parameters:**
- `user_id` (string, required): The UUID of the user whose profile to retrieve

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
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "User profile fetched successfully",
  "data": {
    "user_id": "b3dgb6gd-6074-5b64-b1b9-7e3e361bg9ge",
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com",
    "profile_picture_url": "https://storage.googleapis.com/...",
    "bio": "Designer",
    "profile_accessibility": "public",
    "is_active": true,
    "is_verified": true
  }
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Client prepares request
  ├─► User navigates to another user's profile page
  ├─► Retrieve stored access_token or session_token
  ├─► Get target user_id from route/URL
  └─► Prepare GET request to /{MODE}/settings/profile/{user_id}

Step 2: Client sends request
  GET /{MODE}/settings/profile/{user_id}
  Headers:
    Authorization: Bearer <token>

Step 3: Client receives response
  ├─► Success (200): Display user profile
  ├─► Unauthorized (401): Redirect to login
  ├─► Forbidden (403): Show permission error
  └─► Not Found (404): Show user not found error

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token
  ├─► Extract user_id from path parameters
  └─► Extract current user from token

Step 2: Permission check
  ├─► Check if current user has "view_user" permission
  └─► If no permission: Return 403 Forbidden

Step 3: Database query
  ├─► Query user profile by target user_id
  ├─► Fetch all user fields from database
  └─► Serialize datetime fields

Step 4: Response preparation
  ├─► Build User model from database result
  ├─► Serialize data
  └─► Return SUCCESS response with profile data

Step 5: Error handling
  ├─► User not found: Return 404
  ├─► Permission denied: Return 403
  └─► Server error: Log and return 500
```

---

### Update Profile Picture

**Endpoint:** `POST /{MODE}/settings/update-profile-picture`

**Description:** Upload and update the user's profile picture. The file is uploaded to Google Cloud Storage and the public URL is stored in the database.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `edit_profile`

**Request:**
```
POST /{MODE}/settings/update-profile-picture
Content-Type: multipart/form-data

file: <binary image data>
```

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "Profile picture updated successfully",
  "data": {
    "message": "Profile picture updated successfully",
    "profile_picture_url": "https://storage.googleapis.com/bucket/media/users/johndoe-user_id_a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd-|-f533589d-48d3-4b67-9430-c0b4793ac13e.jpg"
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

Step 1: User selects image
  ├─► User clicks "Change Profile Picture"
  ├─► File picker opens (accepts image/*)
  └─► User selects image file

Step 2: Client validates image
  ├─► Check file size (recommended: < 5MB)
  ├─► Check file type (jpg, png, gif, webp)
  └─► Optionally: Preview image before upload

Step 3: Client prepares request
  ├─► Create FormData object
  ├─► Append image file to FormData
  ├─► Retrieve stored access_token or session_token
  └─► Prepare POST request with multipart/form-data

Step 4: Client sends request
  POST /{MODE}/settings/update-profile-picture
  Headers:
    Authorization: Bearer <token>
    Content-Type: multipart/form-data
  Body:
    file: <File object>

Step 5: Client receives response
  ├─► Success (200): Update UI with new profile picture URL
  ├─► Unauthorized (401): Redirect to login
  ├─► Forbidden (403): Show permission error
  └─► Error (500): Show error message, keep old picture

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token
  ├─► Extract current user from token
  └─► Check permission: "edit_profile"

Step 2: File processing
  ├─► Read file data from request
  ├─► Extract file extension
  ├─► Determine content type
  └─► Generate unique object key: {username}-user_id_{user_id}-|-{uuid}.{ext}

Step 3: Upload to Google Cloud Storage
  ├─► Upload file to "media/users" folder
  ├─► Set content type
  ├─► Make file publicly accessible
  └─► Get public URL

Step 4: Database update
  ├─► Update user.profile_picture_url with new URL
  ├─► Update user.last_updated timestamp
  └─► Return updated user_id

Step 5: Response preparation
  ├─► Build success response with profile_picture_url
  └─► Return SUCCESS response

Step 6: Error handling
  ├─► Upload failed: Return 500 with error details
  ├─► Database update failed: Return 500
  └─► Permission denied: Return 403
```

**Client-Side Implementation Example:**

```javascript
// Update Profile Picture
async function updateProfilePicture(file) {
  try {
    // Validate file
    if (!file || !file.type.startsWith('image/')) {
      throw new Error('Please select a valid image file');
    }
    
    if (file.size > 5 * 1024 * 1024) { // 5MB limit
      throw new Error('Image size must be less than 5MB');
    }
    
    // Create FormData
    const formData = new FormData();
    formData.append('file', file);
    
    // Get token from storage
    const token = localStorage.getItem('access_token') || 
                 localStorage.getItem('session_token');
    
    // Send request
    const response = await fetch('/api/v1/settings/update-profile-picture', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Update UI with new profile picture
      document.getElementById('profile-picture').src = data.data.profile_picture_url;
      showNotification('Profile picture updated successfully');
    } else {
      throw new Error(data.error?.message || 'Failed to update profile picture');
    }
  } catch (error) {
    console.error('Error updating profile picture:', error);
    showError(error.message);
  }
}

// HTML Example
<input 
  type="file" 
  accept="image/*" 
  onChange={(e) => updateProfilePicture(e.target.files[0])}
/>
```

---

### Update Profile

**Endpoint:** `POST /{MODE}/settings/update-profile`

**Description:** Partially update user profile fields. Only provided fields will be updated. Protected fields (user_id, email, phone) cannot be updated through this endpoint.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `edit_profile`

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Software developer passionate about web technologies",
  "country": "US",
  "gender": "male",
  "dob": "1990-01-15T00:00:00Z",
  "portfolio_url": "https://johndoe.dev"
}
```

**Note:** Only include fields you want to update. Omitted fields will remain unchanged.

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "User profile update successfully",
  "data": {
    "user_id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Software developer passionate about web technologies",
    "country": "US",
    "gender": "male",
    "dob": "1990-01-15T00:00:00Z",
    "portfolio_url": "https://johndoe.dev",
    "last_updated": "2025-01-28T15:51:55Z"
  }
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User edits profile form
  ├─► User fills in profile fields (name, bio, country, etc.)
  ├─► Client validates form fields
  └─► User clicks "Save" button

Step 2: Client prepares request
  ├─► Collect form data (only changed fields)
  ├─► Remove protected fields (user_id, email, phone)
  ├─► Convert dates to ISO format
  ├─► Retrieve stored access_token or session_token
  └─► Prepare POST request with JSON body

Step 3: Client sends request
  POST /{MODE}/settings/update-profile
  Headers:
    Authorization: Bearer <token>
    Content-Type: application/json
  Body:
    {
      "first_name": "John",
      "last_name": "Doe",
      "bio": "...",
      ...
    }

Step 4: Client receives response
  ├─► Success (200): Update UI with new profile data
  ├─► Bad Request (400): Show validation errors
  ├─► Unauthorized (401): Redirect to login
  ├─► Forbidden (403): Show permission error
  └─► Error (500): Show error message

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token
  ├─► Extract current user from token
  ├─► Parse request body (User model)
  └─► Check permission: "edit_profile"

Step 2: Data processing
  ├─► Extract only provided fields (exclude_unset=True)
  ├─► Remove protected fields:
  │   ├─► user_id (always protected)
  │   ├─► email (if user has email)
  │   └─► phone (if user has phone)
  ├─► Validate no protected fields in update
  └─► Check if any fields remain to update

Step 3: Build SQL update query
  ├─► Create SET clauses for each field
  ├─► Handle phone_number as JSONB if provided
  ├─► Add last_updated = NOW()
  └─► Prepare parameterized query

Step 4: Database update
  ├─► Execute UPDATE query
  ├─► Verify update succeeded (check RETURNING)
  └─► Fetch updated user data

Step 5: Response preparation
  ├─► Build User model from updated data
  ├─► Serialize data (convert datetime objects)
  └─► Return SUCCESS response with updated profile

Step 6: Error handling
  ├─► No fields to update: Return 400
  ├─► Protected field attempted: Return 400
  ├─► Update failed: Return 500
  └─► Permission denied: Return 403
```

**Protected Fields:**
- `user_id`: Always protected (cannot be changed)
- `email`: Protected if user has email (use `/change-email` endpoint)
- `phone`: Protected if user has phone (use `/change-phone` endpoint)

**Client-Side Implementation Example:**

```javascript
// Update Profile
async function updateProfile(profileData) {
  try {
    // Remove protected fields
    const { user_id, email, phone_number, ...updateData } = profileData;
    
    // Get token
    const token = localStorage.getItem('access_token') || 
                 localStorage.getItem('session_token');
    
    // Send request
    const response = await fetch('/api/v1/settings/update-profile', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updateData)
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Update UI with new profile data
      updateProfileDisplay(data.data);
      showNotification('Profile updated successfully');
    } else {
      throw new Error(data.error?.message || 'Failed to update profile');
    }
  } catch (error) {
    console.error('Error updating profile:', error);
    showError(error.message);
  }
}
```

---

### Profile Accessibility

**Endpoint:** `POST /{MODE}/settings/profile-accessibility`

**Description:** Update user profile accessibility setting (public, private, friends).

**Authentication:** Required (access_token or session_token)

**Required Permission:** `edit_profile`

**Request Body:**
```json
{
  "profile_accessibility": "public"
}
```

**Valid Values:**
- `"public"`: Profile visible to everyone
- `"private"`: Profile visible only to user
- `"friends"`: Profile visible only to friends

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "Profile accessibility update successfully",
  "data": {
    "user_id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
    "profile_accessibility": "public",
    "last_updated": "2025-01-28T15:51:55Z"
  }
}
```

---

### Profile Language

**Endpoint:** `POST /{MODE}/settings/profile-language`

**Description:** Update user's preferred language setting.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `edit_profile`

**Request Body:**
```json
{
  "language": "en"
}
```

**Valid Values:**
- `"en"`: English
- `"es"`: Spanish
- `"fr"`: French
- (Other language codes as supported)

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "Profile language update successfully",
  "data": {
    "user_id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
    "language": "en",
    "last_updated": "2025-01-28T15:51:55Z"
  }
}
```

---

### Change Email

**Endpoint:** `POST /{MODE}/settings/change-email`

**Description:** Change user's email address. Requires OTP verification sent to the new email address.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `edit_profile`

**Prerequisites:**
1. User must first request OTP to new email via `/auth/send-otp` endpoint
2. OTP must be sent to the new email address (channel: "email")

**Request Body:**
```json
{
  "new_email": "newemail@example.com",
  "otp": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "Email updated and verified successfully",
  "data": {
    "message": "Email updated and verified successfully",
    "user": {
      "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
      "email": "newemail@example.com",
      "is_email_verified": true,
      "email_verified_at": "2025-01-28T15:51:55Z"
    }
  }
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User initiates email change
  ├─► User enters new email address
  ├─► User clicks "Send OTP" button
  └─► Client validates email format

Step 2: Request OTP to new email
  POST /{MODE}/auth/send-otp
  Body: {
    "user_id": "newemail@example.com",
    "channel": "email"
  }
  ├─► Server sends OTP to new email
  └─► Client shows "OTP sent" message

Step 3: User enters OTP
  ├─► User receives OTP via email
  ├─► User enters OTP in form
  └─► User clicks "Change Email" button

Step 4: Client sends change email request
  POST /{MODE}/settings/change-email
  Headers:
    Authorization: Bearer <token>
  Body: {
    "new_email": "newemail@example.com",
    "otp": "123456"
  }

Step 5: Client receives response
  ├─► Success (200): Update UI, show success message
  ├─► Bad Request (400): Show error (invalid OTP, email exists)
  ├─► Unauthorized (401): Redirect to login
  └─► Error (500): Show error message

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token
  ├─► Extract current user from token
  ├─► Parse request body
  └─► Check permission: "edit_profile"

Step 2: OTP verification
  ├─► Verify OTP for new_email (delete_after_verify=False)
  ├─► If invalid: Return 400 with "PROFILE_INVALID_OTP"
  └─► OTP must be sent to new_email (not old email)

Step 3: Email uniqueness check
  ├─► Check if new_email already exists for another user
  ├─► If exists: Return 400 with "EMAIL_ALREADY_EXISTS"
  └─► Allow same email if it's the current user

Step 4: Database update
  ├─► Update user.email = new_email
  ├─► Set is_email_verified = TRUE
  ├─► Set email_verified_at = NOW()
  ├─► Update last_updated = NOW()
  └─► Verify update succeeded

Step 5: Cleanup
  ├─► Delete OTP from cache (delete_after_verify=True)
  └─► Prepare response with updated user data

Step 6: Response preparation
  ├─► Build success response
  ├─► Include updated email and verification status
  └─► Return SUCCESS response

Step 7: Error handling
  ├─► Invalid OTP: Return 400
  ├─► Email exists: Return 400
  ├─► Update failed: Return 500
  └─► Permission denied: Return 403
```

**Important Notes:**
- OTP must be sent to the **new email address**, not the old one
- Email change automatically verifies the new email (`is_email_verified = true`)
- Old email is replaced; user cannot revert without going through the process again

---

### Change Phone

**Endpoint:** `POST /{MODE}/settings/change-phone`

**Description:** Change user's phone number. Requires OTP verification sent to the new phone number.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `edit_profile`

**Prerequisites:**
1. User must first request OTP to new phone via `/settings/send-phone-otp` endpoint
2. OTP must be sent to the new phone number (channel: "sms" or "whatsapp")

**Request Body:**
```json
{
  "new_phone": "+1234567890",
  "otp": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "Phone number updated and verified successfully",
  "data": {
    "user": {
      "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
      "phone_number": {
        "phone": "1234567890"
      },
      "is_phone_verified": true,
      "phone_number_verified_at": "2025-01-28T15:51:55Z"
    }
  }
}
```

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User initiates phone change
  ├─► User enters new phone number
  ├─► User selects channel (SMS or WhatsApp)
  ├─► User clicks "Send OTP" button
  └─► Client validates phone format

Step 2: Request OTP to new phone
  POST /{MODE}/settings/send-phone-otp?phone=+1234567890&channel=sms
  Headers:
    Authorization: Bearer <token>
  ├─► Server sends OTP to new phone
  └─► Client shows "OTP sent" message

Step 3: User enters OTP
  ├─► User receives OTP via SMS/WhatsApp
  ├─► User enters OTP in form
  └─► User clicks "Change Phone" button

Step 4: Client sends change phone request
  POST /{MODE}/settings/change-phone
  Headers:
    Authorization: Bearer <token>
  Body: {
    "new_phone": "+1234567890",
    "otp": "123456"
  }

Step 5: Client receives response
  ├─► Success (200): Update UI, show success message
  ├─► Bad Request (400): Show error (invalid OTP, phone exists, invalid format)
  ├─► Unauthorized (401): Redirect to login
  └─► Error (500): Show error message

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token
  ├─► Extract current user from token
  ├─► Parse request body
  ├─► Validate phone format (E.164 format)
  └─► Check permission: "edit_profile"

Step 2: OTP verification
  ├─► Verify OTP for new_phone (delete_after_verify=False)
  ├─► If invalid: Return 400 with "PROFILE_INVALID_OTP"
  └─► OTP must be sent to new_phone (not old phone)

Step 3: Phone uniqueness check
  ├─► Clean phone number (remove +)
  ├─► Check if phone already exists for another user
  ├─► Query: phone_number->>'phone' = cleaned_phone
  ├─► If exists: Return 400 with "EMAIL_ALREADY_EXISTS" (reused error code)
  └─► Allow same phone if it's the current user

Step 4: Database update
  ├─► Format phone as JSON: {"phone": cleaned_phone}
  ├─► Update user.phone_number = JSONB
  ├─► Set is_phone_verified = TRUE
  ├─► Set phone_number_verified_at = NOW()
  ├─► Update last_updated = NOW()
  └─► Verify update succeeded

Step 5: Cleanup
  ├─► Delete OTP from cache (delete_after_verify=True)
  └─► Prepare response with updated user data

Step 6: Response preparation
  ├─► Build success response
  ├─► Include updated phone_number and verification status
  └─► Return SUCCESS response

Step 7: Error handling
  ├─► Invalid phone format: Return 400
  ├─► Invalid OTP: Return 400
  ├─► Phone exists: Return 400
  ├─► Update failed: Return 500
  └─► Permission denied: Return 403
```

**Phone Format:**
- Must be in E.164 format: `+[country code][number]`
- Example: `+1234567890`, `+441234567890`
- The `+` sign is optional but recommended

---

### Send Phone OTP

**Endpoint:** `POST /{MODE}/settings/send-phone-otp`

**Description:** Send OTP to a phone number via SMS or WhatsApp. Used for phone number verification during phone change.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `edit_profile`

**Query Parameters:**
- `phone` (string, required): Phone number in E.164 format
- `channel` (string, required): Delivery channel - `"sms"` or `"whatsapp"`

**Request:**
```
POST /{MODE}/settings/send-phone-otp?phone=+1234567890&channel=sms
```

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
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

Step 1: User enters phone number
  ├─► User enters new phone number
  ├─► User selects channel (SMS or WhatsApp)
  └─► Client validates phone format

Step 2: Client sends request
  POST /{MODE}/settings/send-phone-otp?phone=+1234567890&channel=sms
  Headers:
    Authorization: Bearer <token>

Step 3: Client receives response
  ├─► Success (200): Show "OTP sent" message, enable OTP input
  ├─► Bad Request (400): Show validation error
  ├─► Unauthorized (401): Redirect to login
  └─► Error (500): Show error message

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token
  ├─► Extract query parameters (phone, channel)
  ├─► Validate phone format (E.164)
  ├─► Validate channel (sms or whatsapp)
  └─► Check permission: "edit_profile"

Step 2: Generate and store OTP
  ├─► Generate 6-digit OTP
  ├─► Store OTP in cache with TTL (600 seconds = 10 minutes)
  ├─► Key: phone number
  └─► Value: OTP code

Step 3: Send OTP
  ├─► If channel = "sms": Send SMS via SMS service
  ├─► If channel = "whatsapp": Send WhatsApp message
  └─► Message includes OTP code

Step 4: Response preparation
  ├─► Build success response
  └─► Return SUCCESS response

Step 5: Error handling
  ├─► Invalid phone format: Return 400
  ├─► Invalid channel: Return 400
  ├─► OTP generation failed: Return 500
  ├─► SMS/WhatsApp send failed: Return 500
  └─► Permission denied: Return 403
```

---

### Update Theme

**Endpoint:** `POST /{MODE}/settings/update-theme`

**Description:** Update user's theme preference (light or dark).

**Authentication:** Required (access_token or session_token)

**Required Permission:** `edit_profile`

**Query Parameters:**
- `theme` (string, required): Theme value - `"light"` or `"dark"`

**Request:**
```
POST /{MODE}/settings/update-theme?theme=dark
```

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "Theme updated successfully",
  "data": {
    "user_id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
    "theme": "dark",
    "last_updated": "2025-01-28T15:51:55Z"
  }
}
```

---

### Update Timezone

**Endpoint:** `POST /{MODE}/settings/update-timezone`

**Description:** Update user's timezone preference.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `edit_profile`

**Query Parameters:**
- `timezone` (string, required): Timezone identifier (e.g., `"America/New_York"`, `"Europe/London"`)

**Request:**
```
POST /{MODE}/settings/update-timezone?timezone=America/New_York
```

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "Timezone updated successfully",
  "data": {
    "user_id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
    "timezone": "America/New_York",
    "last_updated": "2025-01-28T15:51:55Z"
  }
}
```

---

### Get Settings

**Endpoint:** `GET /{MODE}/settings/get-settings`

**Description:** Get user settings including theme, language, timezone, verification status, and account status.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `view_profile`

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "User settings retrieved successfully",
  "data": {
    "user_id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
    "theme": "light",
    "language": "en",
    "profile_accessibility": "public",
    "timezone": "America/New_York",
    "country": "US",
    "bio": "Software developer",
    "is_email_verified": true,
    "is_phone_verified": true,
    "is_active": true,
    "is_verified": true,
    "status": "ACTIVE"
  }
}
```

---

### Deactivate Account

**Endpoint:** `POST /{MODE}/settings/deactivate-account`

**Description:** Deactivate user account. Sets `is_active = false` and `status = 'INACTIVE'`. Account data is preserved.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `edit_profile`

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "Account deactivated successfully",
  "data": {
    "user_id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
    "is_active": false,
    "status": "INACTIVE"
  }
}
```

**Note:** Deactivated accounts cannot log in. To reactivate, contact support or use account recovery process.

---

### Delete Account

**Endpoint:** `POST /{MODE}/settings/delete-account`

**Description:** Delete user account. Requires confirmation. Sets `is_active = false` and `status = 'INACTIVE'`. Account data is preserved (soft delete).

**Authentication:** Required (access_token or session_token)

**Required Permission:** `edit_profile`

**Query Parameters:**
- `confirm` (boolean, required): Must be `true` to confirm deletion

**Request:**
```
POST /{MODE}/settings/delete-account?confirm=true
```

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
  "message": "Account deactivated successfully",
  "data": {
    "user_id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd",
    "is_active": false
  }
}
```

**Note:** 
- Currently performs soft delete (same as deactivate)
- Account data is preserved in database
- User cannot log in after deletion
- For permanent deletion, contact support

---

## User Model

The User model contains all user profile information:

```typescript
interface User {
  // Primary identifier
  user_id: string;
  
  // Basic information
  first_name?: string;
  last_name?: string;
  email?: string;
  phone_number?: {
    phone: string;
  };
  country?: string;
  gender?: string;
  dob?: string; // ISO 8601 datetime
  profile_picture_url?: string;
  bio?: string;
  portfolio_url?: string;
  user_name?: string;
  
  // Preferences
  theme?: "light" | "dark";
  language?: string; // Language code (en, es, fr, etc.)
  profile_accessibility?: "public" | "private" | "friends";
  timezone?: string; // IANA timezone (America/New_York, etc.)
  
  // Verification status
  is_email_verified?: boolean;
  is_phone_verified?: boolean;
  email_verified_at?: string; // ISO 8601 datetime
  phone_number_verified_at?: string; // ISO 8601 datetime
  
  // Account status
  is_active?: boolean;
  is_verified?: boolean;
  status?: "ACTIVE" | "INACTIVE" | "SUSPENDED" | "DELETED";
  
  // Timestamps
  created_at?: string; // ISO 8601 datetime
  last_updated?: string; // ISO 8601 datetime
  last_sign_in_at?: string; // ISO 8601 datetime
}
```

---

## Workflows

### Complete Profile Update Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROFILE UPDATE WORKFLOW                      │
└─────────────────────────────────────────────────────────────────┘

Step 1: User Authentication
  ├─► User logs in (via /auth/login-with-password or /auth/login-with-otp)
  ├─► Client receives tokens (access_token, session_token, refresh_token)
  └─► Client stores tokens securely

Step 2: View Profile
  ├─► Client requests profile: GET /{MODE}/settings/profile
  ├─► Server validates token and permissions
  ├─► Server returns user profile data
  └─► Client displays profile in UI

Step 3: Update Profile Information
  ├─► User edits profile fields (name, bio, country, etc.)
  ├─► Client validates form data
  ├─► Client sends: POST /{MODE}/settings/update-profile
  ├─► Server validates token, permissions, and data
  ├─► Server updates database
  └─► Server returns updated profile

Step 4: Update Profile Picture
  ├─► User selects new profile picture
  ├─► Client validates image file
  ├─► Client sends: POST /{MODE}/settings/update-profile-picture (multipart/form-data)
  ├─► Server uploads to Google Cloud Storage
  ├─► Server updates database with new URL
  └─► Server returns new profile_picture_url

Step 5: Change Email (if needed)
  ├─► User enters new email
  ├─► Client requests OTP: POST /{MODE}/auth/send-otp (to new email)
  ├─► User receives OTP via email
  ├─► User enters OTP
  ├─► Client sends: POST /{MODE}/settings/change-email
  ├─► Server verifies OTP and updates email
  └─► Server returns updated user data

Step 6: Change Phone (if needed)
  ├─► User enters new phone
  ├─► Client requests OTP: POST /{MODE}/settings/send-phone-otp
  ├─► User receives OTP via SMS/WhatsApp
  ├─► User enters OTP
  ├─► Client sends: POST /{MODE}/settings/change-phone
  ├─► Server verifies OTP and updates phone
  └─► Server returns updated user data

Step 7: Update Settings
  ├─► User updates theme: POST /{MODE}/settings/update-theme
  ├─► User updates language: POST /{MODE}/settings/profile-language
  ├─► User updates timezone: POST /{MODE}/settings/update-timezone
  ├─► User updates accessibility: POST /{MODE}/settings/profile-accessibility
  └─► Each update returns updated user data
```

### Profile Picture Upload Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              PROFILE PICTURE UPLOAD WORKFLOW                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   CLIENT     │
└──────┬───────┘
       │
       │ 1. User selects image file
       ▼
┌──────────────┐
│   CLIENT     │
│  Validation  │
└──────┬───────┘
       │
       │ 2. Validate file (type, size)
       ▼
┌──────────────┐
│   CLIENT     │
│  FormData    │
└──────┬───────┘
       │
       │ 3. Create FormData with file
       │    Add Authorization header
       ▼
┌──────────────┐
│   SERVER     │
│  Validation  │
└──────┬───────┘
       │
       │ 4. Validate token & permission
       │    Read file data
       ▼
┌──────────────┐
│   SERVER     │
│  Generate    │
│  Object Key  │
└──────┬───────┘
       │
       │ 5. Generate: {username}-user_id_{id}-|-{uuid}.{ext}
       ▼
┌──────────────┐
│   SERVER     │
│  Google      │
│  Cloud       │
│  Storage     │
└──────┬───────┘
       │
       │ 6. Upload to "media/users" folder
       │    Set public access
       ▼
┌──────────────┐
│   SERVER     │
│  Database    │
└──────┬───────┘
       │
       │ 7. Update profile_picture_url
       │    Update last_updated
       ▼
┌──────────────┐
│   SERVER     │
│  Response    │
└──────┬───────┘
       │
       │ 8. Return profile_picture_url
       ▼
┌──────────────┐
│   CLIENT     │
│  Update UI   │
└──────────────┘
```

---

## Error Handling

All profile endpoints return standardized error responses:

### Error Response Format

```json
{
  "success": false,
  "id": null,
  "message": "Error message",
  "error": {
    "code": "ERROR_CODE",
    "details": {
      "field": "value",
      "user_id": "a2cfa5fc-5963-4a53-a0a8-6d2d250af8fd"
    }
  },
  "timestamp": "2025-01-28T15:51:55.980680Z"
}
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `PROFILE_NOT_FOUND` | 404 | User profile not found |
| `PROFILE_INVALID_PAYLOAD` | 400 | Invalid request data |
| `PROFILE_UPDATE_FAILED` | 500 | Profile update operation failed |
| `PROFILE_PICTURE_UPDATE_FAILED` | 500 | Profile picture upload failed |
| `PROFILE_INVALID_OTP` | 400 | Invalid or expired OTP |
| `EMAIL_ALREADY_EXISTS` | 400 | Email already registered to another user |
| `PERMISSION_DENIED` | 403 | User lacks required permission |
| `UNAUTHORIZED` | 401 | Invalid or missing authentication token |
| `PROFILE_PROCESSING_ERROR` | 500 | Internal server error processing profile request |

### Error Handling Best Practices

1. **Client-Side:**
   - Always check `response.success` before processing data
   - Display user-friendly error messages
   - Handle 401 errors by redirecting to login
   - Handle 403 errors by showing permission denied message
   - Log errors for debugging

2. **Server-Side:**
   - All errors are logged with context
   - Sensitive information is not exposed in error messages
   - Errors include user_id for tracking
   - Database errors are caught and returned as 500

---

## Best Practices

### Profile Management

1. **Partial Updates:**
   - Only send fields that need to be updated
   - Don't send protected fields (user_id, email, phone)
   - Use appropriate endpoints for email/phone changes

2. **Profile Picture:**
   - Validate file size (recommended: < 5MB)
   - Validate file type (jpg, png, gif, webp)
   - Show loading state during upload
   - Handle upload failures gracefully

3. **Email/Phone Changes:**
   - Always request OTP first
   - Verify OTP before allowing change
   - Show clear instructions to user
   - Handle OTP expiration (10 minutes)

4. **Token Management:**
   - Use session_token for API calls (recommended)
   - Store tokens securely (httpOnly cookies or secure storage)
   - Handle token expiration with refresh flow
   - Include tokens in all authenticated requests

5. **Permissions:**
   - Check user permissions before showing edit buttons
   - Handle permission errors gracefully
   - Request appropriate permissions from admin if needed

### Security

1. **Authentication:**
   - Always include tokens in request headers
   - Use HTTPS for all API calls
   - Don't expose tokens in URLs or logs

2. **Data Validation:**
   - Validate all user input on client side
   - Server validates all inputs (don't trust client)
   - Sanitize user-generated content (bio, etc.)

3. **File Uploads:**
   - Validate file types and sizes
   - Scan files for malware (if applicable)
   - Store files in secure, isolated storage

---

## Client-Side Implementation

### Token Management

```javascript
// Store tokens after login
function storeTokens(tokens) {
  localStorage.setItem('access_token', tokens.access_token);
  localStorage.setItem('session_token', tokens.session_token);
  localStorage.setItem('refresh_token', tokens.refresh_token);
  localStorage.setItem('session_id', tokens.session_id);
}

// Get token for API calls (prefer session_token)
function getAuthToken() {
  return localStorage.getItem('session_token') || 
         localStorage.getItem('access_token');
}

// API request helper
async function apiRequest(url, options = {}) {
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
    // Token expired, try refresh
    await refreshTokens();
    // Retry request
    return apiRequest(url, options);
  }
  
  return response.json();
}
```

### Profile Update Example

```javascript
// Update Profile
async function updateProfile(profileData) {
  try {
    // Remove protected fields
    const { user_id, email, phone_number, ...updateData } = profileData;
    
    const response = await apiRequest('/api/v1/settings/update-profile', {
      method: 'POST',
      body: JSON.stringify(updateData)
    });
    
    if (response.success) {
      // Update UI
      updateProfileDisplay(response.data);
      showNotification('Profile updated successfully');
      return response.data;
    } else {
      throw new Error(response.error?.message || 'Failed to update profile');
    }
  } catch (error) {
    console.error('Error updating profile:', error);
    showError(error.message);
    throw error;
  }
}

// Update Profile Picture
async function updateProfilePicture(file) {
  try {
    // Validate file
    if (!file || !file.type.startsWith('image/')) {
      throw new Error('Please select a valid image file');
    }
    
    if (file.size > 5 * 1024 * 1024) {
      throw new Error('Image size must be less than 5MB');
    }
    
    // Create FormData
    const formData = new FormData();
    formData.append('file', file);
    
    const token = getAuthToken();
    
    const response = await fetch('/api/v1/settings/update-profile-picture', {
      method: 'POST',
      headers: {
        'X-Session-Token': token
      },
      body: formData
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Update UI
      document.getElementById('profile-picture').src = data.data.profile_picture_url;
      showNotification('Profile picture updated successfully');
      return data.data;
    } else {
      throw new Error(data.error?.message || 'Failed to update profile picture');
    }
  } catch (error) {
    console.error('Error updating profile picture:', error);
    showError(error.message);
    throw error;
  }
}

// Change Email
async function changeEmail(newEmail, otp) {
  try {
    // First, request OTP to new email
    await requestOTP(newEmail, 'email');
    
    // Then, change email with OTP
    const response = await apiRequest('/api/v1/settings/change-email', {
      method: 'POST',
      body: JSON.stringify({
        new_email: newEmail,
        otp: otp
      })
    });
    
    if (response.success) {
      showNotification('Email updated successfully');
      return response.data;
    } else {
      throw new Error(response.error?.message || 'Failed to change email');
    }
  } catch (error) {
    console.error('Error changing email:', error);
    showError(error.message);
    throw error;
  }
}

// Change Phone
async function changePhone(newPhone, otp, channel = 'sms') {
  try {
    // First, request OTP to new phone
    const token = getAuthToken();
    const otpResponse = await fetch(
      `/api/v1/settings/send-phone-otp?phone=${encodeURIComponent(newPhone)}&channel=${channel}`,
      {
        method: 'POST',
        headers: {
          'X-Session-Token': token
        }
      }
    );
    
    const otpData = await otpResponse.json();
    if (!otpData.success) {
      throw new Error('Failed to send OTP');
    }
    
    // Then, change phone with OTP
    const response = await apiRequest('/api/v1/settings/change-phone', {
      method: 'POST',
      body: JSON.stringify({
        new_phone: newPhone,
        otp: otp
      })
    });
    
    if (response.success) {
      showNotification('Phone number updated successfully');
      return response.data;
    } else {
      throw new Error(response.error?.message || 'Failed to change phone');
    }
  } catch (error) {
    console.error('Error changing phone:', error);
    showError(error.message);
    throw error;
  }
}

// Get Profile
async function getProfile() {
  try {
    const response = await apiRequest('/api/v1/settings/profile', {
      method: 'GET'
    });
    
    if (response.success) {
      return response.data;
    } else {
      throw new Error(response.error?.message || 'Failed to fetch profile');
    }
  } catch (error) {
    console.error('Error fetching profile:', error);
    showError(error.message);
    throw error;
  }
}

// Update Theme
async function updateTheme(theme) {
  try {
    if (!['light', 'dark'].includes(theme)) {
      throw new Error('Theme must be "light" or "dark"');
    }
    
    const token = getAuthToken();
    const response = await fetch(
      `/api/v1/settings/update-theme?theme=${theme}`,
      {
        method: 'POST',
        headers: {
          'X-Session-Token': token
        }
      }
    );
    
    const data = await response.json();
    
    if (data.success) {
      showNotification('Theme updated successfully');
      // Apply theme to UI
      document.documentElement.setAttribute('data-theme', theme);
      return data.data;
    } else {
      throw new Error(data.error?.message || 'Failed to update theme');
    }
  } catch (error) {
    console.error('Error updating theme:', error);
    showError(error.message);
    throw error;
  }
}

// Update Timezone
async function updateTimezone(timezone) {
  try {
    const token = getAuthToken();
    const response = await fetch(
      `/api/v1/settings/update-timezone?timezone=${encodeURIComponent(timezone)}`,
      {
        method: 'POST',
        headers: {
          'X-Session-Token': token
        }
      }
    );
    
    const data = await response.json();
    
    if (data.success) {
      showNotification('Timezone updated successfully');
      return data.data;
    } else {
      throw new Error(data.error?.message || 'Failed to update timezone');
    }
  } catch (error) {
    console.error('Error updating timezone:', error);
    showError(error.message);
    throw error;
  }
}

// Deactivate Account
async function deactivateAccount() {
  try {
    const confirmed = confirm('Are you sure you want to deactivate your account?');
    if (!confirmed) {
      return;
    }
    
    const response = await apiRequest('/api/v1/settings/deactivate-account', {
      method: 'POST'
    });
    
    if (response.success) {
      showNotification('Account deactivated successfully');
      // Redirect to login or home page
      window.location.href = '/login';
      return response.data;
    } else {
      throw new Error(response.error?.message || 'Failed to deactivate account');
    }
  } catch (error) {
    console.error('Error deactivating account:', error);
    showError(error.message);
    throw error;
  }
}

// Delete Account
async function deleteAccount() {
  try {
    const confirmed = confirm(
      'Are you sure you want to delete your account? This action cannot be undone.'
    );
    if (!confirmed) {
      return;
    }
    
    const token = getAuthToken();
    const response = await fetch(
      '/api/v1/settings/delete-account?confirm=true',
      {
        method: 'POST',
        headers: {
          'X-Session-Token': token
        }
      }
    );
    
    const data = await response.json();
    
    if (data.success) {
      showNotification('Account deleted successfully');
      // Redirect to login or home page
      window.location.href = '/login';
      return data.data;
    } else {
      throw new Error(data.error?.message || 'Failed to delete account');
    }
  } catch (error) {
    console.error('Error deleting account:', error);
    showError(error.message);
    throw error;
  }
}
```

### Complete Profile Management Example

```javascript
// Complete Profile Management Component
class ProfileManager {
  constructor() {
    this.profile = null;
    this.token = null;
  }
  
  async init() {
    // Load profile on initialization
    this.token = getAuthToken();
    if (this.token) {
      await this.loadProfile();
    }
  }
  
  async loadProfile() {
    try {
      this.profile = await getProfile();
      this.renderProfile();
      return this.profile;
    } catch (error) {
      console.error('Failed to load profile:', error);
      return null;
    }
  }
  
  renderProfile() {
    if (!this.profile) return;
    
    // Update UI elements
    document.getElementById('profile-name').textContent = 
      `${this.profile.first_name || ''} ${this.profile.last_name || ''}`.trim();
    document.getElementById('profile-email').textContent = this.profile.email || '';
    document.getElementById('profile-bio').textContent = this.profile.bio || '';
    
    if (this.profile.profile_picture_url) {
      document.getElementById('profile-picture').src = this.profile.profile_picture_url;
    }
    
    // Update theme
    if (this.profile.theme) {
      document.documentElement.setAttribute('data-theme', this.profile.theme);
    }
  }
  
  async updateProfile(data) {
    try {
      this.profile = await updateProfile(data);
      this.renderProfile();
      return this.profile;
    } catch (error) {
      console.error('Failed to update profile:', error);
      throw error;
    }
  }
  
  async updatePicture(file) {
    try {
      const result = await updateProfilePicture(file);
      this.profile.profile_picture_url = result.profile_picture_url;
      this.renderProfile();
      return result;
    } catch (error) {
      console.error('Failed to update picture:', error);
      throw error;
    }
  }
}

// Initialize profile manager
const profileManager = new ProfileManager();
profileManager.init();
```

---

## Summary

This documentation provides comprehensive coverage of all profile management endpoints:

### Endpoints Covered:
1. ✅ **Get User Profile** - View own profile
2. ✅ **Get User Profile by ID** - View other users' profiles
3. ✅ **Update Profile Picture** - Upload and update profile picture
4. ✅ **Update Profile** - Partial profile updates
5. ✅ **Profile Accessibility** - Update profile visibility
6. ✅ **Profile Language** - Update language preference
7. ✅ **Change Email** - Change email with OTP verification
8. ✅ **Change Phone** - Change phone with OTP verification
9. ✅ **Send Phone OTP** - Request OTP for phone verification
10. ✅ **Update Theme** - Update theme preference
11. ✅ **Update Timezone** - Update timezone preference
12. ✅ **Get Settings** - Get all user settings
13. ✅ **Deactivate Account** - Deactivate user account
14. ✅ **Delete Account** - Delete user account (soft delete)

### Documentation Sections:
- ✅ Overview and system architecture
- ✅ Detailed endpoint documentation with examples
- ✅ Client-server communication flows
- ✅ Complete workflows and diagrams
- ✅ Error handling guide
- ✅ Best practices
- ✅ Complete client-side implementation examples
- ✅ User model reference

### Key Features:
- **Permission-based access control** - All endpoints require appropriate permissions
- **OTP verification** - Email and phone changes require OTP verification
- **Partial updates** - Only send fields that need updating
- **File uploads** - Profile pictures uploaded to Google Cloud Storage
- **Comprehensive error handling** - Standardized error responses
- **Client-side examples** - Ready-to-use JavaScript code

All endpoints are fully documented with request/response examples, client-server communication flows, and implementation guidance.