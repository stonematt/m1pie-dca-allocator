"""
cookie_manager.py: Provide cookie read/write utilities using real browser cookies.

Wraps extra-streamlit-components CookieManager for persistent, client-side storage.
"""

from datetime import datetime, timedelta, timezone

import extra_streamlit_components as stx

from scripts.log_util import app_logger

logger = app_logger(__name__)


def get_cookie_manager():
    """Return a CookieManager instance with a consistent key."""
    return stx.CookieManager(key="cookie_manager_main")


def get_cookie(key: str) -> str | None:
    """Retrieve a value from browser cookies."""
    manager = get_cookie_manager()
    cookies = manager.get_all()
    value = cookies.get(key)
    logger.debug(f"Read cookie [{key}]: {value}")
    return value


def set_cookie(key: str, value: str) -> None:
    """Set a value in browser cookies with a 30-day expiration."""
    manager = get_cookie_manager()
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    manager.set(cookie=key, val=value, expires_at=expires_at)
    logger.debug(f"Set cookie [{key}] = {value}")
