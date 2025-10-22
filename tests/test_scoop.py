"""Scoop updaterのテスト。"""

from unittest.mock import MagicMock, patch

import pytest

from sysup.core.logging import SysupLogger
from sysup.updaters.scoop import ScoopUpdater


@pytest.fixture
def logger():
    """テスト用ロガー。"""
    return MagicMock(spec=SysupLogger)


@pytest.fixture
def updater(logger):
    """テスト用Scoop updater。"""
    return ScoopUpdater(logger, dry_run=False)


def test_get_name(updater):
    """updater名が正しいことを確認。"""
    assert updater.get_name() == "Scoop"


@patch("sysup.updaters.scoop.is_windows")
def test_is_available_on_windows_with_scoop(mock_is_windows, updater):
    """Windows環境でscoopがある場合にTrueを返すことを確認。"""
    mock_is_windows.return_value = True
    with patch.object(updater, "command_exists", return_value=True):
        assert updater.is_available() is True


@patch("sysup.updaters.scoop.is_windows")
def test_is_available_on_windows_without_scoop(mock_is_windows, updater):
    """Windows環境でscoopがない場合にFalseを返すことを確認。"""
    mock_is_windows.return_value = True
    with patch.object(updater, "command_exists", return_value=False):
        assert updater.is_available() is False


@patch("sysup.updaters.scoop.is_windows")
def test_is_available_on_linux(mock_is_windows, updater):
    """Linux環境でFalseを返すことを確認。"""
    mock_is_windows.return_value = False
    assert updater.is_available() is False


def test_perform_update_not_available(updater, logger):
    """scoopが利用不可の場合にスキップすることを確認。"""
    with patch.object(updater, "is_available", return_value=False):
        assert updater.perform_update() is True
        logger.info.assert_called_once()


def test_perform_update_success(updater, logger):
    """正常に更新が完了することを確認。"""
    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "run_command") as mock_run:
            assert updater.perform_update() is True
            assert mock_run.call_count == 3
            logger.success.assert_called()


def test_perform_update_failure(updater, logger):
    """更新失敗時にFalseを返すことを確認。"""
    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "run_command", side_effect=Exception("Test error")):
            assert updater.perform_update() is False
            logger.error.assert_called()
