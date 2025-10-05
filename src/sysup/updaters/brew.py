"""Homebrewパッケージマネージャupdater"""

import subprocess

from .base import BaseUpdater


class BrewUpdater(BaseUpdater):
    """Homebrewパッケージマネージャupdater"""

    def get_name(self) -> str:
        return "Homebrew"

    def is_available(self) -> bool:
        return self.command_exists("brew")

    def check_updates(self) -> int | None:
        """更新可能なパッケージ数を取得"""
        try:
            result = self.run_command(["brew", "outdated", "--quiet"], check=False)
            if result.returncode == 0:
                lines = [line for line in result.stdout.strip().split("\n") if line]
                return len(lines)
            return None
        except Exception:
            return None

    def perform_update(self) -> bool:
        """Homebrew更新実行"""
        name = self.get_name()

        if not self.is_available():
            self.logger.info(f"{name} がインストールされていません - スキップ")
            return True

        try:
            # パッケージリスト更新
            self.logger.info(f"{name} パッケージリストを更新中...")
            self.run_command(["brew", "update"])
            self.logger.success(f"{name} パッケージリスト更新完了")

            # 更新可能パッケージ数確認
            outdated_count = self.check_updates() or 0
            self.logger.info(f"更新可能な{name}パッケージ: {outdated_count} 個")

            if outdated_count > 0:
                # パッケージアップグレード
                self.logger.info(f"{name} パッケージをアップグレード中...")
                self.run_command(["brew", "upgrade"])
                self.logger.success(f"{name} アップグレード完了")
            else:
                self.logger.info(f"すべての{name}パッケージが最新です")

            # クリーンアップ
            self.logger.info(f"{name} クリーンアップ中...")
            self.run_command(["brew", "cleanup"], check=False)

            self.logger.success(f"{name} 更新完了")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"{name} 更新で問題が発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{name} 更新中に予期しないエラー: {e}")
            return False
