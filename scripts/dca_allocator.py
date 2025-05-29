"""DCA capital allocator logic.

Distributes new capital across a nested pie structure using weight ratios.
"""

from decimal import Decimal
from typing import Dict, Any


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
