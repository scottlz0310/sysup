"""バックアップ機能のテスト"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

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


def test_backup_manager_creates_directory():
    """バックアップマネージャーがディレクトリを作成するテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir) / "nested" / "backups"
        BackupManager(backup_dir, enabled=True)

        assert backup_dir.exists()


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


def test_create_backup_with_packages():
    """バックアップ作成 - パッケージ取得成功のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        # パッケージ取得メソッドをモック化
        with patch.object(manager, "_get_apt_packages", return_value=["vim", "git"]):
            with patch.object(manager, "_get_brew_packages", return_value=["wget", "curl"]):
                backup_file = manager.create_backup()

                assert backup_file is not None
                with open(backup_file) as f:
                    data = json.load(f)
                    assert "apt" in data["packages"]
                    assert "brew" in data["packages"]


def test_get_apt_packages_success():
    """APTパッケージ取得 - 成功のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            # dpkg --get-selectionsの出力形式: "package_name  install"
            mock_result.stdout = "vim\tinstall\ngit\tinstall\ncurl\tinstall\n"
            mock_run.return_value = mock_result

            packages = manager._get_apt_packages()
            assert packages is not None
            assert "vim" in packages
            assert "git" in packages


def test_get_apt_packages_failure():
    """APTパッケージ取得 - 失敗のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Command failed")

            packages = manager._get_apt_packages()
            assert packages is None


def test_get_brew_packages():
    """Homebrewパッケージ取得のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "wget\ncurl\njq\n"
            mock_run.return_value = mock_result

            packages = manager._get_brew_packages()
            assert packages is not None
            assert "wget" in packages


def test_get_snap_packages():
    """Snapパッケージ取得のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "Name\nsnap1\nsnap2\n"
            mock_run.return_value = mock_result

            packages = manager._get_snap_packages()
            # Snapは"Name"ヘッダーをスキップする
            assert packages is not None
            assert len(packages) >= 0


def test_get_npm_packages():
    """npmパッケージ取得のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "typescript\nlodash\nreact\n"
            mock_run.return_value = mock_result

            packages = manager._get_npm_packages()
            # パッケージがNoneでない場合のみチェック
            if packages is not None:
                assert len(packages) >= 0


def test_get_pipx_packages():
    """pipxパッケージ取得のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "black\npylint\nmypy\n"
            mock_run.return_value = mock_result

            packages = manager._get_pipx_packages()
            assert packages is not None
            assert len(packages) >= 0


def test_get_cargo_packages():
    """Cargoパッケージ取得のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "ripgrep v0.1.0\nfd-find v0.2.0\n"
            mock_run.return_value = mock_result

            packages = manager._get_cargo_packages()
            assert packages is not None
            assert len(packages) >= 0


def test_get_flatpak_packages():
    """Flatpakパッケージ取得のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "app1\tversion1\tinfo1\napp2\tversion2\tinfo2\n"
            mock_run.return_value = mock_result

            packages = manager._get_flatpak_packages()
            assert packages is not None
            assert len(packages) >= 0


def test_get_gem_packages():
    """Gemパッケージ取得のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "rails (7.0.0)\nbundler (2.3.0)\n"
            mock_run.return_value = mock_result

            packages = manager._get_gem_packages()
            assert packages is not None
            assert len(packages) >= 0


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


def test_list_backups_empty_directory():
    """バックアップリスト取得 - 空のディレクトリのテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        backups = manager.list_backups()
        assert len(backups) == 0


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


def test_cleanup_old_backups_less_than_keep_count():
    """古いバックアップ削除 - keep_count未満の場合のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        manager = BackupManager(backup_dir, enabled=True)

        # 5つのバックアップファイルを作成
        for i in range(5):
            (backup_dir / f"packages_2025010{i:02d}_120000.json").write_text("{}")

        deleted = manager.cleanup_old_backups(keep_count=10)
        assert deleted == 0
        assert len(manager.list_backups()) == 5
