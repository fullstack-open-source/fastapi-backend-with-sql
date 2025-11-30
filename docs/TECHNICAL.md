# KLIKYAI V3 - Technical Documentation

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation & Setup](#installation--setup)
3. [Configuration](#configuration)
4. [Database Schema](#database-schema)
5. [API Specifications](#api-specifications)
6. [External Service Integration](#external-service-integration)
7. [Security Implementation](#security-implementation)
8. [Performance Optimization](#performance-optimization)
9. [Error Handling](#error-handling)
10. [Testing Strategy](#testing-strategy)
11. [Deployment Guide](#deployment-guide)
12. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements
- **Python**: 3.9 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 20GB available space
- **Network**: Stable internet connection for external API calls
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2

### Recommended Production Requirements
- **Python**: 3.11
- **Memory**: 16GB RAM
- **Storage**: 100GB SSD
- **CPU**: 8 cores
- **Network**: High-speed internet with low latency

### Dependencies
```txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
httpx==0.25.2
supabase==2.0.0
redis==5.0.1
firebase-admin==6.2.0
google-cloud-storage==2.10.0
python-multipart==0.0.6
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.1.2
psutil==5.9.6
```

## Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-org/klikyai-v3.git
cd klikyai-v3/api
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Database Setup
```bash
# Run database migrations
python -m alembic upgrade head
```

### 6. Start Development Server
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

#### Core Configuration
```bash
# API Configuration
API_VERSION=3.0.0
API_MODE=development
DEBUG_MODE=true
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4
```

#### Database Configuration
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key
```

#### External API Keys
```bash
# AI Service APIs
HEYGEN_API_KEY=your-heygen-api-key
LEONARDO_API_KEY=your-leonardo-api-key
OPENAI_API_KEY=your-openai-api-key
GOOGLE_API_KEY=your-google-api-key

# Firebase Configuration
FIREBASE_PROJECT_ID=your-firebase-project
FIREBASE_PRIVATE_KEY=your-firebase-private-key
FIREBASE_CLIENT_EMAIL=your-firebase-client-email
```

#### Storage Configuration
```bash
# Google Cloud Storage
GCS_BUCKET_NAME=your-gcs-bucket
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

#### Communication Services
```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SMS Configuration (Twilio)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number
```

#### Monitoring & Security
```bash
# Sentry Configuration
SENTRY_DSN=your-sentry-dsn
APP_MODE=production

# Security
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

### Configuration Files

#### Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${SUPABASE_URL}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

## Database Schema

### Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    full_name VARCHAR(255),
    avatar_url TEXT,
    phone_number VARCHAR(20),
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Generations Table
```sql
CREATE TABLE generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    generation_type VARCHAR(50) NOT NULL,
    prompt TEXT,
    model_used VARCHAR(100),
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    credits_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

#### Wallet Transactions Table
```sql
CREATE TABLE wallet_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL, -- 'credit' or 'debit'
    amount DECIMAL(10,2) NOT NULL,
    balance_after DECIMAL(10,2) NOT NULL,
    usage_type VARCHAR(50),
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Posts Table
```sql
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    content TEXT,
    media_urls TEXT[],
    tags TEXT[],
    is_public BOOLEAN DEFAULT TRUE,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Indexes
```sql
-- Performance indexes
CREATE INDEX idx_generations_user_id ON generations(user_id);
CREATE INDEX idx_generations_type ON generations(generation_type);
CREATE INDEX idx_generations_created_at ON generations(created_at);
CREATE INDEX idx_wallet_transactions_user_id ON wallet_transactions(user_id);
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_posts_created_at ON posts(created_at);
```

## API Specifications

### Authentication Endpoints

#### POST /auth/register
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user_id": "uuid",
    "email": "user@example.com",
    "is_verified": false
  }
}
```

#### POST /auth/login
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "jwt_token",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "John Doe"
    }
  }
}
```

### Avatar Generation Endpoints

#### GET /ai/heygen/avatars
**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "Avatars retrieved successfully",
  "data": {
    "avatars": [
      {
        "avatar_id": "Abigail_expressive_2024112501",
        "avatar_name": "Abigail (Upper Body)",
        "gender": "female",
        "preview_image_url": "https://...",
        "preview_video_url": "https://...",
        "premium": false
      }
    ],
    "total_avatars": 1
  }
}
```

#### POST /ai/heygen/avatar-video-generation
```json
{
  "avatar_id": "Abigail_expressive_2024112501",
  "voice_id": "voice_123",
  "text": "Hello, welcome to our presentation!",
  "dimension": "16:9",
  "quality": "high",
  "caption": true,
  "emotion": "happy"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Avatar video generated successfully",
  "data": {
    "video_id": "video_456",
    "video_url": "https://storage.googleapis.com/...",
    "thumbnail_url": "https://storage.googleapis.com/...",
    "status": "completed",
    "duration": 15.5
  }
}
```

### Health Check Endpoints

#### GET /health/services
**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "success": true,
  "message": "Health check completed. 8/8 services healthy.",
  "data": {
    "overall_status": "healthy",
    "healthy_services": 8,
    "total_services": 8,
    "services": {
      "heygen_api": {
        "status": "healthy",
        "message": "HeyGen API is working. Found 25 avatars.",
        "response_time": 245.67,
        "avatar_count": 25
      },
      "leonardo_api": {
        "status": "healthy",
        "message": "Leonardo AI API is working",
        "response_time": 189.23
      }
    }
  }
}
```

## External Service Integration

### HeyGen API Integration

#### Configuration
```python
# HeyGen API Configuration
HEYGEN_API_BASE_URL = "https://api.heygen.com/v2"
HEYGEN_API_KEY = os.environ.get("HEYGEN_API_KEY")

# Headers for all requests
headers = {
    "accept": "application/json",
    "X-API-KEY": HEYGEN_API_KEY,
    "content-type": "application/json"
}
```

#### Error Handling
```python
async def make_heygen_request(method: str, url: str, **kwargs):
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HeyGen API error: {e.response.status_code}")
        raise HTTPException(status_code=500, detail="HeyGen API error")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="HeyGen API timeout")
```

### Leonardo AI Integration

#### Configuration
```python
# Leonardo AI Configuration
LEONARDO_API_BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"
LEONARDO_API_KEY = os.environ.get("LEONARDO_API_KEY")

# Headers for all requests
headers = {
    "accept": "application/json",
    "authorization": f"Bearer {LEONARDO_API_KEY}",
    "content-type": "application/json"
}
```

#### Video Generation
```python
async def create_leonardo_video(prompt: str, model: str = "MOTION_2_0"):
    payload = {
        "prompt": prompt,
        "model": model,
        "width": 832,
        "height": 480,
        "frameInterpolation": True,
        "promptEnhance": True
    }
    
    response = await make_leonardo_request(
        "POST", 
        f"{LEONARDO_API_BASE_URL}/generations-text-to-video",
        json=payload
    )
    
    return response
```

## Security Implementation

### JWT Token Implementation
```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Token creation
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Token verification
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply rate limiting to endpoints
@router.post("/ai/heygen/avatar-video-generation")
@limiter.limit("10/minute")
async def create_avatar_video(request: Request, ...):
    # Endpoint implementation
```

### Input Validation
```python
from pydantic import BaseModel, Field, validator

class AvatarVideoRequest(BaseModel):
    avatar_id: str = Field(..., min_length=1, max_length=100)
    voice_id: str = Field(..., min_length=1, max_length=100)
    text: str = Field(..., min_length=1, max_length=1000)
    dimension: str = Field(default="16:9", regex="^(16:9|9:16|1:1)$")
    quality: str = Field(default="medium", regex="^(low|medium|high)$")
    
    @validator('text')
    def validate_text(cls, v):
        if len(v.strip()) < 1:
            raise ValueError('Text cannot be empty')
        return v.strip()
```

## Performance Optimization

### Caching Strategy
```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            
            return result
        return wrapper
    return decorator

# Usage
@cache_result(expiration=600)  # Cache for 10 minutes
async def get_heygen_avatars():
    # Expensive API call
    return await fetch_avatars_from_api()
```

### Database Connection Pooling
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Async Processing
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Thread pool for CPU-intensive tasks
executor = ThreadPoolExecutor(max_workers=4)

async def process_multiple_requests(requests):
    # Process multiple requests concurrently
    tasks = [process_single_request(req) for req in requests]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

## Error Handling

### Custom Exception Classes
```python
class KLIKYAIException(Exception):
    """Base exception for KLIKYAI application"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class APIKeyMissingError(KLIKYAIException):
    """Raised when required API key is missing"""
    pass

class ExternalAPIError(KLIKYAIException):
    """Raised when external API call fails"""
    pass

class InsufficientCreditsError(KLIKYAIException):
    """Raised when user has insufficient credits"""
    pass
```

### Global Error Handler
```python
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(KLIKYAIException)
async def klikyai_exception_handler(request: Request, exc: KLIKYAIException):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "type": exc.__class__.__name__
            }
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "type": "HTTPException"
            }
        }
    )
```

## Testing Strategy

### Unit Tests
```python
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_user():
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "full_name": "Test User"
    }

async def test_avatar_generation(client, mock_user):
    with patch('router.generativeai.avatar.utils.heygen_create_video') as mock_create:
        mock_create.return_value = {
            "video_id": "test-video-id",
            "status": "completed",
            "video_url": "https://example.com/video.mp4"
        }
        
        response = client.post(
            "/ai/heygen/avatar-video-generation",
            json={
                "avatar_id": "test-avatar",
                "voice_id": "test-voice",
                "text": "Hello world"
            },
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "video_id" in response.json()["data"]
```

### Integration Tests
```python
async def test_health_check_integration(client):
    """Test health check endpoint with real external API calls"""
    response = client.get("/health/services")
    
    assert response.status_code == 200
    data = response.json()
    assert "services" in data["data"]
    assert "overall_status" in data["data"]
```

### Load Testing
```python
# Using locust for load testing
from locust import HttpUser, task, between

class KLIKYAIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login and get token
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
        self.token = response.json()["data"]["access_token"]
    
    @task(3)
    def get_avatars(self):
        self.client.get(
            "/ai/heygen/avatars",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def generate_avatar_video(self):
        self.client.post(
            "/ai/heygen/avatar-video-generation",
            json={
                "avatar_id": "test-avatar",
                "voice_id": "test-voice",
                "text": "Test generation"
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

## Deployment Guide

### Production Deployment

#### 1. Environment Setup
```bash
# Set production environment variables
export API_MODE=production
export DEBUG_MODE=false
export LOG_LEVEL=INFO
export WORKERS=4
```

#### 2. Database Migration
```bash
# Run database migrations
python -m alembic upgrade head
```

#### 3. Start Production Server
```bash
# Using Gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

#### 4. Nginx Configuration
```nginx
# /etc/nginx/sites-available/klikyai
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /path/to/static/files;
    }
}
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Scale the application
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

### Kubernetes Deployment
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

## Troubleshooting

### Common Issues

#### 1. External API Timeouts
```python
# Increase timeout for external API calls
async with httpx.AsyncClient(timeout=60) as client:
    response = await client.get(url)
```

#### 2. Database Connection Issues
```python
# Check database connection
try:
    with db as cursor:
        cursor.execute("SELECT 1")
        print("Database connection successful")
except Exception as e:
    print(f"Database connection failed: {e}")
```

#### 3. Memory Issues
```python
# Monitor memory usage
import psutil
memory_percent = psutil.virtual_memory().percent
if memory_percent > 90:
    logger.warning(f"High memory usage: {memory_percent}%")
```

### Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### Monitoring Commands
```bash
# Check application status
curl http://localhost:8000/health

# Check specific service health
curl http://localhost:8000/health/heygen

# Monitor logs
tail -f logs/app.log

# Check database connections
ps aux | grep postgres
```

This technical documentation provides comprehensive information about the KLIKYAI V3 system, including setup, configuration, API specifications, and troubleshooting guides. It serves as a reference for developers working on the system and for system administrators managing the deployment.
