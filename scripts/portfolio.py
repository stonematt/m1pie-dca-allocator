"""portfolio.py: Portfolio data loading and normalization functions.

Handles parsing of canonical JSON format and recursive weight normalization.
"""

from decimal import Decimal
from typing import Any, Dict

import pandas as pd
import streamlit as st

from scripts.log_util import app_logger
from scripts.account import add_or_replace_portfolio
from scripts.cookie_account import save_account_to_cookie

logger = app_logger(__name__)


def normalize_portfolio(portfolio: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recalculate and inject weight values for all child nodes recursively
    based on their `value`. Also updates each pie node's `value` to the
    sum of its children. Uses Decimal for precision.

    :param portfolio: Portfolio root node.
    :return: Portfolio with updated weights and values.
    """
    logger.info("Normalizing portfolio weights")

    def recurse(node: Dict[str, Any]) -> Dict[str, Any]:
        if node["type"] == "ticker":
            return node
        if "children" not in node:
            node["children"] = {}

        total = sum(
            Decimal(child.get("value", "0")) for child in node["children"].values()
        )

        node["value"] = total

        for child in node["children"].values():
            if total > 0:
                child["weight"] = Decimal(child["value"]) / total
            else:
                child["weight"] = Decimal("0")
            recurse(child)

        return node

    return recurse(portfolio)


def create_named_portfolio(account: dict, name: str) -> dict:
    """
    Create, persist, and load a new empty pie portfolio into the session.

    :param account: Account dictionary
    :param name: Portfolio name
    :return: Updated account with new portfolio added
    """
    logger.info(f"Creating new portfolio {name}")
    portfolio = {
        "name": name,
        "type": "pie",
        "value": 0.0,
        "children": {},
    }
    portfolio = normalize_portfolio(portfolio)
    updated = add_or_replace_portfolio(account, name, portfolio)
    save_account_to_cookie(updated)
    st.session_state["portfolio"] = portfolio
    st.session_state["portfolio_file"] = name
    return updated


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

    logger.debug(f"Final merged children: {children}")
    save_current_portfolio()
    return portfolio


def save_current_portfolio():
    """
    Save the current portfolio to the session's account and persist to cookie.
    """
    account = st.session_state["account"]
    portfolio = st.session_state["portfolio"]
    updated = add_or_replace_portfolio(account, portfolio["name"], portfolio)
    st.session_state["account"] = updated
    save_account_to_cookie(updated)


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


def create_and_save():
    name = st.session_state["new_portfolio_name"].strip()
    if name:
        st.session_state["account"] = create_named_portfolio(
            st.session_state["account"], name
        )
        st.session_state["new_portfolio_name"] = ""  # Clear input
        st.rerun()
