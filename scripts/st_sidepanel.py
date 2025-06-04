"""Streamlit sidebar: Portfolio selection, creation, deletion."""

import os

import streamlit as st

from scripts.log_util import app_logger, set_log_level
from scripts.portfolio import (
    create_portfolio,
    delete_portfolio,
    list_portfolios,
    load_portfolio,
    normalize_portfolio,
)

logger = app_logger(__name__)


def render_sidepanel():
    """
    Render the sidebar interface for managing portfolios.
    """
    DATA_DIR = st.session_state["DATA_DIR"]
    with st.sidebar:
        st.header("\U0001F4C1 Portfolios")

        portfolio_names = list_portfolios(DATA_DIR)

        for name in portfolio_names:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                if st.button(name, key=f"load_{name}"):
                    path = os.path.join(DATA_DIR, name)
                    portfolio = load_portfolio(path)
                    st.session_state["portfolio"] = normalize_portfolio(portfolio)
                    st.session_state["portfolio_file"] = name
            with col2:
                # TODO: On portfolio delete, clear session state and remove any UI artifacts
                #       if the deleted portfolio was currently loaded.
                if st.button("\u274C", key=f"delete_{name}"):
                    st.session_state["confirm_delete"] = name

        if "confirm_delete" in st.session_state:
            name = st.session_state["confirm_delete"]
            st.warning(f"Confirm delete: {name}")
            confirm_col, cancel_col = st.columns(2)

            if confirm_col.button("Yes, Delete"):
                delete_portfolio(name, DATA_DIR)

                # Clear session state if deleted portfolio was active
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
        st.header("\u2795 New Portfolio")
        st.text_input(
            "New Portfolio Name",
            value="",
            key="new_portfolio_name",
            on_change=create_portfolio,
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
