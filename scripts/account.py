"""
account.py: Portfolio Management for User Accounts

This module manages user accounts comprised of multiple named investment portfolios.
It provides essential CRUD operations to facilitate the creation, retrieval, updating,
and deletion of portfolios within an account. The module is designed to support both
cookie-based and JSON file storage solutions, ensuring flexibility in how account
data is persisted. Logging is integrated to track and debug portfolio operations
efficiently.

Functions:
- create_empty_account: Initializes a new account with no portfolios.
- list_portfolios: Lists all portfolio names within an account.
- add_or_replace_portfolio: Adds a new portfolio or updates an existing one.
- get_portfolio: Retrieves details of a specified portfolio.
- delete_portfolio: Removes a portfolio from the account.

Usage of this module assumes integration with a logging utility and a storage layer
for account persistence.
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
