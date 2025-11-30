"""
UserGroup Model - Matches Prisma UserGroup model
Many-to-Many relationship between User and Group
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base


class UserGroup(Base):
    """
    User-Group Mapping (Many-to-Many)
    Matches: model UserGroup from schema.prisma
    """
    __tablename__ = "user_group"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    group_id = Column(UUID(as_uuid=True), ForeignKey("group.group_id", ondelete="CASCADE"), nullable=False)
    assigned_by_user_id = Column(UUID(as_uuid=True), ForeignKey("user.user_id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    assigned_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=True)

    # Relationships
    user = relationship("User", back_populates="user_groups", foreign_keys=[user_id])
    group = relationship("Group", back_populates="user_groups")
    assigned_by_user = relationship("User", back_populates="assigned_user_groups", foreign_keys=[assigned_by_user_id])

    # Constraints and Indexes
    __table_args__ = (
        UniqueConstraint('user_id', 'group_id', name='uq_user_group'),
        Index('ix_user_group_user_id', 'user_id'),
        Index('ix_user_group_group_id', 'group_id'),
    )

    def __repr__(self):
        return f"<UserGroup(id={self.id}, user_id={self.user_id}, group_id={self.group_id})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id) if self.id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "group_id": str(self.group_id) if self.group_id else None,
            "assigned_by_user_id": str(self.assigned_by_user_id) if self.assigned_by_user_id else None,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
        }

