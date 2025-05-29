"""Utility functions for decimal handling and formatting.

Provides conversion helpers to ensure numerical consistency.
"""

from decimal import Decimal, ROUND_HALF_UP


def to_decimal(value: float) -> Decimal:
    """
    Convert float to Decimal with rounding to two decimal places.

    :param value: Input float value.
    :return: Rounded Decimal value.
    """
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
