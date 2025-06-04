import pytest
from decimal import Decimal
from scripts.dca_allocator import (
    scale_existing_positions,
    add_mock_targets,
    compute_target_weights,
    recalculate_pie_allocation,
)


@pytest.fixture
def base_pie():
    """Base pie with 3 tickers and total value of 300."""
    return {
        "name": "main",
        "type": "pie",
        "value": 300.0,
        "children": {
            "AAPL": {"type": "ticker", "value": 150.0},
            "MSFT": {"type": "ticker", "value": 100.0},
            "GOOGL": {"type": "ticker", "value": 50.0},
        },
    }


def test_scale_existing_positions(base_pie):
    """
    Verify that existing pie positions scale up correctly
    using 20% of new funds, preserving proportional weights.
    """
    updated = scale_existing_positions(
        pie_data=base_pie,
        new_funds=Decimal("50.0"),
        percent_to_new=Decimal("80"),
    )

    assert round(updated["value"], 2) == 310.0
    assert round(updated["children"]["AAPL"]["value"], 2) == 155.0
    assert round(updated["children"]["MSFT"]["value"], 2) == 103.33
    assert round(updated["children"]["GOOGL"]["value"], 2) == 51.67


def test_add_mock_targets(base_pie):
    """
    Verify that mock new tickers are added evenly and total value updates.
    """
    pie = {
        **base_pie,
        "value": 310.0,
        "children": {
            "AAPL": {"type": "ticker", "value": 155.0},
            "MSFT": {"type": "ticker", "value": 103.33},
            "GOOGL": {"type": "ticker", "value": 51.67},
        },
    }

    result = add_mock_targets(
        pie_data=pie,
        new_ticker_count=2,
        new_fund_allocation=Decimal("40.0"),
    )

    children = result["children"]
    assert "NEW_1" in children
    assert "NEW_2" in children
    assert round(children["NEW_1"]["value"], 2) == 20.0
    assert round(children["NEW_2"]["value"], 2) == 20.0
    assert round(result["value"], 2) == 350.0


def test_compute_target_weights():
    """
    Ensure weights are whole integers and sum to 100.
    """
    children = {
        "A": {"value": 150},
        "B": {"value": 100},
        "C": {"value": 50},
    }
    pie = {"children": children}
    weights = compute_target_weights(pie)

    assert sum(weights.values()) == 100
    assert all(isinstance(w, int) for w in weights.values())
    assert weights["A"] > weights["B"] > weights["C"]


def test_recalculate_pie_allocation_full(base_pie):
    """
    Full pipeline test: scale, add tickers, compute weights.
    """
    result = recalculate_pie_allocation(base_pie)

    children = result["children"]
    assert "NEW_1" in children
    assert "NEW_2" in children
    assert all("target_weight" in v for v in children.values())
    assert sum(v["target_weight"] for v in children.values()) == 100
