"""
GroupPermission Model - Matches Prisma GroupPermission model
Many-to-Many relationship between Group and Permission
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class GroupPermission(Base):
    """
    Group-Permission Mapping (Many-to-Many)
    Matches: model GroupPermission from schema.prisma
    """
    __tablename__ = "group_permission"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    group_id = Column(UUID(as_uuid=True), ForeignKey("group.group_id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permission.permission_id", ondelete="CASCADE"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=True)

    # Relationships
    group = relationship("Group", back_populates="group_permissions")
    permission = relationship("Permission", back_populates="group_permissions")

    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('group_id', 'permission_id', name='uq_group_permission'),
        Index('ix_group_permission_group_id', 'group_id'),
        Index('ix_group_permission_permission_id', 'permission_id'),
    )

    def __repr__(self):
        return f"<GroupPermission(id={self.id}, group_id={self.group_id}, permission_id={self.permission_id})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id) if self.id else None,
            "group_id": str(self.group_id) if self.group_id else None,
            "permission_id": str(self.permission_id) if self.permission_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

