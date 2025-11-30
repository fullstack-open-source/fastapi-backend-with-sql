from fastapi import HTTPException, status
from src.response.error import ERROR
from src.logger.logger import logger


async def get_user_by_user_id(cursor, user_id: str):
    """
    Fetch a user by user_id (UUID or text).
    Returns user dict or None if not found.
    Raises HTTPException for database errors.
    """
    try:
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "PROFILE_INVALID_PAYLOAD",
                    details={"error": "user_id is required"}
                )
            )

        user_id = str(user_id).strip()
        query = """
            SELECT user_id, first_name, last_name, email, phone_number, country, gender,
                dob, profile_picture_url, bio, theme,
                profile_accessibility, user_type, user_name, language,
                is_active, is_verified, status, timezone,
                invited_by_user_id, is_protected, is_trashed, last_sign_in_at, email_verified_at, phone_number_verified_at,
                created_at, last_updated, auth_type, is_email_verified, is_phone_verified
            FROM public."user"
            WHERE user_id::text = %s
        """
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()

        if not row:
            logger.warning(f"User not found with user_id: {user_id}", module="Auth", label="GET_USER_BY_ID")
            return None

        user_dict = dict(row)
        # Ensure user_id is a string
        if 'user_id' in user_dict:
            user_dict['user_id'] = str(user_dict['user_id'])

        return user_dict

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error in get_user_by_user_id: {e}", exc_info=True, module="Auth", label="GET_USER_BY_ID")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build(
                "PROFILE_PROCESSING_ERROR",
                details={"user_id": user_id},
                exception=e
            )
        )


async def create_user(cursor, payload: dict):
    """
    Create a new user.
    """
    query = """
        INSERT INTO "user"
        (first_name, last_name, email, phone_number, country, gender, dob, gender,
         profile_picture_url, bio, theme, profile_accessibility,
         user_type, user_name, auth_type, is_email_verified, is_phone_verified)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING user_id;
    """
    cursor.execute(query, (
        payload.get("first_name"),
        payload.get("last_name"),
        payload.get("email"),
        payload.get("phone_number"),  # JSONB (dict will auto-convert)
        payload.get("country"),
        payload.get("gender"),
        payload.get("dob"),
        payload.get("gender"),
        payload.get("profile_picture_url"),
        payload.get("bio"),
        payload.get("portfolio_url"),
        payload.get("theme"),
        payload.get("profile_accessibility"),
        payload.get("user_type"),
        payload.get("user_name"),
        payload.get("auth_type"),
        payload.get("is_email_verified", False),
        payload.get("is_phone_verified", False)
    ))
    row = cursor.fetchone()
    return row


async def edit_user(cursor, user_id: str, payload: dict):
    """
    Update user details.
    """
    query = """
        UPDATE "user"
        SET first_name = %s, last_name = %s, email = %s, phone_number = %s,
            country = %s, gender = %s, dob = %s, profile_picture_url = %s, bio = %s,
            theme = %s, profile_accessibility = %s,
            user_type = %s, user_name = %s, auth_type = %s, is_email_verified = %s, is_phone_verified = %s
        WHERE user_id = %s
        RETURNING user_id;
    """
    cursor.execute(query, (
        payload.get("first_name"),
        payload.get("last_name"),
        payload.get("email"),
        payload.get("phone_number"),
        payload.get("country"),
        payload.get("gender"),
        payload.get("dob"),
        payload.get("profile_picture_url"),
        payload.get("bio"),
        payload.get("theme"),
        payload.get("profile_accessibility"),
        payload.get("user_type"),
        payload.get("user_name"),
        payload.get("auth_type"),
        payload.get("is_email_verified", False),
        payload.get("is_phone_verified", False),
        user_id
    ))
    row = cursor.fetchone()
    return row


async def create_address(cursor, payload: dict):
    query = """
        INSERT INTO ADDRESSList (auth_id, city, state, country, lat, lon)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    cursor.execute(query, (payload["id"], payload["address"]["city"], payload["address"]["state"], payload["address"]["country"], payload["address"]["lat"], payload["address"]["lon"]))
    row = cursor.fetchone()
    return row


async def edit_address(cursor, user_id: str, address_data: dict):
    query = """
        UPDATE ADDRESSList
        SET city = %s, state = %s, country = %s, lat = %s, lon = %s
        WHERE auth_id = %s
        RETURNING id;
    """
    cursor.execute(query, (address_data["city"], address_data["state"], address_data["country"], address_data["lat"], address_data["lon"], user_id))
    row = cursor.fetchone()
    return row
