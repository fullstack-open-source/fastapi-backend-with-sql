"""
Permission Model - Matches Prisma Permission model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class Permission(Base):
    """
    Permission Model
    Matches: model Permission from schema.prisma
    """
    __tablename__ = "permission"

    # Primary Key
    permission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Fields
    name = Column(String(100), unique=True, nullable=False)
    codename = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=True)
    last_updated = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    # Relationships
    # Permission -> GroupPermission -> Group (many-to-many)
    group_permissions = relationship("GroupPermission", back_populates="permission", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_permission_codename', 'codename'),
        Index('ix_permission_category', 'category'),
    )

    def __repr__(self):
        return f"<Permission(permission_id={self.permission_id}, codename={self.codename})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "permission_id": str(self.permission_id) if self.permission_id else None,
            "name": self.name,
            "codename": self.codename,
            "description": self.description,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

