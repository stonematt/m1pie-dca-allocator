"""Streamlit sidebar: Portfolio selection, creation, deletion."""

import streamlit as st

from scripts.account import (
    add_or_replace_portfolio,
    delete_portfolio,
    list_portfolios,
    get_portfolio,
)
from scripts.cookie_account import load_account_from_cookie, save_account_to_cookie
from scripts.portfolio import normalize_portfolio
from scripts.log_util import app_logger, set_log_level

logger = app_logger(__name__)


def render_sidepanel():
    """
    Render the sidebar interface for managing portfolios, using cookie-based account storage.
    """
    if "account" not in st.session_state:
        st.session_state["account"] = load_account_from_cookie()

    account = st.session_state["account"]
    portfolio_names = list_portfolios(account)

    with st.sidebar:
        st.header("\U0001f4c1 Portfolios")

        for name in portfolio_names:
            portfolio = get_portfolio(account, name)
            display_name = portfolio.get("name", name)

            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                if st.button(display_name, key=f"load_{name}"):
                    st.session_state["portfolio"] = normalize_portfolio(portfolio)
                    st.session_state["portfolio_file"] = name
                    st.session_state.pop("adjusted_portfolio", None)

            with col2:
                if st.button("❌", key=f"delete_{name}"):
                    st.session_state["confirm_delete"] = name

        if "confirm_delete" in st.session_state:
            name = st.session_state["confirm_delete"]
            st.warning(f"Confirm delete: {name}")
            confirm_col, cancel_col = st.columns(2)

            if confirm_col.button("Yes, Delete"):
                account = delete_portfolio(account, name)
                st.session_state["account"] = account
                save_account_to_cookie(account)

                if st.session_state.get("portfolio_file") == name:
                    for key in [
                        "portfolio",
                        "portfolio_file",
                        "adjusted_portfolio",
                        "image_processed",
                    ]:
                        st.session_state.pop(key, None)

                del st.session_state["confirm_delete"]
                st.success(f"Deleted {name}")
                st.rerun()

            if cancel_col.button("Cancel"):
                del st.session_state["confirm_delete"]

        st.divider()
        st.header("➕ New Portfolio")

        def create_and_save():
            name = st.session_state["new_portfolio_name"].strip()
            if name:
                empty = {"name": name, "type": "pie", "children": {}, "value": 0}
                st.session_state["account"] = add_or_replace_portfolio(
                    st.session_state["account"], name, empty
                )
                save_account_to_cookie(st.session_state["account"])
                st.rerun()

        st.text_input(
            "New Portfolio Name",
            value="",
            key="new_portfolio_name",
            on_change=create_and_save,
        )

        st.divider()
        st.header("🛠️ Settings")

        log_level = st.selectbox(
            "Log Level",
            options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            index=1,
            key="log_level",
        )
        set_log_level(log_level)
        st.caption(f"Logger set to {log_level}")
