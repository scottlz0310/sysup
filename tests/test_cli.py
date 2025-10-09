"""CLI機能の基本テスト"""

import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from sysup.cli import main, setup_wsl_integration, show_available_updaters
from sysup.core.config import SysupConfig
from sysup.core.logging import SysupLogger


@contextmanager
def mock_sudo_updaters():
    """sudoが必要なUpdater（APT、Snap）のみモック化するコンテキストマネージャー."""
    mock_apt = MagicMock()
    mock_apt.is_available.return_value = False
    mock_apt.get_name.return_value = "APT"
    mock_apt.perform_update.return_value = True

    mock_snap = MagicMock()
    mock_snap.is_available.return_value = False
    mock_snap.get_name.return_value = "Snap"
    mock_snap.perform_update.return_value = True

    with patch("sysup.cli.AptUpdater", return_value=mock_apt):
        with patch("sysup.cli.SnapUpdater", return_value=mock_snap):
            yield (mock_apt, mock_snap)


def test_main_version():
    """CLI - バージョン表示のテスト"""
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])

    assert result.exit_code == 0
    assert "sysup" in result.output


def test_main_help():
    """CLI - ヘルプ表示のテスト"""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "システムと各種パッケージマネージャを統合的に更新" in result.output


def test_main_list_updaters():
    """CLI - updater一覧表示のテスト"""
    runner = CliRunner()

    with patch("sysup.cli.SystemChecker") as mock_checker:
        mock_checker_instance = MagicMock()
        mock_checker_instance.check_process_lock.return_value = True
        mock_checker.return_value = mock_checker_instance

        with mock_sudo_updaters():
            result = runner.invoke(main, ["--list"])

            # プロセスロックのクリーンアップは常に実行されるべき
            assert result.exit_code == 0


def test_main_config_load_error():
    """CLI - 設定ファイル読み込みエラーのテスト"""
    runner = CliRunner()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        # 不正なTOMLファイル
        f.write("invalid toml content [[[")
        config_file = Path(f.name)

    try:
        result = runner.invoke(main, ["--config", str(config_file)])

        assert result.exit_code == 1
        assert "設定ファイル読み込みエラー" in result.output
    finally:
        config_file.unlink()


def test_main_process_lock_failed():
    """CLI - プロセスロック失敗のテスト"""
    runner = CliRunner()

    with patch("sysup.cli.SysupConfig.load_config"):
        with patch("sysup.cli.SysupLogger"):
            with patch("sysup.cli.SystemChecker") as mock_checker:
                mock_checker_instance = MagicMock()
                mock_checker_instance.check_process_lock.return_value = False
                mock_checker.return_value = mock_checker_instance

                result = runner.invoke(main, [])

                assert result.exit_code == 1


def test_show_available_updaters():
    """show_available_updaters関数のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()

        # sudoが必要なupdaterをモック化
        with mock_sudo_updaters():
            # エラーが発生しないことを確認
            show_available_updaters(logger, config)


def test_setup_wsl_integration():
    """setup_wsl_integration関数のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()

        with patch("sysup.cli.WSLIntegration.is_wsl", return_value=False):
            # WSL環境でない場合の動作を確認
            setup_wsl_integration(logger, config)


def test_main_setup_wsl():
    """CLI - WSLセットアップのテスト"""
    runner = CliRunner()

    with patch("sysup.cli.SystemChecker") as mock_checker:
        mock_checker_instance = MagicMock()
        mock_checker_instance.check_process_lock.return_value = True
        mock_checker.return_value = mock_checker_instance

        with patch("sysup.cli.WSLIntegration.is_wsl", return_value=False):
            result = runner.invoke(main, ["--setup-wsl"])

            assert result.exit_code == 0


def test_main_dry_run():
    """CLI - ドライランモードのテスト"""
    runner = CliRunner()

    with patch("sysup.cli.SystemChecker") as mock_checker:
        with patch("sysup.cli.run_updates") as mock_run_updates:
            mock_checker_instance = MagicMock()
            mock_checker_instance.check_process_lock.return_value = True
            mock_checker.return_value = mock_checker_instance

            result = runner.invoke(main, ["--dry-run"])

            # ドライランモードが設定されたことを確認
            assert result.exit_code == 0
            mock_run_updates.assert_called_once()


def test_main_force_run():
    """CLI - 強制実行モードのテスト"""
    runner = CliRunner()

    with patch("sysup.cli.SystemChecker") as mock_checker:
        with patch("sysup.cli.run_updates") as mock_run_updates:
            mock_checker_instance = MagicMock()
            mock_checker_instance.check_process_lock.return_value = True
            mock_checker.return_value = mock_checker_instance

            result = runner.invoke(main, ["--force"])

            assert result.exit_code == 0
            mock_run_updates.assert_called_once()


