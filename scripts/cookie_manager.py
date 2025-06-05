"""
cookie_manager.py: Provide cookie read/write utilities using real browser cookies.

Wraps extra-streamlit-components CookieManager for persistent, client-side storage.
"""

import extra_streamlit_components as stx
from scripts.log_util import app_logger

logger = app_logger(__name__)


def get_cookie_manager():
    """Return a CookieManager instance (do not cache)."""
    return stx.CookieManager()


def get_cookie(key: str) -> str | None:
    """Retrieve a value from browser cookies."""
    manager = get_cookie_manager()
    cookies = manager.get_all()
    value = cookies.get(key)
    logger.debug(f"Read cookie [{key}]: {value}")
    return value


def set_cookie(key: str, value: str) -> None:
    """Set a value in browser cookies."""
    manager = get_cookie_manager()
    manager.set(key, value)
    logger.debug(f"Set cookie [{key}] = {value}")
