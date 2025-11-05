"""sysup自身の更新機能のテスト."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sysup.core.logging import SysupLogger
from sysup.core.self_update import SelfUpdater


class TestSelfUpdaterInit:
    """SelfUpdater初期化のテスト."""

    def test_init(self) -> None:
        """SelfUpdaterの初期化."""
        logger = MagicMock(spec=SysupLogger)
        cache_dir = Path("/tmp/cache")

        updater = SelfUpdater(logger, cache_dir)

        assert updater.logger == logger
        assert updater.cache_dir == cache_dir


class TestUpdateSelf:
    """SelfUpdater.update_self()のテスト."""

    @patch("sysup.core.self_update.subprocess.run")
    def test_update_self_success_with_updated(self, mock_run: MagicMock) -> None:
        """update_self - アップデート成功（Updatedメッセージ）."""
        logger = MagicMock(spec=SysupLogger)
        cache_dir = Path("/tmp/cache")
        updater = SelfUpdater(logger, cache_dir)

        # uv upgradeで更新された場合の出力
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Updated sysup from 0.5.0 to 0.6.0"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = updater.update_self()

        assert result is True
        logger.info.assert_called_once_with("✓ sysupが更新されました")
        mock_run.assert_called_once_with(
            ["uv", "tool", "upgrade", "sysup"],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

    @patch("sysup.core.self_update.subprocess.run")
    def test_update_self_success_with_installed(self, mock_run: MagicMock) -> None:
        """update_self - アップデート成功（Installedメッセージ）."""
        logger = MagicMock(spec=SysupLogger)
        cache_dir = Path("/tmp/cache")
        updater = SelfUpdater(logger, cache_dir)

        # 新規インストールの場合
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = "Installed sysup 0.6.0"
        mock_run.return_value = mock_result

        result = updater.update_self()

        assert result is True
        logger.info.assert_called_once_with("✓ sysupが更新されました")

    @patch("sysup.core.self_update.subprocess.run")
    def test_update_self_already_latest(self, mock_run: MagicMock) -> None:
        """update_self - 既に最新バージョン."""
        logger = MagicMock(spec=SysupLogger)
        cache_dir = Path("/tmp/cache")
        updater = SelfUpdater(logger, cache_dir)

        # 最新の場合
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Nothing to upgrade"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = updater.update_self()

        assert result is False
        logger.debug.assert_called_once_with("sysupは既に最新です")

    @patch("sysup.core.self_update.subprocess.run")
    def test_update_self_subprocess_error(self, mock_run: MagicMock) -> None:
        """update_self - uv コマンド実行エラー."""
        logger = MagicMock(spec=SysupLogger)
        cache_dir = Path("/tmp/cache")
        updater = SelfUpdater(logger, cache_dir)

        # サブプロセスエラー
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error: uv tool not found"
        mock_run.return_value = mock_result

        result = updater.update_self()

        assert result is False
        logger.debug.assert_called_once()
        assert "sysup更新チェック失敗" in logger.debug.call_args[0][0]

    @patch("sysup.core.self_update.subprocess.run")
    def test_update_self_timeout(self, mock_run: MagicMock) -> None:
        """update_self - タイムアウト."""
        logger = MagicMock(spec=SysupLogger)
        cache_dir = Path("/tmp/cache")
        updater = SelfUpdater(logger, cache_dir)

        # タイムアウト例外
        mock_run.side_effect = subprocess.TimeoutExpired("uv", 60)

        result = updater.update_self()

        assert result is False
        logger.debug.assert_called_once()
        assert "sysup更新エラー" in logger.debug.call_args[0][0]

    @patch("sysup.core.self_update.subprocess.run")
    def test_update_self_oserror_exception(self, mock_run: MagicMock) -> None:
        """update_self - OSError例外."""
        logger = MagicMock(spec=SysupLogger)
        cache_dir = Path("/tmp/cache")
        updater = SelfUpdater(logger, cache_dir)

        # OSError例外
        mock_run.side_effect = OSError("Command not found")

        result = updater.update_self()

        assert result is False
        logger.debug.assert_called_once()
        assert "sysup更新エラー" in logger.debug.call_args[0][0]


class TestRestartSelf:
    """SelfUpdater.restart_self()のテスト."""

    @patch("sysup.core.self_update.subprocess.run")
    @patch("sysup.core.self_update.os.execv")
    def test_restart_self(self, mock_execv: MagicMock, mock_run: MagicMock) -> None:
        """restart_self - プロセス置き換え."""
        logger = MagicMock(spec=SysupLogger)
        cache_dir = Path("/tmp/cache")
        updater = SelfUpdater(logger, cache_dir)

        # sys.argv をモック
        original_argv = sys.argv
        sys.argv = ["sysup", "update", "--dry-run"]

        # which sysup の結果をモック
        mock_which_result = MagicMock()
        mock_which_result.stdout = "/usr/local/bin/sysup\n"
        mock_run.return_value = mock_which_result

        try:
            # execvは戻らないので、例外を発生させてシミュレート
            mock_execv.side_effect = OSError("execv simulation")

            with pytest.raises(OSError):
                updater.restart_self()

            # 呼び出し確認
            logger.info.assert_called_once_with("更新されたsysupで再実行中...")
            mock_execv.assert_called_once()

            # execvの引数を確認
            call_args = mock_execv.call_args
            assert call_args[0][0] == "/usr/local/bin/sysup"
            assert call_args[0][1] == [
                "sysup",
                "update",
                "--dry-run",
            ]
        finally:
            sys.argv = original_argv

    @patch("sysup.core.self_update.subprocess.run")
    @patch("sysup.core.self_update.os.execv")
    def test_restart_self_no_args(self, mock_execv: MagicMock, mock_run: MagicMock) -> None:
        """restart_self - 引数なしで再実行."""
        logger = MagicMock(spec=SysupLogger)
        cache_dir = Path("/tmp/cache")
        updater = SelfUpdater(logger, cache_dir)

        original_argv = sys.argv
        sys.argv = ["sysup"]

        # which sysup の結果をモック（見つからない場合）
        mock_which_result = MagicMock()
        mock_which_result.stdout = ""
        mock_run.return_value = mock_which_result

        try:
            mock_execv.side_effect = OSError("execv simulation")

            with pytest.raises(OSError):
                updater.restart_self()

            # execvの引数を確認（フォールバック）
            call_args = mock_execv.call_args
            assert call_args[0][0] == sys.executable
            assert call_args[0][1] == [
                sys.executable,
                "-m",
                "sysup.cli.cli",
            ]
        finally:
            sys.argv = original_argv


class TestCheckAndUpdate:
    """SelfUpdater.check_and_update()のテスト."""

    @patch("sysup.core.self_update.SelfUpdater.restart_self")
    @patch("sysup.core.self_update.SelfUpdater.update_self")
    def test_check_and_update_needs_update(self, mock_update: MagicMock, mock_restart: MagicMock) -> None:
        """check_and_update - アップデートが必要な場合."""
        logger = MagicMock(spec=SysupLogger)
        cache_dir = Path("/tmp/cache")
        updater = SelfUpdater(logger, cache_dir)

        # update_self()がTrueを返す
        mock_update.return_value = True
        # restart_self()は戻らないので、このテストでは呼び出されるかのみ確認
        mock_restart.side_effect = OSError("restart simulation")

        with pytest.raises(OSError):
            updater.check_and_update()

        # 両方のメソッドが呼ばれたことを確認
        mock_update.assert_called_once()
        mock_restart.assert_called_once()

    @patch("sysup.core.self_update.SelfUpdater.update_self")
    def test_check_and_update_no_update_needed(self, mock_update: MagicMock) -> None:
        """check_and_update - アップデートが不要な場合."""
        logger = MagicMock(spec=SysupLogger)
        cache_dir = Path("/tmp/cache")
        updater = SelfUpdater(logger, cache_dir)

        # update_self()がFalseを返す
        mock_update.return_value = False

        result = updater.check_and_update()

        assert result is False
        mock_update.assert_called_once()

    @patch("sysup.core.self_update.SelfUpdater.restart_self")
    @patch("sysup.core.self_update.SelfUpdater.update_self")
    def test_check_and_update_returns_true_before_restart(
        self, mock_update: MagicMock, mock_restart: MagicMock
    ) -> None:
        """check_and_update - Trueを返す（再実行前）."""
        logger = MagicMock(spec=SysupLogger)
        cache_dir = Path("/tmp/cache")
        updater = SelfUpdater(logger, cache_dir)

        # update_self()がTrueを返す
        mock_update.return_value = True
        # restart_self()は例外で通常は戻らない
        mock_restart.return_value = None  # テストのみで戻ると仮定

        # 通常はrestart_selfが例外を発生させるので、Trueには到達しない
        # しかし、restart_selfが何らかの理由で戻る場合のテスト
        result = updater.check_and_update()

        assert result is True


class TestIntegration:
    """統合テスト."""

    @patch("sysup.core.self_update.subprocess.run")
    def test_update_self_integration(self, mock_run: MagicMock) -> None:
        """統合テスト - update_selfの全フロー."""
        logger = SysupLogger(Path("/tmp"))
        cache_dir = Path("/tmp/cache")
        updater = SelfUpdater(logger, cache_dir)

        # シミュレート: アップデートが利用可能
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Updated sysup from 0.5.0 to 0.6.0"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = updater.update_self()

        assert result is True

    @patch("sysup.core.self_update.subprocess.run")
    @patch("sysup.core.self_update.os.execv")
    def test_check_and_update_integration(self, mock_execv: MagicMock, mock_run: MagicMock) -> None:
        """統合テスト - check_and_updateの全フロー."""
        logger = SysupLogger(Path("/tmp"))
        cache_dir = Path("/tmp/cache")
        updater = SelfUpdater(logger, cache_dir)

        # uv tool upgrade の結果をモック
        mock_upgrade_result = MagicMock()
        mock_upgrade_result.returncode = 0
        mock_upgrade_result.stdout = "Updated sysup"
        mock_upgrade_result.stderr = ""

        # which sysup の結果をモック
        mock_which_result = MagicMock()
        mock_which_result.stdout = "/usr/local/bin/sysup\n"

        # subprocess.run を2回呼び出すので side_effect を使用
        mock_run.side_effect = [mock_upgrade_result, mock_which_result]

        # execvで例外を発生させる
        mock_execv.side_effect = OSError("execv simulation")

        with pytest.raises(OSError):
            updater.check_and_update()

        # subprocess.runが2回呼ばれたことを確認（upgrade + which）
        assert mock_run.call_count == 2
        mock_execv.assert_called_once()
