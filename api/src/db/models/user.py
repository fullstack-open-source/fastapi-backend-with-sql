"""
User Model - Matches Prisma User model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    """
    User Model - Basic structure for relationships
    Matches: model User from schema.prisma
    """
    __tablename__ = "user"

    # Primary Key
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=True)
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # Basic Information
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    country = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    dob = Column(DateTime(timezone=True), nullable=True)
    email = Column(String, unique=True, nullable=True)
    profile_picture_url = Column(String, nullable=True)
    phone_number = Column(JSONB, nullable=True)

    # Authentication
    auth_type = Column(String, nullable=True)
    password = Column(String, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=True)
    is_phone_verified = Column(Boolean, default=False, nullable=True)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    phone_number_verified_at = Column(DateTime(timezone=True), nullable=True)
    last_sign_in_at = Column(DateTime(timezone=True), nullable=True)

    # User Preferences
    bio = Column(String, nullable=True)
    theme = Column(String, nullable=True)
    profile_accessibility = Column(String, nullable=True)
    user_type = Column(String, nullable=True)
    user_name = Column(String, unique=True, nullable=True)
    language = Column(String, nullable=True)

    # Status
    status = Column(String, default="INACTIVE", nullable=True)
    timezone = Column(String, nullable=True)
    invited_by_user_id = Column(UUID(as_uuid=True), nullable=True)

    # Protection and Trash
    is_protected = Column(Boolean, default=False, nullable=True)
    is_trashed = Column(Boolean, default=False, nullable=True)

    # Status Model Fields
    is_active = Column(Boolean, default=False, nullable=True)
    is_verified = Column(Boolean, default=False, nullable=True)

    # Relationships
    # User -> UserGroup -> Group -> GroupPermission -> Permission
    user_groups = relationship("UserGroup", back_populates="user", foreign_keys="UserGroup.user_id", cascade="all, delete-orphan")
    assigned_user_groups = relationship("UserGroup", back_populates="assigned_by_user", foreign_keys="UserGroup.assigned_by_user_id")
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_user_email', 'email'),
        Index('ix_user_user_name', 'user_name'),
    )

    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "user_id": str(self.user_id) if self.user_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "country": self.country,
            "gender": self.gender,
            "dob": self.dob.isoformat() if self.dob else None,
            "email": self.email,
            "profile_picture_url": self.profile_picture_url,
            "phone_number": self.phone_number,
            "auth_type": self.auth_type,
            "is_email_verified": self.is_email_verified,
            "is_phone_verified": self.is_phone_verified,
            "email_verified_at": self.email_verified_at.isoformat() if self.email_verified_at else None,
            "phone_number_verified_at": self.phone_number_verified_at.isoformat() if self.phone_number_verified_at else None,
            "last_sign_in_at": self.last_sign_in_at.isoformat() if self.last_sign_in_at else None,
            "bio": self.bio,
            "theme": self.theme,
            "profile_accessibility": self.profile_accessibility,
            "user_type": self.user_type,
            "user_name": self.user_name,
            "language": self.language,
            "status": self.status,
            "timezone": self.timezone,
            "invited_by_user_id": str(self.invited_by_user_id) if self.invited_by_user_id else None,
            "is_protected": self.is_protected,
            "is_trashed": self.is_trashed,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
        }

