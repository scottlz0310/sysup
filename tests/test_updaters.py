"""個別Updaterのテスト（apt, brew, uv）"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from sysup.core.logging import SysupLogger
from sysup.updaters.apt import AptUpdater
from sysup.updaters.brew import BrewUpdater
from sysup.updaters.firmware import FirmwareUpdater
from sysup.updaters.flatpak import FlatpakUpdater
from sysup.updaters.snap import SnapUpdater
from sysup.updaters.uv import UvUpdater


@pytest.fixture
def mock_logger():
    """モックロガーを作成するフィクスチャ"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        yield logger
        logger.close()


# ======================
# APT Updater Tests
# ======================


def test_apt_get_name(mock_logger):
    """APTUpdater - get_nameのテスト"""
    updater = AptUpdater(mock_logger)
    assert updater.get_name() == "APT"


@patch("sysup.updaters.apt.is_windows")
def test_apt_is_available_true(mock_is_windows, mock_logger):
    """APTUpdater - is_available (利用可能)のテスト"""
    mock_is_windows.return_value = False
    updater = AptUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=True):
        assert updater.is_available() is True


def test_apt_is_available_false(mock_logger):
    """APTUpdater - is_available (利用不可)のテスト"""
    updater = AptUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=False):
        assert updater.is_available() is False


@patch("sysup.updaters.apt.is_windows")
def test_apt_is_available_on_windows(mock_is_windows, mock_logger):
    """APTUpdater - Windows環境で無効化されることを確認"""
    mock_is_windows.return_value = True
    updater = AptUpdater(mock_logger)
    assert updater.is_available() is False


def test_apt_check_updates(mock_logger):
    """APTUpdater - check_updatesのテスト"""
    updater = AptUpdater(mock_logger)

    with patch.object(updater, "run_command") as mock_run:
        mock_result = Mock()
        mock_result.stdout = "Listing...\npackage1\npackage2\npackage3\n"
        mock_run.return_value = mock_result

        count = updater.check_updates()
        assert count == 3


def test_apt_check_updates_none(mock_logger):
    """APTUpdater - check_updates (更新なし)のテスト"""
    updater = AptUpdater(mock_logger)

    with patch.object(updater, "run_command") as mock_run:
        mock_result = Mock()
        mock_result.stdout = "Listing...\n"
        mock_run.return_value = mock_result

        count = updater.check_updates()
        assert count == 0


def test_apt_check_updates_exception(mock_logger):
    """APTUpdater - check_updates (例外発生)のテスト"""
    updater = AptUpdater(mock_logger)

    with patch.object(updater, "run_command") as mock_run:
        mock_run.side_effect = Exception("Error")

        count = updater.check_updates()
        assert count is None


def test_apt_perform_update_success(mock_logger):
    """APTUpdater - perform_update (成功)のテスト"""
    updater = AptUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "check_updates", return_value=2):
            with patch.object(updater, "run_command") as mock_run:
                mock_result = Mock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = updater.perform_update()
                assert result is True


def test_apt_perform_update_not_available(mock_logger):
    """APTUpdater - perform_update (利用不可)のテスト"""
    updater = AptUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=False):
        result = updater.perform_update()
        assert result is True


def test_apt_perform_update_no_upgrades(mock_logger):
    """APTUpdater - perform_update (更新なし)のテスト"""
    updater = AptUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "check_updates", return_value=0):
            with patch.object(updater, "run_command") as mock_run:
                mock_result = Mock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = updater.perform_update()
                assert result is True


def test_apt_perform_update_error(mock_logger):
    """APTUpdater - perform_update (エラー)のテスト"""
    updater = AptUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "run_command") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, ["apt"])

            result = updater.perform_update()
            assert result is False


# ======================
# Brew Updater Tests
# ======================


def test_brew_get_name(mock_logger):
    """BrewUpdater - get_nameのテスト"""
    updater = BrewUpdater(mock_logger)
    assert updater.get_name() == "Homebrew"


def test_brew_is_available_true(mock_logger):
    """BrewUpdater - is_available (利用可能)のテスト"""
    updater = BrewUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=True):
        assert updater.is_available() is True


def test_brew_is_available_false(mock_logger):
    """BrewUpdater - is_available (利用不可)のテスト"""
    updater = BrewUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=False):
        assert updater.is_available() is False


def test_brew_check_updates(mock_logger):
    """BrewUpdater - check_updatesのテスト"""
    updater = BrewUpdater(mock_logger)

    with patch.object(updater, "run_command") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "package1\npackage2\npackage3\n"
        mock_run.return_value = mock_result

        count = updater.check_updates()
        assert count == 3


def test_brew_check_updates_none(mock_logger):
    """BrewUpdater - check_updates (更新なし)のテスト"""
    updater = BrewUpdater(mock_logger)

    with patch.object(updater, "run_command") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        count = updater.check_updates()
        assert count == 0


def test_brew_check_updates_error(mock_logger):
    """BrewUpdater - check_updates (エラー)のテスト"""
    updater = BrewUpdater(mock_logger)

    with patch.object(updater, "run_command") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        count = updater.check_updates()
        assert count is None


def test_brew_check_updates_exception(mock_logger):
    """BrewUpdater - check_updates (例外発生)のテスト"""
    updater = BrewUpdater(mock_logger)

    with patch.object(updater, "run_command") as mock_run:
        mock_run.side_effect = Exception("Error")

        count = updater.check_updates()
        assert count is None


