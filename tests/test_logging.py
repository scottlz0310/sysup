"""ログ機能のテスト"""

import tempfile
from pathlib import Path

from sysup.core.logging import SysupLogger


def test_logger_initialization():
    """ロガー初期化のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        logger = SysupLogger(log_dir, "INFO", retention_days=30)

        assert logger.log_dir == log_dir
        assert logger.retention_days == 30


def test_log_file_creation():
    """ログファイル作成のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        _ = SysupLogger(log_dir, "INFO")

        # ログファイルが作成されているか確認
        log_files = list(log_dir.glob("sysup_*.log"))
        assert len(log_files) == 1


def test_log_rotation():
    """ログローテーションのテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)

        # 古いログファイルを作成
        old_log = log_dir / "sysup_20200101_000000.log"
        old_log.write_text("old log")

        # ロガー初期化（ローテーション実行）
        _ = SysupLogger(log_dir, "INFO", retention_days=1)

        # 古いログファイルが削除されているか確認
        assert not old_log.exists()
