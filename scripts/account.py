"""
account.py: Manage an account composed of multiple portfolios.

Provides CRUD operations to manage named portfolios inside a top-level account structure.
Intended to support cookie and JSON storage layers.
"""

from scripts.log_util import app_logger

logger = app_logger(__name__)


ACCOUNT_TEMPLATE = {"type": "account", "portfolios": {}}


def create_empty_account() -> dict:
    """Return a new empty account structure."""
    return ACCOUNT_TEMPLATE.copy()


def list_portfolios(account: dict) -> list[str]:
    """Return a list of portfolio names in the account."""
    return list(account.get("portfolios", {}).keys())


def add_or_replace_portfolio(account: dict, name: str, portfolio: dict) -> dict:
    """Insert or replace a portfolio in the account."""
    account.setdefault("portfolios", {})[name] = portfolio
    return account


def get_portfolio(account: dict, name: str) -> dict:
    """Retrieve a portfolio by name."""
    return account.get("portfolios", {}).get(name)


def delete_portfolio(account: dict, name: str) -> dict:
    """Delete a portfolio by name."""
    portfolios = account.get("portfolios", {})
    if name not in portfolios:
        logger.warning(f"Attempted to delete non-existent portfolio: {name}")
        return account

    del portfolios[name]
    logger.info(f"Portfolio '{name}' deleted.")
    return account