def test_brew_perform_update_success(mock_logger):
    """BrewUpdater - perform_update (成功)のテスト"""
    updater = BrewUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "check_updates", return_value=2):
            with patch.object(updater, "run_command") as mock_run:
                mock_result = Mock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = updater.perform_update()
                assert result is True


def test_brew_perform_update_not_available(mock_logger):
    """BrewUpdater - perform_update (利用不可)のテスト"""
    updater = BrewUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=False):
        result = updater.perform_update()
        assert result is True


def test_brew_perform_update_no_upgrades(mock_logger):
    """BrewUpdater - perform_update (更新なし)のテスト"""
    updater = BrewUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "check_updates", return_value=0):
            with patch.object(updater, "run_command") as mock_run:
                mock_result = Mock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = updater.perform_update()
                assert result is True


def test_brew_perform_update_error(mock_logger):
    """BrewUpdater - perform_update (エラー)のテスト"""
    updater = BrewUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "run_command") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, ["brew"])

            result = updater.perform_update()
            assert result is False


# ======================
# Uv Updater Tests
# ======================


def test_uv_get_name(mock_logger):
    """UvUpdater - get_nameのテスト"""
    updater = UvUpdater(mock_logger)
    assert updater.get_name() == "uv tool"


def test_uv_is_available_true(mock_logger):
    """UvUpdater - is_available (利用可能)のテスト"""
    updater = UvUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=True):
        assert updater.is_available() is True


def test_uv_is_available_false(mock_logger):
    """UvUpdater - is_available (利用不可)のテスト"""
    updater = UvUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=False):
        assert updater.is_available() is False


def test_uv_self_update_success(mock_logger):
    """UvUpdater - _self_update (成功)のテスト"""
    updater = UvUpdater(mock_logger)

    with patch.object(updater, "run_command") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = updater._self_update()
        assert result is True
        mock_run.assert_called_once_with(["uv", "self", "update"])


def test_uv_self_update_not_standalone(mock_logger):
    """UvUpdater - _self_update (standalone以外でインストール)のテスト"""
    updater = UvUpdater(mock_logger)

    with patch.object(updater, "run_command") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, ["uv", "self", "update"])

        # standalone以外でも継続可能（Trueを返す）
        result = updater._self_update()
        assert result is True


def test_uv_self_update_exception(mock_logger):
    """UvUpdater - _self_update (例外発生)のテスト"""
    updater = UvUpdater(mock_logger)

    with patch.object(updater, "run_command") as mock_run:
        mock_run.side_effect = Exception("Unexpected error")

        # 例外でも継続可能（Trueを返す）
        result = updater._self_update()
        assert result is True


def test_uv_perform_update_success(mock_logger):
    """UvUpdater - perform_update (成功)のテスト"""
    updater = UvUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "_self_update", return_value=True):
            with patch.object(updater, "run_command") as mock_run:
                mock_result = Mock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = updater.perform_update()
                assert result is True


def test_uv_perform_update_not_available(mock_logger):
    """UvUpdater - perform_update (利用不可)のテスト"""
    updater = UvUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=False):
        result = updater.perform_update()
        assert result is True


def test_uv_perform_update_error(mock_logger):
    """UvUpdater - perform_update (エラー)のテスト"""
    updater = UvUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "_self_update", return_value=True):
            with patch.object(updater, "run_command") as mock_run:
                mock_run.side_effect = subprocess.CalledProcessError(1, ["uv"])

                result = updater.perform_update()
                assert result is False


def test_uv_perform_update_exception(mock_logger):
    """UvUpdater - perform_update (例外発生)のテスト"""
    updater = UvUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "_self_update", return_value=True):
            with patch.object(updater, "run_command") as mock_run:
                mock_run.side_effect = Exception("Unexpected error")

                result = updater.perform_update()
                assert result is False


def test_uv_perform_update_calls_self_update_first(mock_logger):
    """UvUpdater - perform_updateがself_updateを先に呼ぶことを確認"""
    updater = UvUpdater(mock_logger)
    call_order = []

    def track_self_update():
        call_order.append("self_update")
        return True

    def track_run_command(cmd):
        call_order.append(f"run_command:{cmd}")
        mock_result = Mock()
        mock_result.returncode = 0
        return mock_result

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "_self_update", side_effect=track_self_update):
            with patch.object(updater, "run_command", side_effect=track_run_command):
                result = updater.perform_update()
                assert result is True
                assert call_order[0] == "self_update"
                assert "run_command:['uv', 'tool', 'upgrade', '--all']" in call_order[1]


# ======================
# Linux専用Updater Windows無効化テスト
# ======================


@patch("sysup.updaters.snap.is_windows")
def test_snap_is_available_on_windows(mock_is_windows, mock_logger):
    """SnapUpdater - Windows環境で無効化されることを確認"""
    mock_is_windows.return_value = True
    updater = SnapUpdater(mock_logger)
    assert updater.is_available() is False


@patch("sysup.updaters.flatpak.is_windows")
def test_flatpak_is_available_on_windows(mock_is_windows, mock_logger):
    """FlatpakUpdater - Windows環境で無効化されることを確認"""
    mock_is_windows.return_value = True
    updater = FlatpakUpdater(mock_logger)
    assert updater.is_available() is False


@patch("sysup.updaters.firmware.is_windows")
def test_firmware_is_available_on_windows(mock_is_windows, mock_logger):
    """FirmwareUpdater - Windows環境で無効化されることを確認"""
    mock_is_windows.return_value = True
    updater = FirmwareUpdater(mock_logger)
    assert updater.is_available() is False
