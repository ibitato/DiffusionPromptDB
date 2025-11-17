"""
DiffusionPromptDB REST API

Secure REST API for managing Stable Diffusion prompts and catalogation.
"""

from types import SimpleNamespace
import os

# Normalize bcrypt compatibility before any other modules import it.
os.environ.setdefault("BCRYPT_LONG_PASSWORDS", "1")
import bcrypt  # type: ignore  # noqa: E402

if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = SimpleNamespace(__version__=getattr(bcrypt, "__version__", ""))  # type: ignore[attr-defined]

_ORIGINAL_HASH_PW = bcrypt.hashpw


def _hashpw_with_truncation(secret: bytes, salt: bytes) -> bytes:
    """
    Mirror the pre-4.x behavior by truncating secrets longer than 72 bytes.

    Passlib relies on this legacy behavior for its self-checks, and enforcing it
    keeps backward compatibility for existing hashes.
    """

    try:
        return _ORIGINAL_HASH_PW(secret, salt)
    except ValueError as exc:
        message = str(exc)
        if "password cannot be longer than 72 bytes" not in message:
            raise
        return _ORIGINAL_HASH_PW(secret[:72], salt)


bcrypt.hashpw = _hashpw_with_truncation

__version__ = "1.0.0"
__author__ = "DiffusionPromptDB Team"

from .main import app

__all__ = ["app"]
