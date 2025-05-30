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
from PIL import Image

from scripts.log_util import app_logger

logger = app_logger(__name__)


def extract_hybrid_slices_from_image(file, api_key: str) -> dict:
    """
    Parse an M1 pie screenshot with mixed pies and tickers using GPT-4o Vision.

    :param file: File-like object from Streamlit uploader.
    :param api_key: OpenAI API key.
    :return: Dictionary of {slice_name: {type: "ticker" | "pie", value: float}}
    """
    logger.info(f"[{datetime.now().isoformat()}] Parsing hybrid pie from uploaded file")

    b64_img = _encode_image_to_base64(file)
    prompt = _build_vision_prompt(b64_img)

    raw_response = _call_openai_vision(prompt, api_key)
    return _clean_and_parse_response(raw_response)


def _encode_image_to_base64(file) -> str:
    image = Image.open(file).convert("RGB")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return b64encode(buffer.getvalue()).decode("utf-8")


def _build_vision_prompt(b64_img: str) -> list:
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
    openai.api_key = api_key
    resp = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=500,
    )
    return resp.choices[0].message.content.strip()


def _clean_and_parse_response(raw: str) -> dict:
    cleaned = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding failed: {e}")
        raise ValueError("Failed to parse JSON from GPT response") from e
