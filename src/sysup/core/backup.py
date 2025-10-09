"""バックアップ機能.

このモジュールはパッケージリストのバックアップ機能を提供します。
各種パッケージマネージャのインストール済みパッケージリストを取得し、
JSON形式でバックアップファイルに保存します。
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path


class BackupManager:
    """パッケージリストのバックアップを管理するクラス.

    各種パッケージマネージャのインストール済みパッケージリストを
    JSON形式でバックアップし、古いバックアップの削除も管理します。

    Attributes:
        backup_dir: バックアップファイルの保存ディレクトリ.
        enabled: バックアップ機能の有効/無効フラグ.

    """

    def __init__(self, backup_dir: Path, enabled: bool = True):
        """BackupManagerを初期化する.

        Args:
            backup_dir: バックアップファイルの保存ディレクトリ.
            enabled: バックアップを有効にするかどうか. デフォルトはTrue.

        """
        self.backup_dir = backup_dir
        self.enabled = enabled

        if self.enabled:
            self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> Path | None:
        """現在のパッケージリストをバックアップする.

        各種パッケージマネージャから現在インストールされているパッケージリストを取得し、
        タイムスタンプ付きのJSONファイルとして保存します。

        Returns:
            バックアップファイルのパス. 失敗時またはバックアップ無効時はNone.

        Examples:
            >>> manager = BackupManager(Path("~/.local/share/sysup/backups"))
            >>> backup_file = manager.create_backup()
            >>> print(backup_file)
            ~/.local/share/sysup/backups/packages_20250101_120000.json

        """
        if not self.enabled:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"packages_{timestamp}.json"

        backup_data: dict[str, object] = {"timestamp": timestamp, "packages": {}}
        packages: dict[str, list[str]] = {}

        # APT
        apt_packages = self._get_apt_packages()
        if apt_packages:
            packages["apt"] = apt_packages

        # Snap
        snap_packages = self._get_snap_packages()
        if snap_packages:
            packages["snap"] = snap_packages

        # Homebrew
        brew_packages = self._get_brew_packages()
        if brew_packages:
            packages["brew"] = brew_packages

        # npm
        npm_packages = self._get_npm_packages()
        if npm_packages:
            packages["npm"] = npm_packages

        # pipx
        pipx_packages = self._get_pipx_packages()
        if pipx_packages:
            packages["pipx"] = pipx_packages

        # Cargo
        cargo_packages = self._get_cargo_packages()
        if cargo_packages:
            packages["cargo"] = cargo_packages

        # Flatpak
        flatpak_packages = self._get_flatpak_packages()
        if flatpak_packages:
            packages["flatpak"] = flatpak_packages

        # Gem
        gem_packages = self._get_gem_packages()
        if gem_packages:
            packages["gem"] = gem_packages

        backup_data["packages"] = packages

        try:
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            return backup_file
        except Exception:
            return None

    def _get_apt_packages(self) -> list[str] | None:
        """APTパッケージリストを取得する.

        Returns:
            インストール済みAPTパッケージ名のリスト. 取得失敗時はNone.

        """
        try:
            result = subprocess.run(["dpkg", "--get-selections"], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                packages = []
                for line in result.stdout.splitlines():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == "install":
                        packages.append(parts[0])
                return packages
            return None
        except Exception:
            return None

    def _get_snap_packages(self) -> list[str] | None:
        """Snapパッケージリストを取得する.

        Returns:
            インストール済みSnapパッケージ名のリスト. 取得失敗時はNone.

        """
        try:
            result = subprocess.run(["snap", "list"], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                packages = []
                for line in result.stdout.splitlines()[1:]:  # ヘッダーをスキップ
                    parts = line.split()
                    if parts:
                        packages.append(parts[0])
                return packages
            return None
        except Exception:
            return None

    def _get_brew_packages(self) -> list[str] | None:
        """Homebrewパッケージリストを取得する.

        Returns:
            インストール済みHomebrewパッケージ名のリスト. 取得失敗時はNone.

        """
        try:
            result = subprocess.run(["brew", "list", "--formula"], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout.splitlines()
            return None
        except Exception:
            return None

    def _get_npm_packages(self) -> list[str] | None:
        """npmグローバルパッケージリストを取得する.

        Returns:
            インストール済みnpmグローバルパッケージ名のリスト. 取得失敗時はNone.

        """
        try:
            result = subprocess.run(
                ["npm", "list", "-g", "--depth=0", "--json"], capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return list(data.get("dependencies", {}).keys())
            return None
        except Exception:
            return None

    def _get_pipx_packages(self) -> list[str] | None:
        """pipxパッケージリストを取得する.

        Returns:
            インストール済みpipxパッケージ名のリスト. 取得失敗時はNone.

        """
        try:
            result = subprocess.run(["pipx", "list", "--short"], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout.splitlines()
            return None
        except Exception:
            return None

    def _get_cargo_packages(self) -> list[str] | None:
        """Cargoパッケージリストを取得する.

        Returns:
            インストール済みCargoパッケージ名のリスト. 取得失敗時はNone.

        """
        try:
            result = subprocess.run(["cargo", "install", "--list"], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                packages = []
                for line in result.stdout.splitlines():
                    if line and not line.startswith(" "):
                        package = line.split()[0]
                        packages.append(package)
                return packages
            return None
        except Exception:
            return None

    def _get_flatpak_packages(self) -> list[str] | None:
        """Flatpakパッケージリストを取得する.

        Returns:
            インストール済みFlatpakパッケージ名のリスト. 取得失敗時はNone.

        """
        try:
            result = subprocess.run(
                ["flatpak", "list", "--app", "--columns=application"], capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return result.stdout.splitlines()
            return None
        except Exception:
            return None

    def _get_gem_packages(self) -> list[str] | None:
        """Gemパッケージリストを取得する.

        Returns:
            インストール済みGemパッケージ名のリスト. 取得失敗時はNone.

        """
        try:
            result = subprocess.run(["gem", "list", "--no-versions"], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout.splitlines()
            return None
        except Exception:
            return None

    def list_backups(self) -> list[Path]:
        """バックアップファイルのリストを取得する.

        Returns:
            バックアップファイルのパスリスト(新しい順). ディレクトリが存在しない場合は空リスト.

        """
        if not self.backup_dir.exists():
            return []

        return sorted(self.backup_dir.glob("packages_*.json"), reverse=True)

    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """古いバックアップを削除.

        Args:
            keep_count: 保持するバックアップ数

        Returns:
            削除したファイル数

        """
        backups = self.list_backups()
        if len(backups) <= keep_count:
            return 0

        deleted = 0
        for backup_file in backups[keep_count:]:
            try:
                backup_file.unlink()
                deleted += 1
            except Exception:
                continue

        return deleted
