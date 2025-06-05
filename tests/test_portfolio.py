from decimal import ROUND_HALF_UP, Decimal

import pytest
import streamlit as st

from scripts.portfolio import (
    normalize_portfolio,
    update_children,
)


@pytest.fixture(autouse=True)
def init_streamlit_session(monkeypatch):
    monkeypatch.setitem(st.session_state, "account", {"portfolios": {}})
    monkeypatch.setitem(
        st.session_state,
        "portfolio",
        {"name": "test", "type": "pie", "value": 0, "children": {}},
    )


@pytest.fixture
def base_portfolio():
    """Fixture providing a base test portfolio with known children and values."""
    return {
        "name": "test",
        "type": "pie",
        "value": 0,
        "children": {
            "A": {"type": "ticker", "value": 20},
            "B": {"type": "ticker", "value": 40},
            "C": {"type": "ticker", "value": 80},
        },
    }


def test_normalize_portfolio_weights(base_portfolio):
    """Ensure weights are correctly calculated from values in a flat pie."""
    result = normalize_portfolio(base_portfolio)
    assert result["value"] == Decimal("140")
    assert result["children"]["A"]["value"] == Decimal("20")
    assert result["children"]["B"]["value"] == Decimal("40")
    assert result["children"]["C"]["value"] == Decimal("80")
    assert result["children"]["A"]["weight"].quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    ) == Decimal("0.14")
    assert result["children"]["B"]["weight"].quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    ) == Decimal("0.29")
    assert result["children"]["C"]["weight"].quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    ) == Decimal("0.57")


def test_update_children_merges_correctly():
    """Check that update_children merges new keys into portfolio children."""
    base = {
        "name": "x",
        "type": "pie",
        "value": 0,
        "children": {"A": {"type": "ticker", "value": 50}},
    }
    patch = {"B": {"type": "ticker", "value": 100}}
    out = update_children(base, patch)
    assert "A" in out["children"] and "B" in out["children"]
    assert out["children"]["B"]["value"] == 100


def test_update_children_overwrites_existing():
    """Check that update_children replaces an existing child's value and strips weight."""
    base = {
        "name": "x",
        "type": "pie",
        "value": 0,
        "children": {"A": {"type": "ticker", "value": 50, "weight": Decimal("0.5")}},
    }
    patch = {"A": {"type": "ticker", "value": 100}}
    result = update_children(base, patch)
    assert result["children"]["A"]["value"] == 100
    assert "weight" not in result["children"]["A"]


def test_update_children_accepts_parsed_image_data(base_portfolio):
    """Ensure update_children correctly converts parsed slice input into portfolio structure."""
    parsed = {
        "FRB23Q1": {"type": "pie", "value": 1845.07},
        "RB21Q4": {"type": "pie", "value": 886.61},
        "FB25-4": {"type": "pie", "value": 307.36},
    }
    updated = update_children(base_portfolio, parsed)
    assert updated["children"]["FRB23Q1"]["value"] == Decimal("1845.07")
    assert updated["children"]["FB25-4"]["type"] == "pie"
