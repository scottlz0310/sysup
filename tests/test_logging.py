"""ログ機能のテスト"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from sysup.core.logging import SysupLogger, get_logger


def test_logger_initialization():
    """ロガー初期化のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        logger = SysupLogger(log_dir, "INFO", retention_days=30)

        assert logger.log_dir == log_dir
        assert logger.retention_days == 30
        assert logger.console is not None
        assert logger.logger is not None
        logger.close()


def test_log_file_creation():
    """ログファイル作成のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        logger = SysupLogger(log_dir, "INFO")

        # ログファイルが作成されているか確認
        log_files = list(log_dir.glob("sysup_*.log"))
        assert len(log_files) == 1
        logger.close()


def test_log_rotation():
    """ログローテーションのテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)

        # 古いログファイルを作成
        old_log = log_dir / "sysup_20200101_000000.log"
        old_log.write_text("old log")

        # ロガー初期化（ローテーション実行）
        logger = SysupLogger(log_dir, "INFO", retention_days=1)

        # 古いログファイルが削除されているか確認
        assert not old_log.exists()
        logger.close()


def test_log_rotation_keeps_recent():
    """ログローテーション - 最近のログは保持するテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)

        # 最近のログファイルを作成（昨日）
        yesterday = datetime.now() - timedelta(days=1)
        recent_log = log_dir / f"sysup_{yesterday.strftime('%Y%m%d')}_120000.log"
        recent_log.write_text("recent log")

        # ロガー初期化（ローテーション実行）
        logger = SysupLogger(log_dir, "INFO", retention_days=7)

        # 最近のログファイルは保持されている
        assert recent_log.exists()
        logger.close()


def test_log_rotation_invalid_filename():
    """ログローテーション - 無効なファイル名のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)

        # 無効な形式のログファイルを作成
        invalid_log = log_dir / "sysup_invalid.log"
        invalid_log.write_text("invalid log")

        # ロガー初期化（エラーが発生しない）
        logger = SysupLogger(log_dir, "INFO", retention_days=1)

        # 無効な形式のファイルはスキップされる
        assert invalid_log.exists()
        logger.close()


def test_success_message():
    """成功メッセージ出力のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        logger = SysupLogger(log_dir, "INFO")

        # エラーが発生しないことを確認
        logger.success("Test success message")
        logger.close()


def test_info_message():
    """情報メッセージ出力のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        logger = SysupLogger(log_dir, "INFO")

        # エラーが発生しないことを確認
        logger.info("Test info message")
        logger.close()


def test_warning_message():
    """警告メッセージ出力のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        logger = SysupLogger(log_dir, "INFO")

        # エラーが発生しないことを確認
        logger.warning("Test warning message")
        logger.close()


def test_error_message():
    """エラーメッセージ出力のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        logger = SysupLogger(log_dir, "INFO")

        # エラーが発生しないことを確認
        logger.error("Test error message")
        logger.close()


def test_section_message():
    """セクションメッセージ出力のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        logger = SysupLogger(log_dir, "INFO")

        # エラーが発生しないことを確認
        logger.section("Test Section")
        logger.close()


def test_progress_step():
    """進捗ステップ表示のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        logger = SysupLogger(log_dir, "INFO")

        # エラーが発生しないことを確認
        logger.progress_step(1, 5, "Step 1")
        logger.progress_step(5, 5, "Step 5")
        logger.close()


def test_get_logger_with_path():
    """get_logger関数 - パス指定ありのテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        logger = get_logger(log_dir, "DEBUG")

        assert isinstance(logger, SysupLogger)
        assert logger.log_dir == log_dir
        logger.close()


def test_get_logger_without_path():
    """get_logger関数 - パス指定なしのテスト"""
    logger = get_logger()

    assert isinstance(logger, SysupLogger)
    assert logger.log_dir == Path.home() / ".local" / "share" / "sysup"
    logger.close()


def test_logger_different_levels():
    """異なるログレベルでの初期化テスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)

        # DEBUG レベル
        logger_debug = SysupLogger(log_dir / "debug", "DEBUG")
        assert logger_debug is not None
        logger_debug.close()

        # WARNING レベル
        logger_warning = SysupLogger(log_dir / "warning", "WARNING")
        assert logger_warning is not None
        logger_warning.close()

        # ERROR レベル
        logger_error = SysupLogger(log_dir / "error", "ERROR")
        assert logger_error is not None
        logger_error.close()
