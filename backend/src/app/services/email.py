import logging
import threading
from html import escape

import resend
from resend.exceptions import ResendError  # noqa: F401  re-exported for tests

from app.core.settings import settings

logger = logging.getLogger(__name__)

# The Resend SDK reads `resend.api_key` as module-level state inside its
# request layer, so we set it once under a lock instead of mutating it on
# every send. Without this, two concurrent FastAPI workers could interleave
# their assignments and a request could see another's key — a classic
# global-state footgun.
_api_key_lock = threading.Lock()
_api_key_set = False


def _is_configured() -> bool:
    return bool(settings.resend_api_key)


def _ensure_api_key_configured() -> None:
    global _api_key_set
    if _api_key_set and resend.api_key == settings.resend_api_key:
        return
    with _api_key_lock:
        if _api_key_set and resend.api_key == settings.resend_api_key:
            return
        resend.api_key = settings.resend_api_key
        _api_key_set = True


def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    """Send a password-reset email via Resend.

    Returns True on a successful send, False otherwise. Any exception from
    the SDK (ResendError, network/transport errors, etc.) is caught, logged,
    and turned into False — the caller (forgot_password) must always return
    200 to avoid leaking whether an email is registered.
    """
    if not _is_configured():
        logger.warning(
            "RESEND_API_KEY is not set; skipping password reset email to %s",
            to_email,
        )
        return False

    _ensure_api_key_configured()
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
    except Exception:
        logger.exception("Failed to send password reset email to %s", to_email)
        return False
    return True
