from src.authenticate.checkpoint import (
    authenticate_user_token, authenticate_user_with_data,
    update_user_password, get_user_by_email_or_phone,
    create_user_in_db, update_last_sign_in,
    update_user_verification_status
)
from src.authenticate.session_manager import (
    ACCESS_TOKEN_EXPIRY,
    SESSION_TOKEN_EXPIRY,
    REFRESH_TOKEN_EXPIRY
)
from router.authenticate.utils import (validate_email, validate_phone, serialize_user_data, _extract_origin)
from router.authenticate.models import (CheckUserAvailabilityRequest, ForgetPassword, PasswordChange, SetPassword, RefreshTokenRequest, TokenInfoRequest)
from fastapi import (APIRouter, Request, Depends, HTTPException, status, Body)
from router.authenticate.models import (OTPRequest, OTPVERIFYRequest)
from src.authenticate.otp_cache import (set_otp, verify_otp, is_master_otp)
from src.multilingual.multilingual import normalize_language
from src.authenticate.authenticate import validate_request, SECRET_KEY, ALGORITHM
from src.middleware.permission_middleware import check_permission
from fastapi.security import OAuth2PasswordRequestForm
from src.db.postgres.postgres import connection as db
from src.sms.sms import (send_sms, send_whatsapp)
from src.authenticate.models import User
from src.email.email import (send_otp_email)
from src.response.success import (SUCCESS)
from src.response.error import (ERROR)
from src.logger.logger import (logger)
from datetime import datetime
from typing import Optional

router = APIRouter()


@router.post("/auth/login-with-password")
async def login_with_password(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    """
    Login with username (email/phone) and password.

    Returns:
    - access_token: Short-lived token (24 hours) for API calls
    - refresh_token: Long-lived token (30 days) for refreshing tokens
    - session_token: Medium-lived token (7 days) with full user profile
    - session_id: Unique session identifier
    - user: User profile data

    Security:
    - Validates credentials
    - Checks user account status (active, verified)
    - Generates secure tokens with session_id
    - Returns all tokens and user data for client-side storage
    """
    try:
        # Validate input
        if not form.username or not form.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build("AUTH_INVALID_PAYLOAD", details={"message": "Username and password are required"}),
            )

        # Authenticate user first (without generating tokens yet) to get user_id
        from src.authenticate.checkpoint import authenticate_user
        origin = _extract_origin(request)
        user = authenticate_user(form.username, form.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build("AUTH_INVALID_CREDENTIALS", details={"message": "Invalid username or password"}),
            )

        # Check user account status
        user_id = str(user.get('user_id'))

        if not user.get('is_active'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build("AUTH_INVALID_CREDENTIALS", details={"message": "User account is not active"}),
            )

        if not user.get('is_verified'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build("AUTH_INVALID_CREDENTIALS", details={"message": "User account is not verified"}),
            )

        # Clear user-level blacklist entries BEFORE generating tokens
        # This ensures that after logout and re-login, the new tokens work immediately
        try:
            from src.authenticate.session_manager import (
                clear_user_blacklist,
                clear_user_refresh_token_blacklist
            )
            await clear_user_blacklist(user_id)
            await clear_user_refresh_token_blacklist(user_id)
        except Exception as clear_error:
            # Log but don't fail login if clearing blacklist fails
            logger.warning(f"Failed to clear user blacklist (non-blocking): {clear_error}", module="Auth", label="LOGIN")

        # Now generate tokens (after clearing blacklist)
        from src.authenticate.checkpoint import generate_all_tokens
        tokens = generate_all_tokens(user, origin=origin, request=request)

        # Build auth_result for compatibility
        auth_result = {
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'session_token': tokens['session_token'],
            'session_id': tokens['session_id'],
            'user': user
        }

        # Serialize user data
        user_model = User(**user)
        user_data = serialize_user_data(user_model)

        # Return all tokens and user data
        return SUCCESS.response(
            data={
                "access_token": auth_result['access_token'],
                "refresh_token": auth_result['refresh_token'],
                "session_token": auth_result['session_token'],
                "session_id": auth_result['session_id'],
                "token_type": "bearer",
                "user": user_data
            },
            message="Login successful"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login_with_password: {e}", exc_info=True, module="Auth", label="LOGIN")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("AUTH_SIGNIN_FAILED", exception=e),
        )

