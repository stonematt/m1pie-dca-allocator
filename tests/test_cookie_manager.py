from scripts.cookie_manager import get_cookie, set_cookie


def test_get_cookie_returns_value(mocker):
    mock_mgr = mocker.patch("scripts.cookie_manager.get_cookie_manager")
    mock_mgr.return_value.get_all.return_value = {"test": "abc"}
    assert get_cookie("test") == "abc"


def test_get_cookie_missing_key(mocker):
    mock_mgr = mocker.patch("scripts.cookie_manager.get_cookie_manager")
    mock_mgr.return_value.get_all.return_value = {}
    assert get_cookie("missing") is None


def test_set_cookie_calls_manager(mocker):
    mock_mgr = mocker.patch("scripts.cookie_manager.get_cookie_manager")
    manager = mock_mgr.return_value
    set_cookie("foo", "bar")
    manager.set.assert_called_once_with("foo", "bar")
