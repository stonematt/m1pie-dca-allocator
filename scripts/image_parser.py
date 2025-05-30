"""
image_parser.py: Extract hybrid pie structures from M1 screenshots using GPT-4o Vision.

Parses screenshots via the OpenAI Vision API and returns structured JSON identifying
tickers and sub-pies. Encodes uploaded files to base64 PNG format for transmission.
"""

import json
import re
from base64 import b64encode
from datetime import datetime
from io import BytesIO

import openai
import streamlit as st
from PIL import Image

from scripts.log_util import app_logger

openai.api_key = st.secrets["openai"]["api_key"]

logger = app_logger(__name__)


def extract_hybrid_slices_from_image(file) -> dict:
    """
    Parse an M1 pie screenshot with mixed pies and tickers using GPT-4o Vision.

    Args:
        file: File-like object from Streamlit uploader.

    Returns:
        Dictionary of {slice_name: {type: "ticker" | "pie", value: float}}
    """
    logger.info(f"[{datetime.now().isoformat()}] Parsing hybrid pie from uploaded file")

    # Ensure valid PNG encoding for OpenAI API
    image = Image.open(file).convert("RGB")
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    b64_img = b64encode(buffered.getvalue()).decode("utf-8")

    resp = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Return JSON with structure: "
                            "{name: {type: 'pie'|'ticker', value: float}}. "
                            "Detect tickers vs. sub-pies. No markdown or formatting."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64_img}"},
                    },
                ],
            }
        ],
        max_tokens=500,
    )

    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.error("Failed to parse hybrid pie JSON from GPT response")
        raise
