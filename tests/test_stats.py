"""統計情報管理のテスト"""

import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock

from sysup.core.logging import SysupLogger
from sysup.core.stats import StatsManager, UpdateStats


def test_update_stats_initialization():
    """UpdateStats初期化のテスト"""
    stats = UpdateStats()

    assert stats.start_time > 0
    assert stats.end_time is None
    assert stats.success_count == 0
    assert stats.failure_count == 0
    assert stats.skip_count == 0
    assert stats.successful_updaters == []
    assert stats.failed_updaters == {}
    assert stats.skipped_updaters == {}


def test_record_success():
    """成功記録のテスト"""
    stats = UpdateStats()

    stats.record_success("apt")
    stats.record_success("brew")

    assert stats.success_count == 2
    assert "apt" in stats.successful_updaters
    assert "brew" in stats.successful_updaters


def test_record_failure():
    """失敗記録のテスト"""
    stats = UpdateStats()

    stats.record_failure("apt", "Connection error")
    stats.record_failure("npm", "Permission denied")

    assert stats.failure_count == 2
    assert stats.failed_updaters["apt"] == "Connection error"
    assert stats.failed_updaters["npm"] == "Permission denied"


def test_record_failure_default_reason():
    """失敗記録のデフォルト理由テスト"""
    stats = UpdateStats()

    stats.record_failure("apt")

    assert stats.failure_count == 1
    assert stats.failed_updaters["apt"] == "不明なエラー"


def test_record_skip():
    """スキップ記録のテスト"""
    stats = UpdateStats()

    stats.record_skip("flatpak", "Not installed")
    stats.record_skip("snap", "Not available")

    assert stats.skip_count == 2
    assert stats.skipped_updaters["flatpak"] == "Not installed"
    assert stats.skipped_updaters["snap"] == "Not available"


def test_record_skip_default_reason():
    """スキップ記録のデフォルト理由テスト"""
    stats = UpdateStats()

    stats.record_skip("cargo")

    assert stats.skip_count == 1
    assert stats.skipped_updaters["cargo"] == "利用不可"


def test_finish():
    """統計情報完了のテスト"""
    stats = UpdateStats()

    assert stats.end_time is None

    time.sleep(0.01)  # Windows環境での時間分解能対策
    stats.finish()

    assert stats.end_time is not None
    assert stats.end_time >= stats.start_time


def test_duration_before_finish():
    """完了前の実行時間計測のテスト"""
    stats = UpdateStats()

    time.sleep(0.1)

    duration = stats.duration

    assert duration >= 0.1
    assert stats.end_time is None  # まだ完了していない


def test_duration_after_finish():
    """完了後の実行時間計測のテスト"""
    stats = UpdateStats()

    time.sleep(0.1)
    stats.finish()

    duration = stats.duration

    assert duration >= 0.1
    assert stats.end_time is not None


def test_duration_formatted_seconds_only():
    """フォーマット済み実行時間（秒のみ）のテスト"""
    stats = UpdateStats()

    # start_timeを操作して45秒経過したように見せる
    stats.start_time = time.time() - 45
    stats.finish()

    formatted = stats.duration_formatted

    assert "45秒" in formatted or "46秒" in formatted
    assert "分" not in formatted


def test_duration_formatted_minutes_and_seconds():
    """フォーマット済み実行時間（分と秒）のテスト"""
    stats = UpdateStats()

    # start_timeを操作して2分30秒経過したように見せる
    stats.start_time = time.time() - 150
    stats.finish()

    formatted = stats.duration_formatted

    assert "2分" in formatted
    assert "30秒" in formatted or "31秒" in formatted


def test_stats_manager_initialization():
    """StatsManager初期化のテスト"""
    mock_logger = MagicMock(spec=SysupLogger)
    manager = StatsManager(mock_logger)

    assert manager.logger == mock_logger
    assert isinstance(manager.stats, UpdateStats)


def test_stats_manager_record_success():
    """StatsManager成功記録のテスト"""
    mock_logger = MagicMock(spec=SysupLogger)
    manager = StatsManager(mock_logger)

    manager.record_success("apt")

    assert manager.stats.success_count == 1
    assert "apt" in manager.stats.successful_updaters


def test_stats_manager_record_failure():
    """StatsManager失敗記録のテスト"""
    mock_logger = MagicMock(spec=SysupLogger)
    manager = StatsManager(mock_logger)

    manager.record_failure("brew", "Network error")

    assert manager.stats.failure_count == 1
    assert manager.stats.failed_updaters["brew"] == "Network error"