@router.post("/auth/login-with-otp")
async def login_with_otp(request: Request, payload: OTPVERIFYRequest):
    """
    Login with OTP verification.

    Client sends user_id (email/phone) and OTP.
    Returns all tokens (access, refresh, session) upon successful verification.

    Security:
    - Validates OTP
    - Checks user account status (active, verified)
    - Generates secure tokens with session_id
    - Returns all tokens and user data
    """
    try:
        # Validate and clean user_id
        user_id_clean = payload.user_id.strip()

        if not (validate_email(user_id_clean) or validate_phone(user_id_clean)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "AUTH_INVALID_PAYLOAD",
                    details={"message": "Invalid email or phone number format"}
                )
            )

        # Get user from database
        user = get_user_by_email_or_phone(user_id_clean)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR.build("USER_NOT_FOUND", details={"user_id": user_id_clean})
            )

        # Check user account status
        if not user.get('is_active'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build(
                    "AUTH_INVALID_CREDENTIALS",
                    details={"message": "User account is not active"}
                )
            )

        if not user.get('is_verified'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build(
                    "AUTH_INVALID_CREDENTIALS",
                    details={"message": "User account is not verified"}
                )
            )

        # Verify OTP
        is_valid = await verify_otp(user_id_clean, payload.otp, delete_after_verify=True)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "AUTH_OTP_INVALID",
                    details={"message": "Invalid or expired OTP"}
                )
            )

        # Update user verification status based on channel
        # This verifies the account (email or phone) when logging in with OTP
        channel = getattr(payload, 'channel', None)

        # Determine channel from user_id if not provided in payload
        if not channel:
            if validate_email(user_id_clean):
                channel = "email"
            elif validate_phone(user_id_clean):
                channel = "sms"  # Default to sms for phone

        # Update verification status (email or phone verification)
        if channel:
            update_user_verification_status(str(user['user_id']), channel)

        # Update last sign in
        update_last_sign_in(str(user['user_id']))

        # Clear user-level blacklist entries to allow new sessions after logout
        # This ensures that after logout and re-login, the new session works
        try:
            from src.authenticate.session_manager import (
                clear_user_blacklist,
                clear_user_refresh_token_blacklist
            )
            await clear_user_blacklist(str(user['user_id']))
            await clear_user_refresh_token_blacklist(str(user['user_id']))
        except Exception as clear_error:
            # Log but don't fail login if clearing blacklist fails
            logger.warning(f"Failed to clear user blacklist (non-blocking): {clear_error}", module="Auth", label="LOGIN_OTP")

        # Generate tokens directly (don't use authenticate_user_with_data with OTP as password)
        from src.authenticate.checkpoint import generate_all_tokens
        origin = _extract_origin(request)
        tokens = generate_all_tokens(user, origin=origin, request=request)

        # Serialize user data
        user_model = User(**user)
        user_data = serialize_user_data(user_model)

        return SUCCESS.response(
            message="Login successful",
            data={
                "access_token": tokens['access_token'],
                "refresh_token": tokens['refresh_token'],
                "session_token": tokens['session_token'],
                "session_id": tokens['session_id'],
                "token_type": "bearer",
                "user": user_data
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login_with_otp: {e}", exc_info=True, module="Auth", label="LOGIN_OTP")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("AUTH_PROCESSING_ERROR", exception=e)
        )

@router.post("/auth/check-user-availability")
async def check_user_availability(payload: CheckUserAvailabilityRequest):
    """
    Check if a user is available (not taken) in the database.
    Returns success if available (user doesn't exist), error if not available (user exists).
    """
    try:

        if not payload.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "AUTH_INVALID_PAYLOAD",
                    details={"message": "Either phone or email must be provided"},
                ),
            )


        if not (validate_email(payload.user_id) or validate_phone(payload.user_id)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "AUTH_INVALID_PAYLOAD",
                    details={"identifier": payload.user_id, "message": "Invalid email or phone number format"},
                ),
            )


        user = get_user_by_email_or_phone(payload.user_id)
        if user:
            return SUCCESS.response(
                    data={
                        "available": True,
                        "first_name": user.get("first_name"),
                        "last_name": user.get("last_name")
                    },
                    message="User is available",
                    language=user.get("language")
                )
        else:
            # User doesn't exist - not available
            return SUCCESS.response(
                data={
                    "available": False,
                    "first_name": None,
                    "last_name": None
                },
                message="User is not available"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("AUTH_PROCESSING_ERROR", details={"identifier": payload.user_id}, exception=e),
        )

@router.post("/auth/send-one-time-password", response_model=dict)
async def send_one_time_password(payload: OTPRequest):
    try:
        otp = await set_otp(payload.user_id, ttl=600)

        if not otp:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR.build("AUTH_OTP_SEND_FAILED", details={"user_id": payload.user_id}),
            )
        if payload.channel == "email":
            send_otp_email(payload.user_id, otp)
        elif payload.channel == "sms":
            send_sms(to_number=payload.user_id, message=f"Your OTP is {otp}. It is valid for 10 minutes.")
        elif payload.channel == "whatsapp":
            send_whatsapp(to_number=payload.user_id, otp=otp)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build("AUTH_CHANNEL_UNSUPPORTED", details={"channel": payload.channel}),
            )
        return SUCCESS.response(
            message="OTP sent successfully",
            data={"message": "OTP sent successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_one_time_password: {e}", exc_info=True, module="Auth", label="SEND_OTP")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("AUTH_OTP_SEND_FAILED", exception=e),
        )

@router.post("/auth/verify-one-time-password")
async def verify_and_save_password(payload: OTPVERIFYRequest):
    """
    Verify OTP and set password for the user.
    """
    try:
        is_valid = await verify_otp(payload.user_id, payload.otp, delete_after_verify=False)
        if not is_valid:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR.build("AUTH_OTP_INVALID", details={"user_id": payload.user_id}),
                )
        return SUCCESS.message_with_data("Verify Successfully", {"user_id": payload.user_id})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in verify_and_save_password: {e}", exc_info=True, module="Auth", label="VERIFY_OTP")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("AUTH_OTP_VERIFY_FAILED", exception=e),
        )

