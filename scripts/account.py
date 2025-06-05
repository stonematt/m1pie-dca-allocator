"""
account.py: Manage an account composed of multiple portfolios.

Provides CRUD operations to manage named portfolios inside a top-level account structure.
Intended to support cookie and JSON storage layers.
"""

ACCOUNT_TEMPLATE = {"type": "account", "portfolios": {}}


def create_empty_account() -> dict:
    """Return a new empty account structure."""
    return ACCOUNT_TEMPLATE.copy()


def list_portfolios(account: dict) -> list[str]:
    """Return a list of portfolio names in the account."""
    return list(account.get("portfolios", {}).keys())


def get_portfolio(account: dict, name: str) -> dict:
    """Retrieve a portfolio by name."""
    return account.get("portfolios", {}).get(name)


def add_or_replace_portfolio(account: dict, name: str, portfolio: dict) -> dict:
    """Insert or replace a portfolio in the account."""
    account.setdefault("portfolios", {})[name] = portfolio
    return account


def delete_portfolio(account: dict, name: str) -> dict:
    """Delete a portfolio by name."""
    if name in account.get("portfolios", {}):
        del account["portfolios"][name]
    return account
