import os
import re
import uuid
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import jwt
from fastapi import Request

from src.db.postgres.postgres import connection as db
from src.logger.logger import logger
from src.authenticate.session_manager import (
    ACCESS_TOKEN_EXPIRY,
    SESSION_TOKEN_EXPIRY,
    REFRESH_TOKEN_EXPIRY
)

import bcrypt

# Salt rounds for bcrypt (matching NodeJS) - configurable via .env
BCRYPT_SALT_ROUNDS = int(os.environ.get('BCRYPT_SALT_ROUNDS', '10'))

# JWT Configuration - all configurable via .env
SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')  # Default: HS256, can be HS256, HS384, HS512, RS256, etc.

# Email and phone validators
email_validator = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
phone_validator = re.compile(r'^\+?[1-9]\d{1,14}$')


def verify_password(plain_password: str, hashed_password: str) -> bool:

    if not hashed_password or not plain_password:
        return False

    try:
        # Try bcrypt first (new format)
        # bcrypt hashes start with $2a$, $2b$, or $2y$
        if hashed_password.startswith('$2'):
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )

        # Legacy PBKDF2 support (for backward compatibility with old passwords)
        # PBKDF2 hashes start with pbkdf2_sha256$
        if hashed_password.startswith('pbkdf2_sha256$'):
            try:
                # Try to use passlib for PBKDF2 verification (if available)
                from passlib.context import CryptContext
                pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
                return pwd_context.verify(plain_password, hashed_password)
            except (ImportError, Exception) as e:
                logger.warning(f"Legacy PBKDF2 password verification not available: {e}", module="Auth", label="PASSWORD_VERIFY")
                return False

        # Unknown hash format
        logger.warning(f"Unknown password hash format: {hashed_password[:20]}...", module="Auth", label="PASSWORD_VERIFY")
        return False

    except Exception as e:
        logger.error(f"Password verification error: {e}", module="Auth", label="PASSWORD_VERIFY", exc_info=True)
        return False


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt (matching NodeJS implementation).
    Uses 10 salt rounds like NodeJS bcryptjs.
    """
    try:
        # Generate salt and hash password (matching NodeJS bcryptjs.hashSync)
        hashed = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt(rounds=BCRYPT_SALT_ROUNDS)
        )
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Password hashing error: {e}", module="Auth", label="PASSWORD_HASH", exc_info=True)
        raise


def get_user_by_email_or_phone(identifier: str) -> Optional[Dict[str, Any]]:
    """
    Get user from database by email or phone number.
    Returns user dict or None if not found.
    """
    try:
        with db as cursor:
            # Determine if identifier is email or phone
            if "@" in identifier:
                # Email lookup (case-insensitive)
                # Only select columns that actually exist in the User table
                query = """
                    SELECT user_id, email, password, first_name, last_name, user_name,
                           phone_number, is_active, is_verified, status,
                           profile_picture_url, country, dob, bio, theme,
                           profile_accessibility, user_type, language, timezone,
                           last_sign_in_at, email_verified_at, created_at, last_updated,
                           is_protected, is_trashed, auth_type, invited_by_user_id
                    FROM public."user"
                    WHERE LOWER(email) = LOWER(%s)
                    LIMIT 1
                """
                cursor.execute(query, (identifier,))
            else:
                # Phone number lookup (handle JSON field)
                # Only select columns that actually exist in the User table
                query = """
                    SELECT user_id, email, password, first_name, last_name, user_name,
                           phone_number, is_active, is_verified, status,
                           profile_picture_url, country, dob, bio, theme,
                           profile_accessibility, user_type, language, timezone,
                           last_sign_in_at, email_verified_at, created_at, last_updated,
                           is_protected, is_trashed, auth_type, invited_by_user_id
                    FROM public."user"
                    WHERE phone_number->>'phone' LIKE %s OR phone_number->>'phone' LIKE %s
                    LIMIT 1
                """
                phone_clean = identifier.strip().replace("+", "")
                cursor.execute(query, (f'%{phone_clean}%', f'%+{phone_clean}%'))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    except Exception as e:
        logger.error(f"Error fetching user: {e}", exc_info=True, module="Auth", label="FETCH_USER")
        return None


def check_user_availability_in_db(identifier: str) -> Optional[Dict[str, Any]]:
    """
    Check if a user is available (not taken) in the database.
    Returns True if available (user doesn't exist), False if not available (user exists).
    """
    try:
        with db as cursor:
            if "@" in identifier:
                query = """
                    SELECT first_name FROM public."user" WHERE LOWER(email) = LOWER(%s)
                """
                cursor.execute(query, (identifier,))
                return True
            else:
                query = """
                    SELECT first_name FROM public."user" WHERE phone_number::text LIKE %s OR phone_number::text LIKE %s
                """
                phone_clean = identifier.strip().replace("+", "")
                cursor.execute(query, (f'%{phone_clean}%', f'%+{phone_clean}%'))
                return True

        return False
    except Exception as e:
        logger.error(f"Error checking user availability: {e}", exc_info=True, module="Auth", label="CHECK_AVAILABILITY")
        return False


def authenticate_user(identifier: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate a user by email/phone and password.
    Returns user dict if authentication successful, None otherwise.
    """
    try:
        # Get user from database
        user = get_user_by_email_or_phone(identifier)

        if not user:
            logger.warning(f"User not found: {identifier}", module="Auth", label="AUTH_FAILED")
            return None

        # Check if user is active and verified
        if not user.get('is_active') or not user.get('is_verified'):
            logger.warning(f"User account not active or verified: {identifier}", module="Auth", label="AUTH_FAILED")
            return None

        hashed_password = user.get('password')
        if not hashed_password:
            logger.warning(f"User has no password set: {identifier}", module="Auth", label="AUTH_FAILED")
            return None

        if not verify_password(password, hashed_password):
            logger.warning(f"Invalid password for user: {identifier}", module="Auth", label="AUTH_FAILED")
            return None

        # Update last sign in asynchronously (non-blocking for faster response)
        # This doesn't block the login response
        try:
            update_last_sign_in(str(user['user_id']))
        except Exception as e:
            # Log but don't fail login if this fails
            logger.warning(f"Failed to update last_sign_in: {e}", module="Auth", label="UPDATE_SIGN_IN")

        return user

    except Exception as e:
        logger.error(f"Authentication error: {e}", exc_info=True, module="Auth", label="AUTH_ERROR")
        return None


def update_last_sign_in(user_id: str):
    """Update user's last sign in timestamp"""
    try:
        with db as cursor:
            query = """
                UPDATE public."user"
                SET last_sign_in_at = NOW()
                WHERE user_id::text = %s
            """
            cursor.execute(query, (str(user_id),))
    except Exception as e:
        logger.error(f"Error updating last sign in: {e}", module="Auth", label="UPDATE_SIGN_IN")
        # Don't fail authentication if this fails


def update_user_verification_status(user_id: str, channel: str):
    """
    Update user verification status based on channel (email or phone).
    Similar to update_last_sign_in, but updates verification fields.

    Args:
        user_id: User ID (UUID string)
        channel: Verification channel - "email", "sms", or "whatsapp"
                 - "email" -> updates is_email_verified and email_verified_at
                 - "sms" or "whatsapp" -> updates is_phone_verified and phone_number_verified_at

    Returns:
        bool: True if successful, False otherwise

    Note:
        - Does not raise exceptions (graceful failure)
        - Updates is_verified to True if email or phone is verified
        - Updates appropriate timestamp field
    """
    try:
        with db as cursor:
            # Normalize channel
            channel_lower = channel.lower() if channel else ""

            if channel_lower == "email":
                # Verify email
                query = """
                    UPDATE public."user"
                    SET is_email_verified = TRUE,
                        email_verified_at = NOW(),
                        is_verified = TRUE,
                        last_updated = NOW()
                    WHERE user_id::text = %s
                """
                cursor.execute(query, (str(user_id),))
                return True

            elif channel_lower in ["sms", "whatsapp"]:
                # Verify phone
                query = """
                    UPDATE public."user"
                    SET is_phone_verified = TRUE,
                        phone_number_verified_at = NOW(),
                        is_verified = TRUE,
                        last_updated = NOW()
                    WHERE user_id::text = %s
                """
                cursor.execute(query, (str(user_id),))
                return True
            else:
                logger.warning(f"Invalid channel for verification update: {channel} (user: {user_id})", module="Auth", label="UPDATE_VERIFICATION")
                return False

    except Exception as e:
        logger.error(f"Error updating verification status: {e}", exc_info=True, module="Auth", label="UPDATE_VERIFICATION")
        # Don't fail authentication if this fails
        return False


def _build_user_profile_payload(user: Dict[str, Any]) -> Dict[str, Any]:
    """Build user profile payload for tokens - only uses columns that exist in User table"""
    return {
            # Primary key
            'user_id': str(user.get('user_id')),

            # Basic user information (matching USERList)
            'email': user.get('email'),
            'first_name': user.get('first_name'),
            'last_name': user.get('last_name'),
            'user_name': user.get('user_name'),
            'phone_number': user.get('phone_number'),
            'country': user.get('country'),
        'dob': user.get('dob').isoformat() if user.get('dob') and hasattr(user.get('dob'), 'isoformat') else (user.get('dob') if user.get('dob') else None),
            'profile_picture_url': user.get('profile_picture_url'),
            'bio': user.get('bio'),

            # Enums
            'auth_type': user.get('auth_type'),
            'theme': user.get('theme'),
            'profile_accessibility': user.get('profile_accessibility'),
            'user_type': user.get('user_type'),
            'language': user.get('language'),

            # Status and role
            'status': user.get('status', 'INACTIVE'),
            'timezone': user.get('timezone'),
            'invited_by_user_id': str(user.get('invited_by_user_id')) if user.get('invited_by_user_id') else None,

            # Protection flags
            'is_protected': user.get('is_protected', False),
            'is_trashed': user.get('is_trashed', False),

            # Timestamps
        'last_sign_in_at': user.get('last_sign_in_at').isoformat() if user.get('last_sign_in_at') and hasattr(user.get('last_sign_in_at'), 'isoformat') else (user.get('last_sign_in_at') if user.get('last_sign_in_at') else None),
        'email_verified_at': user.get('email_verified_at').isoformat() if user.get('email_verified_at') and hasattr(user.get('email_verified_at'), 'isoformat') else (user.get('email_verified_at') if user.get('email_verified_at') else None),
        'created_at': user.get('created_at').isoformat() if user.get('created_at') and hasattr(user.get('created_at'), 'isoformat') else (user.get('created_at') if user.get('created_at') else None),
        'last_updated': user.get('last_updated').isoformat() if user.get('last_updated') and hasattr(user.get('last_updated'), 'isoformat') else (user.get('last_updated') if user.get('last_updated') else None),
    }


def _build_permissions_payload(user: Dict[str, Any]) -> Dict[str, Any]:
    """Build permissions payload for tokens - permissions come from Group/Permission relationships, not User table"""
    # These fields don't exist in User table - they should come from Group/Permission relationships
    # For now, return defaults. In the future, these should be fetched from UserGroup -> Group -> GroupPermission -> Permission
    return {
        'is_active': user.get('is_active', True),
        'is_verified': user.get('is_verified', True),
    }


def generate_access_token(user: Dict[str, Any], origin: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """
    Generate short-lived access token (1 hour) - Optimized for speed
    Minimal payload for faster token generation and validation
    """
    try:
        now = datetime.utcnow()
        # Lightweight payload - only essential fields for access token
        payload = {
            'sub': str(user.get('user_id')),  # User ID
            'username': user.get('user_name'),
            'email': user.get('email'),
            'exp': now + timedelta(minutes=ACCESS_TOKEN_EXPIRY),
            'iat': now,
            'jti': str(uuid.uuid4()),
            'type': 'access',
            'aud': 'authenticated',
            'is_active': user.get('is_active', True),
            'is_verified': user.get('is_verified', True),
        }

        if origin:
            payload['origin'] = origin
        if session_id:
            payload['session_id'] = session_id

        if not SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY environment variable is not set")

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    except Exception as e:
        logger.error(f"Error generating access token: {e}", exc_info=True, module="Auth", label="TOKEN_GENERATION")
        raise


def generate_refresh_token(user: Dict[str, Any], origin: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """Generate long-lived refresh token (30 days)"""
    try:
        now = datetime.utcnow()
        payload = {
            'sub': str(user.get('user_id')),
            'exp': now + timedelta(minutes=REFRESH_TOKEN_EXPIRY),
            'iat': now,
            'jti': str(uuid.uuid4()),
            'type': 'refresh',
            'aud': 'authenticated',
        }

        if origin:
            payload['origin'] = origin
        if session_id:
            payload['session_id'] = session_id

        if not SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY environment variable is not set")

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    except Exception as e:
        logger.error(f"Error generating refresh token: {e}", exc_info=True, module="Auth", label="TOKEN_GENERATION")
        raise


def generate_session_token(user: Dict[str, Any], origin: Optional[str] = None, session_id: Optional[str] = None) -> str:
    """Generate medium-lived session token (7 days)"""
    try:
        user_profile = _build_user_profile_payload(user)
        permissions = _build_permissions_payload(user)

        now = datetime.utcnow()
        payload = {
            'sub': str(user.get('user_id')),
            'username': user.get('user_name'),
            'first_name': user.get('first_name'),
            'last_name': user.get('last_name'),
            'email': user.get('email'),
            'exp': now + timedelta(minutes=SESSION_TOKEN_EXPIRY),
            'iat': now,
            'jti': str(uuid.uuid4()),
            'type': 'session',
            'user_profile': user_profile,
            'permissions': permissions,
            'aud': 'authenticated',
        }

        if origin:
            payload['origin'] = origin
        if session_id:
            payload['session_id'] = session_id

        if not SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY environment variable is not set")

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    except Exception as e:
        logger.error(f"Error generating session token: {e}", exc_info=True, module="Auth", label="TOKEN_GENERATION")
        raise


def generate_all_tokens(user: Dict[str, Any], origin: Optional[str] = None, request: Optional[Request] = None) -> Dict[str, Any]:
    """
    Generate all tokens (access, refresh, session) with session_id - Optimized for speed.
    Stateless approach - session_id is embedded in tokens, no database storage.
    Returns dict with tokens and session_id.
    """
    try:
        # Generate session_id once - this will be embedded in all tokens
        session_id = str(uuid.uuid4())

        # Generate all tokens in parallel (they're independent)
        # Access token is lightweight for faster generation
        access_token = generate_access_token(user, origin=origin, session_id=session_id)
        refresh_token = generate_refresh_token(user, origin=origin, session_id=session_id)
        session_token = generate_session_token(user, origin=origin, session_id=session_id)

        # No database storage - tokens are stateless
        # Session invalidation is handled via blacklist in cache

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'session_token': session_token,
            'session_id': session_id,
        }

    except Exception as e:
        logger.error(f"Error generating all tokens: {e}", exc_info=True, module="Auth", label="TOKEN_GENERATION")
        raise


def authenticate_user_token(identifier: str, password: str, origin: Optional[str] = None) -> Optional[str]:
    """
    Authenticate user and return JWT token.
    Matches NodeJS authenticateUserDjango (but without Django dependency).
    """
    try:
        # Authenticate user
        user = authenticate_user(identifier, password)

        if not user:
            return None

        # Generate and return JWT token with origin
        access_token = generate_access_token(user, origin=origin)
        return access_token

    except Exception as e:
        logger.error(f"Authentication failed: {e}", exc_info=True, module="Auth", label="AUTH_TOKEN")
        return None


def authenticate_user_with_data(identifier: str, password: str, origin: Optional[str] = None, request: Optional[Request] = None) -> Optional[Dict[str, Any]]:
    """
    Authenticate user and return all tokens (access, refresh, session) with user data.
    Creates a session in the database.

    Also clears any user-level blacklist entries to allow new sessions after logout.
    """
    try:
        # Authenticate user
        user = authenticate_user(identifier, password)

        if not user:
            return None

        user_id = str(user.get('user_id'))

        # Generate all tokens and create session
        tokens = generate_all_tokens(user, origin=origin, request=request)

        # Return tokens and user data
        return {
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'session_token': tokens['session_token'],
            'session_id': tokens['session_id'],
            'user': user
        }

    except Exception as e:
        logger.error(f"Authentication failed: {e}", exc_info=True, module="Auth", label="AUTH_USER_DATA")
        return None


# Backward compatibility aliases (deprecated - use authenticate_user_token and authenticate_user_with_data)
def authenticate_user_django(identifier: str, password: str, origin: Optional[str] = None) -> Optional[str]:
    """Deprecated: Use authenticate_user_token instead"""
    return authenticate_user_token(identifier, password, origin)


def authenticate_user_django_with_data(identifier: str, password: str, origin: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Deprecated: Use authenticate_user_with_data instead"""
    return authenticate_user_with_data(identifier, password, origin)


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by user_id"""
    try:
        with db as cursor:
            # Only select columns that actually exist in the User table
            query = """
                SELECT user_id, email, password, first_name, last_name, user_name,
                       phone_number, is_active, is_verified, status,
                       profile_picture_url, country, dob, bio, theme,
                       profile_accessibility, user_type, language, timezone,
                       last_sign_in_at, email_verified_at, created_at, last_updated,
                       is_protected, is_trashed, auth_type, invited_by_user_id
                FROM public."user"
                WHERE user_id::text = %s
                LIMIT 1
            """
            cursor.execute(query, (str(user_id),))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    except Exception as e:
        logger.error(f"Error fetching user by ID: {e}", exc_info=True, module="Auth", label="FETCH_USER_BY_ID")
        return None


def update_user_password(user_id: str, new_password: str) -> bool:
    """
    Update user's password in the database.
    Returns True if successful, False otherwise.
    """
    try:
        hashed_password = hash_password(new_password)
        with db as cursor:
            query = """
                UPDATE public."user"
                SET password = %s, last_updated = NOW()
                WHERE user_id::text = %s
            """
            cursor.execute(query, (hashed_password, str(user_id)))
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error updating password: {e}", exc_info=True, module="Auth", label="UPDATE_PASSWORD")
        return False


def create_user_in_db(payload: Dict[str, Any]) -> Optional[str]:
    try:
        user_id = str(uuid.uuid4())

        hashed_password = hash_password(payload.get('password', ''))

        fields = [
            'user_id', 'password',
            # STATUSModel fields (all NOT NULL)
            'is_active', 'is_verified',
            # Protection flags (NOT NULL with defaults)
            'is_protected', 'is_trashed',
            # Timestamps
            'created_at', 'last_updated'
        ]
        values = [
            user_id, hashed_password,
            # STATUSModel defaults
            True,    # is_active
            True,    # is_verified
            # Protection flags defaults
            False,   # is_protected
            False,   # is_trashed
            # Timestamps
            'NOW()', 'NOW()'
        ]

        if 'email' in payload:
            fields.append('email')
            values.append(payload['email'])

        if 'phone_number' in payload:
            fields.append('phone_number')
            # Ensure phone_number is in JSON format
            phone = payload['phone_number']
            if isinstance(phone, str):
                phone = {"phone": phone}
            # Use json.dumps() to properly serialize JSON for PostgreSQL JSONB
            values.append(json.dumps(phone))

        if 'first_name' in payload:
            fields.append('first_name')
            values.append(payload['first_name'])

        if 'last_name' in payload:
            fields.append('last_name')
            values.append(payload['last_name'])

        if 'user_name' in payload:
            fields.append('user_name')
            values.append(payload['user_name'])


        # Add verification fields (required NOT NULL fields)
        if 'is_email_verified' in payload:
            fields.append('is_email_verified')
            values.append(payload['is_email_verified'])
        else:
            # Default to False if not provided
            fields.append('is_email_verified')
            values.append(False)

        if 'is_phone_verified' in payload:
            fields.append('is_phone_verified')
            values.append(payload['is_phone_verified'])
        else:
            # Default to False if not provided
            fields.append('is_phone_verified')
            values.append(False)

        # Add verification timestamps if provided
        if 'email_verified_at' in payload:
            fields.append('email_verified_at')
            timestamp = payload['email_verified_at']
            # If it's a datetime object, psycopg2 will handle it
            # If it's the string 'NOW()', use it directly
            if isinstance(timestamp, str) and timestamp.upper() == 'NOW()':
                values.append('NOW()')
            else:
                values.append(timestamp)

        if 'phone_number_verified_at' in payload:
            fields.append('phone_number_verified_at')
            timestamp = payload['phone_number_verified_at']
            # If it's a datetime object, psycopg2 will handle it
            # If it's the string 'NOW()', use it directly
            if isinstance(timestamp, str) and timestamp.upper() == 'NOW()':
                values.append('NOW()')
            else:
                values.append(timestamp)

        # Add other optional fields (if not already in fields)
        optional_fields = [
            'auth_type', 'profile_accessibility', 'theme', 'user_type', 'language', 'status'
        ]
        for field in optional_fields:
            if field in payload and field not in fields:
                fields.append(field)
                value = payload[field]
                # Convert enum to string if it's an enum
                if hasattr(value, 'value'):
                    value = value.value
                elif not isinstance(value, str):
                    value = str(value)
                values.append(value)

        # Build the query
        placeholders_list = []
        query_values = []

        for i, value in enumerate(values):
            if value == 'NOW()':
                placeholders_list.append('NOW()')
            else:
                placeholders_list.append('%s')
                query_values.append(value)

        placeholders = ', '.join(placeholders_list)
        field_names = ', '.join([f'"{f}"' for f in fields])

        query = f"""
            INSERT INTO public."user" ({field_names})
            VALUES ({placeholders})
            RETURNING user_id
        """

        with db as cursor:
            cursor.execute(query, query_values)
            result = cursor.fetchone()
            if result:
                return user_id

        return None

    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True, module="Auth", label="CREATE_USER")
        return None
