import json
import os
import tempfile
from decimal import ROUND_HALF_UP, Decimal

import pytest

from scripts.portfolio import (
    list_portfolios,
    load_portfolio,
    normalize_portfolio,
    save_portfolio,
    update_children,
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
    assert updated["children"]["FRB23Q1"]["value"] == 1845.07
    assert updated["children"]["FB25-4"]["type"] == "pie"


def test_save_and_load_portfolio_consistency():
    """Test that saving and reloading a portfolio yields the same data."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "portfolio.json")
        data = {"name": "demo", "type": "pie", "value": 0, "children": {}}
        save_portfolio(data, path)
        loaded = load_portfolio(path)
        assert data == loaded


def test_list_portfolios_filters_json():
    """Ensure that only .json files are returned from a directory."""
    with tempfile.TemporaryDirectory() as tmp:
        paths = ["a.json", "b.json", "c.txt"]
        for name in paths:
            with open(os.path.join(tmp, name), "w") as f:
                f.write("{}")
        files = list_portfolios(tmp)
        assert set(files) == {"a.json", "b.json"}


def test_save_portfolio_with_decimals(base_portfolio, tmp_path):
    """Ensure save_portfolio correctly serializes Decimal values."""
    # Normalize to inject Decimal weights
    normalized = normalize_portfolio(base_portfolio)
    path = tmp_path / "portfolio.json"

    save_portfolio(normalized, str(path))

    with open(path) as f:
        data = json.load(f)
    assert data["children"]["A"]["weight"] == float(
        normalized["children"]["A"]["weight"]
    )
