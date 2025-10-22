"""プラットフォーム検出機能のテスト。"""

import platform
from unittest.mock import patch

from sysup.core.platform import get_platform, is_unix, is_windows


def test_is_windows_on_windows():
    """Windows環境でis_windows()がTrueを返すことを確認。"""
    with patch("platform.system", return_value="Windows"):
        assert is_windows() is True


def test_is_windows_on_linux():
    """Linux環境でis_windows()がFalseを返すことを確認。"""
    with patch("platform.system", return_value="Linux"):
        assert is_windows() is False


def test_is_unix_on_linux():
    """Linux環境でis_unix()がTrueを返すことを確認。"""
    with patch("platform.system", return_value="Linux"):
        assert is_unix() is True


def test_is_unix_on_darwin():
    """macOS環境でis_unix()がTrueを返すことを確認。"""
    with patch("platform.system", return_value="Darwin"):
        assert is_unix() is True


def test_is_unix_on_windows():
    """Windows環境でis_unix()がFalseを返すことを確認。"""
    with patch("platform.system", return_value="Windows"):
        assert is_unix() is False


def test_get_platform():
    """get_platform()が正しいプラットフォーム名を返すことを確認。"""
    actual_platform = platform.system()
    assert get_platform() == actual_platform
