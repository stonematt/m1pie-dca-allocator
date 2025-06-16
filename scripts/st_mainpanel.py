"""st_mainpanel.py: Streamlit main panel using cookie-backed portfolio storage."""

from copy import deepcopy
from decimal import Decimal

import streamlit as st

from scripts.account import add_or_replace_portfolio
from scripts.cookie_account import save_account_to_cookie
from scripts.dca_allocator import recalculate_pie_allocation
from scripts.image_parser import handle_image_upload
from scripts.log_util import app_logger
from scripts.portfolio import normalize_portfolio
from scripts.st_aggrid import render_portfolio_aggrid
from scripts.st_utils import (
    render_allocation_comparison_charts,
    render_allocation_review_table,
    render_sankey_diagram,
)

logger = app_logger(__name__)


def render_mainpanel():
    """
    Render the main content panel: portfolio display and tabbed tools.
    Uses cookie-backed session state for account and portfolio.
    """
    st.title("\U0001f4c8 M1 Pie DCA Allocator")

    if "portfolio" not in st.session_state or "portfolio_file" not in st.session_state:
        st.info("Select or create a portfolio to begin.")
        return

    portfolio = st.session_state["portfolio"]

    st.subheader(f"Loaded Portfolio: {portfolio['name']}")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader(f"Total Value: ${portfolio['value']:.2f}")
        if portfolio.get("children"):
            render_portfolio_aggrid()
        else:
            st.info("This portfolio has no children.")

    with col2:
        render_sankey_diagram(portfolio) if portfolio else None

    st.divider()

    tab1, tab2 = st.tabs(["\U0001f4e4 Upload Image", "\U0001f6e0 Adjust Positions"])

    with tab1:
        st.subheader("Upload Screenshot")

        img_file = st.file_uploader(
            "Upload M1 screenshot (mixed pies/tickers)",
            type=["png", "jpg", "jpeg"],
            key="uploaded_image",
        )

        reparse = st.checkbox("Force re-parse image")

        if img_file:
            handle_image_upload(
                img_file,
                reparse,
                portfolio,
                st.secrets["openai"]["api_key"],
            )
            st.session_state["portfolio"] = normalize_portfolio(portfolio)
            st.session_state["account"] = add_or_replace_portfolio(
                st.session_state["account"],
                st.session_state["portfolio_file"],
                st.session_state["portfolio"],
            )
            save_account_to_cookie(st.session_state["account"])
            st.success("Portfolio updated from image.")

        with tab2:
            st.subheader("Adjust Positions")

            with st.form("adjust_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_funds = st.number_input("New funds", min_value=0.0, value=500.0)
                with col2:
                    new_ticker_count = st.number_input(
                        "New tickers", min_value=1, value=4
                    )

                percent_to_new = st.slider("Percent to new", 0, 100, value=80)
                submit = st.form_submit_button("Recalculate Allocation")

            if submit:
                original = deepcopy(st.session_state["portfolio"])
                updated = recalculate_pie_allocation(
                    pie_data=original,
                    new_funds=Decimal(str(new_funds)),
                    new_ticker_count=new_ticker_count,
                    percent_to_new=Decimal(str(percent_to_new)),
                )
                st.session_state["adjusted_portfolio"] = updated
                st.session_state["original_portfolio"] = (
                    original  # cache for true before/after
                )
                st.success("What-if allocation calculated.")

            if "adjusted_portfolio" in st.session_state:
                st.subheader("Adjusted Allocation Review")
                col1, col2 = st.columns([2, 1])
                with col1:
                    render_allocation_review_table(
                        st.session_state["original_portfolio"],
                        st.session_state["adjusted_portfolio"],
                    )
                with col2:
                    render_allocation_comparison_charts(
                        st.session_state["original_portfolio"],
                        st.session_state["adjusted_portfolio"],
                    )

                if st.button("Confirm and Save Changes"):
                    st.session_state["portfolio"] = normalize_portfolio(
                        st.session_state["adjusted_portfolio"]
                    )
                    st.session_state["account"] = add_or_replace_portfolio(
                        st.session_state["account"],
                        st.session_state["portfolio_file"],
                        st.session_state["portfolio"],
                    )
                    save_account_to_cookie(st.session_state["account"])
                    st.success("Portfolio changes saved.")
