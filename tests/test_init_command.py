"""sysup init コマンドのテスト."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sysup.cli.init import (
    PackageManagerDetector,
    check_existing_config,
    handle_existing_config,
    step1_detect_system,
    step2_select_mode,
    step3_select_updaters,
    step4_advanced_settings,
)
from sysup.core.config import SysupConfig


class TestPackageManagerDetector:
    """PackageManagerDetectorのテスト."""

    def test_get_available_managers(self) -> None:
        """利用可能なマネージャを検出."""
        available = PackageManagerDetector.get_available_managers()
        assert isinstance(available, dict)
        assert all(name in available for name in ["apt", "npm", "rustup"])

    def test_get_manager_description(self) -> None:
        """マネージャの説明を取得."""
        desc = PackageManagerDetector.get_manager_description("apt")
        assert "Debian" in desc or "Ubuntu" in desc or "パッケージ" in desc

    def test_get_manager_description_unknown(self) -> None:
        """未知のマネージャの説明を取得."""
        desc = PackageManagerDetector.get_manager_description("unknown_manager")
        assert desc == "unknown_manager"


class TestConfigDetection:
    """設定ファイル検出のテスト."""

    def test_check_existing_config_not_found(self) -> None:
        """設定ファイルが見つからない場合."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                result = check_existing_config()
                assert result is None

    def test_check_existing_config_found(self) -> None:
        """設定ファイルが見つかる場合."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            config_dir = tmppath / ".config" / "sysup"
            config_dir.mkdir(parents=True)
            config_file = config_dir / "sysup.toml"
            config_file.write_text("[general]\n")

            with patch.object(Path, "home", return_value=tmppath):
                result = check_existing_config()
                assert result == config_file


class TestWizardSteps:
    """ウィザード工程のテスト."""

    @patch("sysup.cli.init.console")
    def test_step1_detect_system(self, mock_console: MagicMock) -> None:
        """工程1: システム環境の確認."""
        available = step1_detect_system()
        assert isinstance(available, dict)
        assert all(isinstance(v, bool) for v in available.values())

    @patch("sysup.cli.init.Prompt.ask")
    @patch("sysup.cli.init.console")
    def test_step2_select_mode_standard(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """工程2: 実行モード選択 - 標準モード."""
        mock_ask.return_value = "1"
        result = step2_select_mode()
        assert result == "disabled"

    @patch("sysup.cli.init.Prompt.ask")
    @patch("sysup.cli.init.console")
    def test_step2_select_mode_auto(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """工程2: 実行モード選択 - 自動実行モード."""
        mock_ask.return_value = "2"
        result = step2_select_mode()
        assert result == "enabled"

    @patch("sysup.cli.init.Prompt.ask")
    @patch("sysup.cli.init.console")
    def test_step3_select_updaters(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """工程3: 更新対象の選択."""
        # Enterキー（確定）をシミュレート
        mock_ask.return_value = "q"
        available = {"apt": True, "npm": True, "rustup": False}
        result = step3_select_updaters(available)

        assert isinstance(result, dict)
        # 選択されたものは True のはず
        assert all(isinstance(v, bool) for v in result.values())

    @patch("sysup.cli.init.Prompt.ask")
    @patch("sysup.cli.init.console")
    def test_step4_advanced_settings_default(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """工程4: 詳細設定 - デフォルト値."""
        mock_ask.return_value = "2"
        settings = step4_advanced_settings()

        assert settings["log_level"] == "INFO"
        assert settings["parallel_updates"] is False
        assert settings["backup_enabled"] is True
        assert settings["notification_enabled"] is True

    @patch("sysup.cli.init.Prompt.ask")
    @patch("sysup.cli.init.console")
    def test_step4_advanced_settings_custom(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """工程4: 詳細設定 - カスタム値."""
        # 詳細設定有効, DEBUG, 並列実行有効, バックアップ無効, 通知有効
        mock_ask.side_effect = ["1", "1", "1", "2", "1"]
        settings = step4_advanced_settings()

        assert settings["log_level"] == "DEBUG"
        assert settings["parallel_updates"] is True
        assert settings["backup_enabled"] is False
        assert settings["notification_enabled"] is True


class TestConfigGeneration:
    """設定ファイル生成のテスト."""

    def test_generate_toml_basic(self) -> None:
        """TOML生成 - 基本設定."""
        from sysup.cli.init import _generate_toml

        config = SysupConfig()
        config.updaters.apt = True
        config.updaters.npm = False
        config.logging.level = "DEBUG"

        toml_str = _generate_toml(config)

        assert "apt = true" in toml_str
        assert "npm = false" in toml_str
        assert 'level = "DEBUG"' in toml_str
        assert "[updaters]" in toml_str
        assert "[logging]" in toml_str
        assert "[general]" in toml_str


class TestExistingConfigHandling:
    """既存設定ハンドリングのテスト."""

    @patch("sysup.cli.init.Prompt.ask")
    @patch("sysup.cli.init.console")
    def test_handle_existing_config_continue(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """既存設定検出時 - 続行を選択."""
        mock_ask.return_value = "1"

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "sysup.toml"
            config_path.write_text("")

            result = handle_existing_config(config_path)
            assert result is True

    @patch("sysup.cli.init.Prompt.ask")
    @patch("sysup.cli.init.console")
    def test_handle_existing_config_skip(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """既存設定検出時 - スキップを選択."""
        mock_ask.return_value = "2"

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "sysup.toml"
            config_path.write_text("")

            result = handle_existing_config(config_path)
            assert result is False

    @patch("sysup.cli.init.Prompt.ask")
    @patch("sysup.cli.init.console")
    def test_handle_existing_config_reset(self, mock_console: MagicMock, mock_ask: MagicMock) -> None:
        """既存設定検出時 - リセットを選択."""
        mock_ask.return_value = "3"

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "sysup.toml"
            config_path.write_text("test_config")
            backup_path = Path(tmpdir) / "sysup.toml.bak"

            result = handle_existing_config(config_path)

            assert result is True
            assert backup_path.exists()
            assert backup_path.read_text() == "test_config"


class TestInitCommand:
    """init_command 関数のテスト."""

    @patch("sysup.cli.init.step5_save_config")
    @patch("sysup.cli.init.step4_advanced_settings")
    @patch("sysup.cli.init.step3_select_updaters")
    @patch("sysup.cli.init.step2_select_mode")
    @patch("sysup.cli.init.step1_detect_system")
    @patch("sysup.cli.init.check_existing_config")
    @patch("sysup.cli.init.show_header")
    def test_init_command_new_setup(
        self,
        mock_header: MagicMock,
        mock_check: MagicMock,
        mock_step1: MagicMock,
        mock_step2: MagicMock,
        mock_step3: MagicMock,
        mock_step4: MagicMock,
        mock_step5: MagicMock,
    ) -> None:
        """init_command - 新規セットアップ."""
        mock_check.return_value = None
        mock_step1.return_value = {"apt": True}
        mock_step2.return_value = "disabled"
        mock_step3.return_value = {"apt": True}
        mock_step4.return_value = {"log_level": "INFO", "parallel_updates": False}

        from sysup.cli.init import init_command

        init_command()

        mock_header.assert_called_once()
        mock_check.assert_called_once()
        mock_step1.assert_called_once()
        mock_step2.assert_called_once()
        mock_step3.assert_called_once()
        mock_step4.assert_called_once()
        mock_step5.assert_called_once()

    @patch("sysup.cli.init.handle_existing_config")
    @patch("sysup.cli.init.check_existing_config")
    @patch("sysup.cli.init.show_header")
    def test_init_command_skip_existing_config(
        self,
        mock_header: MagicMock,
        mock_check: MagicMock,
        mock_handle: MagicMock,
    ) -> None:
        """init_command - 既存設定スキップ."""
        mock_check.return_value = Path("/tmp/test.toml")
        mock_handle.return_value = False

        from sysup.cli.init import init_command

        with pytest.raises(SystemExit) as exc_info:
            init_command()

        assert exc_info.value.code == 0
        mock_header.assert_called_once()
        mock_check.assert_called_once()
        mock_handle.assert_called_once()

    @patch("sysup.cli.init.step5_save_config")
    @patch("sysup.cli.init.step4_advanced_settings")
    @patch("sysup.cli.init.step3_select_updaters")
    @patch("sysup.cli.init.step2_select_mode")
    @patch("sysup.cli.init.step1_detect_system")
    @patch("sysup.cli.init.handle_existing_config")
    @patch("sysup.cli.init.check_existing_config")
    @patch("sysup.cli.init.show_header")
    def test_init_command_with_existing_config(
        self,
        mock_header: MagicMock,
        mock_check: MagicMock,
        mock_handle: MagicMock,
        mock_step1: MagicMock,
        mock_step2: MagicMock,
        mock_step3: MagicMock,
        mock_step4: MagicMock,
        mock_step5: MagicMock,
    ) -> None:
        """init_command - 既存設定続行."""
        mock_check.return_value = Path("/tmp/test.toml")
        mock_handle.return_value = True
        mock_step1.return_value = {"apt": True}
        mock_step2.return_value = "disabled"
        mock_step3.return_value = {"apt": True}
        mock_step4.return_value = {"log_level": "INFO", "parallel_updates": False}

        from sysup.cli.init import init_command

        init_command()

        mock_header.assert_called_once()
        mock_check.assert_called_once()
        mock_handle.assert_called_once()
        mock_step1.assert_called_once()

    def test_init_command_keyboard_interrupt(self) -> None:
        """init_command - キーボード割り込み."""
        with patch("sysup.cli.init.show_header", side_effect=KeyboardInterrupt):
            from sysup.cli.init import init_command

            with pytest.raises(SystemExit):
                init_command()

    def test_init_command_exception(self) -> None:
        """init_command - 例外処理."""
        with patch("sysup.cli.init.show_header", side_effect=RuntimeError("test error")):
            from sysup.cli.init import init_command

            with pytest.raises(SystemExit):
                init_command()


class TestTOMLGeneration:
    """TOML生成機能のテスト."""

    def test_generate_toml_all_options(self) -> None:
        """TOML生成 - すべてのオプション設定."""
        from sysup.cli.init import _generate_toml

        config = SysupConfig()
        config.updaters.apt = True
        config.updaters.npm = True
        config.updaters.rustup = False
        config.auto_run.mode = "enabled"
        config.logging.level = "DEBUG"
        config.general.parallel_updates = True
        config.backup.enabled = False
        config.notification.enabled = False

        toml_str = _generate_toml(config)

        assert "[updaters]" in toml_str
        assert "apt = true" in toml_str
        assert "npm = true" in toml_str
        assert "rustup = false" in toml_str
        assert "[auto_run]" in toml_str
        assert 'mode = "enabled"' in toml_str
        assert "[logging]" in toml_str
        assert 'level = "DEBUG"' in toml_str
        assert "[general]" in toml_str
        assert "parallel_updates = true" in toml_str
        assert "[backup]" in toml_str
        assert "enabled = false" in toml_str
        assert "[notification]" in toml_str
        assert "enabled = false" in toml_str
