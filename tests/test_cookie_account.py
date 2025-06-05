"""
test_cookie_account.py: Unit tests for cookie_account.py browser persistence logic.

Mocks Streamlit's query_params API to validate saving, loading, and clearing
account data from browser storage.
"""

import pytest
import streamlit as st
from types import SimpleNamespace

from scripts.account import add_or_replace_portfolio, create_empty_account
from scripts.cookie_account import (
    clear_account_cookie,
    load_account_from_cookie,
    save_account_to_cookie,
)

COOKIE_KEY = "m1pie_account"


@pytest.fixture(autouse=True)
def mock_query_params(monkeypatch):
    """Patch Streamlit's query_params property using a backing store."""
    store = {}

    class QueryParamsMock:
        @property
        def query_params(self):
            return store

        @query_params.setter
        def query_params(self, value):
            store.clear()
            store.update(value)

    monkeypatch.setattr(st, "query_params", QueryParamsMock().query_params)
    return store


def test_save_and_load_account(mock_query_params):
    account = create_empty_account()
    add_or_replace_portfolio(account, "demo", {"name": "demo", "value": 100})
    save_account_to_cookie(account)

    assert COOKIE_KEY in mock_query_params
    loaded = load_account_from_cookie()
    assert loaded is not None
    assert loaded["portfolios"]["demo"]["value"] == 100


def test_clear_cookie(mock_query_params):
    account = create_empty_account()
    add_or_replace_portfolio(account, "demo", {"name": "demo", "value": 100})
    save_account_to_cookie(account)

    assert COOKIE_KEY in mock_query_params
    clear_account_cookie()
    assert COOKIE_KEY not in mock_query_params
    assert load_account_from_cookie() is None
