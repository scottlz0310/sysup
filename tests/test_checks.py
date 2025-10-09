"""システムチェック機能のテスト"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from sysup.core.checks import SystemChecker
from sysup.core.logging import SysupLogger


@pytest.fixture
def mock_logger():
    """モックロガーを作成するフィクスチャ"""
    logger = MagicMock(spec=SysupLogger)
    return logger


@pytest.fixture
def system_checker(mock_logger):
    """SystemCheckerインスタンスを作成するフィクスチャ"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir)
        checker = SystemChecker(mock_logger, cache_dir)
        yield checker


def test_system_checker_initialization(mock_logger):
    """SystemCheckerの初期化テスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "cache"
        checker = SystemChecker(mock_logger, cache_dir)

        assert checker.logger == mock_logger
        assert checker.cache_dir == cache_dir
        assert cache_dir.exists()


def test_check_disk_space_sufficient(system_checker):
    """十分なディスク容量がある場合のテスト"""
    with patch("shutil.disk_usage") as mock_disk_usage:
        # 10GB available
        mock_disk_usage.return_value = (100 * 1024**3, 50 * 1024**3, 10 * 1024**3)

        result = system_checker.check_disk_space(min_space_gb=1.0)

        assert result is True
        system_checker.logger.info.assert_called()


def test_check_disk_space_insufficient(system_checker):
    """ディスク容量が不足している場合のテスト"""
    with patch("shutil.disk_usage") as mock_disk_usage:
        # 0.5GB available
        mock_disk_usage.return_value = (100 * 1024**3, 99 * 1024**3, 0.5 * 1024**3)

        result = system_checker.check_disk_space(min_space_gb=1.0)

        assert result is False
        system_checker.logger.warning.assert_called()


def test_check_disk_space_error(system_checker):
    """ディスク容量チェックでエラーが発生した場合のテスト"""
    with patch("shutil.disk_usage") as mock_disk_usage:
        mock_disk_usage.side_effect = Exception("Disk error")

        result = system_checker.check_disk_space()

        assert result is False
        system_checker.logger.error.assert_called()


def test_check_network_success(system_checker):
    """ネットワーク接続が正常な場合のテスト"""
    with patch("subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = system_checker.check_network()

        assert result is True
        system_checker.logger.info.assert_called_with("ネットワーク接続: OK")


def test_check_network_failure(system_checker):
    """ネットワーク接続に問題がある場合のテスト"""
    with patch("subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = system_checker.check_network()

        assert result is False
        system_checker.logger.warning.assert_called()


def test_check_network_timeout(system_checker):
    """ネットワーク接続がタイムアウトする場合のテスト"""
    import subprocess

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired("ping", 5)

        result = system_checker.check_network()

        assert result is False


def test_check_daily_run_first_time(system_checker):
    """日次実行チェック - 初回実行のテスト"""
    result = system_checker.check_daily_run()

    assert result is True
    lock_file = system_checker.cache_dir / "daily_run"
    assert lock_file.exists()


def test_check_daily_run_already_run(system_checker):
    """日次実行チェック - 既に実行済みの場合のテスト"""
    from datetime import date

    lock_file = system_checker.cache_dir / "daily_run"
    lock_file.write_text(date.today().isoformat())

    result = system_checker.check_daily_run()

    assert result is False
    system_checker.logger.info.assert_called()


def test_check_daily_run_different_day(system_checker):
    """日次実行チェック - 別の日付の場合のテスト"""
    lock_file = system_checker.cache_dir / "daily_run"
    lock_file.write_text("2020-01-01")

    result = system_checker.check_daily_run()

    assert result is True
    assert lock_file.read_text().strip() != "2020-01-01"


def test_check_daily_run_corrupted_file(system_checker):
    """日次実行チェック - 破損したファイルがある場合のテスト"""
    lock_file = system_checker.cache_dir / "daily_run"
    lock_file.write_text("corrupted data")

    result = system_checker.check_daily_run()

    assert result is True


def test_check_reboot_required_true():
    """再起動が必要な場合のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_logger = MagicMock(spec=SysupLogger)
        checker = SystemChecker(mock_logger, Path(tmpdir))

        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.side_effect = lambda: True

            result = checker.check_reboot_required()

            assert result is True
            mock_logger.warning.assert_called()