@router.post("/auth/verify", response_model=dict)
async def signup(request: Request, payload: OTPVERIFYRequest):
    try:

        is_valid = await verify_otp(payload.user_id, payload.otp, delete_after_verify=False)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "AUTH_OTP_INVALID",
                    details={"user_id": payload.user_id, "channel": payload.channel},
                ),
            )


        if not (validate_phone(payload.user_id) or validate_email(payload.user_id)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "AUTH_INVALID_PAYLOAD",
                    details={"user_id": payload.user_id, "channel": payload.channel},
                ),
            )


        existing_user = get_user_by_email_or_phone(payload.user_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=ERROR.build(
                    "AUTH_USER_ALREADY_EXISTS",
                    details={"user_id": payload.user_id, "channel": payload.channel},
                ),
            )
        else:
            from src.enum.enum import (
                AuthTypeEnum, ProfileAccessibilityEnum, ThemeEnum,
                UserTypeEnum, LanguageStatusEnum, UserStatusAuthEnum
            )
            user_data_dict = {
                "password": payload.otp,
                "is_draft": False,
                "is_active": True,
                "is_verified": True,
            }

            if payload.channel in ["sms", "whatsapp"]:
                phone_number = payload.user_id.strip()

                if payload.channel == "whatsapp" and phone_number.startswith("+"):
                    phone_number = phone_number[1:]
                user_data_dict["phone_number"] = {"phone": phone_number}
                user_data_dict["auth_type"] = AuthTypeEnum.phone
                user_data_dict["user_name"] = phone_number.replace("+", "")

                user_data_dict["is_phone_verified"] = True
                user_data_dict["phone_number_verified_at"] = datetime.now()

                user_data_dict["is_email_verified"] = False
            elif payload.channel == "email":
                user_data_dict["email"] = payload.user_id
                user_data_dict["user_name"] = payload.user_id.split('@')[0]
                user_data_dict["auth_type"] = AuthTypeEnum.email

                user_data_dict["is_email_verified"] = True
                user_data_dict["email_verified_at"] = datetime.now()

                user_data_dict["is_phone_verified"] = False

            user_data_dict["profile_accessibility"] = ProfileAccessibilityEnum.public
            user_data_dict["theme"] = ThemeEnum.light
            user_data_dict["user_type"] = UserTypeEnum.customer
            user_data_dict["language"] = LanguageStatusEnum.en
            user_data_dict["status"] = UserStatusAuthEnum.ACTIVE


            created_user_id = create_user_in_db(user_data_dict)
            if not created_user_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=ERROR.build(
                        "AUTH_SIGNUP_FAILED",
                        details={"user_id": payload.user_id, "channel": payload.channel},
                    ),
                )

            # Assign group based on OTP type (master OTP = super_admin, normal OTP = user)
            # This is CRITICAL - user must have a group to have permissions
            try:
                from src.permissions.permissions import assign_groups_to_user

                if is_master_otp(payload.otp):
                    # Master OTP used - assign super_admin group
                    assign_groups_to_user(created_user_id, ["super_admin"])
                else:
                    # Normal OTP - assign user group (required for basic permissions like edit_profile)
                    assign_groups_to_user(created_user_id, ["user"])

                # Verify group was assigned successfully
                from src.permissions.permissions import get_user_groups
                user_groups = get_user_groups(created_user_id)
                if not user_groups:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=ERROR.build(
                            "AUTH_SIGNUP_FAILED",
                            details={
                                "message": "Failed to assign user group. User created but group assignment failed.",
                                "user_id": created_user_id
                            }
                        )
                    )

            except HTTPException:
                raise
            except Exception as group_error:
                # Group assignment is critical - fail signup if it fails
                logger.error(f"CRITICAL: Failed to assign group to user {created_user_id}: {group_error}", exc_info=True, module="Auth", label="SIGNUP")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=ERROR.build(
                        "AUTH_SIGNUP_FAILED",
                        details={
                            "message": f"Failed to assign user group: {str(group_error)}",
                            "user_id": created_user_id,
                            "error": str(group_error)
                        }
                    )
                )

            user_data = get_user_by_email_or_phone(payload.user_id)
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=ERROR.build(
                        "AUTH_SIGNUP_FAILED",
                        details={"user_id": payload.user_id, "channel": payload.channel},
                    ),
                )

        origin = _extract_origin(request)
        auth_result = authenticate_user_with_data(payload.user_id, payload.otp, origin=origin, request=request)
        if not auth_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR.build(
                    "AUTH_SIGNUP_FAILED",
                    details={"user_id": payload.user_id, "channel": payload.channel},
                ),
            )

        await verify_otp(payload.user_id, payload.otp, delete_after_verify=True)


        user_model = User(**auth_result['user'])
        user_data = serialize_user_data(user_model)

        context = {
            "access_token": auth_result['access_token'],
            "refresh_token": auth_result.get('refresh_token'),
            "session_token": auth_result.get('session_token'),
            "session_id": auth_result.get('session_id'),
            "token_type": "bearer",
            "user": user_data
        }

        return SUCCESS.response(
            data=context,
            message="Signup successful"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in signup: {e}", exc_info=True, module="Auth", label="SIGNUP")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build(
                "AUTH_PROCESSING_ERROR",
                details={"user_id": payload.user_id, "channel": payload.channel},
                exception=e,
            ),
        )

