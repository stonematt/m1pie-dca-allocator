"""
cookie_account.py: Manage lightweight account persistence via browser cookies.

Serializes the entire account object into a compact JSON string and stores it
in a browser cookie using Streamlit's experimental query param API. Enables
basic persistence without requiring server-side storage or authentication.
"""

import json
import streamlit as st

from scripts.account import create_empty_account
from scripts.log_util import app_logger

logger = app_logger(__name__)

COOKIE_KEY = "m1_account"


def save_account_to_cookie(account: dict) -> None:
    """Serialize and store the full account structure in the cookie."""
    try:
        json_data = json.dumps(account, separators=(",", ":"))
        st.experimental_set_query_params(**{COOKIE_KEY: json_data})
        logger.info("Account saved to cookie.")
    except Exception as e:
        logger.error(f"Failed to save account to cookie: {e}")


def load_account_from_cookie() -> dict:
    """Attempt to load and deserialize the account structure from cookie."""
    try:
        params = st.experimental_get_query_params()
        raw = params.get(COOKIE_KEY)
        if raw:
            account = json.loads(raw[0])
            logger.info("Account loaded from cookie.")
            return account
    except Exception as e:
        logger.error(f"Failed to load account from cookie: {e}")
    return create_empty_account()


def clear_account_cookie() -> None:
    """Clear the account cookie by removing the query param."""
    try:
        st.experimental_set_query_params(**{COOKIE_KEY: None})
        logger.info("Account cookie cleared.")
    except Exception as e:
        logger.error(f"Failed to clear account cookie: {e}")
