from decimal import Decimal
from io import BytesIO

from scripts.utils import file_hash, to_decimal


def test_to_decimal_rounds_correctly():
    assert to_decimal(3.14159) == Decimal("3.14")
    assert to_decimal(2.999) == Decimal("3.00")


def test_file_hash_is_stable():
    content = BytesIO(b"example content")
    hash1 = file_hash(content)

    content.seek(0)
    hash2 = file_hash(content)

    assert hash1 == hash2
