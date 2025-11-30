from typing import Dict, Optional, Any
from pydantic import BaseModel
from datetime import datetime

from src.enum.enum import LanguageStatusEnum

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Token data model matching USERObject structure.
    Contains all user information stored in JWT token.
    """
    # Primary key
    user_id: Optional[str] = None
    uid: Optional[str] = None  # Alias for user_id for backward compatibility

    # Basic user information (matching USERList)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[Dict[str, Any]] = None
    country: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[datetime] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    portfolio_url: Optional[str] = None
    user_name: Optional[str] = None

    # App settings
    show_kliky_watermark: Optional[bool] = True
    ads_show_type: Optional[str] = None
    wallet: Optional[int] = None
    display_name: Optional[str] = None

    # Enums
    auth_type: Optional[str] = None
    theme: Optional[str] = None
    profile_accessibility: Optional[str] = None
    user_type: Optional[str] = None
    language: Optional[str] = None

    # STATUSModel fields
    is_draft: Optional[bool] = False
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = True
    is_deleted: Optional[bool] = False

    # Status and role
    status: Optional[str] = "Inactive"
    role_id: Optional[str] = None
    timezone: Optional[str] = None
    invited_by_user_id: Optional[str] = None

    # Protection and trash flags
    is_protected: Optional[bool] = False
    is_trashed: Optional[bool] = False

    # Timestamps
    last_sign_in_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    # Legacy permission fields
    is_user: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_admin: Optional[bool] = False
    is_business: Optional[bool] = False
    is_accountant: Optional[bool] = False
    is_developer: Optional[bool] = False
    @property
    def uid(self) -> Optional[str]:
        """Alias for user_id for backward compatibility"""
        return self.user_id

    @uid.setter
    def uid(self, value: Optional[str]):
        """Set both uid and user_id when uid is set"""
        self.user_id = value


class User(BaseModel):
    """
    Unified User model - merged from User and USERObject.
    Contains all user information for authenticated requests and profile display.
    """
    # Primary key
    user_id: Optional[str] = None

    @property
    def uid(self) -> Optional[str]:
        """Alias for user_id for backward compatibility"""
        return self.user_id

    @uid.setter
    def uid(self, value: Optional[str]):
        """Set both uid and user_id when uid is set"""
        self.user_id = value

    # Basic user information (matching USERList)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[Dict[str, Any]] = None
    country: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[datetime] = None
    profile_picture_url: Optional[str] = None
    bio: Optional[str] = None
    portfolio_url: Optional[str] = None
    user_name: Optional[str] = None

    # App settings
    show_kliky_watermark: Optional[bool] = True
    ads_show_type: Optional[Any] = None  # Accepts enum or string
    wallet: Optional[int] = None  # Keep for backward compatibility
    display_name: Optional[str] = None  # Keep for backward compatibility

    # Enums - accept both enum types and strings for flexibility
    auth_type: Optional[Any] = None  # AuthTypeEnum or str
    theme: Optional[Any] = None  # ThemeEnum or str
    profile_accessibility: Optional[Any] = None  # ProfileAccessibilityEnum or str
    user_type: Optional[Any] = None  # UserTypeEnum or str
    language: Optional[Any] = LanguageStatusEnum.en  # LanguageStatusEnum or str

    # STATUSModel fields
    is_draft: Optional[bool] = False
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = True
    is_deleted: Optional[bool] = False

    # Status and role
    status: Optional[str] = "INACTIVE"  # ACTIVE, INACTIVE, SUSPENDED, DELETED
    role_id: Optional[str] = None
    timezone: Optional[str] = None
    invited_by_user_id: Optional[str] = None

    # Protection and trash flags
    is_protected: Optional[bool] = False
    is_trashed: Optional[bool] = False
    is_email_verified: Optional[bool] = False
    is_phone_verified: Optional[bool] = False

    # Timestamps
    last_sign_in_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    phone_number_verified_at: Optional[datetime] = None

    class Config:
        # Allow enum values to be serialized as strings
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

        # Handle enum conversion
        @staticmethod
        def json_schema_extra(schema: dict, model) -> None:
            """Ensure enum fields accept both enum and string values"""
            pass
