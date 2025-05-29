"""Portfolio data loading and normalization functions.

Handles parsing of canonical JSON format and recursive weight normalization.
"""

import json
from decimal import Decimal
from typing import Dict, Any


def load_portfolio(path: str) -> Dict[str, Any]:
    """
    Load and parse portfolio JSON file.

    :param path: File path to the JSON portfolio.
    :return: Portfolio dictionary.
    """
    with open(path, "r") as f:
        return json.load(f)


def normalize_portfolio(portfolio: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recalculate and inject weight values for all child nodes recursively.

    :param portfolio: Portfolio root node.
    :return: Portfolio with weights populated at each pie level.
    """

    def recurse(node):
        if node["type"] == "ticker":
            return node
        total = sum(child["value"] for child in node["children"].values())
        for k, v in node["children"].items():
            v["weight"] = Decimal(v["value"]) / Decimal(total)
            recurse(v)
        return node

    return recurse(portfolio)