def test_check_reboot_required_false():
    """再起動が不要な場合のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_logger = MagicMock(spec=SysupLogger)
        checker = SystemChecker(mock_logger, Path(tmpdir))

        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False

            result = checker.check_reboot_required()

            assert result is False


def test_check_reboot_required_with_packages():
    """再起動が必要でパッケージリストがある場合のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_logger = MagicMock(spec=SysupLogger)
        checker = SystemChecker(mock_logger, Path(tmpdir))

        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True

            with patch("pathlib.Path.read_text") as mock_read:
                mock_read.return_value = "package1\npackage2\npackage3"

                result = checker.check_reboot_required()

                assert result is True


def test_check_sudo_available_true(system_checker):
    """sudo権限が利用可能な場合のテスト"""
    with patch("subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = system_checker.check_sudo_available()

        assert result is True


def test_check_sudo_available_false(system_checker):
    """sudo権限が利用不可な場合のテスト"""
    with patch("subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = system_checker.check_sudo_available()

        assert result is False
        system_checker.logger.warning.assert_called()


def test_check_sudo_available_exception(system_checker):
    """sudo権限チェックで例外が発生した場合のテスト"""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = Exception("Subprocess error")

        result = system_checker.check_sudo_available()

        assert result is False


def test_check_process_lock_first_run(system_checker):
    """プロセスロック - 初回実行のテスト"""
    result = system_checker.check_process_lock()

    assert result is True
    lock_file = system_checker.cache_dir / "sysup.lock"
    pid_file = system_checker.cache_dir / "sysup.pid"
    assert lock_file.exists()
    assert pid_file.exists()
    assert pid_file.read_text().strip() == str(os.getpid())


def test_check_process_lock_already_running(system_checker):
    """プロセスロック - 既に実行中の場合のテスト"""
    lock_file = system_checker.cache_dir / "sysup.lock"
    pid_file = system_checker.cache_dir / "sysup.pid"

    # 現在のプロセスIDを書き込む（生きているプロセス）
    current_pid = os.getpid()
    pid_file.write_text(str(current_pid))
    lock_file.touch()

    with patch("os.kill") as mock_kill:
        # プロセスが生きていることを示す（例外を投げない）
        mock_kill.return_value = None

        result = system_checker.check_process_lock()

        assert result is False
        system_checker.logger.error.assert_called()


def test_check_process_lock_stale_lock(system_checker):
    """プロセスロック - 古いロックファイルがある場合のテスト"""
    lock_file = system_checker.cache_dir / "sysup.lock"
    pid_file = system_checker.cache_dir / "sysup.pid"

    # 存在しないプロセスIDを書き込む
    pid_file.write_text("999999")
    lock_file.touch()

    with patch("os.kill") as mock_kill:
        # プロセスが存在しないことを示す（OSErrorを投げる）
        mock_kill.side_effect = OSError("No such process")

        result = system_checker.check_process_lock()

        assert result is True
        # 新しいロックファイルが作成されている
        assert lock_file.exists()
        assert pid_file.read_text().strip() == str(os.getpid())


def test_check_process_lock_invalid_pid(system_checker):
    """プロセスロック - 無効なPIDファイルがある場合のテスト"""
    lock_file = system_checker.cache_dir / "sysup.lock"
    pid_file = system_checker.cache_dir / "sysup.pid"

    # 無効なPIDを書き込む
    pid_file.write_text("invalid")
    lock_file.touch()

    result = system_checker.check_process_lock()

    assert result is True


def test_cleanup_lock(system_checker):
    """ロックファイルのクリーンアップテスト"""
    lock_file = system_checker.cache_dir / "sysup.lock"
    pid_file = system_checker.cache_dir / "sysup.pid"

    # ロックファイルを作成
    lock_file.touch()
    pid_file.write_text("12345")

    system_checker.cleanup_lock()

    assert not lock_file.exists()
    assert not pid_file.exists()


def test_cleanup_lock_no_files(system_checker):
    """ロックファイルが存在しない場合のクリーンアップテスト"""
    # ファイルが存在しない状態でもエラーが発生しないこと
    system_checker.cleanup_lock()

    lock_file = system_checker.cache_dir / "sysup.lock"
    pid_file = system_checker.cache_dir / "sysup.pid"
    assert not lock_file.exists()
    assert not pid_file.exists()
