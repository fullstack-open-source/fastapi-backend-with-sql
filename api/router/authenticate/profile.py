import json
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from src.middleware.permission_middleware import check_permission
from src.authenticate.otp_cache import verify_otp
from src.response.error import ERROR
from src.response.success import SUCCESS
from src.multilingual.multilingual import normalize_language
from src.storage import upload_to_google_storage_from_string
from .models import (
    ChangeEmailRequest, ChangePhoneRequest, UserProfileAccessibility,
    UserProfileLanguage
)
from src.db.postgres.postgres import connection as db
from src.authenticate.models import User
from .query import get_user_by_user_id
from src.logger.logger import logger
from uuid import uuid4
from .utils import serialize_data

router = APIRouter()


@router.get("/settings/profile", response_model=User)
async def get_user_profile(
    current_user: User = Depends(check_permission("view_profile"))
):
    """
    Get current user profile.

    Required Permission: view_profile
    Returns the current authenticated user's profile.
    """
    target_user_id = current_user.uid

    try:
        with db as cursor:
            user_data = await get_user_by_user_id(cursor, target_user_id)

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR.build(
                    "PROFILE_NOT_FOUND",
                    details={"user_id": target_user_id},
                    language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
                )
            )

        context = User(**user_data)
        serialized_data = serialize_data(context)

        return SUCCESS.response(
            data=serialized_data,
            message="User profile fetched successfully",
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching profile for {target_user_id}: {e}", module="Profile", label="GET_PROFILE", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build(
                "PROFILE_PROCESSING_ERROR",
                details={"user_id": target_user_id},
                exception=e,
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )


@router.get("/settings/profile/{user_id}", response_model=User)
async def get_user_profile_by_id(
    user_id: str,
    current_user: User = Depends(check_permission("view_user"))
):
    """
    Get user profile by ID.

    Required Permission: view_user
    Returns a specific user's profile by user_id.
    """
    target_user_id = user_id

    try:
        with db as cursor:
            user_data = await get_user_by_user_id(cursor, target_user_id)

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR.build(
                    "PROFILE_NOT_FOUND",
                    details={"user_id": target_user_id},
                    language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
                )
            )

        context = User(**user_data)
        serialized_data = serialize_data(context)

        return SUCCESS.response(
            data=serialized_data,
            message="User profile fetched successfully",
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching profile for {target_user_id}: {e}", module="Profile", label="GET_PROFILE", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build(
                "PROFILE_PROCESSING_ERROR",
                details={"user_id": target_user_id},
                exception=e,
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )


