import pytest
import json
import zlib
import base64

from scripts.cookie_account import save_account_to_cookie, load_account_from_cookie
from scripts.account import create_empty_account


@pytest.fixture
def sample_account():
    return {"type": "account", "portfolios": {"foo": {"type": "pie", "value": 100}}}


def test_save_account_to_cookie_success(mocker, sample_account):
    mock_set = mocker.patch("scripts.cookie_account.set_cookie")
    save_account_to_cookie(sample_account)
    mock_set.assert_called_once()


def test_save_account_oversize(mocker):
    big_account = {"portfolios": {"x": "a" * 10000}}
    mock_set = mocker.patch("scripts.cookie_account.set_cookie")
    save_account_to_cookie(big_account)
    mock_set.assert_not_called()


def test_load_account_success(mocker, sample_account):
    encoded = base64.b64encode(
        zlib.compress(json.dumps(sample_account).encode())
    ).decode()
    mocker.patch("scripts.cookie_account.get_cookie", return_value=encoded)
    result = load_account_from_cookie()
    assert result == sample_account


def test_load_account_missing_cookie(mocker):
    mocker.patch("scripts.cookie_account.get_cookie", return_value=None)
    result = load_account_from_cookie()
    assert result == create_empty_account()


def test_load_account_corrupt_cookie(mocker):
    mocker.patch("scripts.cookie_account.get_cookie", return_value="not-valid-base64")
    result = load_account_from_cookie()
    assert result == create_empty_account()
