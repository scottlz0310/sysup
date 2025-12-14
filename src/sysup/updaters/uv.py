"""uv tool管理ツールupdater."""

import subprocess

from .._typing_compat import override
from .base import BaseUpdater


class UvUpdater(BaseUpdater):
    """uv tool管理ツールupdater."""

    @override
    def get_name(self) -> str:
        """Updater名を取得."""
        return "uv tool"

    @override
    def is_available(self) -> bool:
        """uvが利用可能かチェック."""
        return self.command_exists("uv")

    def _self_update(self) -> bool:
        """uv自体を更新."""
        try:
            self.logger.info("uv 自体を更新中...")
            self.run_command(["uv", "self", "update"])
            self.logger.success("uv 更新完了")
            return True
        except subprocess.CalledProcessError as e:
            # standalone以外のインストール方法（pip, brew等）ではself updateが使えない
            self.logger.warning(f"uv self update をスキップ（別の方法でインストールされた可能性）: {e}")
            return True  # 継続可能
        except Exception as e:
            self.logger.warning(f"uv self update で予期しないエラー: {e}")
            return True  # 継続可能

    @override
    def perform_update(self) -> bool:
        """Uv tool更新実行."""
        name = self.get_name()

        if not self.is_available():
            self.logger.info(f"{name} がインストールされていません - スキップ")
            return True

        try:
            # まずuv自体を更新
            self._self_update()

            # 次にuvでインストールしたツールを更新
            self.logger.info(f"{name} パッケージを更新中...")
            self.run_command(["uv", "tool", "upgrade", "--all"])
            self.logger.success(f"{name} 更新完了")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"{name} 更新で問題が発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{name} 更新中に予期しないエラー: {e}")
            return False
