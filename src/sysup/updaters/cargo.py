"""Cargoパッケージupdater"""

import subprocess

from .base import BaseUpdater


class CargoUpdater(BaseUpdater):
    """Cargoパッケージupdater"""

    def get_name(self) -> str:
        return "Cargo"

    def is_available(self) -> bool:
        # cargoが存在すればOK（cargo-install-updateは後でチェック）
        return self.command_exists("cargo")

    def perform_update(self) -> bool:
        """Cargo更新実行"""
        name = self.get_name()

        if not self.command_exists("cargo"):
            self.logger.info(f"{name} がインストールされていません - スキップ")
            return True

        if not self.command_exists("cargo-install-update"):
            self.logger.info(f"cargo-install-updateがインストールされていません - {name}パッケージ更新をスキップ")
            return True

        try:
            self.logger.info(f"{name} パッケージを更新中...")
            self.run_command(["cargo", "install-update", "-a"])
            self.logger.success(f"{name} 更新完了")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"{name} 更新で問題が発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{name} 更新中に予期しないエラー: {e}")
            return False
