"""Portfolio data loading and normalization functions.

Handles parsing of canonical JSON format and recursive weight normalization.
"""

import glob
import json
import os
from decimal import Decimal
from typing import Any, Dict

import pandas as pd

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
        if "children" not in node:
            node["children"] = {}
        total = sum(child["value"] for child in node["children"].values())
        for k, v in node["children"].items():
            v["weight"] = Decimal(v["value"]) / Decimal(total)
            recurse(v)
        return node

    return recurse(portfolio)


def create_portfolio() -> None:
    """
    Create and load a new portfolio from Streamlit input.
    Uses session state: 'new_portfolio_name', 'DATA_DIR'.
    """
    import streamlit as st

    name = st.session_state.get("new_portfolio_name", "main")
    directory = st.session_state["DATA_DIR"]
    path = os.path.join(directory, f"{name}.json")

    if not os.path.exists(path):
        logger.info(f"Creating new portfolio {name}")
        portfolio = {"name": name, "type": "pie", "value": 0.0, "children": {}}
        save_portfolio(portfolio, path)
        st.session_state["portfolio"] = normalize_portfolio(portfolio)
        st.session_state["portfolio_file"] = f"{name}.json"
        st.success(f"Created and loaded {name}.json")
    else:
        st.warning("Portfolio already exists.")


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


def update_children(portfolio: dict, parsed: dict) -> dict:
    """
    Update the children of a portfolio with parsed slice values.

    :param portfolio: The portfolio node to modify.
    :param parsed: Mapping of slice_name to {"type": str, "value": float}.
    :return: The updated portfolio dictionary.
    """
    children = portfolio.setdefault("children", {})

    for name, meta in parsed.items():
        try:
            _type = meta["type"]
            _value = float(meta["value"])
            children[name] = {"type": _type, "value": _value}
        except (KeyError, TypeError, ValueError):
            logger.warning(f"Skipping malformed slice: {name} -> {meta}")

    return portfolio


def format_portfolio_table(portfolio: dict) -> pd.DataFrame:
    """
    Format portfolio children into a display-ready table.

    :param portfolio: Portfolio root node.
    :return: DataFrame with icon, name, value, and weight.
    """
    rows = []
    children = portfolio.get("children", {})
    for name, child in children.items():
        icon = "◔" if child["type"] == "pie" else "📈"
        value = float(child["value"])
        weight = float(child["weight"]) * 100
        rows.append(
            {
                " ": icon,
                "Name": name,
                "Value": f"${value:,.2f}",
                "Weight": f"{weight:.1f}%",
            }
        )
    return pd.DataFrame(rows)
