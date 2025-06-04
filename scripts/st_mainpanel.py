"""Streamlit main panel: Portfolio summary and image parsing."""

from decimal import Decimal

import pandas as pd
import streamlit as st

from scripts.dca_allocator import compute_target_weights, recalculate_pie_allocation
from scripts.image_parser import handle_image_upload
from scripts.log_util import app_logger
from scripts.portfolio import format_portfolio_table

logger = app_logger(__name__)


def render_mainpanel():
    """
    Render the main content panel: portfolio display and tabbed tools.

    :return: None
    """
    st.title("📈 M1 Pie DCA Allocator")

    if "portfolio" not in st.session_state:
        st.info("Select or create a portfolio to begin.")
        return

    portfolio = st.session_state["portfolio"]
    portfolio_file = st.session_state["portfolio_file"]
    DATA_DIR = st.session_state["DATA_DIR"]

    # Always-visible portfolio summary
    st.subheader(f"Loaded Portfolio: {portfolio['name']}")
    st.subheader(f"Total Value: ${portfolio['value']:.2f}")

    if portfolio.get("children"):
        df = format_portfolio_table(portfolio)
        st.table(df)
    else:
        st.info("This portfolio has no children.")

    st.divider()

    # Tabs: Upload + Adjust
    tab1, tab2 = st.tabs(["📤 Upload Image", "🛠 Adjust Positions"])

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
                portfolio_file,
                DATA_DIR,
                st.secrets["openai"]["api_key"],
            )

    with tab2:
        st.subheader("Adjust Positions")

        with st.form("adjust_form"):
            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                new_funds = st.number_input("New funds", min_value=0.0, value=500.0)
            with row1_col2:
                new_ticker_count = st.number_input("New tickers", min_value=1, value=4)

            percent_to_new = st.slider("Percent to new", 0, 100, value=80)

            submit = st.form_submit_button("Recalculate Allocation")

        if submit:
            updated = recalculate_pie_allocation(
                pie_data=st.session_state["portfolio"],
                new_funds=Decimal(str(new_funds)),
                new_ticker_count=new_ticker_count,
                percent_to_new=Decimal(str(percent_to_new)),
            )
            st.session_state["adjusted_portfolio"] = updated
            st.success("Allocation recalculated.")

        if "adjusted_portfolio" in st.session_state:
            st.subheader("Adjusted Allocation Review")

            original = st.session_state["portfolio"]
            adjusted = st.session_state["adjusted_portfolio"]

            original_children = original["children"]
            adjusted_children = adjusted["children"]

            data = []
            total_original = sum(v["value"] for v in original_children.values())
            total_adjusted = sum(v["value"] for v in adjusted_children.values())

            for k in adjusted_children:
                current_val = original_children.get(k, {}).get("value", 0.0)
                target_val = adjusted_children[k]["value"]
                capital_allocated = target_val - current_val

                current_weight = (
                    (current_val / total_original * 100) if total_original else 0
                )
                target_weight = adjusted_children[k].get("target_weight", 0)

                data.append(
                    {
                        "Ticker/Pie": k,
                        "Current Value": f"${current_val:,.2f}",
                        "Current Weight": f"{int(round(current_weight))}%",
                        "Capital Allocated": f"${capital_allocated:,.2f}",
                        "Target Value": f"${target_val:,.2f}",
                        "Target Weight": f"{target_weight}%",
                    }
                )

            df = pd.DataFrame(data)
            st.table(df)
