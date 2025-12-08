"""Ruby Gemパッケージupdater."""

import subprocess

from .._typing_compat import override
from .base import BaseUpdater


class GemUpdater(BaseUpdater):
    """Ruby Gemパッケージupdater."""

    @override
    def get_name(self) -> str:
        """Updater名を取得."""
        return "Gem"

    @override
    def is_available(self) -> bool:
        """Gemが利用可能かチェック."""
        return self.command_exists("gem")

    @override
    def perform_update(self) -> bool:
        """Gem更新実行."""
        name = self.get_name()

        if not self.is_available():
            self.logger.info(f"{name} がインストールされていません - スキップ")
            return True

        try:
            self.logger.info(f"{name} パッケージを更新中...")
            # Windows環境では gem.cmd を使用
            from ..core.platform import is_windows

            gem_cmd = "gem.cmd" if is_windows() else "gem"
            self.run_command([gem_cmd, "update"])
            self.logger.success(f"{name} 更新完了")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"{name} 更新で問題が発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{name} 更新中に予期しないエラー: {e}")
            return False
