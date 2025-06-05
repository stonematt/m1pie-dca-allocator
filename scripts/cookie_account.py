"""
cookie_account.py: Cookie-based persistence for account data.

Handles compression and privacy-respecting storage via real browser cookies.
"""

import base64
import json
import zlib
from decimal import Decimal

from scripts.account import create_empty_account
from scripts.cookie_manager import get_cookie, set_cookie
from scripts.log_util import app_logger

logger = app_logger(__name__)

COOKIE_KEY = "m1pie_account"
COOKIE_LIMIT_BYTES = 4096


def save_account_to_cookie(account: dict) -> None:
    """
    Compress and store account data in a browser cookie.

    :param account: Account dictionary to persist.
    """
    try:
        raw_json = json.dumps(account, separators=(",", ":"), default=_json_fallback)
        compressed = zlib.compress(raw_json.encode())
        encoded = base64.b64encode(compressed).decode()

        if len(encoded) > COOKIE_LIMIT_BYTES:
            logger.warning("Cookie size exceeds 4KB, not saving.")
            return

        set_cookie(COOKIE_KEY, encoded)
        logger.info("Account saved to cookie.")

    except Exception as e:
        logger.error(f"Failed to save account to cookie: {e}")


def load_account_from_cookie() -> dict:
    """
    Load and decompress account data from a browser cookie.

    :return: Account dictionary or a new empty account if missing/invalid.
    """
    try:
        encoded = get_cookie(COOKIE_KEY)
        if not encoded:
            return create_empty_account()

        compressed = base64.b64decode(encoded)
        raw_json = zlib.decompress(compressed).decode()
        data = json.loads(raw_json)

        logger.info("Account loaded from cookie.")
        return data

    except Exception as e:
        logger.warning(f"Failed to load account from cookie: {e}")
        return create_empty_account()


def _json_fallback(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