@router.post("/settings/update-profile-picture", response_model=dict)
async def update_profile_picture( file: UploadFile = File(None), current_user: User = Depends(check_permission("edit_profile")),):
    """
    Update profile picture using file upload or URL.
    Calls the /upload endpoint internally to get the public URL.
    """
    try:

        file_data = await file.read()
        extension = file.filename.split(".")[-1].lower()
        content_type = file.content_type or "application/octet-stream"

        object_key = f"{current_user.user_name}-user_id_{current_user.uid}-|-{uuid4()}.{extension}"


        folder = "media/users"
        public_url = upload_to_google_storage_from_string(
            file_data=file_data,
            folder=folder,
            object_key=object_key,
            content_type=content_type
        )


        with db as cursor:
            query = """
                UPDATE public."user"
                SET profile_picture_url = %s, last_updated = NOW()
                WHERE user_id::text = %s
                RETURNING user_id
            """
            cursor.execute(query, (public_url, str(current_user.uid)))
            result = cursor.fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR.build(
                    "PROFILE_PICTURE_UPDATE_FAILED",
                    details={"user_id": current_user.uid},
                    language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
                )
            )
        return SUCCESS.response(
            message="Profile picture updated successfully",
            data={
                "message": "Profile picture updated successfully",
                "profile_picture_url": public_url
            },
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile picture for {current_user.uid}: {e}", module="Profile", label="UPDATE_PICTURE", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build(
                "PROFILE_PICTURE_UPDATE_FAILED",
                details={"user_id": current_user.uid},
                exception=e,
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.post("/settings/update-profile", response_model=User)
async def update_profile(payload: User, current_user: User = Depends(check_permission("edit_profile"))):
    """
    Partially update user profile fields.
    Only provided fields will be updated.
    user_id and email cannot be updated.
    """
    try:
        update_data = {k: v for k, v in payload.dict(exclude_unset=True).items()}

        protected_fields = {"user_id"}
        if current_user.email:
            protected_fields.add("email")
        else:
            protected_fields.add("phone")


        for field in protected_fields:
            update_data.pop(field, None)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "PROFILE_INVALID_PAYLOAD",
                    details={"user_id": current_user.uid},
                    language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
                )
            )



        set_clauses = []
        update_values = []

        for key, value in update_data.items():
            if key == 'phone_number' and isinstance(value, dict):

                set_clauses.append(f'"{key}" = %s::jsonb')
                update_values.append(json.dumps(value))
            else:
                set_clauses.append(f'"{key}" = %s')
                update_values.append(value)

        set_clauses.append('last_updated = NOW()')
        update_values.append(str(current_user.uid))

        with db as cursor:
            query = f"""
                UPDATE public."user"
                SET {', '.join(set_clauses)}
                WHERE user_id::text = %s
                RETURNING user_id
            """
            cursor.execute(query, update_values)
            result = cursor.fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR.build(
                    "PROFILE_UPDATE_FAILED",
                    details={"user_id": current_user.uid},
                    language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
                )
            )


        with db as cursor:
            user_data = await get_user_by_user_id(cursor, current_user.uid)
        context = User(**user_data)

        serialized_data = serialize_data(context)
        return SUCCESS.response(
            data=serialized_data,
            message="User profile update successfully",
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile for {current_user.uid}: {e}", module="Profile", label="UPDATE_PROFILE", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build(
                "PROFILE_UPDATE_FAILED",
                details={"user_id": current_user.uid},
                exception=e,
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.post("/settings/profile-accessibility", response_model=User)
async def profile_accessibility(payload: UserProfileAccessibility, current_user: User = Depends(check_permission("edit_profile"))):

    try:


        update_data = payload.dict()
        set_clauses = [f'"{k}" = %s' for k in update_data.keys()]
        set_clauses.append('last_updated = NOW()')
        update_values = list(update_data.values()) + [str(current_user.uid)]

        with db as cursor:
            query = f"""
                UPDATE public."user"
                SET {', '.join(set_clauses)}
                WHERE user_id::text = %s
            """
            cursor.execute(query, update_values)


        with db as cursor:
            user_data = await get_user_by_user_id(cursor, current_user.uid)
        context = User(**user_data)

        serialized_data = serialize_data(context)
        return SUCCESS.response(
            data=serialized_data,
            message="Profile accessibility update successfully",
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/settings/profile-language", response_model=User)
async def profile_language(payload: UserProfileLanguage, current_user: User = Depends(check_permission("edit_profile"))):

    try:

        update_data = payload.dict()
        set_clauses = [f'"{k}" = %s' for k in update_data.keys()]
        set_clauses.append('last_updated = NOW()')
        update_values = list(update_data.values()) + [str(current_user.uid)]

        with db as cursor:
            query = f"""
                UPDATE public."user"
                SET {', '.join(set_clauses)}
                WHERE user_id::text = %s
            """
            cursor.execute(query, update_values)


        with db as cursor:
            user_data = await get_user_by_user_id(cursor, current_user.uid)
        context = User(**user_data)

        serialized_data = serialize_data(context)
        return SUCCESS.response(
            data=serialized_data,
            message="Profile language update successfully",
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings/change-email")
async def change_email(payload: ChangeEmailRequest, current_user: User = Depends(check_permission("edit_profile"))):
    """
    Verify OTP and change email for the logged-in user.
    """
    try:

        user_id = current_user.uid
        new_email = payload.new_email.strip()


        is_valid = await verify_otp(new_email, payload.otp, delete_after_verify=False)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "PROFILE_INVALID_OTP",
                    details={"user_id": user_id},
                    language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
                )
            )


        with db as cursor:
            check_query = """
                SELECT user_id, email
                FROM public."user"
                WHERE email = %s AND user_id::text != %s
            """
            cursor.execute(check_query, (new_email, str(user_id)))
            existing_user = cursor.fetchone()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "EMAIL_ALREADY_EXISTS",
                    details={"user_id": user_id, "email": new_email},
                    language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
                )
            )


        with db as cursor:
            query = """
                UPDATE public."user"
                SET email = %s,
                    is_email_verified = TRUE,
                    email_verified_at = NOW(),
                    last_updated = NOW()
                WHERE user_id::text = %s
                RETURNING user_id, email, is_email_verified, email_verified_at
            """
            cursor.execute(query, (new_email, str(user_id)))
            result = cursor.fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR.build(
                    "PROFILE_EMAIL_CHANGE_FAILED",
                    details={"user_id": user_id},
                    language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
                )
            )

        result_dict = dict(result)
        updated_user_email = result_dict.get('email')
        is_email_verified = result_dict.get('is_email_verified')
        email_verified_at = result_dict.get('email_verified_at')


        await verify_otp(new_email, payload.otp, delete_after_verify=True)

        return SUCCESS.response(
            message="Email updated and verified successfully",
            data={
                "message": "Email updated and verified successfully",
                "user": {
                    "id": user_id,
                    "email": updated_user_email,
                    "is_email_verified": is_email_verified,
                    "email_verified_at": email_verified_at.isoformat() if email_verified_at else None
                }
            },
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing email for {user_id}: {e}", module="Profile", label="CHANGE_EMAIL", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build(
                "PROFILE_EMAIL_CHANGE_FAILED",
                details={"user_id": user_id},
                exception=e,
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.post("/settings/change-phone")
async def change_phone(payload: ChangePhoneRequest, current_user: User = Depends(check_permission("edit_profile"))):
    """Verify OTP and change phone number for the logged-in user."""
    try:
        from router.authenticate.utils import validate_phone

        user_id = current_user.uid
        new_phone = payload.new_phone.strip()

        if not validate_phone(new_phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "PROFILE_INVALID_PAYLOAD",
                    details={"message": "Invalid phone number format"},
                    language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
                )
            )

        is_valid = await verify_otp(new_phone, payload.otp, delete_after_verify=False)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "PROFILE_INVALID_OTP",
                    details={"user_id": user_id},
                    language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
                )
            )

        phone_clean = new_phone.replace("+", "")
        phone_number_json = json.dumps({"phone": phone_clean})

        with db as cursor:
            check_query = """
                SELECT user_id FROM public."user"
                WHERE phone_number->>'phone' = %s AND user_id::text != %s
            """
            cursor.execute(check_query, (phone_clean, str(user_id)))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR.build(
                        "EMAIL_ALREADY_EXISTS",
                        details={"user_id": user_id, "phone": new_phone},
                        language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
                    )
                )

            query = """
                UPDATE public."user"
                SET phone_number = %s::jsonb, is_phone_verified = TRUE,
                    phone_number_verified_at = NOW(), last_updated = NOW()
                WHERE user_id::text = %s
                RETURNING user_id, phone_number, is_phone_verified, phone_number_verified_at
            """
            cursor.execute(query, (phone_number_json, str(user_id)))
            result = cursor.fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR.build(
                    "PROFILE_UPDATE_FAILED",
                    details={"user_id": user_id},
                    language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
                )
            )

        await verify_otp(new_phone, payload.otp, delete_after_verify=True)
        result_dict = dict(result)
        return SUCCESS.response(
            message="Phone number updated and verified successfully",
            data={
                "user": {
                    "id": user_id,
                    "phone_number": json.loads(result_dict['phone_number']) if isinstance(result_dict['phone_number'], str) else result_dict['phone_number'],
                    "is_phone_verified": result_dict['is_phone_verified'],
                    "phone_number_verified_at": result_dict['phone_number_verified_at'].isoformat() if result_dict['phone_number_verified_at'] else None
                }
            },
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing phone: {e}", exc_info=True, module="Profile", label="CHANGE_PHONE")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("PROFILE_PROCESSING_ERROR", exception=str(e))
        )

