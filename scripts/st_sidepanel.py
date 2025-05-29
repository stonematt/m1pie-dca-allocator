"""Streamlit sidebar: Portfolio selection, creation, deletion."""

import streamlit as st
import os
from scripts.portfolio import (
    list_portfolios,
    load_portfolio,
    save_portfolio,
    normalize_portfolio,
    delete_portfolio,
)
from scripts.log_util import app_logger

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
                if st.button("\u274C", key=f"delete_{name}"):
                    st.session_state["confirm_delete"] = name

        if "confirm_delete" in st.session_state:
            name = st.session_state["confirm_delete"]
            st.warning(f"Confirm delete: {name}")
            confirm_col, cancel_col = st.columns(2)
            if confirm_col.button("Yes, Delete"):
                delete_portfolio(name, DATA_DIR)
                del st.session_state["confirm_delete"]
                st.success(f"Deleted {name}")
                st.rerun()
            if cancel_col.button("Cancel"):
                del st.session_state["confirm_delete"]

        st.divider()
        st.header("\u2795 New Portfolio")
        new_name = st.text_input("New Portfolio Name", value="new_portfolio")
        if st.button("Create"):
            new_path = os.path.join(DATA_DIR, f"{new_name}.json")
            if not os.path.exists(new_path):
                logger.info(f"Creating new portfolio {new_name}")
                empty = {"name": new_name, "type": "pie", "value": 0.0, "children": {}}
                save_portfolio(empty, new_path)
                st.success(f"Created {new_name}.json")
                st.rerun()
            else:
                st.warning("Portfolio already exists.")
