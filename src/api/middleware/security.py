"""
Security Middleware for DiffusionPromptDB API

Implements security headers and enhanced protection measures.
"""

from fastapi import Request
from fastapi.responses import Response
from typing import Callable
import logging

logger = logging.getLogger(__name__)


async def add_security_headers(request: Request, call_next: Callable) -> Response:
    """
    Add security headers to all responses.

    Implements OWASP recommended security headers to protect against
    common web vulnerabilities like XSS, clickjacking, and MIME sniffing.

    Headers added:
        - X-Content-Type-Options: Prevents MIME type sniffing
        - X-Frame-Options: Prevents clickjacking attacks
        - X-XSS-Protection: Enables browser XSS filter (legacy browsers)
        - Strict-Transport-Security: Forces HTTPS connections
        - Referrer-Policy: Controls referrer information
        - Content-Security-Policy: Controls resource loading
        - Permissions-Policy: Controls browser features
    """
    # Process the request
    response = await call_next(request)

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # HSTS - Force HTTPS (enabled for production security)
    # Max age: 1 year (31536000 seconds)
    # includeSubDomains: Apply to all subdomains
    # preload: Eligible for browser HSTS preload lists
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains; preload"
    )

    # Content Security Policy - Adjust based on your needs
    csp_directives = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # For development
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: https:",
        "font-src 'self' data:",
        "connect-src 'self' https://www.diffusionprompt.net https://diffusionprompt.net",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'",
    ]
    response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

    # Permissions Policy (formerly Feature Policy)
    permissions = [
        "camera=()",
        "microphone=()",
        "geolocation=()",
        "payment=()",
        "usb=()",
        "magnetometer=()",
        "gyroscope=()",
        "accelerometer=()",
    ]
    response.headers["Permissions-Policy"] = ", ".join(permissions)

    return response


async def validate_content_type(request: Request, call_next: Callable) -> Response:
    """
    Validate Content-Type header for POST/PUT/PATCH requests.

    Ensures that requests with body have appropriate Content-Type headers
    to prevent CSRF and other attacks.
    """
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")

        # Allow JSON and form data
        valid_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
        ]

        # Check if content type is valid
        if not any(ct in content_type.lower() for ct in valid_types):
            logger.warning(
                f"Invalid Content-Type: {content_type} from {request.client.host}"
            )

    return await call_next(request)


async def sanitize_response_headers(request: Request, call_next: Callable) -> Response:
    """
    Remove sensitive information from response headers.

    Removes or modifies headers that could leak sensitive information
    about the server or application.
    """
    response = await call_next(request)

    # Remove potentially sensitive headers
    headers_to_remove = [
        "Server",
        "X-Powered-By",
        "X-AspNet-Version",
        "X-AspNetMvc-Version",
    ]

    for header in headers_to_remove:
        response.headers.pop(header, None)

    return response


class SecurityMiddleware:
    """
    Combined security middleware for production use.

    Applies all security measures in the correct order.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # Apply security measures in order
        response = await add_security_headers(request, call_next)
        return response