@router.post("/settings/send-phone-otp")
async def send_phone_otp(phone: str, channel: str, current_user: User = Depends(check_permission("edit_profile"))):
    """Send OTP to phone number"""
    try:
        from router.authenticate.utils import validate_phone
        from src.authenticate.otp_cache import set_otp
        from src.sms.sms import send_sms, send_whatsapp

        if not phone or not channel or channel not in ["sms", "whatsapp"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build("PROFILE_INVALID_PAYLOAD", details={"message": "phone and channel (sms/whatsapp) are required"})
            )

        phone_clean = phone.strip()
        if not validate_phone(phone_clean):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build("PROFILE_INVALID_PAYLOAD", details={"message": "Invalid phone number format"})
            )

        otp = await set_otp(phone_clean, ttl=600)
        if not otp:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR.build("AUTH_OTP_SEND_FAILED", details={"user_id": phone_clean})
            )

        if channel == "sms":
            send_sms(to_number=phone_clean, message=f"Your OTP is {otp}. It is valid for 10 minutes.")
        else:
            send_whatsapp(to_number=phone_clean, otp=otp)

        return SUCCESS.response(
            message="OTP sent successfully",
            data={"message": "OTP sent successfully"},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending phone OTP: {e}", exc_info=True, module="Profile", label="SEND_PHONE_OTP")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("PROFILE_PROCESSING_ERROR", exception=str(e))
        )

