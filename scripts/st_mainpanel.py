"""Streamlit main panel: Portfolio summary and image parsing."""

import streamlit as st
import os
from PIL import Image
from scripts.portfolio import (
    save_portfolio,
    normalize_portfolio,
    summarize_children,
    update_children,
)
from scripts.image_parser import extract_hybrid_slices_from_image
from scripts.log_util import app_logger

logger = app_logger(__name__)


def render_mainpanel():
    """
    Render the main content panel: portfolio display and image upload.
    """
    st.title("\U0001F4C8 M1 Pie DCA Allocator")

    if "portfolio" not in st.session_state:
        st.info("Select or create a portfolio to begin.")
        return

    portfolio = st.session_state["portfolio"]
    portfolio_file = st.session_state["portfolio_file"]
    DATA_DIR = st.session_state["DATA_DIR"]

    st.subheader(f"Loaded Portfolio: {portfolio['name']}")
    st.subheader(f"Total Value: ${portfolio['value']:.2f}")

    if portfolio.get("children"):
        for name, value, percent in summarize_children(portfolio):
            st.markdown(f"- **{name}**: ${value:.2f} ({percent:.2f}%)")
    else:
        st.info("This portfolio has no children.")

    st.divider()
    st.subheader("\U0001F5BC Upload Screenshot")
    img_file = st.file_uploader(
        "Upload M1 screenshot (mixed pies/tickers)", type=["png", "jpg", "jpeg"]
    )

    if img_file:
        image = Image.open(img_file)
        parsed = extract_hybrid_slices_from_image(img_file.name)

        if parsed:
            updated = update_children(portfolio, parsed)
            save_path = os.path.join(DATA_DIR, portfolio_file)
            save_portfolio(updated, save_path)
            st.session_state["portfolio"] = normalize_portfolio(updated)
            st.success(f"Added/updated {len(parsed)} slices.")
            st.rerun()
