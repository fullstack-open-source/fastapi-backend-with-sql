import os
from typing import Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse

try:
    from dateutil import parser as date_parser
except ImportError:
    # Fallback to datetime parsing if dateutil not available
    date_parser = None

from fastapi import Request, Depends, HTTPException, status, Header, Query
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional

from .models import TokenData, User

from src.response.error import ERROR
from src.authenticate.session_manager import (
    is_token_blacklisted, is_session_blacklisted, is_user_blacklisted,
    is_access_token_blacklisted_by_jti, is_user_refresh_token_revoked
)
# JWT Configuration - all configurable via .env
SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')  # Default: HS256

# Get root path from environment to construct proper token URL for Swagger UI
MODE = os.environ.get('MODE', '')
token_url = f"/{MODE}/auth/login-with-password" if MODE else "/auth/login-with-password"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url, auto_error=False)
http_bearer = HTTPBearer(auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def extract_token(
    request: Request,
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    session_token: Optional[str] = Header(None, alias="X-Session-Token"),
    access_token: Optional[str] = Query(None, alias="access_token"),
    oauth_token: Optional[str] = Depends(oauth2_scheme)  # For Swagger UI compatibility (optional)
) -> Optional[str]:
    """
    Extract token from multiple sources with priority (optimized for session_token):
    1. X-Session-Token header (preferred for client-side - fastest and most secure)
    2. Authorization Bearer header (standard OAuth2)
    3. OAuth2 scheme (for Swagger UI)
    4. access_token query parameter (for backward compatibility)

    Session tokens are preferred as they contain full user profile for faster validation.
    No database lookup needed when using session_token.
    """
    # Priority 1: X-Session-Token header (preferred for client-side validation)
    # This is the fastest path as session_token has full user profile embedded
    if session_token:
        return session_token

    # Priority 2: Authorization Bearer header (standard OAuth2)
    if authorization and authorization.credentials:
        return authorization.credentials

    # Priority 3: OAuth2 scheme (for Swagger UI and standard OAuth2)
    if oauth_token:
        return oauth_token

    # Priority 4: access_token query parameter (backward compatibility)
    if access_token:
        return access_token

    # Fallback: Try to extract from Authorization header manually
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "")

    return None


