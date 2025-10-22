"""Scoopパッケージマネージャupdater.

Windows環境でのScoopパッケージマネージャを使用した
パッケージ更新機能を提供します。
"""

import subprocess

from ..core.platform import is_windows
from .base import BaseUpdater


class ScoopUpdater(BaseUpdater):
    """Scoopパッケージマネージャupdater.

    Scoop自体とインストール済みパッケージを更新します。
    """

    def get_name(self) -> str:
        """updaterの名前を返す.

        Returns:
            "Scoop"固定.
        """
        return "Scoop"

    def is_available(self) -> bool:
        """scoopコマンドが利用可能かチェックする.

        Returns:
            scoopコマンドが存在する場合True.
        """
        if not is_windows():
            return False
        return self.command_exists("scoop")

    def perform_update(self) -> bool:
        """Scoop更新を実行する.

        scoop update, scoop update *, scoop cleanup *を実行します。

        Returns:
            更新成功時True、失敗時False.
        """
        name = self.get_name()

        if not self.is_available():
            self.logger.info(f"{name} がインストールされていません - スキップ")
            return True

        try:
            # Scoop自体を更新
            self.logger.info(f"{name} 自体を更新中...")
            self.run_command(["scoop", "update"])
            self.logger.success(f"{name} 自体の更新完了")

            # インストール済みパッケージを更新
            self.logger.info(f"{name} パッケージを更新中...")
            self.run_command(["scoop", "update", "*"])
            self.logger.success(f"{name} パッケージ更新完了")

            # 古いバージョンをクリーンアップ
            self.logger.info(f"{name} 古いバージョンをクリーンアップ中...")
            self.run_command(["scoop", "cleanup", "*"], check=False)
            self.logger.success(f"{name} クリーンアップ完了")

            self.logger.success(f"{name} 更新完了")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"{name} 更新で問題が発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{name} 更新中に予期しないエラー: {e}")
            return False
