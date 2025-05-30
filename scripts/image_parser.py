"""
image_parser.py: Extract hybrid pie structures from M1 screenshots using GPT-4o Vision.

Parses screenshots via the OpenAI Vision API and returns structured JSON identifying
tickers and sub-pies. Encodes uploaded files to base64 PNG format for transmission.
"""

import json
import os
import re
from base64 import b64encode
from datetime import datetime
from io import BytesIO

import openai
import streamlit as st
from PIL import Image

from scripts.log_util import app_logger
from scripts.portfolio import normalize_portfolio, save_portfolio, update_children
from scripts.utils import file_hash

logger = app_logger(__name__)


def extract_hybrid_slices_from_image(file, api_key: str) -> dict:
    """
    Send image to OpenAI Vision API and extract structured JSON slices.

    :param file: Uploaded image file
    :param api_key: OpenAI API key
    :return: Dict containing ticker/pie metadata
    """
    logger.info(f"[{datetime.now().isoformat()}] Parsing hybrid pie from uploaded file")
    b64_img = _encode_image_to_base64(file)
    prompt = _build_vision_prompt(b64_img)
    raw_response = _call_openai_vision(prompt, api_key)
    return _clean_and_parse_response(raw_response)


def _encode_image_to_base64(file) -> str:
    """Convert image file to base64-encoded PNG string."""
    image = Image.open(file).convert("RGB")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return b64encode(buffer.getvalue()).decode("utf-8")


def _build_vision_prompt(b64_img: str) -> list:
    """Construct a vision-compatible prompt for GPT-4o."""
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Return raw JSON with structure: {name: {type: 'pie' | 'ticker', value: float}}. "
                        "A 'pie' contains multiple stocks and is often labeled like a folder. "
                        "Use 'pie' for any container or category of tickers. "
                        "Use 'ticker' only for individual tradable securities. "
                        "Do not include markdown or extra explanation—JSON only."
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64_img}"},
                },
            ],
        }
    ]


def _call_openai_vision(messages: list, api_key: str) -> str:
    """Make a call to OpenAI GPT-4o with image+prompt and return raw response."""
    openai.api_key = api_key
    resp = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=500,
    )
    return resp.choices[0].message.content.strip()


def _clean_and_parse_response(raw: str) -> dict:
    """Remove code block formatting and parse JSON."""
    cleaned = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding failed: {e}")
        raise ValueError("Failed to parse JSON from GPT response") from e


def handle_image_upload(
    img_file, reparse, portfolio, portfolio_file, data_dir, api_key
):
    """
    Handle full image upload lifecycle: hashing, parsing, updating, persisting.

    :param img_file: Uploaded image file
    :param reparse: Force reprocessing of cached image
    :param portfolio: Current in-memory portfolio dict
    :param portfolio_file: Portfolio filename
    :param data_dir: Storage directory for JSON
    :param api_key: OpenAI API key
    """
    current_hash = _get_image_hash(img_file)

    if st.session_state.get("current_image_hash") != current_hash:
        st.session_state["image_processed"] = False
        st.session_state["current_image_hash"] = current_hash

    _show_uploaded_image(img_file)

    if "parsed_images" not in st.session_state:
        st.session_state["parsed_images"] = {}

    try:
        parsed = _parse_and_cache_image(img_file, current_hash, api_key, reparse)
    except Exception as e:
        logger.error(f"Failed to parse image: {e}")
        st.error("Failed to extract portfolio structure from image.")
        return

    if parsed and not st.session_state.get("image_processed"):
        _apply_parsed_to_portfolio(portfolio, parsed, portfolio_file, data_dir)


def _get_image_hash(file) -> str:
    """Hash the uploaded file using SHA-256."""
    file.seek(0)
    return file_hash(file)


def _show_uploaded_image(file):
    """Render the uploaded image to the Streamlit UI."""
    image = Image.open(file)
    st.image(image, caption="Uploaded Image", use_container_width=True)


def _parse_and_cache_image(file, current_hash, api_key, reparse=False) -> dict:
    """
    Parse image using OpenAI if not cached. Store and validate result.

    :param file: Image file
    :param current_hash: SHA-256 hash for caching
    :param api_key: OpenAI API key
    :param reparse: Whether to force re-parse
    :return: Parsed slice dict
    """
    if reparse or current_hash not in st.session_state["parsed_images"]:
        file.seek(0)
        parsed = extract_hybrid_slices_from_image(file, api_key)
        if not isinstance(parsed, dict) or not all(
            isinstance(v, dict) and "type" in v and "value" in v
            for v in parsed.values()
        ):
            raise ValueError("Parsed structure is invalid")
        st.session_state["parsed_images"][current_hash] = parsed
        if reparse:
            st.session_state["image_processed"] = False
        logger.info(f"Parsed slices (new): {parsed}")
    else:
        parsed = st.session_state["parsed_images"][current_hash]
        logger.info(f"Parsed slices (cached): {parsed}")
    return parsed


def _apply_parsed_to_portfolio(portfolio, parsed, portfolio_file, data_dir):
    """
    Update the current portfolio with parsed data and persist it.

    :param portfolio: Current portfolio dict
    :param parsed: Parsed JSON children
    :param portfolio_file: Portfolio file name
    :param data_dir: Directory for file save
    """
    save_path = os.path.join(data_dir, portfolio_file)
    if not os.path.exists(save_path):
        logger.warning(f"Portfolio file missing: {portfolio_file}")
        st.warning("Portfolio file not found. Please create or reload the portfolio.")
        return
    updated = update_children(portfolio, {parsed})
    save_portfolio(updated, save_path)
    st.session_state["portfolio"] = normalize_portfolio(updated)
    st.session_state["image_processed"] = True
    st.success(f"Added/updated {len(parsed)} slices.")
    st.rerun()