@router.post("/auth/set-password")
async def set_password(payload: SetPassword, current_user: User = Depends(check_permission("edit_profile"))):
    try:
        success = update_user_password(current_user.uid, payload.confirm_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR.build(
                    "AUTH_PASSWORD_UPDATE_FAILED",
                    details={"user_id": current_user.uid},
                    language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
                ),
            )

        return SUCCESS.message("Password set successfully", language=normalize_language(getattr(current_user, 'language', None)) if current_user else None)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in set_password: {e}", exc_info=True, module="Auth", label="SET_PASSWORD")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build(
                "AUTH_PROCESSING_ERROR",
                details={"user_id": current_user.uid},
                exception=e,
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            ),
        )

@router.post("/auth/change-password")
async def change_password(payload: PasswordChange, current_user: User = Depends(check_permission("edit_profile"))):
    try:
        user = authenticate_user_token(payload.user_id, payload.old_password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build("AUTH_PASSWORD_INVALID_OLD", details={"user_id": payload.user_id}),
            )

        success = update_user_password(current_user.uid, payload.confirm_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build("AUTH_PASSWORD_UPDATE_FAILED", details={"user_id": payload.user_id}),
            )

        return SUCCESS.message("Password updated successfully", language=normalize_language(getattr(current_user, 'language', None)) if current_user else None)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in change_password: {e}", exc_info=True, module="Auth", label="CHANGE_PASSWORD")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("AUTH_PROCESSING_ERROR", exception=e),
        )

@router.post("/auth/forget-password")
async def forget_password(payload: ForgetPassword):
    """
    Change password after verifying OTP.
    """
    try:

        is_valid = await verify_otp(payload.user_id, payload.otp)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "AUTH_OTP_INVALID",
                    details={"user_id": payload.user_id},
                ),
            )


        user_id = payload.user_id.strip()
        if not (validate_phone(user_id) or validate_email(user_id)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "AUTH_INVALID_PAYLOAD",
                    details={"user_id": user_id},
                ),
            )



        user = get_user_by_email_or_phone(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR.build(
                    "USER_NOT_FOUND",
                    details={"user_id": user_id},
                ),
            )


        success = update_user_password(str(user['user_id']), payload.confirm_password)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "AUTH_FORGOT_PASSWORD_FAILED",
                    details={"user_id": user_id},
                ),
            )

        return SUCCESS.message("Password updated successfully", language=normalize_language(user.get('language')) if user and user.get('language') else None)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in forget_password: {e}", exc_info=True, module="Auth", label="FORGET_PASSWORD")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build(
                "AUTH_PROCESSING_ERROR",
                details={"user_id": payload.user_id},
                exception=e,
            ),
        )

@router.post("/auth/refresh-token")
async def refresh_token(request: Request, payload: RefreshTokenRequest):
    """
    Refresh all tokens using refresh_token from client.

    Client must send refresh_token in request body.

    This endpoint UPDATES ALL TOKENS:
    - access_token: New short-lived token (24 hours)
    - session_token: New medium-lived token (7 days) with full user profile
    - refresh_token: New long-lived token (30 days) - rotated for security
    - session_id: New session identifier

    Security:
    - Validates refresh_token signature and expiration
    - Checks if token is blacklisted or revoked
    - Implements complete token rotation (all old tokens are blacklisted)
    - Creates new session_id for all new tokens
    - Old session is invalidated, ensuring old tokens cannot be used
    """
    from jose import JWTError, jwt
    from src.authenticate.session_manager import (
        is_token_blacklisted, is_session_blacklisted,
        blacklist_token, blacklist_session,
        is_user_refresh_token_revoked
    )
    from src.authenticate.checkpoint import (
        get_user_by_id, generate_all_tokens
    )

    try:
        # Validate refresh_token is provided
        if not payload.refresh_token or not payload.refresh_token.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "AUTH_INVALID_PAYLOAD",
                    details={"message": "refresh_token is required"}
                ),
            )


        if not SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ERROR.build("AUTH_REFRESH_FAILED", details={"message": "JWT configuration error"}),
            )

        # Decode and validate refresh token
        # Try with audience first (tokens are generated with aud: 'authenticated')
        try:
            try:
                token_payload = jwt.decode(payload.refresh_token, SECRET_KEY, algorithms=[ALGORITHM], audience="authenticated")
            except JWTError as audience_error:
                # Fallback: try without audience if token wasn't created with audience
                token_payload = jwt.decode(payload.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build(
                    "AUTH_INVALID_REFRESH_TOKEN",
                    details={"message": "Refresh token has expired"}
                ),
            )
        except JWTError as e:
            logger.error(f"JWT decode error for refresh token: {e}", exc_info=True, module="Auth", label="REFRESH_TOKEN")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build(
                    "AUTH_INVALID_REFRESH_TOKEN",
                    details={"message": f"Invalid refresh token: {str(e)}"}
                ),
            )

        # Validate token type
        if token_payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build(
                    "AUTH_INVALID_TOKEN_TYPE",
                    details={"message": "Token is not a refresh token"}
                ),
            )

        # Extract user_id and session_id
        user_id = token_payload.get("sub")
        session_id = token_payload.get("session_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build(
                    "AUTH_USER_NOT_FOUND",
                    details={"message": "User ID not found in token"}
                ),
            )

        # Security checks (in order of speed - fastest first)
        # 1. Check if refresh token is blacklisted
        if await is_token_blacklisted(payload.refresh_token, token_type="refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build(
                    "AUTH_TOKEN_REVOKED",
                    details={"message": "Refresh token has been revoked"}
                ),
            )

        # 2. Check if session is blacklisted
        if session_id and await is_session_blacklisted(session_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build(
                    "AUTH_SESSION_INVALID",
                    details={"message": "Session has been revoked"}
                ),
            )

        # 3. Check if all refresh tokens for user are revoked (complete logout)
        if await is_user_refresh_token_revoked(user_id):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR.build(
                    "AUTH_SESSION_INVALID",
                    details={"message": "All refresh tokens have been revoked (user logged out)"}
                ),
            )

        # Get user data
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ERROR.build("USER_NOT_FOUND", details={"user_id": user_id}),
            )

        # Get origin for new tokens
        origin = _extract_origin(request)

        # Token rotation: Blacklist old tokens and session before generating new ones
        # This invalidates all old tokens (access, session, refresh) with the old session_id
        await blacklist_token(payload.refresh_token, token_type="refresh")
        if session_id:
            # Blacklisting session_id invalidates ALL tokens (access, session, refresh) with that session_id
            await blacklist_session(session_id)

        # Generate NEW tokens with NEW session_id (complete token rotation)
        # This updates ALL tokens: access_token, session_token, and refresh_token
        tokens = generate_all_tokens(user, origin=origin, request=request)

        return SUCCESS.response(
            message="Tokens refreshed successfully",
            data={
                "access_token": tokens['access_token'],      # NEW access token
                "refresh_token": tokens['refresh_token'],    # NEW refresh token (rotated)
                "session_token": tokens['session_token'],    # NEW session token
                "session_id": tokens['session_id'],          # NEW session ID
                "token_type": "bearer"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}", exc_info=True, module="Auth", label="REFRESH_TOKEN")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("AUTH_REFRESH_FAILED", exception=e),
        )

