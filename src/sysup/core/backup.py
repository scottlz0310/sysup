"""バックアップ機能"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class BackupManager:
    """パッケージリストのバックアップを管理するクラス"""
    
    def __init__(self, backup_dir: Path, enabled: bool = True):
        self.backup_dir = backup_dir
        self.enabled = enabled
        
        if self.enabled:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self) -> Optional[Path]:
        """現在のパッケージリストをバックアップ
        
        Returns:
            バックアップファイルのパス（失敗時はNone）
        """
        if not self.enabled:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"packages_{timestamp}.json"
        
        backup_data = {
            "timestamp": timestamp,
            "packages": {}
        }
        
        # APT
        apt_packages = self._get_apt_packages()
        if apt_packages:
            backup_data["packages"]["apt"] = apt_packages
        
        # Snap
        snap_packages = self._get_snap_packages()
        if snap_packages:
            backup_data["packages"]["snap"] = snap_packages
        
        # Homebrew
        brew_packages = self._get_brew_packages()
        if brew_packages:
            backup_data["packages"]["brew"] = brew_packages
        
        # npm
        npm_packages = self._get_npm_packages()
        if npm_packages:
            backup_data["packages"]["npm"] = npm_packages
        
        # pipx
        pipx_packages = self._get_pipx_packages()
        if pipx_packages:
            backup_data["packages"]["pipx"] = pipx_packages
        
        # Cargo
        cargo_packages = self._get_cargo_packages()
        if cargo_packages:
            backup_data["packages"]["cargo"] = cargo_packages
        
        # Flatpak
        flatpak_packages = self._get_flatpak_packages()
        if flatpak_packages:
            backup_data["packages"]["flatpak"] = flatpak_packages
        
        # Gem
        gem_packages = self._get_gem_packages()
        if gem_packages:
            backup_data["packages"]["gem"] = gem_packages
        
        try:
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            return backup_file
        except Exception:
            return None
    
    def _get_apt_packages(self) -> Optional[List[str]]:
        """APTパッケージリストを取得"""
        try:
            result = subprocess.run(
                ["dpkg", "--get-selections"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                packages = []
                for line in result.stdout.splitlines():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == "install":
                        packages.append(parts[0])
                return packages
        except Exception:
            return None
    
    def _get_snap_packages(self) -> Optional[List[str]]:
        """Snapパッケージリストを取得"""
        try:
            result = subprocess.run(
                ["snap", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                packages = []
                for line in result.stdout.splitlines()[1:]:  # ヘッダーをスキップ
                    parts = line.split()
                    if parts:
                        packages.append(parts[0])
                return packages
        except Exception:
            return None
    
    def _get_brew_packages(self) -> Optional[List[str]]:
        """Homebrewパッケージリストを取得"""
        try:
            result = subprocess.run(
                ["brew", "list", "--formula"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout.splitlines()
        except Exception:
            return None
    
    def _get_npm_packages(self) -> Optional[List[str]]:
        """npmグローバルパッケージリストを取得"""
        try:
            result = subprocess.run(
                ["npm", "list", "-g", "--depth=0", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return list(data.get("dependencies", {}).keys())
        except Exception:
            return None
    
    def _get_pipx_packages(self) -> Optional[List[str]]:
        """pipxパッケージリストを取得"""
        try:
            result = subprocess.run(
                ["pipx", "list", "--short"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout.splitlines()
        except Exception:
            return None
    
    def _get_cargo_packages(self) -> Optional[List[str]]:
        """Cargoパッケージリストを取得"""
        try:
            result = subprocess.run(
                ["cargo", "install", "--list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                packages = []
                for line in result.stdout.splitlines():
                    if line and not line.startswith(" "):
                        package = line.split()[0]
                        packages.append(package)
                return packages
        except Exception:
            return None
    
    def _get_flatpak_packages(self) -> Optional[List[str]]:
        """Flatpakパッケージリストを取得"""
        try:
            result = subprocess.run(
                ["flatpak", "list", "--app", "--columns=application"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout.splitlines()
        except Exception:
            return None
    
    def _get_gem_packages(self) -> Optional[List[str]]:
        """Gemパッケージリストを取得"""
        try:
            result = subprocess.run(
                ["gem", "list", "--no-versions"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout.splitlines()
        except Exception:
            return None
    
    def list_backups(self) -> List[Path]:
        """バックアップファイルのリストを取得"""
        if not self.backup_dir.exists():
            return []
        
        return sorted(self.backup_dir.glob("packages_*.json"), reverse=True)
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """古いバックアップを削除
        
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
