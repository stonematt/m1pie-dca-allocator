"""DCA capital allocator logic.

Distributes new capital across a nested pie structure using weight ratios.
"""

from decimal import Decimal
from typing import Any, Dict

from scripts.log_util import app_logger

logger = app_logger(__name__)


def allocate_dca(portfolio: Dict[str, Any], amount: Decimal) -> Dict[str, Decimal]:
    """
    Allocate new capital across the portfolio using current weight ratios.

    :param portfolio: Portfolio root node.
    :param amount: Total capital to allocate as a Decimal.
    :return: Mapping from ticker ID to allocated capital.
    """
    allocations = {}

    def recurse(node, factor=Decimal(1)):
        if node["type"] == "ticker":
            allocations[node.get("id", "UNNAMED")] = amount * factor
            return
        for k, v in node["children"].items():
            recurse(v, factor * Decimal(v["weight"]))

    recurse(portfolio)
    return allocations


def scale_existing_positions(
    pie_data: Dict[str, Any],
    new_funds: Decimal,
    percent_to_new: Decimal,
) -> Dict[str, Any]:
    """
    Scale up existing pie values by allocating new funds proportionally.

    :param pie_data: Root pie node
    :param new_funds: Total new capital
    :param percent_to_new: Percentage to be allocated to new tickers
    :return: Updated pie structure with scaled existing positions
    """
    total_existing = Decimal(pie_data["value"])
    funds_to_existing = new_funds * (Decimal(100) - percent_to_new) / Decimal(100)
    scale_factor = (total_existing + funds_to_existing) / total_existing

    updated_children = {}
    for k, v in pie_data["children"].items():
        val = Decimal(v["value"]) * scale_factor
        updated_children[k] = {**v, "value": float(round(val, 2))}

    return {
        **pie_data,
        "value": float(total_existing + funds_to_existing),
        "children": updated_children,
    }


def add_mock_targets(
    pie_data: Dict[str, Any],
    new_ticker_count: int,
    new_fund_allocation: Decimal,
) -> Dict[str, Any]:
    """
    Add mock tickers to the pie with equal target values.

    :param pie_data: Pie updated with scaled existing values
    :param new_ticker_count: Number of new mock tickers
    :param new_fund_allocation: Capital to divide among them
    :return: Pie with new tickers added and updated value
    """
    per_ticker = new_fund_allocation / Decimal(new_ticker_count)
    children = pie_data["children"].copy()

    for i in range(1, new_ticker_count + 1):
        key = f"NEW_{i}"
        children[key] = {
            "type": "ticker",
            "value": float(round(per_ticker, 2)),
        }

    return {
        **pie_data,
        "value": float(Decimal(pie_data["value"]) + new_fund_allocation),
        "children": children,
    }


def recalculate_pie_allocation(
    pie_data: Dict[str, Any],
    new_funds: Decimal = Decimal("50.0"),
    new_ticker_count: int = 2,
    percent_to_new: Decimal = Decimal("80"),
) -> Dict[str, Any]:
    """
    Recalculate pie after adding funds and new mock tickers.
    """
    logger.info("Starting DCA allocation")
    logger.info(
        f"New funds: {new_funds}, % to new: {percent_to_new}, New tickers: {new_ticker_count}"
    )

    scaled = scale_existing_positions(pie_data, new_funds, percent_to_new)
    logger.debug(f"Scaled existing positions: {scaled['children']}")

    funds_to_new = new_funds * percent_to_new / Decimal(100)
    updated = add_mock_targets(scaled, new_ticker_count, funds_to_new)
    logger.debug(f"After adding new tickers: {updated['children']}")

    target_weights = compute_target_weights(updated)
    logger.debug(f"Computed target weights: {target_weights}")

    for k, w in target_weights.items():
        updated["children"][k]["target_weight"] = w

    logger.info("Recalculation complete")
    return updated


def compute_target_weights(pie_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Compute whole-number weight percentages for each child in a pie.

    :param pie_data: A pie node with children and values
    :return: Mapping from child ID to integer weight (summing to 100)
    """
    children = pie_data["children"]
    total = sum(v["value"] for v in children.values())
    raw_weights = {k: (v["value"] / total) * 100 for k, v in children.items()}

    floored = {k: int(w) for k, w in raw_weights.items()}
    remainder = 100 - sum(floored.values())

    # Sort keys by fractional remainder descending
    sorted_keys = sorted(
        raw_weights.keys(),
        key=lambda k: raw_weights[k] - floored[k],
        reverse=True,
    )

    for k in sorted_keys[:remainder]:
        floored[k] += 1

    return floored
