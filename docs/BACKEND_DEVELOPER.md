# KLIKYAI V3 - Backend Developer Documentation

## Table of Contents
1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Development Environment](#development-environment)
4. [Code Standards](#code-standards)
5. [API Development](#api-development)
6. [Database Operations](#database-operations)
7. [External Service Integration](#external-service-integration)
8. [Authentication & Authorization](#authentication--authorization)
9. [Error Handling](#error-handling)
10. [Testing](#testing)
11. [Debugging](#debugging)
12. [Performance Optimization](#performance-optimization)
13. [Deployment](#deployment)

## Getting Started

### Prerequisites
- Python 3.9+
- Git
- Docker (optional)
- PostgreSQL/Supabase account
- External API keys (HeyGen, Leonardo AI, OpenAI, Google)

### Initial Setup
```bash
# Clone the repository
git clone https://github.com/your-org/klikyai-v3.git
cd klikyai-v3/api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
python -m alembic upgrade head

# Start development server
uvicorn server:app --reload
```

## Project Structure

```
api/
├── router/                          # API route modules
│   ├── authenticate/               # Authentication endpoints
│   │   ├── authenticate.py        # Login/register logic
│   │   ├── models.py              # Auth data models
│   │   └── utils.py               # Auth utilities
│   ├── generativeai/              # AI generation endpoints
│   │   ├── avatar/               # Avatar generation
│   │   │   ├── api.py           # Avatar endpoints
│   │   │   ├── models.py        # Avatar models
│   │   │   ├── utils.py         # Avatar utilities
│   │   │   └── query.py         # Database queries
│   │   ├── chat/                 # Chat endpoints
│   │   ├── x_to_image/          # Image generation
│   │   └── x_to_video/          # Video generation
│   ├── health/                   # Health check endpoints
│   ├── payments/                 # Payment processing
│   ├── posts/                    # Post management
│   └── wallets/                  # Wallet management
├── src/                          # Core source code
│   ├── authenticate/            # Authentication core
│   ├── cache/                   # Caching utilities
│   ├── db/                      # Database connections
│   ├── email/                   # Email services
│   ├── logger/                  # Logging configuration
│   ├── middleware/              # Custom middleware
│   ├── response/               # Response utilities
│   ├── upload/                 # File upload handling
│   └── wallet/                 # Wallet core logic
├── docs/                        # Documentation
├── tests/                       # Test files
├── server.py                    # Main application
├── requirements.txt             # Python dependencies
└── .env.example                # Environment template
```

## Development Environment

### IDE Setup (VS Code)
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.9
  
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
```

### Development Scripts
```bash
# Start development server with auto-reload
make dev

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Run type checking
make type-check
```

## Code Standards

### Python Style Guide
- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Use descriptive variable and function names
- Keep functions small and focused (max 50 lines)
- Use docstrings for all public functions and classes

### Example Code Structure
```python
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from src.authenticate.authenticate import validate_request
from src.authenticate.models import User
from src.response.success import SUCCESS
from src.response.error import ERROR

router = APIRouter()

class ExampleRequest(BaseModel):
    """Request model for example endpoint."""
    name: str = Field(..., description="Name of the item")
    value: int = Field(..., ge=0, description="Value must be non-negative")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "example_item",
                "value": 42
            }
        }

@router.post("/example")
@ai_endpoint("example_action")
async def create_example(
    request: ExampleRequest,
    current_user: User = Depends(validate_request)
) -> Dict[str, Any]:
    """
    Create a new example item.
    
    Args:
        request: Example request data
        current_user: Authenticated user
        
    Returns:
        Success response with created item data
        
    Raises:
        HTTPException: If creation fails
    """
    try:
        # Business logic here
        result = await process_example(request, current_user)
        
        return SUCCESS.response(
            message="Example created successfully",
            data=result,
            meta={"user_id": current_user.uid}
        )
        
    except Exception as e:
        logger.error(f"Example creation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                error_key="EXAMPLE_CREATION_FAILED",
                details={"user_id": current_user.uid},
                exception=str(e)
            )
        )
```

### Error Handling Standards
```python
# Always use structured error responses
try:
    result = await risky_operation()
except SpecificException as e:
    raise HTTPException(
        status_code=400,
        detail=ERROR.build(
            error_key="SPECIFIC_ERROR",
            details={"context": "additional_info"},
            exception=str(e)
        )
    )
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail=ERROR.build(
            error_key="UNEXPECTED_ERROR",
            details={},
            exception=str(e)
        )
    )
```

## API Development

### Creating New Endpoints

#### 1. Define Request/Response Models
```python
# models.py
from pydantic import BaseModel, Field
from typing import Optional, List

class NewFeatureRequest(BaseModel):
    """Request model for new feature."""
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    tags: List[str] = Field(default_factory=list)
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

class NewFeatureResponse(BaseModel):
    """Response model for new feature."""
    id: str
    title: str
    description: Optional[str]
    tags: List[str]
    created_at: str
    user_id: str
```

#### 2. Create Service Functions
```python
# utils.py
from typing import Dict, Any
from src.db.postgres.postgres import connection as db
from src.logger.logger import logger

async def create_new_feature(
    request_data: Dict[str, Any],
    user_id: str
) -> Dict[str, Any]:
    """
    Create a new feature in the database.
    
    Args:
        request_data: Feature data from request
        user_id: ID of the user creating the feature
        
    Returns:
        Created feature data
        
    Raises:
        Exception: If database operation fails
    """
    try:
        with db as cursor:
            cursor.execute("""
                INSERT INTO features (title, description, tags, user_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id, title, description, tags, created_at
            """, (
                request_data["title"],
                request_data["description"],
                request_data["tags"],
                user_id
            ))
            
            result = cursor.fetchone()
            
            return {
                "id": str(result[0]),
                "title": result[1],
                "description": result[2],
                "tags": result[3],
                "created_at": result[4].isoformat(),
                "user_id": user_id
            }
            
    except Exception as e:
        logger.error(f"Failed to create feature: {str(e)}")
        raise
```

#### 3. Create API Endpoint
```python
# api.py
from fastapi import APIRouter, Depends, HTTPException
from src.authenticate.authenticate import validate_request
from src.authenticate.models import User
from src.response.success import SUCCESS
from src.response.error import ERROR
from src.documentation import ai_endpoint
from .models import NewFeatureRequest, NewFeatureResponse
from .utils import create_new_feature

router = APIRouter()

@router.post("/new-feature", response_model=Dict[str, Any])
@ai_endpoint("new_feature_create")
async def create_feature(
    request: NewFeatureRequest,
    current_user: User = Depends(validate_request)
) -> Dict[str, Any]:
    """
    Create a new feature.
    
    This endpoint allows authenticated users to create new features
    with title, description, and tags.
    """
    try:
        # Convert Pydantic model to dict
        request_data = request.dict()
        
        # Call service function
        result = await create_new_feature(request_data, current_user.uid)
        
        return SUCCESS.response(
            message="Feature created successfully",
            data=result,
            meta={"user_id": current_user.uid}
        )
        
    except Exception as e:
        logger.error(f"Feature creation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=ERROR.build(
                error_key="FEATURE_CREATION_FAILED",
                details={"user_id": current_user.uid},
                exception=str(e)
            )
        )
```

#### 4. Add Router to Main App
```python
# server.py
from router.new_feature.api import router as new_feature_router

app.include_router(
    new_feature_router,
    tags=["New Feature"]
)
```

### API Documentation
```python
# Use docstrings for automatic OpenAPI documentation
@router.post("/example")
async def example_endpoint(
    request: ExampleRequest,
    current_user: User = Depends(validate_request)
):
    """
    Example endpoint with detailed documentation.
    
    This endpoint demonstrates proper documentation practices:
    
    - Clear description of what the endpoint does
    - Parameter descriptions
    - Return value descriptions
    - Error conditions
    
    Args:
        request: The request payload containing example data
        current_user: The authenticated user making the request
        
    Returns:
        A success response containing the processed data
        
    Raises:
        HTTPException: If the request is invalid or processing fails
        
    Example:
        ```json
        {
            "name": "example",
            "value": 42
        }
        ```
    """
    pass
```

## Database Operations

### Database Connection
```python
from src.db.postgres.postgres import connection as db

# Using context manager (recommended)
with db as cursor:
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()

# Manual connection management
cursor = db.cursor()
try:
    cursor.execute("INSERT INTO table VALUES (%s)", (value,))
    db.commit()
finally:
    cursor.close()
```

### Query Patterns
```python
# Single record query
async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    with db as cursor:
        cursor.execute("""
            SELECT id, email, full_name, created_at
            FROM users 
            WHERE id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                "id": result[0],
                "email": result[1],
                "full_name": result[2],
                "created_at": result[3].isoformat()
            }
        return None

# Multiple records query
async def get_user_posts(user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    with db as cursor:
        cursor.execute("""
            SELECT id, title, content, created_at
            FROM posts 
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (user_id, limit, offset))
        
        results = cursor.fetchall()
        return [
            {
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "created_at": row[3].isoformat()
            }
            for row in results
        ]

# Insert with return
async def create_post(user_id: str, title: str, content: str) -> Dict[str, Any]:
    with db as cursor:
        cursor.execute("""
            INSERT INTO posts (user_id, title, content)
            VALUES (%s, %s, %s)
            RETURNING id, title, content, created_at
        """, (user_id, title, content))
        
        result = cursor.fetchone()
        return {
            "id": result[0],
            "title": result[1],
            "content": result[2],
            "created_at": result[3].isoformat()
        }
```

### Transaction Management
```python
async def transfer_credits(from_user: str, to_user: str, amount: int):
    """Transfer credits between users with transaction safety."""
    with db as cursor:
        try:
            # Start transaction
            cursor.execute("BEGIN")
            
            # Check sender balance
            cursor.execute("SELECT balance FROM wallets WHERE user_id = %s", (from_user,))
            sender_balance = cursor.fetchone()[0]
            
            if sender_balance < amount:
                raise ValueError("Insufficient balance")
            
            # Deduct from sender
            cursor.execute("""
                UPDATE wallets 
                SET balance = balance - %s 
                WHERE user_id = %s
            """, (amount, from_user))
            
            # Add to receiver
            cursor.execute("""
                UPDATE wallets 
                SET balance = balance + %s 
                WHERE user_id = %s
            """, (amount, to_user))
            
            # Record transaction
            cursor.execute("""
                INSERT INTO wallet_transactions 
                (user_id, transaction_type, amount, description)
                VALUES (%s, 'debit', %s, 'Transfer to user %s')
            """, (from_user, amount, to_user))
            
            cursor.execute("""
                INSERT INTO wallet_transactions 
                (user_id, transaction_type, amount, description)
                VALUES (%s, 'credit', %s, 'Transfer from user %s')
            """, (to_user, amount, from_user))
            
            # Commit transaction
            cursor.execute("COMMIT")
            
        except Exception as e:
            # Rollback on error
            cursor.execute("ROLLBACK")
            raise
```

## External Service Integration

### HeyGen API Integration
```python
import httpx
from typing import Dict, Any

class HeyGenService:
    def __init__(self):
        self.api_key = os.environ.get("HEYGEN_API_KEY")
        self.base_url = "https://api.heygen.com/v2"
    
    async def get_avatars(self) -> Dict[str, Any]:
        """Fetch available avatars from HeyGen."""
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {
                "accept": "application/json",
                "X-API-KEY": self.api_key
            }
            
            response = await client.get(f"{self.base_url}/avatars", headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def create_video(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create avatar video using HeyGen API."""
        async with httpx.AsyncClient(timeout=60) as client:
            headers = {
                "accept": "application/json",
                "X-API-KEY": self.api_key,
                "content-type": "application/json"
            }
            
            response = await client.post(
                f"{self.base_url}/video/av4/generate",
                json=request_data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """Get video generation status."""
        async with httpx.AsyncClient(timeout=30) as client:
            headers = {
                "accept": "application/json",
                "X-API-KEY": self.api_key
            }
            
            response = await client.get(
                f"{self.base_url}/video/{video_id}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()

# Usage in endpoints
heygen_service = HeyGenService()

@router.post("/avatar-video")
async def create_avatar_video(request: AvatarVideoRequest):
    try:
        # Convert request to HeyGen format
        heygen_data = {
            "avatar_id": request.avatar_id,
            "voice_id": request.voice_id,
            "text": request.text,
            "dimension": request.dimension,
            "quality": request.quality
        }
        
        # Call HeyGen API
        result = await heygen_service.create_video(heygen_data)
        
        return SUCCESS.response(
            message="Video generation started",
            data=result
        )
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=500,
            detail=f"HeyGen API error: {e.response.status_code}"
        )
```

### Leonardo AI Integration
```python
class LeonardoService:
    def __init__(self):
        self.api_key = os.environ.get("LEONARDO_API_KEY")
        self.base_url = "https://cloud.leonardo.ai/api/rest/v1"
    
    async def generate_image(self, prompt: str, model: str = "LEONARDO") -> Dict[str, Any]:
        """Generate image using Leonardo AI."""
        async with httpx.AsyncClient(timeout=60) as client:
            headers = {
                "accept": "application/json",
                "authorization": f"Bearer {self.api_key}",
                "content-type": "application/json"
            }
            
            payload = {
                "prompt": prompt,
                "model": model,
                "width": 832,
                "height": 480,
                "num_images": 1
            }
            
            response = await client.post(
                f"{self.base_url}/generations",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    
    async def poll_generation_status(self, generation_id: str) -> Dict[str, Any]:
        """Poll generation status until completion."""
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            async with httpx.AsyncClient(timeout=30) as client:
                headers = {
                    "accept": "application/json",
                    "authorization": f"Bearer {self.api_key}"
                }
                
                response = await client.get(
                    f"{self.base_url}/generations/{generation_id}",
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "COMPLETE":
                    return data
                elif data.get("status") == "FAILED":
                    raise Exception("Generation failed")
                
                await asyncio.sleep(10)
                attempt += 1
        
        raise Exception("Generation timeout")
```

## Authentication & Authorization

### JWT Token Implementation
```python
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.secret_key = os.environ.get("JWT_SECRET_KEY")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return user ID."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return user_id
        except JWTError:
            return None

# Authentication dependency
async def validate_request(token: str = Depends(oauth2_scheme)) -> User:
    """Validate JWT token and return user."""
    auth_service = AuthService()
    user_id = auth_service.verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
```

### Role-Based Access Control
```python
from enum import Enum

class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

def require_role(required_role: UserRole):
    """Decorator to require specific user role."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            if current_user.role != required_role.value:
                raise HTTPException(
                    status_code=403,
                    detail=f"Role {required_role.value} required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
@router.delete("/admin/users/{user_id}")
@require_role(UserRole.ADMIN)
async def delete_user(user_id: str, current_user: User = Depends(validate_request)):
    """Delete user (admin only)."""
    pass
```

## Error Handling

### Custom Exception Classes
```python
class KLIKYAIException(Exception):
    """Base exception for KLIKYAI application."""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(KLIKYAIException):
    """Raised when input validation fails."""
    pass

class ExternalAPIError(KLIKYAIException):
    """Raised when external API call fails."""
    pass

class InsufficientCreditsError(KLIKYAIException):
    """Raised when user has insufficient credits."""
    pass

class RateLimitExceededError(KLIKYAIException):
    """Raised when rate limit is exceeded."""
    pass
```

### Global Error Handlers
```python
from fastapi import Request
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
                "details": exc.details,
                "type": exc.__class__.__name__
            }
        }
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": exc.message,
                "details": exc.details,
                "type": "ValidationError"
            }
        }
    )
```

### Error Logging
```python
import logging
from src.logger.logger import logger

async def risky_operation():
    try:
        # Risky operation
        result = await external_api_call()
        return result
    except httpx.HTTPStatusError as e:
        logger.error(
            f"External API error: {e.response.status_code}",
            extra={
                "status_code": e.response.status_code,
                "response_text": e.response.text,
                "url": str(e.request.url)
            }
        )
        raise ExternalAPIError(
            f"External API returned {e.response.status_code}",
            error_code="EXTERNAL_API_ERROR",
            details={
                "status_code": e.response.status_code,
                "url": str(e.request.url)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error in risky_operation: {str(e)}")
        raise KLIKYAIException(
            "An unexpected error occurred",
            error_code="UNEXPECTED_ERROR"
        )
```

## Testing

### Unit Testing
```python
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_user():
    return User(
        id="test-user-id",
        email="test@example.com",
        full_name="Test User"
    )

@pytest.fixture
def auth_headers(mock_user):
    return {"Authorization": f"Bearer {create_test_token(mock_user.id)}"}

async def test_create_avatar_video(client, auth_headers):
    """Test avatar video creation endpoint."""
    with patch('router.generativeai.avatar.utils.heygen_create_video') as mock_create:
        mock_create.return_value = {
            "video_id": "test-video-id",
            "status": "pending"
        }
        
        response = client.post(
            "/ai/heygen/avatar-video-generation",
            json={
                "avatar_id": "test-avatar",
                "voice_id": "test-voice",
                "text": "Hello world"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "video_id" in data["data"]

async def test_insufficient_credits(client, auth_headers):
    """Test handling of insufficient credits."""
    with patch('src.wallet.wallet.check_wallet_balance') as mock_balance:
        mock_balance.return_value = 0
        
        response = client.post(
            "/ai/heygen/avatar-video-generation",
            json={
                "avatar_id": "test-avatar",
                "voice_id": "test-voice",
                "text": "Hello world"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "insufficient" in data["error"]["message"].lower()
```

### Integration Testing
```python
async def test_health_check_integration(client):
    """Test health check with real external API calls."""
    response = client.get("/health/services")
    
    assert response.status_code == 200
    data = response.json()
    assert "services" in data["data"]
    assert "overall_status" in data["data"]

async def test_database_integration():
    """Test database operations."""
    with db as cursor:
        # Test insert
        cursor.execute("""
            INSERT INTO test_table (name, value) 
            VALUES (%s, %s) 
            RETURNING id
        """, ("test", 42))
        
        test_id = cursor.fetchone()[0]
        
        # Test select
        cursor.execute("SELECT * FROM test_table WHERE id = %s", (test_id,))
        result = cursor.fetchone()
        
        assert result is not None
        assert result[1] == "test"
        assert result[2] == 42
        
        # Cleanup
        cursor.execute("DELETE FROM test_table WHERE id = %s", (test_id,))
```

### Test Configuration
```python
# conftest.py
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_db():
    """Create test database connection."""
    engine = create_engine("sqlite:///test.db")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()
```

## Debugging

### Logging Configuration
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'logs/app.log',
                maxBytes=10485760,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    # Set specific loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
```

### Debug Endpoints
```python
@router.get("/debug/info")
async def debug_info(current_user: User = Depends(validate_request)):
    """Debug endpoint for development."""
    if os.environ.get("DEBUG_MODE") != "true":
        raise HTTPException(status_code=404, detail="Not found")
    
    return {
        "user": {
            "id": current_user.uid,
            "email": current_user.email
        },
        "environment": {
            "api_mode": os.environ.get("API_MODE"),
            "debug_mode": os.environ.get("DEBUG_MODE")
        },
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Performance Monitoring
```python
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {str(e)}")
            raise
    return wrapper

# Usage
@monitor_performance
async def expensive_operation():
    # Expensive operation
    pass
```

## Performance Optimization

### Caching Strategy
```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration: int = 300, key_prefix: str = ""):
    """Cache function result with expiration."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            try:
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    return json.loads(cached_result)
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            
            try:
                redis_client.setex(cache_key, expiration, json.dumps(result))
            except Exception as e:
                logger.warning(f"Cache write failed: {e}")
            
            return result
        return wrapper
    return decorator

# Usage
@cache_result(expiration=600, key_prefix="avatars:")
async def get_heygen_avatars():
    # Expensive API call
    pass
```

### Database Optimization
```python
# Use connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Use prepared statements
async def get_user_posts_optimized(user_id: str, limit: int = 20):
    """Optimized query with prepared statement."""
    with db as cursor:
        cursor.execute("""
            SELECT p.id, p.title, p.content, p.created_at, u.username
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.user_id = %s
            ORDER BY p.created_at DESC
            LIMIT %s
        """, (user_id, limit))
        
        return cursor.fetchall()
```

### Async Optimization
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Thread pool for CPU-intensive tasks
executor = ThreadPoolExecutor(max_workers=4)

async def process_multiple_requests(requests):
    """Process multiple requests concurrently."""
    tasks = [process_single_request(req) for req in requests]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle exceptions
    successful_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Request processing failed: {result}")
        else:
            successful_results.append(result)
    
    return successful_results

def cpu_intensive_task(data):
    """CPU-intensive task that runs in thread pool."""
    # Heavy computation
    return processed_data

async def async_cpu_task(data):
    """Run CPU-intensive task asynchronously."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, cpu_intensive_task, data)
```

## Deployment

### Environment Configuration
```bash
# Production environment variables
export API_MODE=production
export DEBUG_MODE=false
export LOG_LEVEL=INFO
export WORKERS=4
export DATABASE_URL=postgresql://user:pass@host:port/db
export REDIS_URL=redis://host:port
```

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Server
```bash
# Using Gunicorn with Uvicorn workers
gunicorn server:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    -b 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
```

### Health Checks
```python
# Health check endpoint for load balancer
@app.get("/health")
async def health_check():
    """Simple health check for load balancer."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Detailed health check
@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with service status."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check database
    try:
        with db as cursor:
            cursor.execute("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Redis
    try:
        redis_client.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status
```

This backend developer documentation provides comprehensive guidance for developers working on the KLIKYAI V3 system, covering everything from initial setup to advanced deployment strategies.
