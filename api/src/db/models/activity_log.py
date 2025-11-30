"""
ActivityLog Model - Matches Prisma ActivityLog model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base

class ActivityLog(Base):
    """
    User Activity Log Model
    Matches: model ActivityLog from schema.prisma
    """
    __tablename__ = "activity_log"

    # Primary Key
    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Key
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.user_id", ondelete="SET NULL"), nullable=True)

    # Log Details
    level = Column(String(20), default="info", nullable=False)  # info, warn, error, debug, audit
    message = Column(Text, nullable=False)
    action = Column(String(100), nullable=True)  # e.g., "login", "logout", "create_user", "update_permission"
    module = Column(String(50), nullable=True)  # e.g., "authentication", "permissions", "dashboard"

    # Request Details
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    device = Column(String(100), nullable=True)  # e.g., "Desktop", "Mobile", "Tablet"
    browser = Column(String(100), nullable=True)  # e.g., "Chrome", "Firefox", "Safari"
    os = Column(String(100), nullable=True)  # e.g., "Windows", "Linux", "macOS", "iOS", "Android"
    platform = Column(String(50), nullable=True)  # e.g., "web", "mobile_app", "api"

    # API Details
    endpoint = Column(String(255), nullable=True)  # API endpoint or page URL
    method = Column(String(10), nullable=True)  # HTTP method: GET, POST, PUT, DELETE, etc.
    status_code = Column(Integer, nullable=True)  # HTTP status code
    request_id = Column(String(100), nullable=True)  # Unique request identifier
    session_id = Column(String(100), nullable=True)  # Session identifier

    # Additional Data
    # Note: Using 'log_metadata' as Python attribute name to avoid conflict with SQLAlchemy's reserved 'metadata'
    # Database column name remains 'metadata' to match Prisma schema
    log_metadata = Column("metadata", JSONB, nullable=True)  # Additional data as JSON
    error_details = Column(JSONB, nullable=True)  # Error stack trace, details
    duration_ms = Column(Integer, nullable=True)  # Request/action duration in milliseconds

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="activity_logs")

    # Indexes
    __table_args__ = (
        Index('ix_activity_log_user_id', 'user_id'),
        Index('ix_activity_log_level', 'level'),
        Index('ix_activity_log_action', 'action'),
        Index('ix_activity_log_module', 'module'),
        Index('ix_activity_log_created_at', 'created_at'),
        Index('ix_activity_log_ip_address', 'ip_address'),
        Index('ix_activity_log_request_id', 'request_id'),
        Index('ix_activity_log_session_id', 'session_id'),
    )

    def __repr__(self):
        return f"<ActivityLog(log_id={self.log_id}, action={self.action}, level={self.level})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "log_id": str(self.log_id) if self.log_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "level": self.level,
            "message": self.message,
            "action": self.action,
            "module": self.module,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "device": self.device,
            "browser": self.browser,
            "os": self.os,
            "platform": self.platform,
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "metadata": self.log_metadata,  # Use log_metadata but output as metadata
            "error_details": self.error_details,
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