async def validate_user(request: Request, token: Optional[str] = Depends(extract_token)) -> User:
    """
    Validate user token - optimized for session_token (preferred) and access_token.

    Performance Optimization:
    - Session tokens: Fastest validation (no database lookup needed - full user profile in token)
    - Access tokens: Still supported but requires minimal data extraction

    Token Sources (in priority order):
    1. X-Session-Token header (preferred for client-side - fastest)
    2. Authorization Bearer header (standard OAuth2)
    3. OAuth2 scheme (for Swagger UI)
    4. access_token query parameter (backward compatibility)

    Security:
    - All tokens are validated against blacklist (cache-based)
    - Session validation checks session_id blacklist
    - User-level blacklist support
    - Domain/origin validation
    """
    credentials_exception =  HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ERROR.build(
            error_key="UNAUTHORIZED",
            details={
                "Reason": "Missing or invalid Bearer token or Expired session",
                "WWW-Authenticate": "Bearer",
                "Tips": [
                    "Ensure your Authorization header includes a valid Bearer token (session_token or access_token)",
                    "Login again to refresh expired tokens"
                ]
            },
        )
    )

    # Check if token is provided
    if not token:
        raise credentials_exception

    try:
        # Try with audience first, fallback without if that fails
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience="authenticated")
        except JWTError:
            # Fallback: try without audience if token wasn't created with audience
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid: str = payload.get("sub")
        if uid is None:
            raise credentials_exception

        # Get token type, session_id, and user_id
        token_type = payload.get("type", "access")
        session_id = payload.get("session_id")
        user_id = payload.get("sub")

        # Validate token type - only accept access or session tokens for authentication
        if token_type not in ["access", "session"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build(
                    error_key="AUTH_INVALID_TOKEN_TYPE",
                    details={
                        "Reason": f"Token type '{token_type}' is not valid for authentication",
                        "WWW-Authenticate": "Bearer",
                        "Tips": [
                            "Use session_token or access_token for authentication",
                            "Refresh tokens cannot be used for API authentication"
                        ]
                    },
                )
            )

        # Fast blacklist checks - optimized order (fastest checks first)
        # 1. Check token blacklist first (most common, fastest check)
        if await is_token_blacklisted(token, token_type=token_type):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build(
                    error_key="TOKEN_INVALID",
                    details={
                        "Reason": "Token has been revoked",
                        "WWW-Authenticate": "Bearer",
                        "Tips": [
                            "This token has been revoked",
                            "Please login again to get a new token"
                        ]
                    },
                )
            )

        # 1b. Check JTI-based blacklist for access tokens (more efficient)
        if token_type == "access":
            token_jti = payload.get("jti")
            if token_jti and await is_access_token_blacklisted_by_jti(token_jti):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=ERROR.build(
                        error_key="TOKEN_INVALID",
                        details={
                            "Reason": "Token has been revoked",
                            "WWW-Authenticate": "Bearer",
                            "Tips": [
                                "This token has been revoked",
                                "Please login again to get a new token"
                            ]
                        },
                    )
                )

        # 2. Check session blacklist (if session_id exists)
        if session_id and await is_session_blacklisted(session_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build(
                    error_key="SESSION_INVALID",
                    details={
                        "Reason": "Session has been revoked",
                        "WWW-Authenticate": "Bearer",
                        "Tips": [
                            "Your session has been revoked or logged out",
                            "Please login again to create a new session"
                        ]
                    },
                )
            )

        # 3. Check user blacklist last (least common, but still important)
        if user_id and await is_user_blacklisted(user_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build(
                    error_key="SESSION_INVALID",
                    details={
                        "Reason": "All sessions for this user have been revoked",
                        "WWW-Authenticate": "Bearer",
                        "Tips": [
                            "Your sessions have been revoked",
                            "Please login again to create a new session"
                        ]
                    },
                )
            )

        # 4. Check if all refresh tokens for user have been revoked (complete logout)
        if user_id and await is_user_refresh_token_revoked(user_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build(
                    error_key="SESSION_INVALID",
                    details={
                        "Reason": "All refresh tokens have been revoked (user logged out)",
                        "WWW-Authenticate": "Bearer",
                        "Tips": [
                            "Your session has been invalidated",
                            "Please login again to get new tokens"
                        ]
                    },
                )
            )

        # Validate origin/domain if token contains origin claim
        token_origin = payload.get("origin")
        if token_origin:
            # Extract current request origin
            current_origin = _extract_origin_from_request(request)

            # Normalize origins for comparison (remove trailing slashes, lowercase)
            token_origin_normalized = token_origin.lower().rstrip('/')
            current_origin_normalized = current_origin.lower().rstrip('/')

            # Check if origins match
            origins_match = token_origin_normalized == current_origin_normalized

            # In development, allow localhost origins to be flexible (different ports are OK)
            api_mode = os.environ.get('API_MODE', 'development')
            if not origins_match and api_mode != 'production':
                token_parsed = urlparse(token_origin_normalized)
                current_parsed = urlparse(current_origin_normalized)

                # Allow if both are localhost/127.0.0.1 (different ports OK in dev)
                is_localhost_token = token_parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']
                is_localhost_current = current_parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']

                if is_localhost_token and is_localhost_current:
                    origins_match = True

            if not origins_match:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=ERROR.build(
                        error_key="TOKEN_DOMAIN_MISMATCH",
                        details={
                            "Reason": "Token was issued for a different domain",
                            "token_origin": token_origin,
                            "request_origin": current_origin,
                            "Tips": [
                                "Tokens are domain-specific for security",
                                "Please login again from the correct domain"
                            ]
                        },
                    )
                )

        # Parse datetime strings if they exist
        def parse_datetime(dt_str):
            if not dt_str:
                return None
            try:
                if date_parser:
                    return date_parser.parse(dt_str)
                else:
                    # Fallback to datetime.fromisoformat for Python 3.7+
                    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            except (ValueError, TypeError, AttributeError):
                return None

        # Optimized: If session_token, use full user_profile from token (no DB query needed)
        # If access_token, we have minimal data but it's still valid
        user_profile = payload.get("user_profile", {})
        permissions = payload.get("permissions", {})

        # Set user_id/uid - primary key
        user_id_value = uid or user_profile.get("user_id")

        # PERFORMANCE OPTIMIZATION: Fast path for session_token
        # Session tokens contain full user profile - no database lookup needed
        # This is the fastest validation path (recommended for client-side)
        if token_type == "session" and user_profile:
            # Session token contains complete user data - fastest validation path
            # No database query required - all user data is in the token
            token_data = TokenData(
                # Primary key
                user_id=user_id_value,
                uid=user_id_value,

                # Basic user information (from user_profile in session token)
                first_name=payload.get("first_name") or user_profile.get("first_name"),
                last_name=payload.get("last_name") or user_profile.get("last_name"),
                email=payload.get("email") or user_profile.get("email"),
                phone_number=user_profile.get("phone_number"),
                country=user_profile.get("country"),
                gender=user_profile.get("gender"),
                dob=parse_datetime(user_profile.get("dob")),
                profile_picture_url=user_profile.get("profile_picture_url"),
                bio=user_profile.get("bio"),
                portfolio_url=user_profile.get("portfolio_url"),
                user_name=payload.get("username") or user_profile.get("user_name"),

                # App settings
                show_kliky_watermark=user_profile.get("show_kliky_watermark", True),
                ads_show_type=payload.get("ads_show_type") or user_profile.get("ads_show_type"),
                wallet=payload.get("wallet"),
                display_name=payload.get("display_name"),

                # Enums
                auth_type=user_profile.get("auth_type"),
                theme=user_profile.get("theme"),
                profile_accessibility=user_profile.get("profile_accessibility"),
                user_type=user_profile.get("user_type"),
                language=user_profile.get("language"),

                # STATUSModel fields
                is_draft=user_profile.get("is_draft", False),
                is_active=permissions.get("is_active", True),
                is_verified=permissions.get("is_verified", True),
                is_deleted=user_profile.get("is_deleted", False),

                # Status and role
                status=user_profile.get("status", "INACTIVE"),
                role_id=user_profile.get("role_id"),
                timezone=user_profile.get("timezone"),
                invited_by_user_id=user_profile.get("invited_by_user_id"),

                # Protection flags
                is_protected=user_profile.get("is_protected", False),
                is_trashed=user_profile.get("is_trashed", False),

                # Timestamps
                last_sign_in_at=parse_datetime(user_profile.get("last_sign_in_at")),
                email_verified_at=parse_datetime(user_profile.get("email_verified_at")),
                created_at=parse_datetime(user_profile.get("created_at")),
                last_updated=parse_datetime(user_profile.get("last_updated")),

                # Legacy permission fields
                is_user=permissions.get("is_user", True),
                is_superuser=permissions.get("is_superuser", False),
                is_admin=permissions.get("is_admin", False),
                is_business=permissions.get("is_business", False),
                is_accountant=permissions.get("is_accountant", False),
                is_developer=permissions.get("is_developer", False),
            )
        else:
            # Access token path - minimal data, but still valid
            token_data = TokenData(
                # Primary key
                user_id=user_id_value,
                uid=user_id_value,

                # Basic user information (from access token payload)
                first_name=payload.get("first_name"),
                last_name=payload.get("last_name"),
                email=payload.get("email"),
                user_name=payload.get("username"),

                # Essential permissions from access token
                is_active=payload.get("is_active", True),
                is_verified=payload.get("is_verified", True),

                # Default values for missing fields
                is_draft=False,
                is_deleted=False,
                status="ACTIVE",
                is_protected=False,
                is_trashed=False,
                is_user=True,
                is_superuser=False,
                is_admin=False,
                is_business=False,
                is_accountant=False,
                is_developer=False,
            )

        return User(**token_data.dict())
    except JWTError:
        raise credentials_exception

