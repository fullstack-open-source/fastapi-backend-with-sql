from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.response.error import ERROR
import time
import os

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Professional security middleware for FastAPI
    Features:
    - API Key / Token validation
    - IP whitelist/blacklist
    - Rate limiting
    - Logging suspicious requests
    """

    def __init__(self, app, api_key_header: str = "X-API-KEY", allowed_ips: list = None, rate_limit: int = 100):
        super().__init__(app)
        self.api_key_header = api_key_header
        self.allowed_ips = allowed_ips or []  # whitelist IPs
        self.rate_limit = rate_limit  # requests per IP per time window
        self.ip_request_log = {}  # simple in-memory request tracking

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"

        # 1️⃣ IP Whitelist / Blacklist
        if self.allowed_ips and client_ip not in self.allowed_ips:
            return ERROR.response(
                "FORBIDDEN",
                status_code=403,
                details={"client_ip": client_ip, "reason": "IP not allowed"},
                request=request
            )

        # 2️⃣ API Key / Token Validation
        api_key = request.headers.get(self.api_key_header)
        expected_api_key = os.getenv("APP_API_KEY")
        if expected_api_key and api_key != expected_api_key:
            return ERROR.response(
                "UNAUTHORIZED",
                status_code=401,
                details={"client_ip": client_ip, "reason": "Invalid API key"},
                request=request
            )

        # 3️⃣ Rate limiting
        now = time.time()
        window = 60  # 60 seconds window
        if client_ip not in self.ip_request_log:
            self.ip_request_log[client_ip] = []
        self.ip_request_log[client_ip] = [t for t in self.ip_request_log[client_ip] if now - t < window]
        if len(self.ip_request_log[client_ip]) >= self.rate_limit:
            return ERROR.response(
                "TOO_MANY_REQUESTS",
                status_code=429,
                details={"client_ip": client_ip, "reason": "Rate limit exceeded"},
                request=request
            )
        self.ip_request_log[client_ip].append(now)

        # 4️⃣ Call next middleware / route
        response = await call_next(request)

        # 5️⃣ Optional security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response
