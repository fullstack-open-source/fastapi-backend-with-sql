"""
Session Manager - Handles token blacklisting for stateless authentication
Multi-token session management with access_token, refresh_token, session_token, and session_id
Uses cache (Redis or in-memory) for blacklisting instead of database storage
Optimized for fast and secure authentication
"""
import os
from typing import Optional
import hashlib

from src.cache.cache import cache
from src.logger.logger import logger

# Token expiration times (in minutes)
ACCESS_TOKEN_EXPIRY = int(os.environ.get('ACCESS_TOKEN_EXPIRY_MINUTES', '60'))  # 1 hour
SESSION_TOKEN_EXPIRY = int(os.environ.get('SESSION_TOKEN_EXPIRY_MINUTES', '10080'))  # 7 days
REFRESH_TOKEN_EXPIRY = int(os.environ.get('REFRESH_TOKEN_EXPIRY_MINUTES', '43200'))  # 30 days


def hash_token(token: str) -> str:
    """Create a hash of a token for blacklisting"""
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


async def blacklist_token(token: str, token_type: str = "access", expires_in_minutes: Optional[int] = None) -> bool:
    """
    Add a token to the blacklist.
    token_type can be 'access', 'refresh', or 'session'
    Returns True if successful, False otherwise.
    """
    try:
        token_hash = hash_token(token)
        blacklist_key = f"blacklist:{token_type}:{token_hash}"

        # Set expiration based on token type if not provided
        if expires_in_minutes is None:
            if token_type == "access":
                expires_in_minutes = ACCESS_TOKEN_EXPIRY
            elif token_type == "session":
                expires_in_minutes = SESSION_TOKEN_EXPIRY
            else:  # refresh
                expires_in_minutes = REFRESH_TOKEN_EXPIRY

        # Store in cache with TTL (convert minutes to seconds)
        ttl_seconds = expires_in_minutes * 60
        await cache.set(blacklist_key, "1", ttl=ttl_seconds)

        return True

    except Exception as e:
        logger.error(f"Error blacklisting token: {e}", exc_info=True, module="Auth", label="TOKEN_BLACKLIST")
        return False


async def is_token_blacklisted(token: str, token_type: str = "access") -> bool:
    """
    Check if a token is blacklisted.
    Returns True if blacklisted, False otherwise.
    """
    try:
        token_hash = hash_token(token)
        blacklist_key = f"blacklist:{token_type}:{token_hash}"

        result = await cache.get(blacklist_key)
        return result is not None

    except Exception as e:
        logger.error(f"Error checking token blacklist: {e}", exc_info=True, module="Auth", label="TOKEN_BLACKLIST_CHECK")
        # On error, assume not blacklisted to avoid blocking valid requests
        return False


async def blacklist_session(session_id: str, expires_in_minutes: Optional[int] = None) -> bool:
    """
    Blacklist a session by session_id.
    This will invalidate all tokens associated with this session.
    """
    try:
        blacklist_key = f"blacklist:session:{session_id}"

        # Default to refresh token expiry (longest)
        if expires_in_minutes is None:
            expires_in_minutes = REFRESH_TOKEN_EXPIRY

        ttl_seconds = expires_in_minutes * 60
        await cache.set(blacklist_key, "1", ttl=ttl_seconds)

        return True

    except Exception as e:
        logger.error(f"Error blacklisting session: {e}", exc_info=True, module="Auth", label="SESSION_BLACKLIST")
        return False


async def is_session_blacklisted(session_id: str) -> bool:
    """
    Check if a session is blacklisted.
    Returns True if blacklisted, False otherwise.
    """
    try:
        blacklist_key = f"blacklist:session:{session_id}"
        result = await cache.get(blacklist_key)
        return result is not None

    except Exception as e:
        logger.error(f"Error checking session blacklist: {e}", exc_info=True, module="Auth", label="SESSION_BLACKLIST_CHECK")
        # On error, assume not blacklisted to avoid blocking valid requests
        return False


async def blacklist_all_user_sessions(user_id: str, expires_in_minutes: Optional[int] = None) -> int:
    """
    Blacklist all sessions for a user by storing a user-level blacklist entry.
    This is a pattern-based approach - we'll check user_id in token validation.
    Returns 1 if successful (we track it as a single operation).
    """
    try:
        blacklist_key = f"blacklist:user:{user_id}"

        if expires_in_minutes is None:
            expires_in_minutes = REFRESH_TOKEN_EXPIRY

        ttl_seconds = expires_in_minutes * 60
        await cache.set(blacklist_key, "1", ttl=ttl_seconds)

        return 1

    except Exception as e:
        logger.error(f"Error blacklisting user sessions: {e}", exc_info=True, module="Auth", label="USER_SESSIONS_BLACKLIST")
        return 0


