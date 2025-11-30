"""
Group Model - Matches Prisma Group model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class Group(Base):
    """
    Group Model
    Matches: model Group from schema.prisma
    """
    __tablename__ = "group"

    # Primary Key
    group_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Fields
    name = Column(String(100), unique=True, nullable=False)
    codename = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=True)
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # Relationships
    # Group -> GroupPermission -> Permission (many-to-many)
    # Group -> UserGroup -> User (many-to-many)
    group_permissions = relationship("GroupPermission", back_populates="group", cascade="all, delete-orphan")
    user_groups = relationship("UserGroup", back_populates="group", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_group_codename', 'codename'),
        Index('ix_group_is_active', 'is_active'),
    )

    def __repr__(self):
        return f"<Group(group_id={self.group_id}, codename={self.codename})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "group_id": str(self.group_id) if self.group_id else None,
            "name": self.name,
            "codename": self.codename,
            "description": self.description,
            "is_system": self.is_system,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

