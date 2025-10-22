"""Updater基底クラスのテスト"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from sysup.core.logging import SysupLogger
from sysup.updaters.base import BaseUpdater


# テスト用の具体的なUpdaterクラス
class TestUpdater(BaseUpdater):
    """テスト用のUpdater実装"""

    def get_name(self) -> str:
        return "TestUpdater"

    def is_available(self) -> bool:
        return True

    def perform_update(self) -> bool:
        return True


@pytest.fixture
def mock_logger():
    """モックロガーを作成するフィクスチャ"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")
        yield logger
        logger.close()


def test_base_updater_initialization(mock_logger):
    """BaseUpdater初期化のテスト"""
    updater = TestUpdater(mock_logger, dry_run=False)

    assert updater.logger == mock_logger
    assert updater.dry_run is False


def test_base_updater_dry_run_mode(mock_logger):
    """BaseUpdaterドライランモードのテスト"""
    updater = TestUpdater(mock_logger, dry_run=True)

    assert updater.dry_run is True


def test_get_name(mock_logger):
    """get_nameメソッドのテスト"""
    updater = TestUpdater(mock_logger)

    assert updater.get_name() == "TestUpdater"


def test_is_available(mock_logger):
    """is_availableメソッドのテスト"""
    updater = TestUpdater(mock_logger)

    assert updater.is_available() is True


def test_perform_update(mock_logger):
    """perform_updateメソッドのテスト"""
    updater = TestUpdater(mock_logger)

    assert updater.perform_update() is True


def test_check_updates_default(mock_logger):
    """check_updatesメソッドのデフォルト実装テスト"""
    updater = TestUpdater(mock_logger)

    result = updater.check_updates()

    assert result is None


def test_pre_update_default(mock_logger):
    """pre_updateメソッドのデフォルト実装テスト"""
    updater = TestUpdater(mock_logger)

    result = updater.pre_update()

    assert result is True


def test_post_update_default(mock_logger):
    """post_updateメソッドのデフォルト実装テスト"""
    updater = TestUpdater(mock_logger)

    result = updater.post_update()

    assert result is True


def test_run_command_success(mock_logger):
    """run_commandメソッド - 成功のテスト"""
    updater = TestUpdater(mock_logger)

    with patch("subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = updater.run_command(["echo", "test"])

        assert result.returncode == 0
        mock_run.assert_called_once()


def test_run_command_dry_run(mock_logger):
    """run_commandメソッド - ドライランモードのテスト"""
    updater = TestUpdater(mock_logger, dry_run=True)

    result = updater.run_command(["apt", "update"])

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_run_command_with_check_false(mock_logger):
    """run_commandメソッド - check=Falseのテスト"""
    updater = TestUpdater(mock_logger)

    with patch("subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error"
        mock_run.return_value = mock_result

        result = updater.run_command(["false"], check=False)

        assert result.returncode == 1


def test_run_command_error(mock_logger):
    """run_commandメソッド - エラーのテスト"""
    updater = TestUpdater(mock_logger)

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, ["false"], stderr="Error occurred")

        with pytest.raises(subprocess.CalledProcessError):
            updater.run_command(["false"])


def test_run_command_timeout(mock_logger):
    """run_commandメソッド - タイムアウトのテスト"""
    updater = TestUpdater(mock_logger)

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(["sleep", "10"], 5)

        with pytest.raises(subprocess.TimeoutExpired):
            updater.run_command(["sleep", "10"], timeout=5)


def test_run_command_custom_timeout(mock_logger):
    """run_commandメソッド - カスタムタイムアウトのテスト"""
    updater = TestUpdater(mock_logger)

    with patch("subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        updater.run_command(["echo", "test"], timeout=60)

        # timeoutが正しく渡されたか確認
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["timeout"] == 60


def test_command_exists_true(mock_logger):
    """command_existsメソッド - コマンドが存在する場合のテスト"""
    updater = TestUpdater(mock_logger)

    with patch("subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = updater.command_exists("apt")

        assert result is True


def test_command_exists_false(mock_logger):
    """command_existsメソッド - コマンドが存在しない場合のテスト"""
    updater = TestUpdater(mock_logger)

    with patch("subprocess.run") as mock_run:
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = updater.command_exists("nonexistent_command")

        assert result is False


def test_command_exists_exception(mock_logger):
    """command_existsメソッド - 例外発生時のテスト"""
    updater = TestUpdater(mock_logger)

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = Exception("Command error")

        result = updater.command_exists("apt")

        assert result is False


def test_abstract_methods_must_be_implemented(mock_logger):
    """抽象メソッドが実装されていない場合のテスト"""
    with pytest.raises(TypeError):
        # BaseUpdaterを直接インスタンス化しようとするとTypeErrorが発生
        BaseUpdater(mock_logger)  # type: ignore[abstract]


class IncompleteUpdater(BaseUpdater):
    """不完全なUpdater実装（抽象メソッドの一部を実装していない）"""

    def get_name(self) -> str:
        return "IncompleteUpdater"


def test_incomplete_implementation():
    """抽象メソッドの一部のみ実装した場合のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = SysupLogger(Path(tmpdir), "INFO")

        with pytest.raises(TypeError):
            # is_availableとperform_updateを実装していないため、TypeErrorが発生
            IncompleteUpdater(logger)  # type: ignore[abstract]
        logger.close()


class CustomUpdater(BaseUpdater):
    """カスタムcheck_updatesを実装したUpdater"""

    def get_name(self) -> str:
        return "CustomUpdater"

    def is_available(self) -> bool:
        return True

    def perform_update(self) -> bool:
        return True

    def check_updates(self) -> int | None:
        """カスタム実装：5個の更新があると返す"""
        return 5


def test_custom_check_updates(mock_logger):
    """カスタムcheck_updates実装のテスト"""
    updater = CustomUpdater(mock_logger)

    result = updater.check_updates()

    assert result == 5


class CustomPrePostUpdater(BaseUpdater):
    """カスタムpre_update/post_updateを実装したUpdater"""

    def __init__(self, logger, dry_run=False):
        super().__init__(logger, dry_run)
        self.pre_called = False
        self.post_called = False

    def get_name(self) -> str:
        return "CustomPrePostUpdater"

    def is_available(self) -> bool:
        return True

    def perform_update(self) -> bool:
        return True

    def pre_update(self) -> bool:
        self.pre_called = True
        return True

    def post_update(self) -> bool:
        self.post_called = True
        return True


def test_custom_pre_post_update(mock_logger):
    """カスタムpre_update/post_update実装のテスト"""
    updater = CustomPrePostUpdater(mock_logger)

    assert updater.pre_called is False
    assert updater.post_called is False

    updater.pre_update()
    assert updater.pre_called is True

    updater.post_update()
    assert updater.post_called is True