def _extract_origin_from_request(request: Request) -> str:
    """
    Extract origin/domain from request headers.
    Priority: Origin header > Host header > X-Forwarded-Host
    Returns normalized origin (scheme + host only)
    """
    # Try Origin header first (most reliable for CORS)
    origin = request.headers.get("Origin")
    if origin:
        # Parse to get scheme + host
        parsed = urlparse(origin)
        return f"{parsed.scheme}://{parsed.netloc}"

    # Try Host header
    host = request.headers.get("Host")
    if host:
        # Determine scheme from request
        scheme = "https" if request.url.scheme == "https" or request.headers.get("X-Forwarded-Proto") == "https" else "http"
        return f"{scheme}://{host}"

    # Try X-Forwarded-Host (for reverse proxy scenarios)
    forwarded_host = request.headers.get("X-Forwarded-Host")
    if forwarded_host:
        scheme = request.headers.get("X-Forwarded-Proto", "https")
        return f"{scheme}://{forwarded_host}"

    # Fallback to request URL
    return f"{request.url.scheme}://{request.url.netloc}"

async def validate_request(request: Request, user: User = Depends(validate_user)):
    """
    Validate user authentication request.

    This is the FIRST check in the authentication/authorization flow.
    It validates:
    1. Token exists and is provided
    2. Token is valid (signature, expiration)
    3. Token is not blacklisted
    4. Session is not blacklisted
    5. User is not blacklisted

    After this check passes, permission/group checks can proceed.

    Returns:
        User: Authenticated user object if all checks pass

    Raises:
        HTTPException: 401 UNAUTHORIZED if authentication fails
    """
    # from src.logger.logger import logger

    user_id = str(user.uid) if hasattr(user, 'uid') else str(getattr(user, 'user_id', ''))

    return user