def test_stats_manager_record_skip():
    """StatsManagerスキップ記録のテスト"""
    mock_logger = MagicMock(spec=SysupLogger)
    manager = StatsManager(mock_logger)

    manager.record_skip("cargo", "Not found")

    assert manager.stats.skip_count == 1
    assert manager.stats.skipped_updaters["cargo"] == "Not found"


def test_show_summary_success_only():
    """サマリー表示 - 成功のみの場合のテスト"""
    mock_logger = MagicMock(spec=SysupLogger)
    manager = StatsManager(mock_logger)

    manager.record_success("apt")
    manager.record_success("brew")

    manager.show_summary()

    # sectionメソッドが呼ばれたことを確認
    mock_logger.section.assert_called_with("更新サマリー")

    # successメソッドが呼ばれたことを確認
    assert mock_logger.success.call_count >= 2


def test_show_summary_with_failures():
    """サマリー表示 - 失敗を含む場合のテスト"""
    mock_logger = MagicMock(spec=SysupLogger)
    manager = StatsManager(mock_logger)

    manager.record_success("apt")
    manager.record_failure("brew", "Connection error")

    manager.show_summary()

    # errorメソッドが呼ばれたことを確認
    mock_logger.error.assert_called()


def test_show_summary_with_skips():
    """サマリー表示 - スキップを含む場合のテスト"""
    mock_logger = MagicMock(spec=SysupLogger)
    manager = StatsManager(mock_logger)

    manager.record_success("apt")
    manager.record_skip("flatpak", "Not installed")

    manager.show_summary()

    # infoメソッドが呼ばれたことを確認
    mock_logger.info.assert_called()


def test_show_summary_no_updates():
    """サマリー表示 - 更新なしの場合のテスト"""
    mock_logger = MagicMock(spec=SysupLogger)
    manager = StatsManager(mock_logger)

    manager.show_summary()

    # warningメソッドが呼ばれたことを確認
    mock_logger.warning.assert_called()


def test_show_summary_all_success():
    """サマリー表示 - 全て成功の場合のテスト"""
    mock_logger = MagicMock(spec=SysupLogger)
    manager = StatsManager(mock_logger)

    manager.record_success("apt")
    manager.record_success("brew")

    manager.show_summary()

    # 最後のsuccessメッセージを確認
    calls = [str(call) for call in mock_logger.success.call_args_list]
    assert any("全ての更新が正常に完了" in str(call) for call in calls)


def test_show_summary_with_some_failures():
    """サマリー表示 - 一部失敗の場合のテスト"""
    mock_logger = MagicMock(spec=SysupLogger)
    manager = StatsManager(mock_logger)

    manager.record_success("apt")
    manager.record_failure("brew", "Error")

    manager.show_summary()

    # warningメソッドが呼ばれたことを確認
    calls = [str(call) for call in mock_logger.warning.call_args_list]
    assert any("件の更新で問題が発生" in str(call) for call in calls)


def test_save_to_log():
    """ログファイルへの保存テスト"""
    mock_logger = MagicMock(spec=SysupLogger)
    manager = StatsManager(mock_logger)

    manager.record_success("apt")
    manager.record_failure("brew", "Connection error")
    manager.record_skip("flatpak", "Not installed")

    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)

        manager.save_to_log(log_dir)

        log_file = log_dir / "update.log"
        assert log_file.exists()

        content = log_file.read_text(encoding="utf-8")
        assert "Update Summary" in content
        assert "Success: 1 items" in content
        assert "Failed: 1 items" in content
        assert "Skipped: 1 items" in content
        assert "apt" in content
        assert "brew" in content
        assert "flatpak" in content


def test_save_to_log_multiple_times():
    """ログファイルへの複数回保存テスト"""
    mock_logger = MagicMock(spec=SysupLogger)

    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)

        # 1回目
        manager1 = StatsManager(mock_logger)
        manager1.record_success("apt")
        manager1.save_to_log(log_dir)

        # 2回目
        manager2 = StatsManager(mock_logger)
        manager2.record_success("brew")
        manager2.save_to_log(log_dir)

        log_file = log_dir / "update.log"
        content = log_file.read_text(encoding="utf-8")

        # 両方の記録が含まれていることを確認
        assert content.count("Update Summary") == 2
        assert "apt" in content
        assert "brew" in content


def test_save_to_log_creates_directory():
    """ログディレクトリが存在しない場合の作成テスト"""
    mock_logger = MagicMock(spec=SysupLogger)
    manager = StatsManager(mock_logger)

    manager.record_success("apt")

    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir) / "logs" / "sysup"

        # ディレクトリが存在しないことを確認
        assert not log_dir.exists()

        manager.save_to_log(log_dir)

        # ディレクトリが作成されたことを確認
        assert log_dir.exists()
        assert (log_dir / "update.log").exists()