def test_main_keyboard_interrupt():
    """CLI - キーボード割り込みのテスト"""
    runner = CliRunner()

    with patch("sysup.cli.SystemChecker") as mock_checker:
        with patch("sysup.cli.run_updates") as mock_run_updates:
            mock_checker_instance = MagicMock()
            mock_checker_instance.check_process_lock.return_value = True
            mock_checker.return_value = mock_checker_instance

            mock_run_updates.side_effect = KeyboardInterrupt()

            result = runner.invoke(main, [])

            assert result.exit_code == 1


def test_main_unexpected_exception():
    """CLI - 予期しないエラーのテスト"""
    runner = CliRunner()

    with patch("sysup.cli.SystemChecker") as mock_checker:
        with patch("sysup.cli.run_updates") as mock_run_updates:
            mock_checker_instance = MagicMock()
            mock_checker_instance.check_process_lock.return_value = True
            mock_checker.return_value = mock_checker_instance

            mock_run_updates.side_effect = Exception("Unexpected error")

            result = runner.invoke(main, [])

            assert result.exit_code == 1


def test_setup_wsl_integration_with_wsl():
    """setup_wsl_integration - WSL環境でのテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()

        with patch("sysup.cli.WSLIntegration.is_wsl", return_value=True):
            with patch("sysup.cli.WSLIntegration.get_shell_rc_file", return_value=Path("/home/user/.bashrc")):
                with patch("sysup.cli.WSLIntegration.is_auto_run_configured", return_value=False):
                    with patch("sysup.cli.WSLIntegration.setup_wsl_integration", return_value=(True, "Success")):
                        # プロンプトへの入力をシミュレート
                        with patch("click.prompt", return_value=1):
                            setup_wsl_integration(logger, config)


def test_setup_wsl_integration_already_configured():
    """setup_wsl_integration - 既に設定済みの場合のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()

        with patch("sysup.cli.WSLIntegration.is_wsl", return_value=True):
            with patch("sysup.cli.WSLIntegration.get_shell_rc_file", return_value=Path("/home/user/.bashrc")):
                with patch("sysup.cli.WSLIntegration.is_auto_run_configured", return_value=True):
                    with patch("sysup.cli.WSLIntegration.setup_wsl_integration", return_value=(True, "Disabled")):
                        with patch("click.confirm", return_value=True):
                            setup_wsl_integration(logger, config)


