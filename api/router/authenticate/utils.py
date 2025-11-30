from src.enum.enum import LanguageStatusEnum, ProfileAccessibilityEnum, UserTypeEnum, ThemeEnum, AuthTypeEnum
from src.authenticate.checkpoint import get_user_by_email_or_phone, create_user_in_db
from src.db.postgres.postgres import connection as db

import datetime, re
from typing import Dict
from src.authenticate.models import User
from src.response.error import ERROR
from fastapi import HTTPException, status
from src.logger.logger import logger
from datetime import datetime
from typing import Any, Dict
from fastapi import (Request)
from urllib.parse import urlparse

phone_pattern = r'^\+?[1-9]\d{1,14}$'
email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

def validate_phone(phone: str) -> bool:
    return re.match(phone_pattern, phone) is not None

def validate_email(email: str) -> bool:
    return re.match(email_pattern, email) is not None


def get_request_user(user_id: str, channel: str):
    try:
        user = get_user_by_email_or_phone(user_id)
        if user:
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR.build(
                    "PROFILE_NOT_FOUND",
                    details={"user_id": user_id, "channel": channel}
                )
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}", exc_info=True, module="Auth", label="GET_USER")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build(
                "PROFILE_PROCESSING_ERROR",
                details={"user_id": user_id},
                exception=e
            )
        )


def check_and_insert_user(user_id: str, username: str, channel:str):
    try:
        # Check if user already exists
        try:
            existing = get_request_user(username, channel)
            if existing:
                # User already exists, return None
                return None
        except HTTPException:
            # User doesn't exist, create new user
            pass

        # Prepare user data for creation
        user_data = {}

        if channel in ["sms", "whatsapp"]:
            phone_number = username.strip()
            if channel == "whatsapp":
                phone_number = phone_number.replace("+", "")
            user_data['phone_number'] = {"phone": phone_number}
            user_data['auth_type'] = AuthTypeEnum.phone
        elif channel == "email":
            user_data['user_name'] = username.split('@')[0]
            user_data['email'] = username
            user_data['auth_type'] = AuthTypeEnum.email

        user_data['profile_accessibility'] = ProfileAccessibilityEnum.public
        user_data['theme'] = ThemeEnum.light
        user_data['user_type'] = UserTypeEnum.customer
        user_data['language'] = LanguageStatusEnum.en

        created_user_id = create_user_in_db(user_data)

        # Assign default "user" group to new user (required for permissions)
        if created_user_id:
            try:
                from src.permissions.permissions import assign_groups_to_user
                assign_groups_to_user(created_user_id, ["user"])
            except Exception as group_error:
                logger.warning(f"Failed to assign default group to user {created_user_id}: {group_error}", module="Auth", label="CHECK_INSERT_USER")
                # Don't fail the function, but log the warning

        return {"user_id": created_user_id} if created_user_id else None

    except Exception as e:
        logger.error(f"Error in check_and_insert_user: {e}", exc_info=True, module="Auth", label="CHECK_INSERT_USER")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build(
                "PROFILE_PROCESSING_ERROR",
                details={"user_id": user_id},
                exception=e
            )
        )



def update_user_by_email(email: str, data: dict):
    try:
        user = get_user_by_email_or_phone(email)
        if not user:
            raise ValueError(f"No user found with email: {email}")

        user_id = user.get('user_id')
        if not user_id:
            raise ValueError(f"User ID not found for email: {email}")

        # Build update query
        set_clauses = [f'"{k}" = %s' for k in data.keys() if k != 'user_id']
        if set_clauses:
            set_clauses.append('last_updated = NOW()')
            update_values = [v for k, v in data.items() if k != 'user_id'] + [str(user_id)]

            with db as cursor:
                query = f"""
                    UPDATE public."user"
                    SET {', '.join(set_clauses)}
                    WHERE user_id::text = %s
                    RETURNING user_id
                """
                cursor.execute(query, update_values)
                result = cursor.fetchone()
                return dict(result) if result else None

        return None
    except Exception as e:
        logger.error(f"Error updating user by email: {e}", exc_info=True, module="Auth", label="UPDATE_USER_EMAIL")
        raise


