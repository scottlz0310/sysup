"""ファームウェア更新updater."""

import subprocess

from .base import BaseUpdater


class FirmwareUpdater(BaseUpdater):
    """ファームウェア更新updater."""

    def get_name(self) -> str:
        """Updater名を取得."""
        return "Firmware"

    def is_available(self) -> bool:
        """fwupdmgrが利用可能かチェック."""
        return self.command_exists("fwupdmgr")

    def perform_update(self) -> bool:
        """ファームウェア更新実行."""
        name = self.get_name()

        if not self.is_available():
            self.logger.info(f"{name} (fwupdmgr) がインストールされていません - スキップ")
            return True

        try:
            # メタデータ更新
            self.logger.info(f"{name} メタデータを更新中...")
            self.run_command(["fwupdmgr", "refresh"], check=False)

            # ファームウェア更新
            self.logger.info(f"{name} を確認中...")
            result = self.run_command(["fwupdmgr", "update", "-y"], check=False)

            if result.returncode == 0:
                self.logger.success(f"{name} 更新完了")
            else:
                self.logger.info(f"{name} 更新なし")

            return True

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"{name} 更新で問題が発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{name} 更新中に予期しないエラー: {e}")
            return False