def test_setup_wsl_integration_cancel():
    """setup_wsl_integration - キャンセルのテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()

        with patch("sysup.cli.WSLIntegration.is_wsl", return_value=True):
            with patch("sysup.cli.WSLIntegration.get_shell_rc_file", return_value=Path("/home/user/.bashrc")):
                with patch("sysup.cli.WSLIntegration.is_auto_run_configured", return_value=False):
                    # キャンセルを選択
                    with patch("click.prompt", return_value=3):
                        setup_wsl_integration(logger, config)


def test_run_updates_basic():
    """run_updates - 基本的な更新実行のテスト"""
    from sysup.cli import run_updates

    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()
        checker = MagicMock()

        # システムチェックを全てパス
        checker.check_daily_run.return_value = True
        checker.check_disk_space.return_value = True
        checker.check_network.return_value = True
        checker.check_sudo_available.return_value = True
        checker.check_reboot_required.return_value = False

        # sudoが必要なupdaterのみモック化
        with mock_sudo_updaters():
            with patch("sysup.cli.Notifier.is_available", return_value=False):
                run_updates(logger, config, checker, auto_run=True, force=False)


def test_run_updates_with_backup():
    """run_updates - バックアップ有効時のテスト"""
    from sysup.cli import run_updates

    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()
        config.backup.enabled = True
        checker = MagicMock()

        checker.check_daily_run.return_value = True
        checker.check_disk_space.return_value = True
        checker.check_network.return_value = True
        checker.check_sudo_available.return_value = True
        checker.check_reboot_required.return_value = False

        with patch("sysup.cli.BackupManager") as mock_backup:
            mock_backup_instance = MagicMock()
            mock_backup_instance.create_backup.return_value = Path(tmpdir) / "backup.json"
            mock_backup_instance.cleanup_old_backups.return_value = 5
            mock_backup.return_value = mock_backup_instance

            with mock_sudo_updaters():
                with patch("sysup.cli.Notifier.is_available", return_value=False):
                    run_updates(logger, config, checker, auto_run=True, force=False)


def test_run_updates_daily_check_failed():
    """run_updates - 日次チェック失敗時のテスト"""
    from sysup.cli import run_updates

    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()
        checker = MagicMock()

        checker.check_daily_run.return_value = False
        checker.check_disk_space.return_value = True
        checker.check_network.return_value = True
        checker.check_sudo_available.return_value = True
        checker.check_reboot_required.return_value = False

        # auto_run=Trueでも処理が続行されるため、sudo必要なupdaterをモック化
        with mock_sudo_updaters():
            with patch("sysup.cli.Notifier.is_available", return_value=False):
                run_updates(logger, config, checker, auto_run=True, force=False)


def test_run_updates_disk_space_insufficient():
    """run_updates - ディスク容量不足時のテスト"""
    from sysup.cli import run_updates

    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()
        checker = MagicMock()

        checker.check_daily_run.return_value = True
        checker.check_disk_space.return_value = False

        # 自動実行モードでは早期リターンしない（警告のみ）
        checker.check_network.return_value = True
        checker.check_sudo_available.return_value = True
        checker.check_reboot_required.return_value = False

        with mock_sudo_updaters():
            with patch("sysup.cli.Notifier.is_available", return_value=False):
                run_updates(logger, config, checker, auto_run=True, force=False)


def test_run_updates_network_failed():
    """run_updates - ネットワーク接続失敗時のテスト"""
    from sysup.cli import run_updates

    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()
        checker = MagicMock()

        checker.check_daily_run.return_value = True
        checker.check_disk_space.return_value = True
        checker.check_network.return_value = False
        checker.check_sudo_available.return_value = True
        checker.check_reboot_required.return_value = False

        with mock_sudo_updaters():
            with patch("sysup.cli.Notifier.is_available", return_value=False):
                run_updates(logger, config, checker, auto_run=True, force=False)


def test_run_updates_sudo_not_available():
    """run_updates - sudo利用不可時のテスト"""
    from sysup.cli import run_updates

    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()
        checker = MagicMock()

        checker.check_daily_run.return_value = True
        checker.check_disk_space.return_value = True
        checker.check_network.return_value = True
        checker.check_sudo_available.return_value = False

        # 自動実行モードでsudo不可の場合は早期リターン
        run_updates(logger, config, checker, auto_run=True, force=False)


def test_run_updates_no_updaters():
    """run_updates - 有効なupdaterなし時のテスト"""
    from sysup.cli import run_updates

    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()
        # すべてのupdaterを無効化
        config.updaters = {
            "apt": False,
            "snap": False,
            "brew": False,
            "npm": False,
            "pipx": False,
            "uv": False,
            "rustup": False,
            "cargo": False,
            "flatpak": False,
            "gem": False,
            "nvm": False,
            "firmware": False,
        }
        checker = MagicMock()

        checker.check_daily_run.return_value = True
        checker.check_disk_space.return_value = True
        checker.check_network.return_value = True
        checker.check_sudo_available.return_value = True

        run_updates(logger, config, checker, auto_run=True, force=False)


def test_run_updates_parallel_mode():
    """run_updates - 並列更新モードのテスト"""
    from sysup.cli import run_updates

    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()
        config.general.parallel_updates = True
        checker = MagicMock()

        checker.check_daily_run.return_value = True
        checker.check_disk_space.return_value = True
        checker.check_network.return_value = True
        checker.check_sudo_available.return_value = True
        checker.check_reboot_required.return_value = False

        with mock_sudo_updaters():
            with patch("sysup.cli.Notifier.is_available", return_value=False):
                run_updates(logger, config, checker, auto_run=True, force=False)


def test_run_updates_reboot_required():
    """run_updates - 再起動が必要な場合のテスト"""
    from sysup.cli import run_updates

    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()
        checker = MagicMock()

        checker.check_daily_run.return_value = True
        checker.check_disk_space.return_value = True
        checker.check_network.return_value = True
        checker.check_sudo_available.return_value = True
        checker.check_reboot_required.return_value = True

        with mock_sudo_updaters():
            with patch("sysup.cli.Notifier.is_available", return_value=False):
                # 自動実行モードでは再起動プロンプトなし
                run_updates(logger, config, checker, auto_run=True, force=False)


def test_run_updates_updater_exception():
    """run_updates - updaterで例外発生時のテスト"""
    from sysup.cli import run_updates

    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        config = SysupConfig()
        checker = MagicMock()

        checker.check_daily_run.return_value = True
        checker.check_disk_space.return_value = True
        checker.check_network.return_value = True
        checker.check_sudo_available.return_value = True
        checker.check_reboot_required.return_value = False

        mock_apt = MagicMock()
        mock_apt.is_available.return_value = True
        mock_apt.perform_update.side_effect = Exception("Update failed")
        mock_apt.get_name.return_value = "APT"

        mock_snap = MagicMock()
        mock_snap.is_available.return_value = False
        mock_snap.get_name.return_value = "Snap"

        with patch("sysup.cli.AptUpdater", return_value=mock_apt):
            with patch("sysup.cli.SnapUpdater", return_value=mock_snap):
                with patch("sysup.cli.Notifier.is_available", return_value=False):
                    # 例外が発生しても他のupdaterに影響しない
                    run_updates(logger, config, checker, auto_run=True, force=False)