@router.post("/settings/update-theme")
async def update_theme(theme: str, current_user: User = Depends(check_permission("edit_profile"))):
    """Update user theme"""
    try:
        if not theme or theme not in ["light", "dark"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build("PROFILE_INVALID_PAYLOAD", details={"message": 'theme must be "light" or "dark"'})
            )

        with db as cursor:
            cursor.execute(
                "UPDATE public.\"user\" SET theme = %s, last_updated = NOW() WHERE user_id::text = %s",
                (theme, str(current_user.uid))
            )

        with db as cursor:
            user_data = await get_user_by_user_id(cursor, current_user.uid)
        serialized_data = serialize_data(User(**user_data))

        return SUCCESS.response(
            message="Theme updated successfully",
            data=serialized_data,
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating theme: {e}", exc_info=True, module="Profile", label="UPDATE_THEME")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("PROFILE_PROCESSING_ERROR", exception=str(e))
        )

@router.post("/settings/deactivate-account")
async def deactivate_account(current_user: User = Depends(check_permission("edit_profile"))):
    """Deactivate user account"""
    try:
        with db as cursor:
            cursor.execute(
                "UPDATE public.\"user\" SET is_active = FALSE, status = 'INACTIVE', last_updated = NOW() WHERE user_id::text = %s",
                (str(current_user.uid),)
            )

        return SUCCESS.response(
            message="Account deactivated successfully",
            data={"user_id": current_user.uid, "is_active": False, "status": "INACTIVE"},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except Exception as e:
        logger.error(f"Error deactivating account: {e}", exc_info=True, module="Profile", label="DEACTIVATE_ACCOUNT")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("PROFILE_PROCESSING_ERROR", exception=str(e))
        )

@router.post("/settings/delete-account")
async def delete_account(confirm: bool, current_user: User = Depends(check_permission("edit_profile"))):
    """Delete user account"""
    try:
        if confirm is not True:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build("PROFILE_INVALID_PAYLOAD", details={"message": "Account deletion must be confirmed"})
            )

        with db as cursor:
            cursor.execute(
                "UPDATE public.\"user\" SET is_active = FALSE, status = 'INACTIVE', last_updated = NOW() WHERE user_id::text = %s",
                (str(current_user.uid),)
            )

        return SUCCESS.response(
            message="Account deactivated successfully",
            data={"user_id": current_user.uid, "is_active": False},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting account: {e}", exc_info=True, module="Profile", label="DELETE_ACCOUNT")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("PROFILE_PROCESSING_ERROR", exception=str(e))
        )

@router.get("/settings/get-settings")
async def get_settings(current_user: User = Depends(check_permission("view_profile"))):
    """Get user settings"""
    try:
        with db as cursor:
            cursor.execute("""
                SELECT user_id, theme, language, profile_accessibility, timezone, country, bio,
                    is_email_verified, is_phone_verified, is_active, is_verified, status
                FROM public."user" WHERE user_id::text = %s
            """, (str(current_user.uid),))
            row = cursor.fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR.build("PROFILE_NOT_FOUND", details={"user_id": current_user.uid})
            )

        settings = {
            "user_id": str(row[0]), "theme": row[1], "language": row[2],
            "profile_accessibility": row[3], "timezone": row[4], "country": row[5], "bio": row[6],
            "is_email_verified": row[7], "is_phone_verified": row[8],
            "is_active": row[9], "is_verified": row[10], "status": row[11]
        }

        return SUCCESS.response(
            message="User settings retrieved successfully",
            data=serialize_data(settings),
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting settings: {e}", exc_info=True, module="Profile", label="GET_SETTINGS")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("PROFILE_PROCESSING_ERROR", exception=str(e))
        )

@router.post("/settings/update-timezone")
async def update_timezone(timezone: str, current_user: User = Depends(check_permission("edit_profile"))):
    """Update user timezone"""
    try:
        if not timezone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build("PROFILE_INVALID_PAYLOAD", details={"message": "timezone is required"})
            )

        with db as cursor:
            cursor.execute(
                "UPDATE public.\"user\" SET timezone = %s, last_updated = NOW() WHERE user_id::text = %s",
                (timezone, str(current_user.uid))
            )

        with db as cursor:
            user_data = await get_user_by_user_id(cursor, current_user.uid)
        serialized_data = serialize_data(User(**user_data))

        return SUCCESS.response(
            message="Timezone updated successfully",
            data=serialized_data,
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating timezone: {e}", exc_info=True, module="Profile", label="UPDATE_TIMEZONE")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("PROFILE_PROCESSING_ERROR", exception=str(e))
        )

