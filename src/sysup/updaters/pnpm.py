"""pnpmグローバルパッケージupdater."""

import subprocess

from .._typing_compat import override
from ..core.platform import is_windows
from .base import BaseUpdater


class PnpmUpdater(BaseUpdater):
    """pnpmグローバルパッケージupdater."""

    @override
    def get_name(self) -> str:
        """Updater名を取得."""
        return "pnpm"

    @override
    def is_available(self) -> bool:
        """pnpmが利用可能かチェック."""
        return self.command_exists("pnpm")

    @override
    def perform_update(self) -> bool:
        """pnpm更新実行."""
        name = self.get_name()

        if not self.is_available():
            self.logger.info(f"{name} がインストールされていません - スキップ")
            return True

        try:
            self.logger.info(f"{name} グローバルパッケージを更新中...")
            pnpm_cmd = "pnpm.cmd" if is_windows() else "pnpm"
            self.run_command([pnpm_cmd, "update", "-g"])
            self.logger.success(f"{name} 更新完了")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"{name} 更新で問題が発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{name} 更新中に予期しないエラー: {e}")
            return False
