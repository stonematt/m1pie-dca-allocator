"""
cookie_portfolio.py: Manage lightweight portfolio persistence via browser cookies.

Uses Streamlit's experimental cookie API to serialize portfolio data as compact JSON
and store it in the user's browser. Enables basic cross-session continuity for users
without requiring authentication or server-side storage.

Includes functions to load, save, and clear portfolios from a reserved cookie key.
Logs key operations for transparency and debugging.
"""

import json

import streamlit as st

from scripts.log_util import app_logger

logger = app_logger(__name__)


COOKIE_KEY = "m1pie_portfolio"


def save_portfolio_to_cookie(portfolio: dict) -> None:
    """Serialize and store the given portfolio into the browser cookie."""
    try:
        json_data = json.dumps(portfolio, separators=(",", ":"))
        st.experimental_set_query_params(**{COOKIE_KEY: json_data})
        logger.info("Portfolio saved to cookie.")
    except Exception as e:
        logger.error(f"Failed to save portfolio to cookie: {e}")


def load_portfolio_from_cookie() -> dict | None:
    """Attempt to load and deserialize the portfolio from cookie."""
    try:
        params = st.experimental_get_query_params()
        raw = params.get(COOKIE_KEY)
        if raw:
            portfolio = json.loads(raw[0])
            logger.info("Portfolio loaded from cookie.")
            return portfolio
    except Exception as e:
        logger.error(f"Failed to load portfolio from cookie: {e}")
    return None


def clear_portfolio_cookie() -> None:
    """Clear the portfolio cookie."""
    try:
        st.experimental_set_query_params()
        logger.info("Portfolio cookie cleared.")
    except Exception as e:
        logger.error(f"Failed to clear portfolio cookie: {e}")