async def is_user_blacklisted(user_id: str) -> bool:
    """
    Check if all sessions for a user are blacklisted.
    Returns True if blacklisted, False otherwise.
    """
    try:
        blacklist_key = f"blacklist:user:{user_id}"
        result = await cache.get(blacklist_key)
        return result is not None

    except Exception as e:
        logger.error(f"Error checking user blacklist: {e}", exc_info=True, module="Auth", label="USER_BLACKLIST_CHECK")
        return False


async def clear_user_blacklist(user_id: str) -> bool:
    """
    Clear/remove user-level blacklist entry.
    This allows the user to create new sessions after logout.

    Args:
        user_id: User ID whose blacklist should be cleared

    Returns:
        True if successful, False otherwise
    """
    try:
        blacklist_key = f"blacklist:user:{user_id}"
        await cache.delete(blacklist_key)

        return True

    except Exception as e:
        logger.error(f"Error clearing user blacklist: {e}", exc_info=True, module="Auth", label="CLEAR_USER_BLACKLIST")
        return False


async def clear_user_refresh_token_blacklist(user_id: str) -> bool:
    """
    Clear/remove user-level refresh token blacklist entry.
    This allows the user to use refresh tokens after logout.

    Args:
        user_id: User ID whose refresh token blacklist should be cleared

    Returns:
        True if successful, False otherwise
    """
    try:
        # Check the actual key format used in revoke_all_user_refresh_tokens
        blacklist_key = f"blacklist:user_refresh_revoke:{user_id}"
        await cache.delete(blacklist_key)

        return True

    except Exception as e:
        logger.error(f"Error clearing user refresh token blacklist: {e}", exc_info=True, module="Auth", label="CLEAR_REFRESH_BLACKLIST")
        return False


async def blacklist_access_token_by_jti(token_jti: str, user_id: str, expires_in_seconds: Optional[int] = None) -> bool:
    """
    Blacklist an access token by its JTI (JWT ID).
    This is more efficient than hashing the entire token.

    Args:
        token_jti: JWT ID from the token payload
        user_id: User ID for logging purposes
        expires_in_seconds: Optional expiration time in seconds (defaults to access token expiry)

    Returns:
        True if successful, False otherwise
    """
    try:
        if not token_jti:
            logger.warning(f"No JTI provided for blacklisting access token for user {user_id}", module="Auth", label="TOKEN_BLACKLIST_JTI")
            return False

        blacklist_key = f"blacklist:access:jti:{token_jti}"

        # Default to access token expiry (convert minutes to seconds)
        if expires_in_seconds is None:
            expires_in_seconds = ACCESS_TOKEN_EXPIRY * 60

        await cache.set(blacklist_key, "1", ttl=expires_in_seconds)

        return True

    except Exception as e:
        logger.error(f"Error blacklisting access token by JTI: {e}", exc_info=True, module="Auth", label="TOKEN_BLACKLIST_JTI")
        return False


async def is_access_token_blacklisted_by_jti(token_jti: str) -> bool:
    """
    Check if an access token is blacklisted by its JTI.

    Args:
        token_jti: JWT ID from the token payload

    Returns:
        True if blacklisted, False otherwise
    """
    try:
        if not token_jti:
            return False

        blacklist_key = f"blacklist:access:jti:{token_jti}"
        result = await cache.get(blacklist_key)
        return result is not None

    except Exception as e:
        logger.error(f"Error checking access token blacklist by JTI: {e}", exc_info=True, module="Auth", label="TOKEN_BLACKLIST_CHECK_JTI")
        return False


async def revoke_all_user_refresh_tokens(user_id: str) -> bool:
    """
    Revoke all refresh tokens for a user by blacklisting them.
    This is done by storing a user-level refresh token blacklist entry.

    Args:
        user_id: User ID whose refresh tokens should be revoked

    Returns:
        True if successful, False otherwise
    """
    try:
        blacklist_key = f"blacklist:refresh:user:{user_id}"

        # Use refresh token expiry (longest)
        ttl_seconds = REFRESH_TOKEN_EXPIRY * 60
        await cache.set(blacklist_key, "1", ttl=ttl_seconds)

        return True

    except Exception as e:
        logger.error(f"Error revoking all refresh tokens for user: {e}", exc_info=True, module="Auth", label="REVOKE_REFRESH_TOKENS")
        return False


async def is_user_refresh_token_revoked(user_id: str) -> bool:
    """
    Check if all refresh tokens for a user have been revoked.

    Args:
        user_id: User ID to check

    Returns:
        True if revoked, False otherwise
    """
    try:
        blacklist_key = f"blacklist:refresh:user:{user_id}"
        result = await cache.get(blacklist_key)
        return result is not None

    except Exception as e:
        logger.error(f"Error checking user refresh token revocation: {e}", exc_info=True, module="Auth", label="CHECK_REFRESH_REVOKED")
        return False
