"""
Activity Router - Models
Pydantic models for request/response validation
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any


class ActivityLogCreate(BaseModel):
    level: Optional[str] = "info"
    message: str
    action: Optional[str] = None
    module: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    platform: Optional[str] = "web"
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None