@router.post("/auth/logout")
async def logout(request: Request, current_user: User = Depends(check_permission("view_profile"))):
    """
    Logout user and revoke all tokens and sessions.

    Client must send access_token or session_token in Authorization header.
    This endpoint:
    - Blacklists the current access token
    - Revokes all refresh tokens for the user
    - Revokes all sessions for the user (complete logout from all devices)

    Returns detailed revocation status for each operation.

    Security:
    - Works even with expired tokens
    - Complete logout from all devices
    - All tokens are immediately invalidated
    """
    import uuid
    from src.authenticate.session_manager import (
        blacklist_access_token_by_jti,
        revoke_all_user_refresh_tokens,
        blacklist_all_user_sessions
    )
    from jose import jwt, JWTError

    user_id = str(current_user.uid)
    response_id = str(uuid.uuid4())

    # Initialize revocation statuses
    access_token_revoked = False
    refresh_tokens_revoked = False
    sessions_revoked = False
    tokens_revoked = False

    try:
        # Extract access token from request header (same as old project)
        auth_header = request.headers.get("Authorization", "")
        token = None
        token_jti = None

        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "").strip()
        else:
            # Try X-Session-Token header as fallback
            token = request.headers.get("X-Session-Token", "").strip()

        # Decode token to get JTI (for logout, we need to decode even expired tokens)
        if token:
            try:

                if not SECRET_KEY:
                    logger.error("JWT_SECRET_KEY not set in environment", module="Auth", label="LOGOUT")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=ERROR.build("AUTH_LOGOUT_FAILED", details={"message": "JWT configuration error"}),
                    )

                # Try to decode with audience first, without expiration check (for expired tokens)
                try:
                    payload = jwt.decode(
                        token,
                        SECRET_KEY,
                        algorithms=[ALGORITHM],
                        audience="authenticated",
                        options={"verify_signature": True, "verify_exp": False}
                    )
                    token_jti = payload.get("jti")
                except JWTError:
                    # Fallback: try without audience
                    try:
                        payload = jwt.decode(
                            token,
                            SECRET_KEY,
                            algorithms=[ALGORITHM],
                            options={"verify_signature": True, "verify_exp": False}
                        )
                        token_jti = payload.get("jti")
                    except JWTError:
                        # Last resort: decode without signature verification (for corrupted tokens)
                        try:
                            payload = jwt.decode(
                                token,
                                SECRET_KEY,
                                algorithms=[ALGORITHM],
                                options={"verify_signature": False, "verify_exp": False}
                            )
                            token_jti = payload.get("jti")
                        except Exception:
                            token_jti = None
                            logger.warning(f"Could not decode token for user: {user_id}", module="Auth", label="LOGOUT")

                # Blacklist current access token if JTI is available (same as old project)
                if token_jti:
                    # Use 45 days expiry (same as old project: 3888000 seconds = 45 days)
                    access_token_revoked = await blacklist_access_token_by_jti(
                        token_jti,
                        user_id,
                        expires_in_seconds=3888000  # 45 days
                    )
                    if not access_token_revoked:
                        logger.warning(f"Failed to blacklist access token for user: {user_id}, jti: {token_jti}", module="Auth", label="LOGOUT")
                else:
                    logger.warning(f"Token JTI not found in token payload for user: {user_id}", module="Auth", label="LOGOUT")

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Could not extract or blacklist access token: {e}", exc_info=True, module="Auth", label="LOGOUT")
                # Continue with logout even if token extraction fails

        # Revoke all refresh tokens for this user (same as old project)
        refresh_tokens_revoked = await revoke_all_user_refresh_tokens(user_id)
        if not refresh_tokens_revoked:
            logger.warning(f"Failed to revoke refresh tokens for user: {user_id}", module="Auth", label="LOGOUT")

        # Revoke all sessions for this user (complete logout from all devices - same as old project)
        sessions_revoked_count = await blacklist_all_user_sessions(user_id)
        sessions_revoked = sessions_revoked_count > 0
        if not sessions_revoked:
            logger.warning(f"Failed to revoke sessions for user: {user_id}", module="Auth", label="LOGOUT")

        # Determine overall tokens_revoked status
        tokens_revoked = access_token_revoked and refresh_tokens_revoked and sessions_revoked

        # Build response message (same format as old project)
        if access_token_revoked and refresh_tokens_revoked and sessions_revoked:
            logout_message = "Logged out successfully. All tokens and sessions have been revoked."
        else:
            logout_message = "Logged out successfully. Some tokens may still be active."

        # Build response data (same format as old project)
        response_data = {
            "message": "Logged out successfully",
            "access_token_revoked": access_token_revoked,
            "refresh_tokens_revoked": refresh_tokens_revoked,
            "sessions_revoked": sessions_revoked,
            "tokens_revoked": tokens_revoked
        }

        return SUCCESS.response(
            request_id=response_id,
            message=logout_message,
            data=response_data,
            meta={"type": "dict"},
            language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in logout: {e}", exc_info=True, module="Auth", label="LOGOUT")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build(
                "AUTH_LOGOUT_FAILED",
                details={"user_id": user_id},
                exception=e,
                language=normalize_language(getattr(current_user, 'language', None)) if current_user else None
            )
        )

