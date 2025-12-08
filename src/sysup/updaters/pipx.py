"""pipx管理ツールupdater."""

import subprocess

from .._typing_compat import override
from ..core.platform import is_windows
from .base import BaseUpdater


class PipxUpdater(BaseUpdater):
    """pipx管理ツールupdater."""

    @override
    def get_name(self) -> str:
        """Updater名を取得."""
        return "pipx"

    @override
    def is_available(self) -> bool:
        """pipxが利用可能かチェック."""
        return self.command_exists("pipx")

    @override
    def perform_update(self) -> bool:
        """pipx更新実行."""
        name = self.get_name()

        if not self.is_available():
            self.logger.info(f"{name} がインストールされていません - スキップ")
            return True

        try:
            self.logger.info(f"{name} パッケージを更新中...")
            pipx_cmd = "pipx.exe" if is_windows() else "pipx"
            self.run_command([pipx_cmd, "upgrade-all"])
            self.logger.success(f"{name} 更新完了")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"{name} 更新で問題が発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{name} 更新中に予期しないエラー: {e}")
            return False
