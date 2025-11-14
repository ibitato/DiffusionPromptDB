"""
Enhanced Rate Limiting for DiffusionPromptDB API

Implements tiered rate limiting based on endpoint sensitivity.
All limits are configurable via environment variables.
"""

import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Dict

# Create rate limiter instance
limiter = Limiter(key_func=get_remote_address)

# Rate limit configurations from environment variables
# All values have sensible defaults if not configured
RATE_LIMITS: Dict[str, str] = {
    # Authentication endpoints - strict limits to prevent brute force
    "auth_login": os.getenv("RATE_LIMIT_AUTH_LOGIN", "5/minute"),
    "auth_register": os.getenv("RATE_LIMIT_AUTH_REGISTER", "3/minute"),
    "auth_reset": os.getenv("RATE_LIMIT_AUTH_RESET", "3/hour"),
    
    # Public read endpoints - moderate limits
    "public_read": os.getenv("RATE_LIMIT_PUBLIC_READ", "100/minute"),
    "search": os.getenv("RATE_LIMIT_SEARCH", "30/minute"),
    "catalog": os.getenv("RATE_LIMIT_CATALOG", "60/minute"),
    
    # Authenticated write endpoints - balanced limits
    "prompt_create": os.getenv("RATE_LIMIT_PROMPT_CREATE", "10/minute"),
    "prompt_update": os.getenv("RATE_LIMIT_PROMPT_UPDATE", "20/minute"),
    "prompt_delete": os.getenv("RATE_LIMIT_PROMPT_DELETE", "10/minute"),
    
    # Admin endpoints - relaxed limits for admins
    "admin_operations": os.getenv("RATE_LIMIT_ADMIN", "100/minute"),
    
    # Health and monitoring - minimal limits
    "health": os.getenv("RATE_LIMIT_HEALTH", "10/minute"),
    
    # Default fallback
    "default": os.getenv("RATE_LIMIT_DEFAULT", "60/minute")
}

def get_rate_limit(endpoint_type: str) -> str:
    """
    Get rate limit configuration for a specific endpoint type.
    
    Args:
        endpoint_type: Type of endpoint (e.g., 'auth_login', 'public_read')
        
    Returns:
        Rate limit string (e.g., '5/minute')
    """
    return RATE_LIMITS.get(endpoint_type, RATE_LIMITS["default"])

# Pre-configured decorators for common use cases
auth_limit = limiter.limit(get_rate_limit("auth_login"))
public_limit = limiter.limit(get_rate_limit("public_read"))
search_limit = limiter.limit(get_rate_limit("search"))
write_limit = limiter.limit(get_rate_limit("prompt_create"))
admin_limit = limiter.limit(get_rate_limit("admin_operations"))

# Custom rate limit for specific IPs or users (can be extended)
def get_custom_rate_limit(request):
    """
    Get custom rate limit based on user role or IP.
    
    Can be extended to provide different limits for:
    - Premium users
    - Trusted IPs
    - API keys with higher quotas
    """
    # Example: Check for premium user token
    # if hasattr(request.state, "user") and request.state.user.get("premium"):
    #     return "200/minute"
    
    # Default to standard limit
    return get_rate_limit("default")

# Rate limit message customization
RATE_LIMIT_MESSAGES = {
    "auth_login": "Too many login attempts. Please try again later.",
    "auth_register": "Registration rate limit exceeded. Please wait before trying again.",
    "search": "Search rate limit exceeded. Please wait before making more searches.",
    "default": "Rate limit exceeded. Please slow down your requests."
}

def get_rate_limit_message(endpoint_type: str) -> str:
    """
    Get custom rate limit exceeded message for endpoint type.
    
    Args:
        endpoint_type: Type of endpoint
        
    Returns:
        Custom error message
    """
    return RATE_LIMIT_MESSAGES.get(endpoint_type, RATE_LIMIT_MESSAGES["default"])
