"""Streamlit main panel: Portfolio summary and image parsing."""

import os

import streamlit as st
from PIL import Image

from scripts.image_parser import extract_hybrid_slices_from_image
from scripts.log_util import app_logger
from scripts.portfolio import (
    format_portfolio_table,
    normalize_portfolio,
    save_portfolio,
    update_children,
)
from scripts.utils import file_hash

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
        img_file.seek(0)
        current_hash = file_hash(img_file)

        if st.session_state.get("current_image_hash") != current_hash:
            st.session_state["image_processed"] = False
            st.session_state["current_image_hash"] = current_hash

        image = Image.open(img_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        if "parsed_images" not in st.session_state:
            st.session_state["parsed_images"] = {}

        if reparse or current_hash not in st.session_state["parsed_images"]:
            img_file.seek(0)
            parsed = extract_hybrid_slices_from_image(
                img_file, st.secrets["openai"]["api_key"]
            )
            st.session_state["parsed_images"][current_hash] = parsed
            logger.info(f"Parsed slices (new): {parsed}")
        else:
            parsed = st.session_state["parsed_images"][current_hash]
            logger.info(f"Parsed slices (cached): {parsed}")

        if parsed and not st.session_state.get("image_processed"):
            updated = update_children(portfolio, parsed)
            save_path = os.path.join(DATA_DIR, portfolio_file)
            save_portfolio(updated, save_path)
            st.session_state["portfolio"] = normalize_portfolio(updated)
            st.session_state["image_processed"] = True
            st.success(f"Added/updated {len(parsed)} slices.")
            st.rerun()