@router.post("/auth/verify-email-and-phone", response_model=dict)
async def verify_email_and_phone(request: Request, payload: OTPVERIFYRequest):
    try:

        if payload.channel not in ["email", "sms"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build("AUTH_CHANNEL_UNSUPPORTED", details={"channel": payload.channel}),
            )


        user_id = payload.user_id.strip()
        if payload.channel == "email":
            if not validate_email(user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR.build(
                        "AUTH_INVALID_PAYLOAD",
                        details={"user_id": user_id, "channel": payload.channel, "message": "Invalid email format"},
                    ),
                )
        elif payload.channel == "sms":
            if not validate_phone(user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR.build(
                        "AUTH_INVALID_PAYLOAD",
                        details={"user_id": user_id, "channel": payload.channel, "message": "Invalid phone number format"},
                    ),
                )


        is_valid = await verify_otp(user_id, payload.otp, delete_after_verify=False)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR.build(
                    "AUTH_OTP_INVALID",
                    details={"user_id": user_id, "channel": payload.channel},
                ),
            )


        with db as cursor:
            if payload.channel == "email":
                query = """
                    UPDATE public."user"
                    SET is_email_verified = TRUE, email_verified_at = NOW()
                    WHERE LOWER(email) = LOWER(%s)
                    RETURNING user_id, is_email_verified, email_verified_at
                """
                cursor.execute(query, (payload.user_id,))
            elif payload.channel == "sms":

                phone_clean = payload.user_id.strip().replace("+", "")
                query = """
                    UPDATE public."user"
                    SET is_phone_verified = TRUE, phone_number_verified_at = NOW()
                    WHERE phone_number->>'phone' = %s OR phone_number->>'phone' = %s
                    RETURNING user_id, is_phone_verified, phone_number_verified_at
                """
                cursor.execute(query, (phone_clean, f"+{phone_clean}"))

            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=ERROR.build(
                        "AUTH_VERIFICATION_UPDATE_FAILED",
                        details={"user_id": user_id, "channel": payload.channel},
                    ),
                )


        verification_data = {
            "user_id": user_id,
            "channel": payload.channel,
            "verified": True
        }

        return SUCCESS.response(
            data=verification_data,
            message=f"{payload.channel.capitalize()} verified successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in verify_email_and_phone: {e}", exc_info=True, module="Auth", label="VERIFY_EMAIL_PHONE")
        user_id = getattr(payload, 'user_id', None)
        channel = getattr(payload, 'channel', None)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build(
                "AUTH_PROCESSING_ERROR",
                details={"user_id": user_id, "channel": channel},
                exception=e,
            ),
        )

@router.get("/auth/token-info", include_in_schema=False)
async def get_token_info_get(request: Request, current_user: User = Depends(validate_request)):
    """GET version - extracts tokens from headers only"""
    return await _get_token_info_impl(request, current_user, None)

@router.post("/auth/token-info", include_in_schema=False)
async def get_token_info_post(
    request: Request,
    current_user: User = Depends(validate_request),
    token_data: Optional[TokenInfoRequest] = Body(None)
):
    """POST version - can accept tokens in request body for comparison"""
    return await _get_token_info_impl(request, current_user, token_data)

