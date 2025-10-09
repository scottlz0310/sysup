"""Snapパッケージマネージャupdater."""

import subprocess

from .base import BaseUpdater


class SnapUpdater(BaseUpdater):
    """Snapパッケージマネージャupdater."""

    def get_name(self) -> str:
        """Updater名を取得."""
        return "Snap"

    def is_available(self) -> bool:
        """Snapが利用可能かチェック."""
        return self.command_exists("snap")

    def check_updates(self) -> int | None:
        """更新可能なパッケージ数を取得."""
        try:
            result = self.run_command(["snap", "list"], check=False)
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                return max(0, len(lines) - 1) if lines[0] else 0
            return None
        except Exception:
            return None

    def perform_update(self) -> bool:
        """Snap更新実行."""
        name = self.get_name()

        if not self.is_available():
            self.logger.info(f"{name} がインストールされていません - スキップ")
            return True

        try:
            snap_count = self.check_updates() or 0
            self.logger.info(f"{name} パッケージ数: {snap_count}")

            # Snap更新
            self.logger.info(f"{name} パッケージを更新中...")
            self.run_command(["sudo", "snap", "refresh"])
            self.logger.success(f"{name} 更新完了")

            return True

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"{name} 更新で問題が発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{name} 更新中に予期しないエラー: {e}")
            return False
