"""Streamlit main panel: Portfolio summary and image parsing."""

import streamlit as st

from scripts.image_parser import handle_image_upload
from scripts.log_util import app_logger
from scripts.portfolio import format_portfolio_table

logger = app_logger(__name__)


def render_mainpanel():
    """
    Render the main content panel: portfolio display and image upload.

    :return: None
    """
    st.title("📈 M1 Pie DCA Allocator")

    if "portfolio" not in st.session_state:
        st.info("Select or create a portfolio to begin.")
        return

    portfolio = st.session_state["portfolio"]
    portfolio_file = st.session_state["portfolio_file"]
    DATA_DIR = st.session_state["DATA_DIR"]

    st.subheader(f"Loaded Portfolio: {portfolio['name']}")
    st.subheader(f"Total Value: ${portfolio['value']:.2f}")

    if portfolio.get("children"):
        df = format_portfolio_table(portfolio)
        st.table(df)
    else:
        st.info("This portfolio has no children.")

    st.divider()
    st.subheader("🖼️ Upload Screenshot")

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
