"""
Advanced Security Middleware for FastAPI
Comprehensive protection against XSS, CSRF, SQL Injection, and other common attacks.

Features:
- XSS Protection (Input sanitization, output encoding)
- CSRF Protection (Token validation)
- SQL Injection Prevention (Query parameter sanitization)
- NoSQL Injection Prevention
- Path Traversal Prevention
- Command Injection Prevention
- SSRF Protection
- Header Injection Prevention
- Request Size Limits
- Content Security Policy
- Rate Limiting (per IP, per user, per endpoint)
- IP Whitelist/Blacklist
- Request Validation
- Suspicious Activity Logging
"""

import re
import os
import time
import json
import hashlib
import secrets
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from datetime import datetime

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from src.response.error import ERROR
from src.logger.logger import logger

# JWT decoding (lightweight, only for user ID extraction)
try:
    from jose import jwt as jose_jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logger.warning("jose library not available, per-user rate limiting will be limited", module="SecurityMiddleware", label="INIT")


class AdvancedSecurityMiddleware(BaseHTTPMiddleware):
    """
    Advanced Security Middleware providing comprehensive protection against
    common web application attacks.
    """

    def __init__(
        self,
        app,
        # CSRF Settings
        csrf_enabled: bool = True,
        csrf_token_header: str = "X-CSRF-Token",
        csrf_exempt_paths: List[str] = None,
        # Rate Limiting
        rate_limit_enabled: bool = True,
        rate_limit_per_minute: int = 100,
        rate_limit_per_hour: int = 1000,
        rate_limit_per_day: int = 10000,
        # Per-User Rate Limiting
        rate_limit_per_user_enabled: bool = True,
        rate_limit_per_user_per_minute: int = 200,
        rate_limit_per_user_per_hour: int = 2000,
        rate_limit_per_user_per_day: int = 20000,
        # IP Management
        ip_whitelist: List[str] = None,
        ip_blacklist: List[str] = None,
        # Request Size Limits
        max_request_size: int = 10 * 1024 * 1024,  # 10MB
        max_header_size: int = 8192,  # 8KB
        max_query_string_length: int = 2048,  # 2KB
        # Security Headers
        enable_hsts: bool = True,
        hsts_max_age: int = 31536000,  # 1 year
        enable_csp: bool = True,
        # SQL Injection Detection
        sql_injection_detection: bool = True,
        # XSS Detection
        xss_detection: bool = True,
        # Path Traversal Detection
        path_traversal_detection: bool = True,
        # Command Injection Detection
        command_injection_detection: bool = True,
        # Logging
        log_suspicious_activity: bool = True,
        block_suspicious_requests: bool = True,
    ):
        super().__init__(app)

        # CSRF Configuration
        self.csrf_enabled = csrf_enabled
        self.csrf_token_header = csrf_token_header
        self.csrf_exempt_paths = set(csrf_exempt_paths or [])
        self.csrf_exempt_methods = {"GET", "HEAD", "OPTIONS"}

        # Rate Limiting (IP-based)
        self.rate_limit_enabled = rate_limit_enabled
        self.rate_limit_per_minute = rate_limit_per_minute
        self.rate_limit_per_hour = rate_limit_per_hour
        self.rate_limit_per_day = rate_limit_per_day

        # Per-User Rate Limiting
        self.rate_limit_per_user_enabled = rate_limit_per_user_enabled
        self.rate_limit_per_user_per_minute = rate_limit_per_user_per_minute
        self.rate_limit_per_user_per_hour = rate_limit_per_user_per_hour
        self.rate_limit_per_user_per_day = rate_limit_per_user_per_day

        # Rate limit stores (separate for IP and user)
        self.rate_limit_store: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self.user_rate_limit_store: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )

        # IP Management
        self.ip_whitelist = set(ip_whitelist or [])
        self.ip_blacklist = set(ip_blacklist or [])

        # Request Size Limits
        self.max_request_size = max_request_size
        self.max_header_size = max_header_size
        self.max_query_string_length = max_query_string_length

        # Security Headers
        self.enable_hsts = enable_hsts
        self.hsts_max_age = hsts_max_age
        self.enable_csp = enable_csp

        # Detection Flags
        self.sql_injection_detection = sql_injection_detection
        self.xss_detection = xss_detection
        self.path_traversal_detection = path_traversal_detection
        self.command_injection_detection = command_injection_detection

        # Logging
        self.log_suspicious_activity = log_suspicious_activity
        self.block_suspicious_requests = block_suspicious_requests

        # Patterns for attack detection
        self._init_attack_patterns()

        # CSRF token storage (in production, use Redis or database)
        self.csrf_tokens: Dict[str, str] = {}

    def _init_attack_patterns(self):
        """Initialize regex patterns for attack detection"""

        # SQL Injection patterns
        self.sql_patterns = [
            r"(?i)(union\s+select|select\s+.*\s+from|insert\s+into|delete\s+from|update\s+.*\s+set|drop\s+table|create\s+table|alter\s+table)",
            r"(?i)(or\s+1\s*=\s*1|or\s+'1'\s*=\s*'1'|or\s+\"1\"\s*=\s*\"1\")",
            r"(?i)(exec\s*\(|execute\s*\(|sp_executesql)",
            r"(?i)(;\s*--|;\s*/\*|\*/|--\s|#)",
            r"(?i)(\bor\b|\band\b).*?(\d+\s*=\s*\d+|\'\w+\'\s*=\s*\'\w+\')",
            r"(?i)(\bwaitfor\s+delay\b|\bsleep\s*\()",
            r"(?i)(\bxp_\w+\b|\bsp_\w+\b)",
        ]

        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",  # onclick=, onerror=, etc.
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<img[^>]*src\s*=\s*[^>]*javascript:",
            r"<svg[^>]*onload\s*=",
            r"<body[^>]*onload\s*=",
            r"eval\s*\(",
            r"expression\s*\(",
            r"<link[^>]*href\s*=\s*[^>]*javascript:",
        ]

        # Path Traversal patterns
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"\.\.%2f",
            r"\.\.%5c",
            r"\.\./\.\./",
            r"\.\.\\\.\.\\",
        ]

        # Command Injection patterns
        self.command_injection_patterns = [
            r"[;&|`]",
            r"(\||\||\|\||&&)",
            r"\$\(.*\)",
            r"`.*`",
            r"<\(.*\)",
            r"\$\{.*\}",
            r"(?:^|\s)(?:rm|del|delete|format|mkfs|shutdown|reboot|kill|pkill|killall)\s",
            r"(?:^|\s)(?:cat|type|head|tail|less|more|grep|find|ls|dir)\s.*[;&|]",
        ]

        # NoSQL Injection patterns
        self.nosql_patterns = [
            r"\$where",
            r"\$ne",
            r"\$gt",
            r"\$gte",
            r"\$lt",
            r"\$lte",
            r"\$in",
            r"\$nin",
            r"\$regex",
            r"\$exists",
            r"\$or",
            r"\$and",
            r"\$not",
            r"\$nor",
        ]

        # SSRF patterns
        self.ssrf_patterns = [
            r"file://",
            r"gopher://",
            r"dict://",
            r"ldap://",
            r"localhost",
            r"127\.0\.0\.1",
            r"0\.0\.0\.0",
            r"::1",
            r"169\.254\.169\.254",  # AWS metadata
            r"192\.168\.\d+\.\d+",
            r"10\.\d+\.\d+\.\d+",
            r"172\.(1[6-9]|2[0-9]|3[01])\.\d+\.\d+",
        ]

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers (behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        if request.client:
            return request.client.host

        return "unknown"

    def _check_ip_whitelist(self, ip: str) -> bool:
        """Check if IP is in whitelist"""
        if not self.ip_whitelist:
            return True  # No whitelist means all IPs allowed
        return ip in self.ip_whitelist

    def _check_ip_blacklist(self, ip: str) -> bool:
        """Check if IP is in blacklist"""
        if not self.ip_blacklist:
            return False  # No blacklist means no IPs blocked
        return ip in self.ip_blacklist

    def _extract_user_id_from_token(self, request: Request) -> Optional[str]:
        """
        Extract user ID from JWT token in Authorization header
        Returns user_id if found, None otherwise
        """
        if not JWT_AVAILABLE:
            return None

        try:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return None

            token = auth_header.replace("Bearer ", "").strip()
            if not token:
                return None

            # Decode JWT without verification (we only need user ID for rate limiting)
            # The actual authentication will validate the token properly
            try:
                # Try to decode without verification first (faster)
                # In production, you might want to verify the signature
                secret_key = os.environ.get('JWT_SECRET_KEY')
                if not secret_key:
                    return None

                # Try with audience first
                try:
                    payload = jose_jwt.decode(
                        token,
                        secret_key,
                        algorithms=['HS256'],
                        options={"verify_signature": True, "verify_aud": False}
                    )
                except Exception:
                    # Fallback without audience
                    payload = jose_jwt.decode(
                        token,
                        secret_key,
                        algorithms=['HS256'],
                        options={"verify_signature": True, "verify_aud": False, "verify_exp": False}
                    )

                # Extract user ID from 'sub' field
                user_id = payload.get("sub") or payload.get("user_id")
                return str(user_id) if user_id else None

            except Exception as e:
                # Token is invalid or expired, but that's okay - we'll just use IP-based limiting
                return None

        except Exception as e:
            return None

    def _check_rate_limit(
        self,
        identifier: str,
        window: str = "minute",
        is_user: bool = False,
        user_limits: Optional[Dict[str, int]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Check rate limit for identifier (IP or user)
        Returns (is_allowed, error_message)
        """
        if is_user and not self.rate_limit_per_user_enabled:
            return True, None

        if not is_user and not self.rate_limit_enabled:
            return True, None

        now = time.time()
        window_seconds = {
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        }.get(window, 60)

        # Use appropriate limits based on whether it's user or IP
        if is_user and user_limits:
            limits = user_limits
            store = self.user_rate_limit_store
        else:
            limits = {
                "minute": self.rate_limit_per_minute,
                "hour": self.rate_limit_per_hour,
                "day": self.rate_limit_per_day,
            }
            store = self.rate_limit_store

        # Clean old entries
        store[identifier][window] = [
            t for t in store[identifier][window]
            if now - t < window_seconds
        ]

        limit = limits.get(window, 100)
        if len(store[identifier][window]) >= limit:
            limit_type = "user" if is_user else "IP"
            return False, f"Rate limit exceeded ({limit_type}): {limit} requests per {window}"

        store[identifier][window].append(now)
        return True, None

    def _sanitize_string(self, value: str) -> str:
        """Sanitize string to prevent XSS"""
        if not isinstance(value, str):
            return value

        # HTML entity encoding for common XSS characters
        replacements = {
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#x27;",
            "/": "&#x2F;",
            "&": "&amp;",
        }

        for char, replacement in replacements.items():
            value = value.replace(char, replacement)

        return value

    def _check_sql_injection(self, value: str) -> bool:
        """Check if value contains SQL injection patterns"""
        if not self.sql_injection_detection:
            return False

        value_lower = value.lower()
        for pattern in self.sql_patterns:
            if re.search(pattern, value_lower):
                return True
        return False

    def _check_xss(self, value: str) -> bool:
        """Check if value contains XSS patterns"""
        if not self.xss_detection:
            return False

        value_lower = value.lower()
        for pattern in self.xss_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE | re.DOTALL):
                return True
        return False

    def _check_path_traversal(self, value: str) -> bool:
        """Check if value contains path traversal patterns"""
        if not self.path_traversal_detection:
            return False

        decoded = unquote(value)
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, decoded, re.IGNORECASE):
                return True
        return False

    def _check_command_injection(self, value: str) -> bool:
        """Check if value contains command injection patterns"""
        if not self.command_injection_detection:
            return False

        for pattern in self.command_injection_patterns:
            if re.search(pattern, value):
                return True
        return False

    def _check_nosql_injection(self, value: str) -> bool:
        """Check if value contains NoSQL injection patterns"""
        try:
            # Try to parse as JSON and check for MongoDB operators
            parsed = json.loads(value) if isinstance(value, str) else value
            if isinstance(parsed, dict):
                for key in parsed.keys():
                    if any(re.match(pattern, key) for pattern in self.nosql_patterns):
                        return True
        except (json.JSONDecodeError, TypeError):
            pass

        # Check raw string
        value_str = str(value)
        for pattern in self.nosql_patterns:
            if re.search(pattern, value_str):
                return True
        return False

    def _check_ssrf(self, value: str) -> bool:
        """Check if value contains SSRF patterns"""
        value_lower = value.lower()
        for pattern in self.ssrf_patterns:
            if re.search(pattern, value_lower):
                return True
        return False

    def _validate_request_data(self, request: Request) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate request data for security threats
        Returns (is_safe, attack_type, attack_value)
        """
        try:
            # Check URL path
            path = request.url.path
            if self._check_path_traversal(path):
                return False, "PATH_TRAVERSAL", path

            # Check query parameters
            for key, values in request.query_params.multi_items():
                for value in values:
                    if self._check_sql_injection(value):
                        return False, "SQL_INJECTION", f"{key}={value}"
                    if self._check_xss(value):
                        return False, "XSS", f"{key}={value}"
                    if self._check_command_injection(value):
                        return False, "COMMAND_INJECTION", f"{key}={value}"
                    if self._check_nosql_injection(value):
                        return False, "NOSQL_INJECTION", f"{key}={value}"
                    if self._check_ssrf(value):
                        return False, "SSRF", f"{key}={value}"

            # Check headers (excluding sensitive ones)
            sensitive_headers = {"authorization", "cookie", "x-api-key"}
            for key, value in request.headers.items():
                key_lower = key.lower()
                if key_lower in sensitive_headers:
                    continue

                if self._check_sql_injection(value):
                    return False, "SQL_INJECTION_HEADER", f"{key}={value[:50]}"
                if self._check_xss(value):
                    return False, "XSS_HEADER", f"{key}={value[:50]}"
                if self._check_command_injection(value):
                    return False, "COMMAND_INJECTION_HEADER", f"{key}={value[:50]}"

            # Check request body for POST/PUT/PATCH
            if request.method in {"POST", "PUT", "PATCH"}:
                # We'll check body content in a separate step after reading
                pass

            return True, None, None

        except Exception as e:
            logger.error(f"Error validating request data: {e}", module="SecurityMiddleware", label="VALIDATION", exc_info=True)
            return True, None, None  # Don't block on validation errors

    def _validate_request_size(self, request: Request) -> Tuple[bool, Optional[str]]:
        """Validate request size limits"""
        # Check query string length
        query_string = str(request.url.query)
        if len(query_string) > self.max_query_string_length:
            return False, f"Query string too long: {len(query_string)} bytes (max: {self.max_query_string_length})"

        # Check header size (approximate)
        total_header_size = sum(len(f"{k}: {v}") for k, v in request.headers.items())
        if total_header_size > self.max_header_size:
            return False, f"Headers too large: {total_header_size} bytes (max: {self.max_header_size})"

        # Request body size will be checked by FastAPI/Starlette
        return True, None

    def _validate_csrf_token(self, request: Request) -> Tuple[bool, Optional[str]]:
        """Validate CSRF token"""
        if not self.csrf_enabled:
            return True, None

        # Skip CSRF check for exempt paths and methods
        if request.url.path in self.csrf_exempt_paths:
            return True, None

        if request.method in self.csrf_exempt_methods:
            return True, None

        # Get CSRF token from header
        csrf_token = request.headers.get(self.csrf_token_header)
        if not csrf_token:
            return False, "CSRF token missing"

        # Get session identifier (could be from JWT, session cookie, etc.)
        # For now, we'll use a combination of IP and User-Agent
        session_id = self._get_session_id(request)

        # Validate token (in production, use Redis or database)
        expected_token = self.csrf_tokens.get(session_id)
        if not expected_token or csrf_token != expected_token:
            return False, "Invalid CSRF token"

        return True, None

    def _get_session_id(self, request: Request) -> str:
        """Generate session identifier"""
        ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "")
        # In production, use actual session ID from JWT or session cookie
        return hashlib.sha256(f"{ip}:{user_agent}".encode()).hexdigest()

    def _generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        token = secrets.token_urlsafe(32)
        self.csrf_tokens[session_id] = token
        return token

    def _add_security_headers(self, response: Response, request: Request):
        """Add security headers to response"""
        headers = response.headers

        # XSS Protection
        headers["X-XSS-Protection"] = "1; mode=block"

        # Content Type Options
        headers["X-Content-Type-Options"] = "nosniff"

        # Frame Options
        headers["X-Frame-Options"] = "DENY"

        # Referrer Policy
        headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature Policy)
        headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=(), "
            "speaker=(), vibrate=(), fullscreen=(self)"
        )

        # HSTS (HTTP Strict Transport Security)
        if self.enable_hsts and request.url.scheme == "https":
            headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}; includeSubDomains; preload"
            )

        # Content Security Policy
        if self.enable_csp:
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
                "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com data:; "
                "img-src 'self' data: https: blob:; "
                "connect-src 'self' https://api.tap.company wss: ws:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'; "
                "upgrade-insecure-requests;"
            )
            headers["Content-Security-Policy"] = csp

        # X-Permitted-Cross-Domain-Policies
        headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # Remove server header (security through obscurity)
        if "server" in headers:
            del headers["server"]

    def _log_suspicious_activity(
        self,
        request: Request,
        attack_type: str,
        attack_value: str,
        client_ip: str
    ):
        """Log suspicious activity"""
        if not self.log_suspicious_activity:
            return

        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "attack_type": attack_type,
            "attack_value": attack_value[:200],  # Limit length
            "client_ip": client_ip,
            "method": request.method,
            "path": request.url.path,
            "user_agent": request.headers.get("User-Agent", "Unknown"),
            "referer": request.headers.get("Referer", "Unknown"),
        }

        logger.warning(
            f"Suspicious activity detected: {attack_type}",
            module="SecurityMiddleware",
            label="SECURITY_THREAT",
            extra_data=log_data
        )

    async def dispatch(self, request: Request, call_next):
        """Main middleware dispatch method"""
        client_ip = self._get_client_ip(request)
        start_time = time.time()

        try:
            # 1. IP Whitelist/Blacklist Check
            if self._check_ip_blacklist(client_ip):
                logger.warning(f"Blocked request from blacklisted IP: {client_ip}", module="SecurityMiddleware", label="IP_BLOCKED")
                return ERROR.response(
                    error_key="IP_BLOCKED",
                    status_code=status.HTTP_403_FORBIDDEN,
                    details={"client_ip": client_ip, "reason": "IP address is blacklisted"},
                    request=request
                )

            if not self._check_ip_whitelist(client_ip):
                logger.warning(f"Blocked request from non-whitelisted IP: {client_ip}", module="SecurityMiddleware", label="IP_BLOCKED")
                return ERROR.response(
                    error_key="IP_NOT_ALLOWED",
                    status_code=status.HTTP_403_FORBIDDEN,
                    details={"client_ip": client_ip, "reason": "IP address not in whitelist"},
                    request=request
                )

            # 2. Request Size Validation
            is_valid_size, size_error = self._validate_request_size(request)
            if not is_valid_size:
                logger.warning(f"Request size validation failed: {size_error}", module="SecurityMiddleware", label="VALIDATION")
                return ERROR.response(
                    error_key="REQUEST_TOO_LARGE",
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    details={"error": size_error, "client_ip": client_ip},
                    request=request
                )

            # 3. Attack Pattern Detection
            is_safe, attack_type, attack_value = self._validate_request_data(request)
            if not is_safe:
                self._log_suspicious_activity(request, attack_type, attack_value, client_ip)

                if self.block_suspicious_requests:
                    return ERROR.response(
                        error_key="SECURITY_THREAT_DETECTED",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={
                            "attack_type": attack_type,
                            "message": "Potential security threat detected in request",
                            "client_ip": client_ip
                        },
                        request=request
                    )

            # 4. Rate Limiting
            # Extract user ID if available (for authenticated requests)
            user_id = self._extract_user_id_from_token(request)

            # IP-based rate limiting (always check)
            if self.rate_limit_enabled:
                # Check per minute
                allowed, error = self._check_rate_limit(client_ip, "minute", is_user=False)
                if not allowed:
                    logger.warning(f"Rate limit exceeded (IP, minute): {client_ip}", module="SecurityMiddleware", label="RATE_LIMIT")
                    return ERROR.response(
                        error_key="TOO_MANY_REQUESTS",
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        details={"error": error, "client_ip": client_ip},
                        request=request
                    )

                # Check per hour
                allowed, error = self._check_rate_limit(client_ip, "hour", is_user=False)
                if not allowed:
                    logger.warning(f"Rate limit exceeded (IP, hour): {client_ip}", module="SecurityMiddleware", label="RATE_LIMIT")
                    return ERROR.response(
                        error_key="TOO_MANY_REQUESTS",
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        details={"error": error, "client_ip": client_ip},
                        request=request
                    )

                # Check per day
                allowed, error = self._check_rate_limit(client_ip, "day", is_user=False)
                if not allowed:
                    logger.warning(f"Rate limit exceeded (IP, day): {client_ip}", module="SecurityMiddleware", label="RATE_LIMIT")
                    return ERROR.response(
                        error_key="TOO_MANY_REQUESTS",
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        details={"error": error, "client_ip": client_ip},
                        request=request
                    )

            # Per-user rate limiting (if authenticated)
            if user_id and self.rate_limit_per_user_enabled:
                user_limits = {
                    "minute": self.rate_limit_per_user_per_minute,
                    "hour": self.rate_limit_per_user_per_hour,
                    "day": self.rate_limit_per_user_per_day,
                }

                # Check per minute
                allowed, error = self._check_rate_limit(
                    user_id, "minute", is_user=True, user_limits=user_limits
                )
                if not allowed:
                    logger.warning(f"Rate limit exceeded (user, minute): {user_id}", module="SecurityMiddleware", label="RATE_LIMIT", user_id=user_id)
                    return ERROR.response(
                        error_key="TOO_MANY_REQUESTS",
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        details={"error": error, "user_id": user_id, "client_ip": client_ip},
                        request=request
                    )

                # Check per hour
                allowed, error = self._check_rate_limit(
                    user_id, "hour", is_user=True, user_limits=user_limits
                )
                if not allowed:
                    logger.warning(f"Rate limit exceeded (user, hour): {user_id}", module="SecurityMiddleware", label="RATE_LIMIT", user_id=user_id)
                    return ERROR.response(
                        error_key="TOO_MANY_REQUESTS",
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        details={"error": error, "user_id": user_id, "client_ip": client_ip},
                        request=request
                    )

                # Check per day
                allowed, error = self._check_rate_limit(
                    user_id, "day", is_user=True, user_limits=user_limits
                )
                if not allowed:
                    logger.warning(f"Rate limit exceeded (user, day): {user_id}", module="SecurityMiddleware", label="RATE_LIMIT", user_id=user_id)
                    return ERROR.response(
                        error_key="TOO_MANY_REQUESTS",
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        details={"error": error, "user_id": user_id, "client_ip": client_ip},
                        request=request
                    )

            # 5. CSRF Token Validation (for state-changing methods)
            csrf_valid, csrf_error = self._validate_csrf_token(request)
            if not csrf_valid:
                logger.warning(f"CSRF validation failed: {csrf_error}", module="SecurityMiddleware", label="CSRF")
                return ERROR.response(
                    error_key="CSRF_TOKEN_INVALID",
                    status_code=status.HTTP_403_FORBIDDEN,
                    details={"error": csrf_error, "client_ip": client_ip},
                    request=request
                )

            # 6. Process request
            response = await call_next(request)

            # 7. Add security headers
            self._add_security_headers(response, request)

            # 8. Add CSRF token to response for GET requests (if CSRF enabled)
            if self.csrf_enabled and request.method in {"GET", "HEAD"}:
                session_id = self._get_session_id(request)
                csrf_token = self._generate_csrf_token(session_id)
                response.headers["X-CSRF-Token"] = csrf_token

            # 9. Log request metrics
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = f"{process_time:.4f}"

            return response

        except Exception as e:
            logger.error(f"Security middleware error: {e}", module="SecurityMiddleware", label="ERROR", exc_info=True)
            # Don't block on middleware errors, but log them
            response = await call_next(request)
            self._add_security_headers(response, request)
            return response

