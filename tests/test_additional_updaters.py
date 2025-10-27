"""追加Updaterの基本テスト（cargo, npm, pipx, rustup, snap, flatpak, gem, firmware, nvm）"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from sysup.core.logging import SysupLogger
from sysup.updaters.cargo import CargoUpdater
from sysup.updaters.firmware import FirmwareUpdater
from sysup.updaters.flatpak import FlatpakUpdater
from sysup.updaters.gem import GemUpdater
from sysup.updaters.npm import NpmUpdater
from sysup.updaters.nvm import NvmUpdater
from sysup.updaters.pipx import PipxUpdater
from sysup.updaters.rustup import RustupUpdater
from sysup.updaters.snap import SnapUpdater


@pytest.fixture
def mock_logger():
    """モックロガーを作成するフィクスチャ"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        yield logger
        logger.close()


# ======================
# Cargo Updater Tests
# ======================


def test_cargo_get_name(mock_logger):
    """CargoUpdater - get_nameのテスト"""
    updater = CargoUpdater(mock_logger)
    assert updater.get_name() == "Cargo"


def test_cargo_is_available(mock_logger):
    """CargoUpdater - is_availableのテスト"""
    updater = CargoUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=True):
        assert updater.is_available() is True


def test_cargo_perform_update(mock_logger):
    """CargoUpdater - perform_updateのテスト"""
    updater = CargoUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "run_command") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = updater.perform_update()
            assert result is True


# ======================
# Npm Updater Tests
# ======================


def test_npm_get_name(mock_logger):
    """NpmUpdater - get_nameのテスト"""
    updater = NpmUpdater(mock_logger)
    assert updater.get_name() == "npm"


def test_npm_is_available(mock_logger):
    """NpmUpdater - is_availableのテスト"""
    updater = NpmUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=True):
        assert updater.is_available() is True


def test_npm_perform_update(mock_logger):
    """NpmUpdater - perform_updateのテスト"""
    updater = NpmUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "run_command") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = updater.perform_update()
            assert result is True


# ======================
# Pipx Updater Tests
# ======================


def test_pipx_get_name(mock_logger):
    """PipxUpdater - get_nameのテスト"""
    updater = PipxUpdater(mock_logger)
    assert updater.get_name() == "pipx"


def test_pipx_is_available(mock_logger):
    """PipxUpdater - is_availableのテスト"""
    updater = PipxUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=True):
        assert updater.is_available() is True


def test_pipx_perform_update(mock_logger):
    """PipxUpdater - perform_updateのテスト"""
    updater = PipxUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "run_command") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = updater.perform_update()
            assert result is True


# ======================
# Rustup Updater Tests
# ======================


def test_rustup_get_name(mock_logger):
    """RustupUpdater - get_nameのテスト"""
    updater = RustupUpdater(mock_logger)
    assert updater.get_name() == "Rustup"


def test_rustup_is_available(mock_logger):
    """RustupUpdater - is_availableのテスト"""
    updater = RustupUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=True):
        assert updater.is_available() is True


def test_rustup_perform_update(mock_logger):
    """RustupUpdater - perform_updateのテスト"""
    updater = RustupUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "run_command") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = updater.perform_update()
            assert result is True


# ======================
# Snap Updater Tests
# ======================


def test_snap_get_name(mock_logger):
    """SnapUpdater - get_nameのテスト"""
    updater = SnapUpdater(mock_logger)
    assert updater.get_name() == "Snap"


@patch("sysup.updaters.snap.is_windows")
def test_snap_is_available(mock_is_windows, mock_logger):
    """SnapUpdater - is_availableのテスト"""
    mock_is_windows.return_value = False
    updater = SnapUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=True):
        assert updater.is_available() is True


def test_snap_perform_update(mock_logger):
    """SnapUpdater - perform_updateのテスト"""
    updater = SnapUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "run_command") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = updater.perform_update()
            assert result is True


# ======================
# Flatpak Updater Tests
# ======================


def test_flatpak_get_name(mock_logger):
    """FlatpakUpdater - get_nameのテスト"""
    updater = FlatpakUpdater(mock_logger)
    assert updater.get_name() == "Flatpak"


