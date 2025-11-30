from src.enum.enum import ProfileAccessibilityEnum, LanguageStatusEnum
from pydantic import BaseModel, validator
from typing import Optional
import re

class OTPRequest(BaseModel):
    user_id: str
    channel: str

class OTPVERIFYRequest(BaseModel):
    user_id: str
    channel: str
    otp: str


class UserProfileAccessibility(BaseModel):
    profile_accessibility: ProfileAccessibilityEnum = ProfileAccessibilityEnum.public

class UserProfileLanguage(BaseModel):
    language: LanguageStatusEnum = LanguageStatusEnum.en


class ChangeEmailRequest(BaseModel):
    new_email: str = None
    otp: str  = None

class ChangePhoneRequest(BaseModel):
    new_phone: str = None
    otp: str  = None

class ImageModel(BaseModel):
    url: str

class SetPassword(BaseModel):
    password: str
    confirm_password: str

    @validator("password")
    def strong_password(cls, v):
        """
        Validate password strength.
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values):
        """
        Ensure confirm_password matches password.
        """
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v
class PasswordChange(SetPassword):
    user_id: str
    channel: str
    old_password: str


class ForgetPassword(SetPassword):
    user_id: str
    otp: Optional[str] = ""
    channel: Optional[str] = ""

class CheckUserAvailabilityRequest(BaseModel):
    user_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    """
    Request model for refresh token endpoint.

    Client must send refresh_token in request body.
    Example:
    {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    """
    refresh_token: str

    @validator("refresh_token")
    def validate_refresh_token(cls, v):
        """Validate refresh_token is provided and not empty"""
        if not v or not v.strip():
            raise ValueError("refresh_token is required and cannot be empty")
        return v.strip()


class TokenInfoRequest(BaseModel):
    """
    Optional request model for token-info endpoint.
    Allows passing tokens in request body for detailed comparison.
    """
    access_token: Optional[str] = None
    session_token: Optional[str] = None
    refresh_token: Optional[str] = None
