# 🚀 FastAPI Backend API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B-blue.svg)](https://postgresql.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-purple.svg)](https://www.sqlalchemy.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

> **Enterprise-Grade FastAPI Backend API with Advanced Features**

FastAPI Backend is a comprehensive, production-ready RESTful API built with FastAPI (Python), featuring JWT authentication with Instagram-style multi-token pattern, role-based access control, real-time activity logging, advanced security middleware, and comprehensive monitoring capabilities.

**Repository**: [https://github.com/fullstack-open-source/fastapi-backend-with-sql](https://github.com/fullstack-open-source/fastapi-backend-with-sql)

## 📋 Table of Contents

- [🚀 Features](#-features)
- [🏗️ Architecture](#️-architecture)
  - [System Architecture](#system-architecture)
  - [Authentication Architecture](#authentication-architecture)
  - [Request Flow](#request-flow)
  - [Middleware Stack](#middleware-stack)
  - [Database Architecture](#database-architecture)
  - [Module Structure](#module-structure)
- [📚 API Documentation](#-api-documentation)
- [📦 Installation & Setup](#-installation--setup)
  - [Prerequisites](#prerequisites)
  - [Quick Start](#quick-start)
  - [Development Setup](#development-setup)
  - [Production Setup](#production-setup)
  - [Docker Setup](#docker-setup)
- [🔄 Complete Project Workflow](#-complete-project-workflow)
- [📖 Detailed Documentation](#-detailed-documentation)

## 🚀 Features

### 🎯 Core Capabilities

- **RESTful API**: Comprehensive REST API with FastAPI framework
- **JWT Authentication**: Instagram-style multi-token authentication system (Access, Session, Refresh tokens)
- **Role-Based Access Control**: Flexible permission system with groups and permissions
- **Activity Logging**: Comprehensive audit trail with detailed metadata
- **File Upload**: Google Cloud Storage integration for media files
- **Email & SMS**: Twilio integration for notifications and OTP
- **Error Tracking**: Sentry integration for production monitoring and error tracking
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Rate Limiting**: Request throttling and rate limiting for traffic management
- **Docker Ready**: Production-ready containerization with multi-stage builds
- **Kubernetes Support**: K8s deployment configurations included

### 🔧 Technical Features

- **FastAPI 0.109+**: Modern, fast web framework for building APIs with Python
- **Python 3.11+**: Modern Python with type hints and async support (3.11+ recommended for Google Cloud libraries)
- **PostgreSQL 16+**: Robust relational database with advanced features
- **SQLAlchemy 2.0+**: Modern ORM with async support and type safety
- **Alembic**: Database migration tool for schema versioning
- **Redis**: Caching and session management for improved performance
- **JWT**: Secure token-based authentication with multi-token pattern
- **Pydantic**: Data validation using Python type annotations
- **Sentry**: Error tracking and performance monitoring
- **Google Cloud Storage**: Object storage for media files
- **Nginx Reverse Proxy**: Production-ready reverse proxy configuration

### 🔐 Authentication Features

- **Multi-Token System**: Access token (1 hour), Session token (7 days), Refresh token (30 days)
- **Token Blacklisting**: Redis-based token invalidation for secure logout
- **OTP Verification**: Email, SMS, and WhatsApp OTP support
- **Password Management**: Set, change, and reset password functionality
- **Email/Phone Verification**: Two-step verification for contact changes
- **Session Management**: Stateless session management with unique session IDs
- **Token Rotation**: Automatic token rotation on refresh for enhanced security

## 🏗️ Architecture

### System Architecture

The system follows a layered architecture with clear separation of concerns:

```
┌───────────────────────────────────────────────────────────────┐
│                        External Proxy                         │
│                    (api.example.com)                          │
│                    SSL/TLS Termination                        │
└────────────────────────────┬──────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                    Internal Nginx Proxy                        │
│                    (Port 9080:80)                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Security Layer:                                         │  │
│  │  - Rate Limiting (200 req/min per IP)                    │  │
│  │  - Request Size Validation (15MB max)                    │  │
│  │  - Attack Pattern Detection                              │  │
│  │  - Content Security Policy                               │  │
│  │  - DDoS Protection                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                    FastAPI Application                         │
│                    (Port 8000)                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Middleware Stack:                                       │  │
│  │  1. Sentry Request Handler                               │  │
│  │  2. CORS (Cross-Origin)                                  │  │
│  │  3. Advanced Security Middleware                         │  │
│  │  4. Input Sanitization                                   │  │
│  │  5. Permission Middleware                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Application Modules:                                    │  │
│  │  - Authentication (JWT, OTP, Login)                      │  │
│  │  - Profile Management                                    │  │
│  │  - Permissions (Groups, Permissions)                     │  │
│  │  - Dashboard (Analytics)                                 │  │
│  │  - Activity Logging                                      │  │
│  │  - File Upload (GCS)                                     │  │
│  │  - Health Monitoring                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬──────────────────────────────-────┘
                             │
                ┌────────────┴─────────────┐
                ▼                          ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│   PostgreSQL Database    │   │   Redis Cache            │
│   (SQLAlchemy ORM)       │   │   (Sessions, Cache)      │
│   - User Data            │   │   - Session Storage      │
│   - Permissions          │   │   - OTP Cache            │
│   - Activity Logs        │   │   - Token Blacklist      │
│   - Groups               │   │   - Rate Limiting        │
└──────────────────────────┘   └──────────────────────────┘
                │
                ▼
┌──────────────────────────┐
│   Google Cloud Storage   │
│   (Media & Static Files) │
│   - User Uploads         │
│   - Generated Content    │
│   - Static Assets        │
└──────────────────────────┘
```

### Authentication Architecture

The authentication system implements a **stateless, multi-token architecture** similar to Instagram:

**Key Features:**
- **Multi-Token System**: Access token (1 hour), Session token (7 days), Refresh token (30 days)
- **Token Blacklisting**: Redis-based cache for token invalidation
- **Session Management**: Unique session_id links all tokens together
- **Token Rotation**: Refresh tokens rotate on each refresh for security
- **Origin Validation**: Domain-specific token validation

**Complete Documentation**: See [Authentication Architecture](./api/AUTH_ARCHITECTURE.md)

### Request Flow

```
1. Client Request
   │
   ├─► External Proxy (api.example.com)
   │
   ├─► Internal Nginx (Port 9080)
   │   ├─► Security Checks (Rate Limiting, Attack Detection)
   │   ├─► Request Size Validation
   │   ├─► Content Security Policy Headers
   │   └─► Proxy to FastAPI (http://api:8000)
   │
   ├─► FastAPI Middleware Stack
   │   ├─► Sentry Request Handler
   │   │   └─► Request Context Capture
   │   │
   │   ├─► CORS
   │   │   └─► Origin Validation
   │   │
   │   ├─► Advanced Security Middleware
   │   │   ├─► Input Sanitization
   │   │   ├─► SQL Injection Detection
   │   │   ├─► XSS Detection
   │   │   └─► Command Injection Detection
   │   │
   │   └─► Permission Middleware
   │       └─► JWT Validation & Permission Check
   │
   ├─► Route Handler
   │   ├─► Request Validation (Pydantic)
   │   ├─► Business Logic
   │   ├─► Database Operations (SQLAlchemy)
   │   └─► Response Formatting
   │
   ├─► Activity Logging
   │   └─► Log to Database
   │
   └─► Response
       ├─► Error Handling (if any)
       ├─► Sentry Error Capture (if error)
       ├─► Security Headers
       └─► Client Response
```

### Middleware Stack

The middleware stack processes requests in a specific order to ensure security, performance, and reliability:

1. **Sentry Request Handler** - Captures request context for error tracking and performance monitoring
2. **CORS** - Handles cross-origin requests with whitelist validation for allowed origins
3. **Advanced Security Middleware** - Sanitizes input data and detects attack patterns
4. **Permission Middleware** - Validates JWT tokens and checks user permissions
5. **Route Handlers** - Application-specific logic execution
6. **Error Handler** - Catches and formats errors with appropriate status codes
7. **Sentry Error Handler** - Captures errors for monitoring and alerting

### Database Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  User Model                                          │   │
│  │  - user_id (UUID, Primary Key)                       │   │
│  │  - email, phone_number, user_name                    │   │
│  │  - password, auth_type                               │   │
│  │  - is_email_verified, is_phone_verified              │   │
│  │  - status, is_active, is_verified                    │   │
│  │  - profile_picture_url, bio                          │   │
│  │  - Relationships: UserGroup[], ActivityLog[]         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Permission Model                                    │   │
│  │  - permission_id (UUID, Primary Key)                 │   │
│  │  - name, codename (unique)                           │   │
│  │  - description, category                             │   │
│  │  - Relationships: GroupPermission[]                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Group Model                                         │   │
│  │  - group_id (UUID, Primary Key)                      │   │
│  │  - name, codename (unique)                           │   │
│  │  - description, is_system, is_active                 │   │
│  │  - Relationships: GroupPermission[], UserGroup[]     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  GroupPermission Model (Many-to-Many)                │   │
│  │  - id (UUID, Primary Key)                            │   │
│  │  - group_id (FK → Group)                             │   │
│  │  - permission_id (FK → Permission)                   │   │
│  │  - Unique constraint: (group_id, permission_id)      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  UserGroup Model (Many-to-Many)                      │   │
│  │  - id (UUID, Primary Key)                            │   │
│  │  - user_id (FK → User)                               │   │
│  │  - group_id (FK → Group)                             │   │
│  │  - assigned_at, assigned_by_user_id                  │   │
│  │  - Unique constraint: (user_id, group_id)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ActivityLog Model                                   │   │
│  │  - log_id (UUID, Primary Key)                        │   │
│  │  - user_id (FK → User, nullable)                     │   │
│  │  - level, message, action, module                    │   │
│  │  - ip_address, user_agent, device, browser, os       │   │
│  │  - endpoint, method, status_code                     │   │
│  │  - request_id, session_id                            │   │
│  │  - metadata, error_details (JSONB)                   │   │
│  │  - duration_ms, created_at                           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Module Structure

```
FastAPI Backend API
├── 📁 api/                              # Main application directory
│   ├── 📄 server.py                     # FastAPI server entry point
│   ├── 📄 db.py                         # Database CLI (Alembic wrapper)
│   ├── 📄 Dockerfile                    # Multi-stage Docker build
│   ├── 📄 requirements.txt              # Python dependencies
│   ├── 📄 start.sh                      # Container startup script
│   ├── 📄 alembic.ini                   # Alembic configuration
│   │
│   ├── 📁 router/                       # API route handlers
│   │   ├── 🔐 authenticate/              # Authentication routes
│   │   │   ├── authenticate.py          # Login, OTP, token management
│   │   │   ├── authenticate.md          # Complete authentication docs
│   │   │   ├── profile.py               # User profile management
│   │   │   ├── profile.md               # Profile management docs
│   │   │   ├── models.py                # Request validation schemas
│   │   │   ├── query.py                 # Database queries
│   │   │   └── utils.py                 # Helper functions
│   │   │
│   │   ├── 📊 dashboard/                # Dashboard routes
│   │   │   ├── api.py                   # Analytics and statistics
│   │   │   └── dashboard.md            # Dashboard documentation
│   │   │
│   │   ├── 🔑 permissions/              # Permission management
│   │   │   ├── api.py                   # Groups, permissions, users
│   │   │   └── permissions.md          # Permissions documentation
│   │   │
│   │   ├── 📝 activity/                 # Activity logging
│   │   │   ├── api.py                   # Activity log endpoints
│   │   │   └── activity.md              # Activity logging docs
│   │   │
│   │   ├── 📤 upload/                   # File upload
│   │   │   ├── api.py                   # Media upload endpoints
│   │   │   └── upload.md                # Upload documentation
│   │   │
│   │   └── ❤️ health/                   # Health monitoring
│   │       ├── api.py                   # Health check endpoints
│   │       ├── health.md                # Health check docs
│   │       └── test_sentry.py          # Sentry test endpoint
│   │
│   ├── 📁 src/                          # Source code modules
│   │   ├── 🔐 authenticate/             # Authentication logic
│   │   │   ├── authenticate.py         # JWT validation
│   │   │   ├── checkpoint.py            # User authentication
│   │   │   ├── models.py                # User models
│   │   │   ├── otp_cache.py             # OTP management
│   │   │   └── session_manager.py       # Session management
│   │   │
│   │   ├── 📊 activity/                 # Activity logging
│   │   │   └── activityLog.py           # Activity log service
│   │   │
│   │   ├── 💾 cache/                    # Caching layer
│   │   │   └── cache.py                # Redis cache utilities
│   │   │
│   │   ├── 🗄️ db/                       # Database layer
│   │   │   ├── models/                  # SQLAlchemy models
│   │   │   │   ├── user.py              # User model
│   │   │   │   ├── permission.py        # Permission model
│   │   │   │   ├── group.py             # Group model
│   │   │   │   └── activity_log.py      # Activity log model
│   │   │   └── postgres/                # PostgreSQL utilities
│   │   │       ├── postgres.py          # Connection pool
│   │   │       ├── triggers.py          # Database triggers
│   │   │       └── init_triggers.py     # Trigger initialization
│   │   │
│   │   ├── 📧 email/                    # Email service
│   │   │   ├── email.py                 # Email sending
│   │   │   └── templete.py              # Email templates
│   │   │
│   │   ├── 📋 enum/                     # Enumerations
│   │   │   └── enum.py                  # Application enums
│   │   │
│   │   ├── 📝 logger/                   # Logging system
│   │   │   └── logger.py                # Custom logger
│   │   │
│   │   ├── 🛡️ middleware/               # FastAPI middleware
│   │   │   ├── advanced_security_middleware.py  # Security checks
│   │   │   ├── input_sanitizer.py       # Input sanitization
│   │   │   ├── permission_middleware.py # Permission checking
│   │   │   └── security_middleware.py  # Security middleware
│   │   │
│   │   ├── 🔑 permissions/               # Permission system
│   │   │   └── permissions.py            # Permission utilities
│   │   │
│   │   ├── 📤 response/                  # Response handlers
│   │   │   ├── success.py               # Success responses
│   │   │   ├── error.py                 # Error responses
│   │   │   └── map.py                   # Response mapping
│   │   │
│   │   ├── 📱 sms/                       # SMS service
│   │   │   └── sms.py                   # Twilio integration
│   │   │
│   │   ├── 💾 storage/                   # File storage
│   │   │   ├── base_cloud_storage.py    # Base storage class
│   │   │   └── media_storage.py         # Google Cloud Storage
│   │   │
│   │   └── 🌐 multilingual/              # Multilingual support
│   │       └── multilingual.py          # Language utilities
│   │
│   ├── 📁 alembic/                       # Database migrations
│   │   ├── versions/                     # Migration files
│   │   └── env.py                       # Alembic environment
│   │
│   ├── 📁 credentials/                   # Service credentials
│   │   └── google-backend-master.json   # GCS credentials
│   │
│   ├── 📁 logs/                          # Application logs
│   │   └── server.log                   # Server logs
│   │
│   ├── 📄 AUTH_ARCHITECTURE.md           # Authentication architecture
│   └── 📄 JWT_CONFIG.md                 # JWT configuration
│
├── 📁 docs/                              # Documentation
│   ├── ARCHITECTURE.md                   # System architecture
│   ├── TECHNICAL.md                      # Technical specifications
│   ├── BACKEND_DEVELOPER.md              # Backend developer guide
│   ├── FRONTEND_DEVELOPER.md             # Frontend developer guide
│   └── README.md                         # Documentation index
│
├── 📁 nginx/                             # Nginx configuration
│   ├── nginx.conf                        # Main nginx config
│   ├── proxy.conf                        # Proxy settings
│   ├── security.conf                    # Security headers
│   └── conf.d/                          # Additional configs
│
├── 📁 k8s/                               # Kubernetes configurations
│   ├── README.md                         # K8s documentation
│   ├── ARCHITECTURE.md                   # K8s architecture
│   └── SETUP.md                         # K8s setup guide
│
├── 📄 docker-compose.yaml                # Docker Compose config
├── 📄 reload.sh                          # Deployment script
└── 📄 README.md                          # This file
```

## 📚 API Documentation

### Authentication & User Management

**Complete Documentation**: [Authentication Router](./api/router/authenticate/authenticate.md)

**Endpoints:**
- `POST /{MODE}/auth/login-with-password` - Login with email/phone and password
- `POST /{MODE}/auth/login-with-otp` - Login with OTP
- `POST /{MODE}/auth/send-one-time-password` - Send OTP via email/SMS/WhatsApp
- `POST /{MODE}/auth/verify-one-time-password` - Verify OTP
- `POST /{MODE}/auth/verify` - Signup/Register with OTP
- `POST /{MODE}/auth/set-password` - Set password for authenticated user
- `POST /{MODE}/auth/change-password` - Change user password
- `POST /{MODE}/auth/forget-password` - Reset password with OTP
- `POST /{MODE}/auth/refresh-token` - Refresh access tokens
- `POST /{MODE}/auth/logout` - Logout and revoke tokens
- `POST /{MODE}/auth/check-user-availability` - Check email/phone availability
- `POST /{MODE}/auth/verify-email-and-phone` - Verify email/phone with OTP

**Profile Management**: [Profile Router](./api/router/authenticate/profile.md)

**Endpoints:**
- `GET /{MODE}/settings/profile` - Get user profile
- `GET /{MODE}/settings/profile/{user_id}` - Get profile by ID
- `POST /{MODE}/settings/profile-picture` - Update profile picture
- `PUT /{MODE}/settings/profile` - Update user profile
- `POST /{MODE}/settings/change-email` - Change email with OTP verification
- `POST /{MODE}/settings/change-phone` - Change phone with OTP verification
- `POST /{MODE}/settings/profile-accessibility` - Update profile accessibility
- `POST /{MODE}/settings/profile-language` - Update profile language
- `POST /{MODE}/settings/update-theme` - Update theme preference
- `POST /{MODE}/settings/update-timezone` - Update timezone
- `GET /{MODE}/settings` - Get user settings
- `POST /{MODE}/settings/deactivate-account` - Deactivate account
- `POST /{MODE}/settings/delete-account` - Delete account

### Permissions & Groups

**Complete Documentation**: [Permissions Router](./api/router/permissions/permissions.md)

**Endpoints:**
- `GET /{MODE}/permissions` - Get all permissions
- `GET /{MODE}/permissions/{permission_id}` - Get permission by ID
- `POST /{MODE}/permissions` - Create new permission
- `PUT /{MODE}/permissions/{permission_id}` - Update permission
- `DELETE /{MODE}/permissions/{permission_id}` - Delete permission
- `GET /{MODE}/groups` - Get all groups
- `GET /{MODE}/groups/{group_id}` - Get group by ID
- `POST /{MODE}/groups` - Create new group
- `PUT /{MODE}/groups/{group_id}` - Update group
- `DELETE /{MODE}/groups/{group_id}` - Delete group
- `POST /{MODE}/groups/{group_id}/permissions` - Assign permissions to group
- `GET /{MODE}/users/{user_id}/groups` - Get user groups
- `GET /{MODE}/users/{user_id}/permissions` - Get user permissions
- `POST /{MODE}/users/{user_id}/groups` - Assign groups to user
- `GET /{MODE}/users/me/groups` - Get current user groups
- `GET /{MODE}/users/me/permissions` - Get current user permissions

### Dashboard & Analytics

**Complete Documentation**: [Dashboard Router](./api/router/dashboard/dashboard.md)

**Endpoints:**
- `GET /{MODE}/dashboard/overview` - Get dashboard overview statistics
- `GET /{MODE}/dashboard/users-by-status` - Get users grouped by status
- `GET /{MODE}/dashboard/users-by-type` - Get users grouped by type
- `GET /{MODE}/dashboard/users-by-auth-type` - Get users grouped by auth type
- `GET /{MODE}/dashboard/users-by-country` - Get users grouped by country
- `GET /{MODE}/dashboard/users-by-language` - Get users grouped by language
- `GET /{MODE}/dashboard/user-growth` - Get user growth statistics
- `GET /{MODE}/dashboard/role-statistics` - Get role/group statistics
- `GET /{MODE}/dashboard/recent-sign-ins` - Get recent sign-in activity
- `GET /{MODE}/dashboard/all-statistics` - Get all statistics

### File Upload

**Complete Documentation**: [Upload Router](./api/router/upload/upload.md)

**Endpoints:**
- `POST /{MODE}/upload/media` - Upload media file (direct upload or URL)
- `DELETE /{MODE}/upload/media/{file_id}` - Delete uploaded media

**Features:**
- Direct file upload with multipart/form-data
- URL-based upload (downloads and stores file from URL)
- Google Cloud Storage integration
- Automatic file validation and processing
- Support for images, videos, and documents

### Activity Logging

**Complete Documentation**: [Activity Router](./api/router/activity/activity.md)

**Endpoints:**
- `GET /{MODE}/activity` - Get activity logs with filtering
- `GET /{MODE}/activity/{log_id}` - Get specific activity log
- `POST /{MODE}/activity` - Create activity log entry

**Features:**
- Comprehensive audit trail
- User action tracking
- Request/response logging
- Error logging with details
- Metadata storage (JSONB)

### Health Monitoring

**Complete Documentation**: [Health Router](./api/router/health/health.md)

**Endpoints:**
- `GET /health` - Basic health check (no prefix)
- `GET /{MODE}/health` - Detailed health check
- `GET /{MODE}/health/system` - System health with metrics
- `GET /{MODE}/health/database` - Database connection health
- `GET /{MODE}/health/storage` - Storage (GCS) health check
- `GET /{MODE}/health/test-sentry` - Test Sentry integration

## 📦 Installation & Setup

### Prerequisites

**System Requirements:**
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **Python**: 3.11 or higher (recommended for Google Cloud libraries compatibility)
  - ⚠️ **Note**: Python 3.10 will reach end-of-life for Google API Core in 2026-10-04
- **PostgreSQL**: 12+ (for production)
- **Redis**: 6+ (optional, for caching and token blacklisting)
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+ (for multi-container orchestration)
- **Google Cloud Storage**: Account and bucket (for media files)

**Development Tools:**
- Git 2.30+
- Code editor (VS Code recommended)
- Postman or similar API testing tool

### Quick Start

#### Step 1: Clone Repository

```bash
git clone https://github.com/fullstack-open-source/fastapi-backend-with-sql.git
cd fastapi-backend-with-sql
```

#### Step 2: Setup Environment

```bash
# Copy example environment file
cp example.env .env

# Edit .env file with your configuration
nano .env
```

#### Step 3: Setup Google Cloud Storage Credentials (Optional)

If you plan to use file upload features, you need to configure Google Cloud Storage credentials:

```bash
# Navigate to credentials directory
cd api/credentials

# Copy the template credential file
cp "google-backend-master copy.json" google-backend-master.json

# Edit the credential file with your Google Cloud Service Account credentials
nano google-backend-master.json
```

**How to get Google Cloud Service Account credentials:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select or create a project
3. Navigate to **IAM & Admin** → **Service Accounts**
4. Create a new service account or select an existing one
5. Click on the service account → **Keys** tab
6. Click **Add Key** → **Create new key** → Choose **JSON** format
7. Download the JSON file
8. Copy the contents of the downloaded JSON file into `api/credentials/google-backend-master.json`

#### Step 4: Start Services with Docker Compose

```bash
# Create Docker network (if not exists)
docker network create fastapi_backend_with_postgresql_network

# Start all services
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f api
```

#### Step 5: Setup Database Schema

```bash
# Run database migrations
docker compose exec api python db.py upgrade

# Seed database (optional)
docker compose exec api python db.py seed
```

#### Step 6: Access Services

- **API Base**: http://localhost:9080
- **API Docs**: http://localhost:9080/docs
- **Health Check**: http://localhost:9080/health (no prefix) or http://localhost:9080/{MODE}/health
- **API Routes**: http://localhost:9080/{MODE}/* (e.g., /prod/v1/auth/login, /dev/v1/settings)
- **pgAdmin**: http://localhost:5050 (if enabled)

**Note:** Replace `{MODE}` with your configured MODE value (e.g., `prod/v1` or `dev/v1`)

### API Route Prefix (MODE)

All API routes are prefixed with the `MODE` environment variable. This allows you to version your API and separate environments.

**Configuration in `.env`:**
```bash
MODE=prod/v1    # For production API version 1
# or
MODE=dev/v1     # For development API version 1
```

**API Route Examples:**

If `MODE=prod/v1`, all routes will be prefixed with `/prod/v1/`:
- Health Check: `http://localhost:9080/prod/v1/health`
- Authentication: `http://localhost:9080/prod/v1/auth/login-with-password`
- Profile: `http://localhost:9080/prod/v1/settings/profile`
- Dashboard: `http://localhost:9080/prod/v1/dashboard/overview`
- Permissions: `http://localhost:9080/prod/v1/permissions`
- Activity: `http://localhost:9080/prod/v1/activity`
- Upload: `http://localhost:9080/prod/v1/upload/media`

**Note:** The `/health` endpoint is available without the MODE prefix for health checks:
- Direct Health Check: `http://localhost:9080/health` (no prefix)

### Development Setup

#### Step 1: System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3.9 python3.9-venv python3-pip -y

# Install Docker (optional, for containerized development)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose-plugin -y
```

#### Step 2: Project Setup

```bash
# Clone repository
git clone https://github.com/fullstack-open-source/fastapi-backend-with-sql.git
cd fastapi-backend-with-sql/api

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Environment Configuration

```bash
# Copy example environment file
cp ../example.env ../.env

# Edit .env file with your settings
nano ../.env
```

#### Step 4: Database Setup (Local PostgreSQL)

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE fastapi_backend;
CREATE USER fastapi_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fastapi_backend TO fastapi_user;
\q
EOF

# Update .env with local database connection
# DATABASE_URL=postgresql://fastapi_user:your_password@localhost:5432/fastapi_backend
```

#### Step 5: Database Migrations

```bash
# Database CLI commands (using db.py)
python db.py upgrade       # Apply all pending migrations
python db.py migrate       # Create a new migration
python db.py downgrade     # Rollback last migration
python db.py history       # Show migration history
python db.py current       # Show current migration
python db.py seed          # Seed the database with default data
python db.py reset         # Reset database (drop all tables and recreate)
```

#### Step 6: Start Development Server

```bash
# Development mode with auto-reload
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Or using the start script
./start.sh
```

#### Step 7: Access Application

- **API Base**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health (no prefix) or http://localhost:8000/{MODE}/health
- **API Routes**: http://localhost:8000/{MODE}/* (e.g., /prod/v1/auth/login, /dev/v1/settings)

**Note:** Replace `{MODE}` with your configured MODE value (e.g., `prod/v1` or `dev/v1`)

### Production Setup

#### Step 1: Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3.9 python3.9-venv python3-pip -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose-plugin -y
```

#### Step 2: Clone and Setup Project

```bash
# Clone repository
git clone https://github.com/fullstack-open-source/fastapi-backend-with-sql.git
cd fastapi-backend-with-sql

# Create production .env file
cp example.env .env

# Edit .env file with production settings
nano .env
```

**Important**: Update `.env` file with production values:
- Set `API_MODE=production`
- Set `DEBUG_MODE=false`
- Configure production database credentials
- Set strong JWT secret (generate with: `openssl rand -base64 32`)
- Configure production Redis, Sentry, and other services
- Set `GOOGLE_STORAGE_BUCKET_NAME` with your production bucket name

#### Step 3: Deploy with Docker (Recommended)

```bash
# Build and start services
docker compose build
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f api

# Run migrations
docker compose exec api python db.py upgrade
```

#### Step 4: Configure External Proxy (Nginx)

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/api.example.com
```

Add configuration:

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:9080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/api.example.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Docker Setup

#### Step 1: Prerequisites

```bash
# Check Docker version
docker --version
docker compose version

# Install Docker if needed
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose-plugin -y
```

#### Step 2: Docker Compose Services

The `docker-compose.yaml` includes:
- **api**: FastAPI application (Python server)
- **db**: PostgreSQL database
- **redis**: Redis cache and session store
- **nginx**: Internal reverse proxy
- **pgadmin**: PostgreSQL admin interface

#### Step 3: Build and Start Services

```bash
# Create Docker network
docker network create fastapi_backend_with_postgresql_network

# Build images
docker compose build

# Start all services
docker compose up -d

# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f api
docker compose logs -f nginx
```

#### Step 4: Service Management

```bash
# Stop services
docker compose stop

# Start services
docker compose start

# Restart services
docker compose restart

# Restart specific service
docker compose restart api

# Stop and remove containers
docker compose down

# Stop, remove containers, and volumes
docker compose down -v
```

#### Step 5: Execute Commands in Containers

```bash
# Run database migrations
docker compose exec api python db.py upgrade

# Seed database
docker compose exec api python db.py seed

# Access container shell
docker compose exec api sh

# Access PostgreSQL
docker compose exec db psql -U postgres -d postgres
```

#### Step 6: Health Checks

```bash
# Check service health
docker compose ps

# Test API health endpoint
curl http://localhost:9080/health

# Test Nginx health endpoint
curl http://localhost:9080/health
```

## 🔄 Complete Project Workflow

### Service Connection Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Network                               │
│              (fastapi_backend_with_postgresql_network)          │
│                                                                 │
│  ┌──────────────┐                                               │
│  │   Client     │                                               │
│  │  (Browser)   │                                               │
│  └──────┬───────┘                                               │
│         │                                                       │
│         │ HTTP/HTTPS (Port 9080)                                │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Nginx Service                                           │   │
│  │  Container: fastapi-backend-nginx                        │   │
│  │  Port: 9080:80 (host:container)                          │   │
│  │  Config: ./nginx/nginx.conf                              │   │
│  └──────┬───────────────────────────────────────────────────┘   │
│         │                                                       │
│         │ Proxy to http://api:8000                              │
│         ▼                                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  API Service (FastAPI)                                   │   │
│  │  Container: fastapi-backend                              │   │
│  │  Port: 8000 (internal only)                              │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  SQLAlchemy ORM                                    │  │   │
│  │  │  - Database models                                 │  │   │
│  │  │  - Connection pooling                              │  │   │
│  │  └──────┬─────────────────────────────────────────────┘  │   │
│  └─────────┼────────────────────────────────────────────────┘   │
│            │                                                    │
│            │ PostgreSQL Connection                              │
│            │ (postgresql://postgres:postgres@                   │
│            │  fastapi-backend-db:5432/postgres)                 │
│            ▼                                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  PostgreSQL Service                                      │   │
│  │  Container: fastapi-backend-db                           │   │
│  │  Port: 5432 (internal only)                              │   │
│  │  Volume: postgres_data (persistent)                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│            ▲                                                    │
│            │                                                    │
│            │ Redis Connection                                   │
│            │ (redis://fastapi-backend-redis:6379)               │
│            │                                                    │
│  ┌─────────┴──────────────────────────────────────────────┐     │
│  │  Redis Service                                         │     │
│  │  Container: fastapi-backend-redis                      │     │
│  │  Port: 6379 (internal only)                            │     │
│  │  ┌──────────────────────────────────────────────────┐  │     │
│  │  │  Cache Storage                                   │  │     │
│  │  │  - OTP cache                                     │  │     │
│  │  │  - Session storage                               │  │     │
│  │  │  - Token blacklist                               │  │     │
│  │  │  - Rate limiting data                            │  │     │
│  │  └──────────────────────────────────────────────────┘  │     │
│  └────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### Service Startup Order

```
1. Docker Network
   └─► fastapi_backend_with_postgresql_network

2. Database Services (Start First)
   ├─► PostgreSQL (fastapi-backend-db:5432)
   └─► Redis (fastapi-backend-redis:6379)

3. API Service (Waits for Database Health Checks)
   ├─► Connects to PostgreSQL via SQLAlchemy
   └─► Connects to Redis for Cache

4. Nginx Service (Waits for API Health Check)
   └─► Proxies to API (http://api:8000)

5. pgAdmin Service (Optional, Waits for Database)
   └─► Connects to PostgreSQL
```

### Connection Flow

```
Client Request
    │
    ▼
Port 9080 (Host) ──► Nginx ──► Port 8000 ──► FastAPI Service
                                         │
                                         ├─► PostgreSQL (Port 5432)
                                         └─► Redis (Port 6379)
```

## 📖 Detailed Documentation

### Core Documentation

- **[Authentication Architecture](./api/AUTH_ARCHITECTURE.md)** - Complete guide to the Instagram-style multi-token authentication system
- **[JWT Configuration](./api/JWT_CONFIG.md)** - JWT token configuration and setup

### API Router Documentation

- **[Authentication Router](./api/router/authenticate/authenticate.md)** - Complete authentication endpoints documentation
- **[Profile Router](./api/router/authenticate/profile.md)** - User profile management endpoints
- **[Dashboard Router](./api/router/dashboard/dashboard.md)** - Analytics and statistics endpoints
- **[Permissions Router](./api/router/permissions/permissions.md)** - Permission and group management
- **[Upload Router](./api/router/upload/upload.md)** - File upload and media management
- **[Activity Router](./api/router/activity/activity.md)** - Activity logging and audit trail
- **[Health Router](./api/router/health/health.md)** - Health check and system monitoring

### Developer Documentation

- **[Architecture Documentation](./docs/ARCHITECTURE.md)** - System architecture and design
- **[Technical Documentation](./docs/TECHNICAL.md)** - Technical specifications and details
- **[Backend Developer Guide](./docs/BACKEND_DEVELOPER.md)** - Backend development guide
- **[Frontend Developer Guide](./docs/FRONTEND_DEVELOPER.md)** - Frontend integration guide

### Database Documentation

- **[Database README](./api/src/db/postgres/docs/README.md)** - Database overview
- **[Database Triggers](./api/src/db/postgres/docs/TRIGGERS.md)** - Database trigger documentation
- **[Database Indexes](./api/src/db/postgres/docs/INDEX.md)** - Index optimization guide
- **[Database Analytics](./api/src/db/postgres/docs/ANALYTICS.md)** - Analytics queries
- **[Database Quick Reference](./api/src/db/postgres/docs/QUICK_REFERENCE.md)** - Quick reference guide

### Kubernetes Documentation

- **[K8s README](./k8s/README.md)** - Kubernetes overview
- **[K8s Architecture](./k8s/ARCHITECTURE.md)** - Kubernetes architecture
- **[K8s Setup Guide](./k8s/SETUP.md)** - Kubernetes setup instructions
- **[K8s Quick Start](./k8s/QUICK_START.md)** - Quick start guide

## 🔐 Authentication System

### Multi-Token Architecture

The authentication system uses a **three-token approach** similar to Instagram:

1. **Access Token** (1 hour)
   - Lightweight token for API authentication
   - Minimal payload for fast validation
   - Includes JTI (JWT ID) for efficient blacklisting

2. **Session Token** (7 days) - **Recommended**
   - Contains full user profile and permissions
   - Fastest validation (no database lookup needed)
   - Preferred for frontend API calls

3. **Refresh Token** (30 days)
   - Used to obtain new tokens when they expire
   - Cannot be used for API authentication
   - Rotates on each refresh for security

**Complete Documentation**: [Authentication Architecture](./api/AUTH_ARCHITECTURE.md)

### Token Usage

**Recommended Approach (Session Token):**
```python
# Store tokens after login
{
    "access_token": "...",
    "session_token": "...",  # RECOMMENDED for API calls
    "refresh_token": "...",
    "session_id": "..."
}

# Use session_token for API calls (fastest validation)
headers = {
    "X-Session-Token": session_token  # Preferred
    # OR
    "Authorization": f"Bearer {session_token}"  # Also works
}
```

## 📄 License & Open Source

This project is **open source** and **free to use** for all purposes with **no restrictions**.

### 🎯 Open Source License

This project is released under the **[MIT License](LICENSE)**, which means:

- ✅ **Free to use** for any purpose (commercial or personal)
- ✅ **No restrictions** on usage, modification, or distribution
- ✅ **No warranty** provided
- ✅ **Attribution** is appreciated but not required

**📄 Full License Text**: See [LICENSE](LICENSE) file for complete license terms and conditions.

### 🙏 Technologies & Acknowledgments

This project is built with amazing open-source technologies. Special thanks to:

#### Core Framework & Runtime
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for building APIs with Python
- **[Python](https://www.python.org/)** - High-level programming language

#### Database & ORM
- **[PostgreSQL](https://www.postgresql.org/)** - Advanced open-source relational database
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - Python SQL toolkit and ORM
- **[Alembic](https://alembic.sqlalchemy.org/)** - Database migration tool
- **[Redis](https://redis.io/)** - In-memory data structure store

#### Security & Authentication
- **[PyJWT](https://pyjwt.readthedocs.io/)** - JSON Web Token implementation
- **[bcrypt](https://github.com/pyca/bcrypt/)** - Password hashing library
- **[passlib](https://passlib.readthedocs.io/)** - Password hashing library

#### Monitoring & Logging
- **[Sentry](https://sentry.io/)** - Error tracking and performance monitoring
- **[Python Logging](https://docs.python.org/3/library/logging.html)** - Built-in logging module

#### API Documentation
- **[Swagger/OpenAPI](https://swagger.io/)** - API documentation and testing tools
- **[FastAPI Docs](https://fastapi.tiangolo.com/features/)** - Built-in API documentation

#### Utilities & Validation
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation using Python type annotations
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** - Environment variable management

#### Communication Services
- **[Twilio](https://www.twilio.com/)** - Cloud communications platform

#### Storage
- **[Google Cloud Storage](https://cloud.google.com/storage)** - Object storage service

#### Containerization
- **[Docker](https://www.docker.com/)** - Containerization platform
- **[Docker Compose](https://docs.docker.com/compose/)** - Multi-container Docker application tool

#### Web Server
- **[Nginx](https://www.nginx.com/)** - High-performance web server and reverse proxy

### 🌟 Contributing

Contributions are welcome! This is an open-source project, and we encourage:

- 🐛 Bug reports
- 💡 Feature requests
- 📝 Documentation improvements
- 🔧 Code contributions
- ⭐ Starring the repository

### 📞 Support

For issues, questions, or contributions, please visit:
- **Repository**: [https://github.com/fullstack-open-source/fastapi-backend-with-sql](https://github.com/fullstack-open-source/fastapi-backend-with-sql)
- **Issues**: Open an issue on GitHub

---

**Made with ❤️ using open-source technologies**

*This project is free to use, modify, and distribute for any purpose without restrictions.*

---

## 📜 License

Copyright (c) 2025 Full Stack Open Source

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
