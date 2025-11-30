# File Upload Router

> **Complete Documentation for Media File Upload and Management Endpoints**

This router handles file upload operations including uploading files from URLs or direct file uploads to Google Cloud Storage, and deleting uploaded files.

## 📋 Table of Contents

- [Overview](#overview)
- [Endpoints](#endpoints)
  - [Upload Media](#upload-media)
  - [Delete Media](#delete-media)
- [Workflows](#workflows)
- [Error Handling](#error-handling)
- [Client-Side Implementation](#client-side-implementation)
- [Summary](#summary)

## Overview

The File Upload router provides comprehensive media file management functionality including:
- **File Upload**: Upload files directly or from URLs to Google Cloud Storage
- **File Deletion**: Delete files from Google Cloud Storage
- **Multiple Formats**: Support for images, documents, videos, and other file types
- **Size Limits**: 15MB maximum file size
- **Automatic Processing**: Automatic file type detection and content type handling

**Base Path:** `/{MODE}/upload-media`, `/{MODE}/delete-media`

**Authentication:** All endpoints require authentication

**Permissions:** 
- Upload: `add_upload` permission
- Delete: `delete_upload` permission

## Endpoints

### Upload Media

**Endpoint:** `POST /{MODE}/upload-media`

**Description:** Upload a media file either from URL or direct file upload to Google Cloud Storage.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `add_upload`

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data (for file upload)
# OR
Content-Type: application/x-www-form-urlencoded (for URL upload)
# OR
X-Session-Token: <session_token>
```

**Request Options:**

**Option 1: Direct File Upload (Multipart Form Data)**
```http
POST /dev/v1/upload-media HTTP/1.1
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: [binary file data]
```

**Option 2: Upload from URL (Form Data)**
```http
POST /dev/v1/upload-media HTTP/1.1
Authorization: Bearer <token>
Content-Type: application/x-www-form-urlencoded

url: https://example.com/image.jpg
```

**Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "data": {
    "url": "https://storage.googleapis.com/bucket-name/media/users/user-uuid-file.jpg"
  }
}
```

**Workflow (Direct File Upload):**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (add_upload)
   │
   ├─► Validate Request
   │   └─► Check file or url exists
   │
   ├─► Process File Upload
   │   ├─► Extract file buffer
   │   ├─► Get file extension from filename
   │   └─► Get content type from mimetype
   │
   ├─► Generate Object Key
   │   └─► {userId}-|-{uuid}.{extension}
   │
   ├─► Upload to Google Cloud Storage
   │   ├─► Folder: media/users
   │   ├─► Object Key: generated key
   │   └─► uploadToGoogleStorageFromString()
   │
   └─► Return Public URL
```

**Workflow (Upload from URL):**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (add_upload)
   │
   ├─► Validate Request
   │   └─► Check url exists
   │
   ├─► Download File from URL
   │   ├─► axios.get(url, { responseType: 'arraybuffer' })
   │   ├─► Max size: 15MB
   │   └─► Convert to Buffer
   │
   ├─► Extract File Information
   │   ├─► Extension from URL or Content-Type header
   │   └─► Content type from response headers
   │
   ├─► Generate Object Key
   │   └─► {userId}-|-{uuid}.{extension}
   │
   ├─► Upload to Google Cloud Storage
   │   └─► uploadToGoogleStorageFromString()
   │
   └─► Return Public URL
```

**Supported File Types:**
- Images: jpg, jpeg, png, gif, webp, svg
- Documents: pdf, doc, docx, txt
- Videos: mp4, avi, mov, webm
- Other: Based on content type

**File Size Limit:** 15MB maximum

**Storage Location:**
- Folder: `media/users`
- Object Key Format: `{userId}-|-{uuid}.{extension}`
- Public URL: `https://storage.googleapis.com/{bucket-name}/media/users/{object-key}`

**Client-Server Communication Flow (Direct File Upload):**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User selects file
  ├─► User clicks "Choose File" button
  ├─► File picker opens
  └─► User selects file (image, document, video, etc.)

Step 2: Client validates file
  ├─► Check file size (must be < 15MB)
  ├─► Check file type (optional validation)
  ├─► Optionally: Preview file before upload
  └─► Show upload progress indicator

Step 3: Client prepares request
  ├─► Create FormData object
  ├─► Append file to FormData with key "file"
  ├─► Retrieve stored access_token or session_token
  └─► Prepare POST request with multipart/form-data

Step 4: Client sends request
  POST /{MODE}/upload-media
  Headers:
    Authorization: Bearer <token>
    Content-Type: multipart/form-data
  Body:
    file: <File object>

Step 5: Client receives response
  ├─► Success (200): Display uploaded file URL, show success message
  ├─► Bad Request (400): Show validation error
  ├─► Unauthorized (401): Redirect to login
  ├─► Forbidden (403): Show permission error
  ├─► Payload Too Large (413): Show file size error
  └─► Error (500): Show error message

Step 6: Client processes response
  ├─► Extract public URL from response.data.url
  ├─► Store URL for later use
  ├─► Display uploaded file (if image, show preview)
  └─► Update UI with uploaded file information

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token (JWT verification)
  ├─► Check token blacklist
  ├─► Extract user from token
  ├─► Check permission: "add_upload"
  └─► Validate request has either file or url

Step 2: File processing (if file provided)
  ├─► Read file data from request
  ├─► Extract file extension from filename
  ├─► Get content type from file.content_type
  └─► Generate unique object key: {userId}-|-{uuid}.{extension}

Step 3: URL processing (if url provided)
  ├─► Download file from URL using httpx
  ├─► Check response status (raise_for_status)
  ├─► Get file data from response.content
  ├─► Extract extension from URL or Content-Type header
  ├─► Get content type from response headers
  └─► Generate unique object key: {userId}-|-{uuid}.{extension}

Step 4: Upload to Google Cloud Storage
  ├─► Set folder: "media/users"
  ├─► Upload file using upload_to_google_storage_from_string()
  ├─► Set content type
  ├─► Make file publicly accessible
  └─► Get public URL

Step 5: Response preparation
  ├─► Build SUCCESS response
  ├─► Include public URL in data.url
  └─► Return response with user's language preference

Step 6: Error handling
  ├─► No file or URL: Return 400
  ├─► File too large: Return 413
  ├─► Download error: Return 500
  ├─► Upload error: Return 500
  ├─► Permission denied: Return 403
  └─► Token invalid: Return 401
```

**Client-Server Communication Flow (Upload from URL):**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User enters URL
  ├─► User enters file URL in input field
  ├─► User clicks "Upload from URL" button
  └─► Client validates URL format

Step 2: Client validates URL
  ├─► Check URL format (http:// or https://)
  ├─► Optionally: Preview file from URL
  └─► Show loading indicator

Step 3: Client sends request
  POST /{MODE}/upload-media
  Headers:
    Authorization: Bearer <token>
    Content-Type: application/x-www-form-urlencoded
  Body:
    url: https://example.com/image.jpg

Step 4: Client receives response
  ├─► Success (200): Display uploaded file URL
  ├─► Bad Request (400): Show validation error
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
  ├─► Check permission: "add_upload"
  └─► Validate url parameter exists

Step 2: Download file from URL
  ├─► Create httpx AsyncClient
  ├─► GET request to URL with responseType: 'arraybuffer'
  ├─► Check response status
  ├─► Get file data from response.content
  └─► Handle download errors

Step 3: Extract file information
  ├─► Get extension from URL (split by '.')
  ├─► If no extension, get from Content-Type header
  ├─► Get content type from response headers
  └─► Generate unique object key: {userId}-|-{uuid}.{extension}

Step 4: Upload to Google Cloud Storage
  ├─► Set folder: "media/users"
  ├─► Upload file using upload_to_google_storage_from_string()
  └─► Get public URL

Step 5: Response preparation
  ├─► Build SUCCESS response
  ├─► Include public URL in data.url
  └─► Return response

Step 6: Error handling
  ├─► Invalid URL: Return 400
  ├─► Download failed: Return 500
  ├─► Upload error: Return 500
  └─► Permission denied: Return 403
```

**Error Responses:**

```json
// 400 - No File or URL
{
  "success": false,
  "id": null,
  "message": "File or URL required",
  "error": {
    "code": "MEDIA_FILE_OR_URL",
    "details": {
      "user_id": "uuid",
      "message": "Either file or url must be provided"
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
      "required_permission": "add_upload"
    }
  }
}

// 500 - Upload Error
{
  "success": false,
  "id": null,
  "message": "Upload processing error",
  "error": {
    "code": "MEDIA_UPLOADING_PROCESSING_ERROR",
    "details": {
      "user_id": "uuid",
      "exception": "Error details"
    }
  }
}
```

---

### Delete Media

**Endpoint:** `DELETE /{MODE}/delete-media`

**Description:** Delete a media file from Google Cloud Storage.

**Authentication:** Required (access_token or session_token)

**Required Permission:** `delete_upload`

**Query Parameters:**
- `url` (required): GCS URL of the file to delete

**Request Headers:**
```
Authorization: Bearer <access_token>
# OR
X-Session-Token: <session_token>
```

**Request Example:**
```http
DELETE /dev/v1/delete-media?url=https://storage.googleapis.com/bucket-name/media/users/user-uuid-file.jpg HTTP/1.1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "File deleted successfully from bucket 'bucket-name'",
  "data": {
    "bucket": "bucket-name"
  }
}
```

**Workflow:**
```
1. Authenticated Request
   │
   ├─► Validate JWT Token
   │
   ├─► Check Permission (delete_upload)
   │
   ├─► Validate Request
   │   └─► Check url parameter exists
   │
   ├─► Validate Bucket Configuration
   │   └─► Check GOOGLE_STORAGE_BUCKET_NAME exists
   │
   ├─► Parse GCS URL
   │   ├─► Decode URL
   │   ├─► Validate domain (storage.googleapis.com)
   │   └─► Extract bucket and object path
   │
   ├─► Validate Bucket Match
   │   └─► Ensure URL bucket matches configured bucket
   │
   ├─► Extract Object Path
   │   ├─► Folder: media/users (or other)
   │   └─► Object Key: file name
   │
   ├─► Delete from Google Cloud Storage
   │   └─► deleteFromGoogleStorage(folder, objectKey)
   │
   └─► Return Success Response
```

**URL Format:**
```
https://storage.googleapis.com/{bucket-name}/{folder}/{object-key}
```

**Example:**
```
https://storage.googleapis.com/my-bucket/media/users/user-123-file.jpg
```

**Validation:**
- URL must be from `storage.googleapis.com`
- Bucket in URL must match configured bucket
- URL must have valid path structure

**Client-Server Communication Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: User initiates deletion
  ├─► User clicks "Delete" button on file
  ├─► Client shows confirmation dialog
  └─► User confirms deletion

Step 2: Client prepares request
  ├─► Get GCS URL of file to delete
  ├─► URL encode the URL parameter
  ├─► Retrieve stored access_token or session_token
  └─► Prepare DELETE request with query parameter

Step 3: Client sends request
  DELETE /{MODE}/delete-media?url={encoded_url}
  Headers:
    Authorization: Bearer <token>
    # OR
    X-Session-Token: <session_token>

Step 4: Client receives response
  ├─► Success (200): Remove file from UI, show success message
  ├─► Bad Request (400): Show validation error
  ├─► Unauthorized (401): Redirect to login
  ├─► Forbidden (403): Show permission/bucket error
  ├─► Not Found (404): Show file not found error
  └─► Error (500): Show error message

Step 5: Client processes response
  ├─► Remove file from display
  ├─► Update file list
  └─► Clear file URL from storage

┌─────────────────────────────────────────────────────────────────┐
│                    SERVER SIDE                                  │
└─────────────────────────────────────────────────────────────────┘

Step 1: Request validation
  ├─► Extract token from headers
  ├─► Validate token (JWT verification)
  ├─► Check token blacklist
  ├─► Extract user from token
  ├─► Extract url query parameter
  ├─► Check permission: "delete_upload"
  └─► Validate url parameter exists

Step 2: Validate bucket configuration
  ├─► Get GOOGLE_STORAGE_BUCKET_NAME from environment
  └─► If not configured: Return 500

Step 3: Parse and validate GCS URL
  ├─► Decode URL (unquote)
  ├─► Parse URL using urlparse
  ├─► Validate domain contains "storage.googleapis.com"
  ├─► Extract bucket and object path from URL
  ├─► Validate URL format (bucket/path structure)
  └─► Check if URL bucket matches configured bucket

Step 4: Validate bucket match
  ├─► Compare URL bucket with configured bucket
  └─► If mismatch: Return 403 Forbidden

Step 5: Check file existence
  ├─► Get blob from Google Cloud Storage
  ├─► Check if blob.exists()
  └─► If not exists: Return 404 Not Found

Step 6: Delete file
  ├─► Delete blob from Google Cloud Storage
  └─► Verify deletion succeeded

Step 7: Response preparation
  ├─► Build SUCCESS response
  ├─► Include bucket name in data.bucket
  └─► Return response with user's language preference

Step 8: Error handling
  ├─► No URL: Return 400
  ├─► Invalid URL format: Return 400
  ├─► Bucket mismatch: Return 403
  ├─► File not found: Return 404
  ├─► Delete error: Return 500
  ├─► Permission denied: Return 403
  └─► Token invalid: Return 401
```

**Error Responses:**

```json
// 400 - No URL Provided
{
  "success": false,
  "message": "No URL provided",
  "statusCode": 400
}

// 400 - Invalid GCS URL
{
  "success": false,
  "message": "Invalid GCS URL",
  "statusCode": 400
}

// 403 - Bucket Mismatch
{
  "success": false,
  "message": "URL bucket does not match configured bucket",
  "statusCode": 403
}

// 404 - File Not Found
{
  "success": false,
  "message": "File not found in GCS",
  "statusCode": 404
}

// 500 - Delete Error
{
  "success": false,
  "id": null,
  "message": "Delete processing error",
  "error": {
    "code": "MEDIA_DELETING_PROCESSING_ERROR",
    "details": {
      "user_id": "uuid",
      "exception": "Error details"
    }
  }
}
```

---

## Workflows

### Complete File Upload Flow

```
┌─────────────────────────────────────────────────────────────┐
│              File Upload Flow                               │
└────────────────────────────┬────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
        ┌───────────────┐         ┌───────────────┐
        │  Direct Upload │         │  Upload from │
        │   (Multipart)  │         │     URL      │
        └───────┬───────┘         └───────┬───────┘
                │                           │
                ▼                           ▼
        ┌───────────────┐         ┌───────────────┐
        │ Extract File  │         │ Download File │
        │   Buffer      │         │   from URL    │
        └───────┬───────┘         └───────┬───────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Get File Info   │
                    │ (ext, type)     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Generate Key    │
                    │ {userId}-uuid.ext│
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Upload to GCS   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Return Public   │
                    │      URL        │
                    └─────────────────┘
```

### File Deletion Flow

```
1. User Requests File Deletion
   │
   ├─► Validate Authentication
   │   └─► Check JWT token
   │
   ├─► Check Permission
   │   └─► delete_upload permission
   │
   ├─► Validate URL Parameter
   │   └─► URL must be provided
   │
   ├─► Parse GCS URL
   │   ├─► Decode URL
   │   ├─► Validate domain
   │   └─► Extract bucket and path
   │
   ├─► Validate Bucket
   │   └─► URL bucket must match config
   │
   ├─► Extract Object Path
   │   ├─► Folder name
   │   └─► Object key
   │
   ├─► Delete from GCS
   │   └─► deleteFromGoogleStorage()
   │
   └─► Return Success Response
```

## Error Handling

### Common Error Responses

**400 Bad Request - No File or URL:**
```json
{
  "success": false,
  "message": "File or URL required",
  "error": "Either file or url must be provided",
  "statusCode": 400
}
```

**400 Bad Request - Invalid URL:**
```json
{
  "success": false,
  "message": "Invalid URL",
  "error": "URL must be from storage.googleapis.com",
  "statusCode": 400
}
```

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
  "error": "Insufficient permissions. Requires add_upload permission",
  "statusCode": 403
}
```

**404 Not Found - File Not Found:**
```json
{
  "success": false,
  "message": "File not found",
  "error": "File not found in Google Cloud Storage",
  "statusCode": 404
}
```

**413 Payload Too Large:**
```json
{
  "success": false,
  "message": "File too large",
  "error": "File size exceeds 15MB limit",
  "statusCode": 413
}
```

**500 Internal Server Error - Download Error:**
```json
{
  "success": false,
  "message": "Download error",
  "error": "Failed to download file from URL",
  "statusCode": 500
}
```

**500 Internal Server Error - Upload Error:**
```json
{
  "success": false,
  "message": "Upload processing error",
  "error": "Failed to upload file to Google Cloud Storage",
  "statusCode": 500
}
```

---

## Best Practices

1. **File Size**: Always validate file size before upload (max 15MB)
2. **File Types**: Validate file types based on your application requirements
3. **Content Type**: Set appropriate content type for proper file handling
4. **URL Validation**: Validate URLs before downloading
5. **Error Handling**: Handle download and upload errors gracefully
6. **Security**: Only allow deletion of files from your configured bucket
7. **Object Keys**: Use unique object keys to prevent overwrites
8. **Cleanup**: Implement cleanup for failed uploads
9. **CORS**: Configure CORS on GCS bucket for web uploads
10. **Permissions**: Use IAM roles for GCS access, not service account keys in code

---

## Google Cloud Storage Configuration

**Required Environment Variables:**
- `GOOGLE_STORAGE_BUCKET_NAME`: Name of the GCS bucket

**Required Credentials:**
- Google Cloud Service Account JSON file
- Proper IAM permissions for bucket access

**Storage Structure:**
```
bucket-name/
  └── media/
      └── users/
          ├── user-123-uuid1.jpg
          ├── user-123-uuid2.png
          └── user-456-uuid3.pdf
```

**Public URL Format:**
```
https://storage.googleapis.com/{bucket-name}/media/users/{object-key}
```

---

## Security Considerations

1. **Authentication**: All endpoints require authentication
2. **Authorization**: Check permissions before allowing upload/delete
3. **Bucket Validation**: Ensure files are only deleted from your bucket
4. **URL Validation**: Validate URLs to prevent SSRF attacks
5. **File Type Validation**: Validate file types to prevent malicious uploads
6. **Size Limits**: Enforce size limits to prevent DoS attacks
7. **Content Scanning**: Consider scanning uploaded files for malware
8. **Access Control**: Use GCS IAM for fine-grained access control

---

## Performance Considerations

1. **File Size**: Large files may take time to upload/download
2. **Concurrent Uploads**: Handle multiple concurrent uploads efficiently
3. **Streaming**: For large files, consider streaming uploads
4. **Caching**: Cache public URLs if files don't change
5. **CDN**: Consider using CDN for frequently accessed files
6. **Compression**: Compress images before upload for better performance

---

## Client-Side Implementation

### Token Management

```javascript
// Get authentication token (prefer session_token)
function getAuthToken() {
  return localStorage.getItem('session_token') || 
         localStorage.getItem('access_token');
}

// API request helper for upload endpoints
async function uploadRequest(url, options = {}) {
  const token = getAuthToken();
  
  const headers = {
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
    throw new Error('You do not have permission to upload files');
  }
  
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error?.message || 'Upload failed');
  }
  
  return data;
}
```

### Direct File Upload

```javascript
// Upload file directly
async function uploadFile(file) {
  try {
    // Validate file size (15MB limit)
    const maxSize = 15 * 1024 * 1024; // 15MB in bytes
    if (file.size > maxSize) {
      throw new Error('File size exceeds 15MB limit');
    }
    
    // Validate file type (optional)
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf'];
    if (!allowedTypes.includes(file.type)) {
      throw new Error('File type not allowed');
    }
    
    // Create FormData
    const formData = new FormData();
    formData.append('file', file);
    
    // Show upload progress
    showUploadProgress(0);
    
    // Upload file
    const response = await uploadRequest('/api/v1/upload-media', {
      method: 'POST',
      body: formData
    });
    
    if (response && response.data) {
      showUploadProgress(100);
      showNotification('File uploaded successfully');
      return response.data.url;
    }
  } catch (error) {
    console.error('Error uploading file:', error);
    showError(error.message || 'Failed to upload file');
    throw error;
  }
}

// Upload with progress tracking
async function uploadFileWithProgress(file, onProgress) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const token = getAuthToken();
    
    const xhr = new XMLHttpRequest();
    
    // Track upload progress
    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percentComplete = (e.loaded / e.total) * 100;
        if (onProgress) {
          onProgress(percentComplete);
        }
      }
    });
    
    return new Promise((resolve, reject) => {
      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          if (response.success) {
            resolve(response.data.url);
          } else {
            reject(new Error(response.error?.message || 'Upload failed'));
          }
        } else {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      });
      
      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed'));
      });
      
      xhr.open('POST', '/api/v1/upload-media');
      xhr.setRequestHeader('X-Session-Token', token);
      xhr.send(formData);
    });
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  }
}
```

### Upload from URL

```javascript
// Upload file from URL
async function uploadFromURL(fileUrl) {
  try {
    // Validate URL format
    if (!fileUrl || !fileUrl.startsWith('http://') && !fileUrl.startsWith('https://')) {
      throw new Error('Invalid URL');
    }
    
    // Create form data
    const formData = new FormData();
    formData.append('url', fileUrl);
    
    // Show loading
    showLoading('Downloading file from URL...');
    
    // Upload from URL
    const response = await uploadRequest('/api/v1/upload-media', {
      method: 'POST',
      body: formData
    });
    
    hideLoading();
    
    if (response && response.data) {
      showNotification('File uploaded successfully from URL');
      return response.data.url;
    }
  } catch (error) {
    hideLoading();
    console.error('Error uploading from URL:', error);
    showError(error.message || 'Failed to upload from URL');
    throw error;
  }
}
```

### Delete File

```javascript
// Delete file from Google Cloud Storage
async function deleteFile(gcsUrl) {
  try {
    if (!gcsUrl) {
      throw new Error('File URL is required');
    }
    
    // Confirm deletion
    const confirmed = confirm('Are you sure you want to delete this file?');
    if (!confirmed) {
      return;
    }
    
    // Encode URL for query parameter
    const encodedUrl = encodeURIComponent(gcsUrl);
    
    const token = getAuthToken();
    
    const response = await fetch(
      `/api/v1/delete-media?url=${encodedUrl}`,
      {
        method: 'DELETE',
        headers: {
          'X-Session-Token': token
        }
      }
    );
    
    const data = await response.json();
    
    if (response.status === 200 && data.success) {
      showNotification('File deleted successfully');
      return true;
    } else {
      throw new Error(data.error?.message || 'Failed to delete file');
    }
  } catch (error) {
    console.error('Error deleting file:', error);
    showError(error.message || 'Failed to delete file');
    throw error;
  }
}
```

### Complete File Upload Component

```javascript
// Complete File Upload Manager Class
class FileUploadManager {
  constructor() {
    this.uploadedFiles = [];
    this.maxFileSize = 15 * 1024 * 1024; // 15MB
    this.allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf'];
  }
  
  async init() {
    // Set up file input listeners
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
      fileInput.addEventListener('change', (e) => {
        this.handleFileSelect(e.target.files[0]);
      });
    }
    
    // Set up URL upload form
    const urlForm = document.getElementById('url-upload-form');
    if (urlForm) {
      urlForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const url = document.getElementById('file-url').value;
        this.uploadFromURL(url);
      });
    }
  }
  
  async handleFileSelect(file) {
    try {
      // Validate file
      if (!this.validateFile(file)) {
        return;
      }
      
      // Show preview if image
      if (file.type.startsWith('image/')) {
        this.showImagePreview(file);
      }
      
      // Upload file
      const url = await this.uploadFile(file);
      
      // Add to uploaded files list
      this.uploadedFiles.push({
        name: file.name,
        url: url,
        size: file.size,
        type: file.type
      });
      
      // Update UI
      this.renderUploadedFiles();
      
    } catch (error) {
      console.error('Error handling file:', error);
      showError(error.message);
    }
  }
  
  validateFile(file) {
    // Check file size
    if (file.size > this.maxFileSize) {
      showError(`File size exceeds ${this.maxFileSize / 1024 / 1024}MB limit`);
      return false;
    }
    
    // Check file type
    if (this.allowedTypes.length > 0 && !this.allowedTypes.includes(file.type)) {
      showError('File type not allowed');
      return false;
    }
    
    return true;
  }
  
  showImagePreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const preview = document.getElementById('image-preview');
      if (preview) {
        preview.src = e.target.result;
        preview.style.display = 'block';
      }
    };
    reader.readAsDataURL(file);
  }
  
  async uploadFile(file) {
    try {
      showLoading('Uploading file...');
      
      const url = await uploadFileWithProgress(file, (progress) => {
        this.updateUploadProgress(progress);
      });
      
      hideLoading();
      showNotification('File uploaded successfully');
      
      return url;
    } catch (error) {
      hideLoading();
      throw error;
    }
  }
  
  async uploadFromURL(fileUrl) {
    try {
      showLoading('Uploading from URL...');
      
      const url = await uploadFromURL(fileUrl);
      
      hideLoading();
      showNotification('File uploaded successfully from URL');
      
      // Add to uploaded files
      this.uploadedFiles.push({
        name: fileUrl.split('/').pop(),
        url: url,
        type: 'url'
      });
      
      this.renderUploadedFiles();
      
      return url;
    } catch (error) {
      hideLoading();
      throw error;
    }
  }
  
  async deleteFile(gcsUrl) {
    try {
      await deleteFile(gcsUrl);
      
      // Remove from uploaded files list
      this.uploadedFiles = this.uploadedFiles.filter(f => f.url !== gcsUrl);
      
      // Update UI
      this.renderUploadedFiles();
      
    } catch (error) {
      console.error('Error deleting file:', error);
      throw error;
    }
  }
  
  updateUploadProgress(percent) {
    const progressBar = document.getElementById('upload-progress');
    if (progressBar) {
      progressBar.style.width = `${percent}%`;
      progressBar.textContent = `${Math.round(percent)}%`;
    }
  }
  
  renderUploadedFiles() {
    const container = document.getElementById('uploaded-files');
    if (!container) return;
    
    if (this.uploadedFiles.length === 0) {
      container.innerHTML = '<p>No files uploaded yet</p>';
      return;
    }
    
    container.innerHTML = this.uploadedFiles.map((file, index) => `
      <div class="uploaded-file-item">
        <div class="file-info">
          <h4>${file.name}</h4>
          <p>${file.type}</p>
          <p>${(file.size / 1024).toFixed(2)} KB</p>
        </div>
        <div class="file-actions">
          <a href="${file.url}" target="_blank" class="btn-view">View</a>
          <button onclick="fileUploadManager.deleteFile('${file.url}')" class="btn-delete">Delete</button>
        </div>
      </div>
    `).join('');
  }
}

// Initialize file upload manager
document.addEventListener('DOMContentLoaded', () => {
  window.fileUploadManager = new FileUploadManager();
  fileUploadManager.init();
});
```

### Drag and Drop Upload

```javascript
// Drag and drop file upload
function setupDragAndDrop() {
  const dropZone = document.getElementById('drop-zone');
  
  if (!dropZone) return;
  
  // Prevent default drag behaviors
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });
  
  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }
  
  // Highlight drop zone when item is dragged over it
  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, highlight, false);
  });
  
  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, unhighlight, false);
  });
  
  function highlight(e) {
    dropZone.classList.add('drag-over');
  }
  
  function unhighlight(e) {
    dropZone.classList.remove('drag-over');
  }
  
  // Handle dropped files
  dropZone.addEventListener('drop', handleDrop, false);
  
  function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
      fileUploadManager.handleFileSelect(files[0]);
    }
  }
}

// Initialize drag and drop
setupDragAndDrop();
```

### Image Preview and Cropping

```javascript
// Image preview with cropping option
async function uploadImageWithPreview(file) {
  try {
    // Show image preview
    const reader = new FileReader();
    reader.onload = (e) => {
      const preview = document.getElementById('image-preview');
      if (preview) {
        preview.src = e.target.result;
        preview.style.display = 'block';
        
        // Optionally integrate with image cropping library
        // Example: Cropper.js
        const cropper = new Cropper(preview, {
          aspectRatio: 1,
          viewMode: 1
        });
        
        // Get cropped image on upload
        document.getElementById('upload-btn').addEventListener('click', () => {
          cropper.getCroppedCanvas().toBlob((blob) => {
            uploadFile(blob);
          });
        });
      }
    };
    reader.readAsDataURL(file);
  } catch (error) {
    console.error('Error previewing image:', error);
    showError('Failed to preview image');
  }
}
```

---

## Summary

This documentation provides comprehensive coverage of all file upload and management endpoints:

### Endpoints Covered:
1. ✅ **Upload Media** - Upload files directly or from URL
2. ✅ **Delete Media** - Delete files from Google Cloud Storage

### Documentation Sections:
- ✅ Overview and system architecture
- ✅ Detailed endpoint documentation with examples
- ✅ Client-server communication flows
- ✅ Complete workflows and diagrams
- ✅ Error handling guide
- ✅ Best practices and security considerations
- ✅ Complete client-side implementation examples
- ✅ File Upload Manager component
- ✅ Drag and drop upload examples
- ✅ Image preview and cropping examples

### Key Features:
- **Multiple Upload Methods** - Direct file upload or upload from URL
- **File Validation** - Size limits (15MB) and type validation
- **Progress Tracking** - Upload progress indicators
- **Google Cloud Storage** - Integration with GCS for file storage
- **Security** - Authentication, permissions, and bucket validation
- **Client-side examples** - Ready-to-use JavaScript code

All endpoints are fully documented with request/response examples, client-server communication flows, and implementation guidance.

---

**Last Updated**: January 2025