@patch("sysup.updaters.flatpak.is_windows")
def test_flatpak_is_available(mock_is_windows, mock_logger):
    """FlatpakUpdater - is_availableのテスト"""
    mock_is_windows.return_value = False
    updater = FlatpakUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=True):
        assert updater.is_available() is True


def test_flatpak_perform_update(mock_logger):
    """FlatpakUpdater - perform_updateのテスト"""
    updater = FlatpakUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "run_command") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = updater.perform_update()
            assert result is True


# ======================
# Gem Updater Tests
# ======================


def test_gem_get_name(mock_logger):
    """GemUpdater - get_nameのテスト"""
    updater = GemUpdater(mock_logger)
    assert updater.get_name() == "Gem"


def test_gem_is_available(mock_logger):
    """GemUpdater - is_availableのテスト"""
    updater = GemUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=True):
        assert updater.is_available() is True


def test_gem_perform_update(mock_logger):
    """GemUpdater - perform_updateのテスト"""
    updater = GemUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "run_command") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = updater.perform_update()
            assert result is True
            # 実際のWindows環境では gem.cmd が呼ばれる
            import platform
            expected_cmd = "gem.cmd" if platform.system() == "Windows" else "gem"
            mock_run.assert_called_once_with([expected_cmd, "update"])


# ======================
# Firmware Updater Tests
# ======================


def test_firmware_get_name(mock_logger):
    """FirmwareUpdater - get_nameのテスト"""
    updater = FirmwareUpdater(mock_logger)
    assert updater.get_name() == "Firmware"


@patch("sysup.updaters.firmware.is_windows")
def test_firmware_is_available(mock_is_windows, mock_logger):
    """FirmwareUpdater - is_availableのテスト"""
    mock_is_windows.return_value = False
    updater = FirmwareUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=True):
        assert updater.is_available() is True


def test_firmware_perform_update(mock_logger):
    """FirmwareUpdater - perform_updateのテスト"""
    updater = FirmwareUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch.object(updater, "run_command") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = updater.perform_update()
            assert result is True


# ======================
# Nvm Updater Tests
# ======================


def test_nvm_get_name(mock_logger):
    """NvmUpdater - get_nameのテスト"""
    updater = NvmUpdater(mock_logger)
    assert updater.get_name() == "nvm"


def test_nvm_is_available(mock_logger):
    """NvmUpdater - is_availableのテスト"""
    updater = NvmUpdater(mock_logger)

    with patch("subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "nvm"
        mock_run.return_value = mock_result

        assert updater.is_available() is True


def test_nvm_perform_update(mock_logger):
    """NvmUpdater - perform_updateのテスト"""
    updater = NvmUpdater(mock_logger)

    with patch.object(updater, "is_available", return_value=True):
        with patch("subprocess.run") as mock_run:
            with patch("pathlib.Path.exists", return_value=True):
                mock_result = Mock()
                mock_result.returncode = 0
                mock_run.return_value = mock_result

                result = updater.perform_update()
                assert result is True


# ======================
# Not Available Tests
# ======================


def test_updater_not_available_returns_true(mock_logger):
    """Updater - 利用不可の場合Trueを返すテスト"""
    # 各updaterが利用不可の場合、perform_updateはTrueを返す（スキップ扱い）
    updaters = [
        CargoUpdater(mock_logger),
        NpmUpdater(mock_logger),
        PipxUpdater(mock_logger),
        RustupUpdater(mock_logger),
        SnapUpdater(mock_logger),
        FlatpakUpdater(mock_logger),
        GemUpdater(mock_logger),
        FirmwareUpdater(mock_logger),
    ]

    for updater in updaters:
        with patch.object(updater, "is_available", return_value=False):
            result = updater.perform_update()
            assert result is True


# ======================
# Error Handling Tests
# ======================


def test_updater_error_handling(mock_logger):
    """Updater - エラーハンドリングのテスト"""
    updater = CargoUpdater(mock_logger)

    with patch.object(updater, "command_exists", return_value=True):
        with patch.object(updater, "run_command") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, ["cargo"])

            result = updater.perform_update()
            assert result is False