def update_user_by_phone(phone: str, data: dict):
    try:
        user = get_user_by_email_or_phone(phone)
        if not user:
            raise ValueError(f"No user found with phone: {phone}")

        user_id = user.get('user_id')
        if not user_id:
            raise ValueError(f"User ID not found for phone: {phone}")

        # Build update query
        set_clauses = [f'"{k}" = %s' for k in data.keys() if k != 'user_id']
        if set_clauses:
            set_clauses.append('last_updated = NOW()')
            update_values = [v for k, v in data.items() if k != 'user_id'] + [str(user_id)]

            with db as cursor:
                query = f"""
                    UPDATE public."user"
                    SET {', '.join(set_clauses)}
                    WHERE user_id::text = %s
                    RETURNING user_id
                """
                cursor.execute(query, update_values)
                result = cursor.fetchone()
                return dict(result) if result else None

        return None
    except Exception as e:
        logger.error(f"Error updating user by phone: {e}", exc_info=True, module="Auth", label="UPDATE_USER_PHONE")
        raise


def serialize_user_data(user: Any) -> Dict[str, Any]:
    if isinstance(user, User):
        user_dict = user.dict(exclude_none=True)
    elif isinstance(user, dict):
        user_dict = user.copy()
    else:
        user_dict = {}

    datetime_fields = ['dob', 'last_sign_in_at', 'email_verified_at', 'created_at', 'last_updated']
    for field in datetime_fields:
        if field in user_dict and user_dict[field] is not None:
            value = user_dict[field]
            if isinstance(value, datetime):
                user_dict[field] = value.isoformat()
            # If it's already a string, keep it as is

    # Also handle any other datetime objects that might be in the dict
    def convert_datetime(obj):
        """Recursively convert datetime objects in dict/list structures"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: convert_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_datetime(item) for item in obj]
        return obj

    user_dict = convert_datetime(user_dict)

    return user_dict



def serialize_data(data: Any) -> Dict[str, Any]:
    def convert_datetime(obj):
        """Recursively convert datetime objects in dict/list structures"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: convert_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_datetime(item) for item in obj]
        elif hasattr(obj, 'dict'):
            # Handle Pydantic models
            return convert_datetime(obj.dict(exclude_none=True))
        return obj

    return convert_datetime(data)

def update_email_and_phone_verification(user_id: str, channel: str):
    try:
        user = get_user_by_email_or_phone(user_id)
        if not user:
            raise ValueError(f"No user found with user_id: {user_id}")

        user_id = user.get('user_id')
        if not user_id:
            raise ValueError(f"User ID not found for user_id: {user_id}")

        # Update email and phone verification status
        if channel == "email":
            user['is_email_verified'] = True
            user['email_verified_at'] = datetime.now()
            with db as cursor:
                query = f"""
                    UPDATE public."user"
                    SET is_email_verified = %s, email_verified_at = NOW()
                    WHERE user_id::text = %s
                    RETURNING user_id
                """
                cursor.execute(query, (user['is_email_verified'], user_id))
                result = cursor.fetchone()
                return dict(result) if result else None
        elif channel == "phone":
            user['is_phone_verified'] = True
            user['phone_number_verified_at'] = datetime.now()
            with db as cursor:
                query = f"""
                    UPDATE public."user"
                    SET is_email_verified = %s, email_verified_at = NOW(), is_phone_verified = %s, phone_number_verified_at = NOW()
                    WHERE user_id::text = %s
                    RETURNING user_id
                """
                cursor.execute(query, (user['is_email_verified'], user['is_phone_verified'], user_id))
                result = cursor.fetchone()
                return dict(result) if result else None
        return True
    except Exception as e:
        logger.error(f"Error updating email and phone verification status: {e}", exc_info=True, module="Auth", label="UPDATE_VERIFICATION")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build(
                "PROFILE_PROCESSING_ERROR",
                details={"user_id": user_id},
                exception=e
            )
        )



def _extract_origin(request: Request) -> str:
    """
    Extract origin/domain from request headers.
    Priority: Origin header > Host header > X-Forwarded-Host
    Returns normalized origin (scheme + host only)
    """

    origin = request.headers.get("Origin")
    if origin:

        parsed = urlparse(origin)
        return f"{parsed.scheme}://{parsed.netloc}"


    host = request.headers.get("Host")
    if host:

        scheme = "https" if request.url.scheme == "https" or request.headers.get("X-Forwarded-Proto") == "https" else "http"
        return f"{scheme}://{host}"


    forwarded_host = request.headers.get("X-Forwarded-Host")
    if forwarded_host:
        scheme = request.headers.get("X-Forwarded-Proto", "https")
        return f"{scheme}://{forwarded_host}"


    return f"{request.url.scheme}://{request.url.netloc}"
