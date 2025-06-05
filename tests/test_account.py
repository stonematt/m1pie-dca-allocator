# import pytest
from scripts.account import (
    create_empty_account,
    list_portfolios,
    get_portfolio,
    add_or_replace_portfolio,
    delete_portfolio,
)


def test_create_empty_account():
    account = create_empty_account()
    assert account["type"] == "account"
    assert account["portfolios"] == {}


def test_add_and_list_portfolios():
    account = create_empty_account()
    add_or_replace_portfolio(account, "Growth", {"name": "Growth", "value": 1000})
    add_or_replace_portfolio(account, "Income", {"name": "Income", "value": 500})
    names = list_portfolios(account)
    assert set(names) == {"Growth", "Income"}


def test_get_portfolio():
    account = create_empty_account()
    portfolio = {"name": "Tech", "value": 1200}
    add_or_replace_portfolio(account, "Tech", portfolio)
    result = get_portfolio(account, "Tech")
    assert result == portfolio


def test_delete_portfolio():
    account = create_empty_account()
    add_or_replace_portfolio(account, "Old", {"name": "Old", "value": 300})
    delete_portfolio(account, "Old")
    assert "Old" not in account["portfolios"]
