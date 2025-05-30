"""Utility functions for decimal handling and formatting.

Provides conversion helpers to ensure numerical consistency.
"""

import hashlib
from decimal import ROUND_HALF_UP, Decimal
from typing import BinaryIO


def to_decimal(value: float) -> Decimal:
    """
    Convert float to Decimal with rounding to two decimal places.

    :param value: Input float value.
    :return: Rounded Decimal value.
    """
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def file_hash(file: BinaryIO) -> str:
    """Generate SHA-256 hash for a file-like object."""
    return hashlib.sha256(file.read()).hexdigest()
