"""バックアップ機能のテスト"""

import json
import tempfile
from pathlib import Path

from sysup.core.backup import BackupManager


def test_backup_manager_initialization():
    """バックアップマネージャー初期化のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        assert manager.backup_dir == backup_dir
        assert manager.enabled is True
        assert backup_dir.exists()


def test_backup_manager_disabled():
    """バックアップ無効時のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir) / "backups"
        manager = BackupManager(backup_dir, enabled=False)

        assert manager.enabled is False
        backup_file = manager.create_backup()
        assert backup_file is None


def test_create_backup():
    """バックアップ作成のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        backup_file = manager.create_backup()

        if backup_file:
            assert backup_file.exists()
            assert backup_file.suffix == ".json"

            # JSONとして読み込めるか確認
            with open(backup_file) as f:
                data = json.load(f)
                assert "timestamp" in data
                assert "packages" in data


def test_list_backups():
    """バックアップリスト取得のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        # バックアップファイルを作成
        (backup_dir / "packages_20250101_120000.json").write_text("{}")
        (backup_dir / "packages_20250102_120000.json").write_text("{}")

        backups = manager.list_backups()
        assert len(backups) == 2


def test_cleanup_old_backups():
    """古いバックアップ削除のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        # 複数のバックアップファイルを作成
        for i in range(15):
            (backup_dir / f"packages_2025010{i:02d}_120000.json").write_text("{}")

        deleted = manager.cleanup_old_backups(keep_count=10)
        assert deleted == 5
        assert len(manager.list_backups()) == 10
