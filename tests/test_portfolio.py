import json
import os
import tempfile
from decimal import Decimal, ROUND_HALF_UP

from scripts.portfolio import (
    list_portfolios,
    load_portfolio,
    normalize_portfolio,
    save_portfolio,
    update_children,
)


def test_normalize_portfolio_weights():
    """Verify weights are correctly calculated from values after normalization."""
    p = {
        "name": "test",
        "type": "pie",
        "value": 0,
        "children": {
            "A": {"type": "ticker", "value": 20},
            "B": {"type": "ticker", "value": 40},
            "C": {"type": "ticker", "value": 80},
        },
    }
    result = normalize_portfolio(p)
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
    """Ensure new slices are merged into portfolio without removing existing ones."""
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
    """Verify patch correctly replaces existing child values and strips weight."""
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


def test_save_and_load_portfolio_consistency():
    """Check that portfolio JSON saves and loads without data loss."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "portfolio.json")
        data = {"name": "demo", "type": "pie", "value": 0, "children": {}}
        save_portfolio(data, path)
        loaded = load_portfolio(path)
        assert data == loaded


def test_list_portfolios_filters_json():
    """Ensure only `.json` files are returned when listing portfolios."""
    with tempfile.TemporaryDirectory() as tmp:
        paths = ["a.json", "b.json", "c.txt"]
        for name in paths:
            with open(os.path.join(tmp, name), "w") as f:
                f.write("{}")
        files = list_portfolios(tmp)
        assert set(files) == {"a.json", "b.json"}