async def _get_token_info_impl(
    request: Request,
    current_user: User,
    token_data: Optional[TokenInfoRequest]
):
    """
    Internal implementation for token-info endpoint.

    Returns simplified token information:
    - Current token status (what is)
    - Token configuration
    - Extension info (how long extended when refreshed)
    """
    from jose import jwt, JWTError
    from datetime import datetime

    try:
        # Extract current token from headers
        auth_header = request.headers.get("Authorization", "")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "").strip()
        else:
            token = request.headers.get("X-Session-Token", "").strip()

        # Helper function to convert minutes to human-readable format
        def format_duration(minutes: int) -> str:
            """Convert minutes to human-readable format"""
            if minutes < 60:
                return f"{minutes} minute{'s' if minutes != 1 else ''}"
            elif minutes < 1440:  # Less than 24 hours
                hours = minutes // 60
                remaining_minutes = minutes % 60
                if remaining_minutes == 0:
                    return f"{hours} hour{'s' if hours != 1 else ''}"
                else:
                    return f"{hours} hour{'s' if hours != 1 else ''} and {remaining_minutes} minute{'s' if remaining_minutes != 1 else ''}"
            elif minutes < 10080:  # Less than 7 days
                days = minutes // 1440
                remaining_hours = (minutes % 1440) // 60
                if remaining_hours == 0:
                    return f"{days} day{'s' if days != 1 else ''}"
                else:
                    return f"{days} day{'s' if days != 1 else ''} and {remaining_hours} hour{'s' if remaining_hours != 1 else ''}"
            else:  # 7 days or more
                days = minutes // 1440
                weeks = days // 7
                remaining_days = days % 7
                if remaining_days == 0:
                    return f"{weeks} week{'s' if weeks != 1 else ''}" if weeks > 0 else f"{days} day{'s' if days != 1 else ''}"
                else:
                    return f"{weeks} week{'s' if weeks != 1 else ''} and {remaining_days} day{'s' if remaining_days != 1 else ''}" if weeks > 0 else f"{days} day{'s' if days != 1 else ''}"

        # Get token configuration from environment
        token_config = {
            "access_token": {
                "expiry_minutes": ACCESS_TOKEN_EXPIRY,
                "expires_in": format_duration(ACCESS_TOKEN_EXPIRY)
            },
            "session_token": {
                "expiry_minutes": SESSION_TOKEN_EXPIRY,
                "expires_in": format_duration(SESSION_TOKEN_EXPIRY)
            },
            "refresh_token": {
                "expiry_minutes": REFRESH_TOKEN_EXPIRY,
                "expires_in": format_duration(REFRESH_TOKEN_EXPIRY)
            }
        }

        # Helper function to decode and analyze a token
        def decode_token_info(token_str: str, token_name: str = "token") -> dict:
            """Decode token and return detailed information"""
            try:
                # Try with audience first
                try:
                    payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM], audience="authenticated", options={"verify_exp": False})
                except JWTError:
                    # Fallback without audience
                    payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})

                token_type = payload.get("type", "access")
                exp_timestamp = payload.get("exp")
                iat_timestamp = payload.get("iat")
                session_id = payload.get("session_id")

                if exp_timestamp:
                    # Convert timestamp to datetime
                    # JWT exp/iat are Unix timestamps (seconds since epoch)
                    if isinstance(exp_timestamp, (int, float)):
                        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
                    elif isinstance(exp_timestamp, datetime):
                        exp_datetime = exp_timestamp
                    else:
                        exp_datetime = datetime.utcnow()

                    # Calculate time until expiration
                    now = datetime.utcnow()
                    if isinstance(iat_timestamp, (int, float)):
                        iat_datetime = datetime.utcfromtimestamp(iat_timestamp)
                    elif isinstance(iat_timestamp, datetime):
                        iat_datetime = iat_timestamp
                    else:
                        iat_datetime = now

                    time_until_expiry = exp_datetime - now
                    minutes_until_expiry = int(time_until_expiry.total_seconds() / 60)
                    is_expired = minutes_until_expiry <= 0

                    # Calculate age of token (how long since it was issued)
                    token_age = now - iat_datetime
                    minutes_old = int(token_age.total_seconds() / 60)
                    hours_old = minutes_old // 60
                    days_old = minutes_old // 1440

                    # Calculate token lifetime (total duration from issue to expiry)
                    token_lifetime = exp_datetime - iat_datetime
                    total_lifetime_minutes = int(token_lifetime.total_seconds() / 60)

                    # Calculate percentage of lifetime used
                    lifetime_percentage = round((minutes_old / total_lifetime_minutes * 100), 1) if total_lifetime_minutes > 0 else 0

                    return {
                        "token_type": token_type,
                        "token_age": format_duration(abs(minutes_old)),
                        "token_age_minutes": minutes_old,
                        "token_age_hours": hours_old if hours_old > 0 else None,
                        "token_age_days": days_old if days_old > 0 else None,
                        "expires_in": format_duration(abs(minutes_until_expiry)) if not is_expired else "EXPIRED",
                        "expires_in_minutes": minutes_until_expiry,
                        "lifetime_percentage_used": lifetime_percentage,
                        "is_expired": is_expired,
                        "status": "EXPIRED" if is_expired else "ACTIVE"
                    }
                else:
                    return {
                        "error": "No expiration time in token",
                        "token_type": token_type
                    }
            except Exception as e:
                logger.warning(f"Could not decode token: {e}", module="Auth", label="TOKEN_INFO")
                return {
                    "error": "Could not decode token",
                    "message": str(e)
                }

        # Decode all available tokens for comprehensive age information
        current_token_info = None
        access_token_info = None
        session_token_info = None
        refresh_token_info = None

        if token:
            current_token_info = decode_token_info(token, "current_token")

        # Extract and decode all tokens from headers for complete age information
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            access_token = auth_header.replace("Bearer ", "").strip()
            if access_token and access_token != token:
                access_token_info = decode_token_info(access_token, "access_token")

        session_token_header = request.headers.get("X-Session-Token", "").strip()
        if session_token_header and session_token_header != token:
            session_token_info = decode_token_info(session_token_header, "session_token")

        # If tokens provided in request body, decode them for comparison (before/after)
        before_token_info = None
        if token_data:
            # Decode all provided tokens to show their ages
            if token_data.access_token:
                if not access_token_info:
                    access_token_info = decode_token_info(token_data.access_token, "access_token")
                else:
                    before_token_info = decode_token_info(token_data.access_token, "before")
            if token_data.session_token:
                if not session_token_info:
                    session_token_info = decode_token_info(token_data.session_token, "session_token")
                else:
                    before_token_info = decode_token_info(token_data.session_token, "before")
            if token_data.refresh_token:
                refresh_token_info = decode_token_info(token_data.refresh_token, "refresh_token")
                if not before_token_info:
                    before_token_info = refresh_token_info

        # Calculate extension info (how long extended when refreshed)
        extension_info = {}
        if current_token_info and not current_token_info.get("error"):
            token_type = current_token_info.get("token_type")
            if token_type == "access":
                extension_info = {
                    "current_expires_in": current_token_info.get("expires_in"),
                    "after_refresh_expires_in": format_duration(ACCESS_TOKEN_EXPIRY),
                    "extension_minutes": ACCESS_TOKEN_EXPIRY
                }
            elif token_type == "session":
                extension_info = {
                    "current_expires_in": current_token_info.get("expires_in"),
                    "after_refresh_expires_in": format_duration(SESSION_TOKEN_EXPIRY),
                    "extension_minutes": SESSION_TOKEN_EXPIRY
                }
            elif token_type == "refresh":
                extension_info = {
                    "current_expires_in": current_token_info.get("expires_in"),
                    "after_refresh_expires_in": format_duration(REFRESH_TOKEN_EXPIRY),
                    "extension_minutes": REFRESH_TOKEN_EXPIRY
                }

        # Build all tokens info with ages
        all_tokens_ages = {}

        if current_token_info and not current_token_info.get("error"):
            all_tokens_ages["current"] = {
                "token_type": current_token_info.get("token_type"),
                "token_age": current_token_info.get("token_age"),
                "token_age_minutes": current_token_info.get("token_age_minutes"),
                "expires_in": current_token_info.get("expires_in"),
                "expires_in_minutes": current_token_info.get("expires_in_minutes"),
                "lifetime_percentage_used": current_token_info.get("lifetime_percentage_used"),
                "status": current_token_info.get("status")
            }

        if access_token_info and not access_token_info.get("error"):
            all_tokens_ages["access_token"] = {
                "token_age": access_token_info.get("token_age"),
                "token_age_minutes": access_token_info.get("token_age_minutes"),
                "expires_in": access_token_info.get("expires_in"),
                "expires_in_minutes": access_token_info.get("expires_in_minutes"),
                "lifetime_percentage_used": access_token_info.get("lifetime_percentage_used"),
                "status": access_token_info.get("status")
            }

        if session_token_info and not session_token_info.get("error"):
            all_tokens_ages["session_token"] = {
                "token_age": session_token_info.get("token_age"),
                "token_age_minutes": session_token_info.get("token_age_minutes"),
                "expires_in": session_token_info.get("expires_in"),
                "expires_in_minutes": session_token_info.get("expires_in_minutes"),
                "lifetime_percentage_used": session_token_info.get("lifetime_percentage_used"),
                "status": session_token_info.get("status")
            }

        if refresh_token_info and not refresh_token_info.get("error"):
            all_tokens_ages["refresh_token"] = {
                "token_age": refresh_token_info.get("token_age"),
                "token_age_minutes": refresh_token_info.get("token_age_minutes"),
                "expires_in": refresh_token_info.get("expires_in"),
                "expires_in_minutes": refresh_token_info.get("expires_in_minutes"),
                "lifetime_percentage_used": refresh_token_info.get("lifetime_percentage_used"),
                "status": refresh_token_info.get("status")
            }

        # Build simplified response (no sensitive security info)
        response_data = {
            "token_ages": all_tokens_ages if all_tokens_ages else {"current": current_token_info if current_token_info else {"error": "No token found"}},
            "token_configuration": token_config,
            "extension_info": extension_info
        }

        # Add before/after comparison if available
        if before_token_info and not before_token_info.get("error"):
            response_data["before_token"] = {
                "token_age": before_token_info.get("token_age"),
                "token_age_minutes": before_token_info.get("token_age_minutes"),
                "expires_in": before_token_info.get("expires_in"),
                "expires_in_minutes": before_token_info.get("expires_in_minutes"),
                "status": before_token_info.get("status")
            }
            # Calculate how much time was extended
            if current_token_info and not current_token_info.get("error"):
                before_expires = before_token_info.get("expires_in_minutes", 0)
                current_expires = current_token_info.get("expires_in_minutes", 0)
                if before_expires > 0 and current_expires > 0:
                    extended_minutes = current_expires - before_expires
                    if extended_minutes > 0:
                        response_data["extension_info"]["extended_by"] = format_duration(extended_minutes)
                        response_data["extension_info"]["extended_by_minutes"] = extended_minutes

        return SUCCESS.response(
            message="Token information retrieved successfully",
            data=response_data,
            meta={"type": "dict"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting token info: {e}", exc_info=True, module="Auth", label="TOKEN_INFO")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR.build("AUTH_PROCESSING_ERROR", exception=e),
        )