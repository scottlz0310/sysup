"""Flatpakパッケージマネージャupdater."""

import subprocess

from .base import BaseUpdater


class FlatpakUpdater(BaseUpdater):
    """Flatpakパッケージマネージャupdater."""

    def get_name(self) -> str:
        """Updater名を取得."""
        return "Flatpak"

    def is_available(self) -> bool:
        """Flatpakが利用可能かチェック."""
        return self.command_exists("flatpak")

    def perform_update(self) -> bool:
        """Flatpak更新実行."""
        name = self.get_name()

        if not self.is_available():
            self.logger.info(f"{name} がインストールされていません - スキップ")
            return True

        try:
            self.logger.info(f"{name} パッケージを更新中...")
            self.run_command(["flatpak", "update", "-y"])
            self.logger.success(f"{name} 更新完了")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"{name} 更新で問題が発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{name} 更新中に予期しないエラー: {e}")
            return False
