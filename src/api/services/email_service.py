"""
Simple SMTP email helper.
"""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from ..config import settings

logger = logging.getLogger(__name__)


def is_configured() -> bool:
    return bool(
        settings.smtp_host
        and settings.smtp_username
        and settings.smtp_password
        and settings.smtp_sender
    )


def send_email(subject: str, recipient: str, body: str) -> bool:
    if not is_configured():
        logger.warning("SMTP not configured; skipping email to %s", recipient)
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_sender
    msg["To"] = recipient
    msg.set_content(body)

    try:
        if settings.smtp_use_tls:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
                server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", recipient, exc)
        return False


def send_verification_email(email: str, token: str) -> bool:
    base = settings.public_app_url.rstrip("/")
    verification_url = f"{base}/verify?token={token}"
    body = (
        f"Hola,\n\n"
        f"Para activar tu cuenta, visita:\n{verification_url}\n\n"
        f"Si no solicitaste este registro, ignora este mensaje."
    )
    return send_email("Verifica tu cuenta en DiffusionPromptDB", email, body)
