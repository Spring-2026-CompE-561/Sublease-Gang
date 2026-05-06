import logging
from html import escape

import resend
from resend.exceptions import ResendError

from app.core.settings import settings

logger = logging.getLogger(__name__)


def _is_configured() -> bool:
    return bool(settings.resend_api_key)


def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    """Send a password-reset email via Resend.

    Returns True on a successful send, False otherwise. Failures are logged
    but never raised — the caller (forgot_password) must always return 200
    to avoid leaking whether an email is registered.
    """
    if not _is_configured():
        logger.warning(
            "RESEND_API_KEY is not set; skipping password reset email to %s",
            to_email,
        )
        return False

    resend.api_key = settings.resend_api_key
    safe_url = escape(reset_url, quote=True)
    params: resend.Emails.SendParams = {
        "from": settings.resend_from_email,
        "to": [to_email],
        "subject": "Reset your SubLease password",
        "html": (
            "<p>We received a request to reset your password.</p>"
            f'<p><a href="{safe_url}">Reset your password</a></p>'
            "<p>This link expires in "
            f"{settings.reset_token_expire_minutes} minutes. If you did not "
            "request a reset, you can safely ignore this email.</p>"
        ),
        "text": (
            "We received a request to reset your password.\n\n"
            f"Reset your password: {reset_url}\n\n"
            f"This link expires in {settings.reset_token_expire_minutes} "
            "minutes. If you did not request a reset, you can safely ignore "
            "this email."
        ),
    }
    try:
        resend.Emails.send(params)
    except ResendError:
        logger.exception("Failed to send password reset email to %s", to_email)
        return False
    return True
