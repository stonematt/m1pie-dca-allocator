"""Portfolio data loading and normalization functions.

Handles parsing of canonical JSON format and recursive weight normalization.
"""

import os
import glob
import json
from decimal import Decimal
from typing import Dict, Any
from scripts.log_util import app_logger

logger = app_logger(__name__)


def load_portfolio(path: str) -> Dict[str, Any]:
    """
    Load and parse portfolio JSON file.

    :param path: File path to the JSON portfolio.
    :return: Portfolio dictionary.
    """
    logger.info(f"Loading portfolio from {path}")
    with open(path, "r") as f:
        return json.load(f)


def normalize_portfolio(portfolio: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recalculate and inject weight values for all child nodes recursively.

    :param portfolio: Portfolio root node.
    :return: Portfolio with weights populated at each pie level.
    """
    logger.info("Normalizing portfolio weights")

    def recurse(node):
        if node["type"] == "ticker":
            return node
        total = sum(child["value"] for child in node["children"].values())
        for k, v in node["children"].items():
            v["weight"] = Decimal(v["value"]) / Decimal(total)
            recurse(v)
        return node

    return recurse(portfolio)


def load_or_create_portfolio(path: str = "data/portfolio.json") -> Dict[str, Any]:
    """
    Load portfolio JSON if it exists, else return empty structure.

    :param path: File path to the JSON portfolio.
    :return: Portfolio dictionary (existing or new).
    """
    if os.path.exists(path):
        logger.info(f"Found existing portfolio at {path}")
        with open(path, "r") as f:
            return json.load(f)
    logger.info(f"Creating new empty portfolio at {path}")
    return {
        "name": os.path.splitext(os.path.basename(path))[0],
        "type": "pie",
        "value": 0.0,
        "children": {},
    }


def save_portfolio(
    portfolio: Dict[str, Any], path: str = "data/portfolio.json"
) -> None:
    """
    Save portfolio dictionary to disk.

    :param portfolio: Portfolio structure to save.
    :param path: File path for JSON output.
    """
    logger.info(f"Saving portfolio to {path}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(portfolio, f, indent=2)


def summarize_children(portfolio: Dict[str, Any]) -> list[tuple[str, float, float]]:
    """
    Return list of (name, value, weight%) for each child in the portfolio.

    :param portfolio: Root or nested pie node.
    :return: List of tuples: (child_name, value, percent_weight)
    """
    logger.info("Summarizing child nodes of portfolio")
    children = portfolio.get("children", {})
    summary = []
    for name, child in children.items():
        weight_pct = float(Decimal(child["weight"]) * 100)
        summary.append((name, child["value"], weight_pct))
    return summary


def list_portfolios(directory: str = "data") -> list[str]:
    """
    List all portfolio JSON files in the given directory.

    :param directory: Folder to search for portfolio files.
    :return: List of filenames.
    """
    logger.info(f"Listing portfolios in {directory}")
    return sorted(
        os.path.basename(p) for p in glob.glob(os.path.join(directory, "*.json"))
    )


def delete_portfolio(filename: str, directory: str = "data") -> None:
    """
    Delete a portfolio JSON file by filename.

    :param filename: Filename of the portfolio to delete.
    :param directory: Folder containing the file.
    """
    path = os.path.join(directory, filename)
    logger.info(f"Deleting portfolio {path}")
    os.remove(path)


def update_children(
    portfolio: Dict[str, Any], new_children: Dict[str, float]
) -> Dict[str, Any]:
    """
    Merge new tickers and values into an existing portfolio's children.

    :param portfolio: Existing portfolio dictionary.
    :param new_children: Mapping of ticker symbol to value.
    :return: Updated portfolio dictionary.
    """
    logger.info("Updating portfolio with parsed children")
    children = portfolio.get("children", {})
    for ticker, value in new_children.items():
        children[ticker] = {"type": "ticker", "value": float(value)}
    portfolio["children"] = children
    return portfolio
