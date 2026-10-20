"""
Production-grade security middleware for MedAI backend.
Adds security headers, request tracing, and input sanitization.
"""

import time
import uuid
import logging
import re
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# ── Security Headers ──────────────────────────────────────────────────────────
SECURITY_HEADERS = {
    # Prevent clickjacking
    "X-Frame-Options": "DENY",
    # Prevent MIME-type sniffing
    "X-Content-Type-Options": "nosniff",
    # Enforce HTTPS for 1 year (only effective when behind HTTPS)
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    # Referrer policy
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # Permissions policy — disable unnecessary browser features
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    # Content-Security-Policy — strict; images from self and data URIs only
    "Content-Security-Policy": (
        "default-src 'none'; "
        "script-src 'none'; "
        "style-src 'none'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    ),
    # Remove server info leak
    "Server": "MedAI-API",
    # XSS Protection for older browsers
    "X-XSS-Protection": "1; mode=block",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Injects security headers on every response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        return response


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """
    Assigns a unique X-Request-ID to every request for distributed tracing.
    Logs method, path, status code, and processing time.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        # Attach request ID to request state for use in route handlers
        request.state.request_id = request_id

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"→ {response.status_code} ({duration_ms:.1f}ms)"
        )
        return response


# ── Input Sanitization ────────────────────────────────────────────────────────

# Characters that are safe in medical symptom text
_SAFE_SYMPTOM_PATTERN = re.compile(r"[<>{}\[\]\\|`~^]")


def sanitize_text_input(text: str) -> str:
    """
    Strip control characters and potential XSS/injection payloads from free text.
    Keeps all normal medical terminology intact.
    """
    # Remove null bytes and control chars (except newline, tab)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Strip obvious script/html injection attempts
    text = re.sub(r"<[^>]*>", "", text)
    # Remove shell-injection candidates
    text = _SAFE_SYMPTOM_PATTERN.sub("", text)
    return text.strip()
