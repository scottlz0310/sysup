"""APTパッケージマネージャupdater.

Debian/UbuntuシステムのAPT (Advanced Package Tool)パッケージマネージャを
使用したシステムパッケージの更新機能を提供します。
"""

import subprocess

from .base import BaseUpdater


class AptUpdater(BaseUpdater):
    """APTパッケージマネージャupdater.

    apt updateでパッケージリストを更新し、
    apt full-upgradeでシステムパッケージを更新します。
    """

    def get_name(self) -> str:
        """updaterの名前を返す.

        Returns:
            "APT"固定.

        """
        return "APT"

    def is_available(self) -> bool:
        """aptコマンドが利用可能かチェックする.

        Returns:
            aptコマンドが存在する場合True.

        """
        return self.command_exists("apt")

    def check_updates(self) -> int | None:
        """更新可能なパッケージ数を取得する.

        Returns:
            更新可能なパッケージ数. 取得失敗時はNone.

        """
        try:
            result = self.run_command(["apt", "list", "--upgradable"], check=False)
            # ヘッダー行を除いた行数
            lines = result.stdout.strip().split("\n")
            return max(0, len(lines) - 1) if lines[0] else 0
        except Exception:
            return None

    def perform_update(self) -> bool:
        """APT更新を実行する.

        apt update, apt upgrade, apt autoremove, apt autocleanを実行します。

        Returns:
            更新成功時True、失敗時False.

        """
        name = self.get_name()

        if not self.is_available():
            self.logger.info(f"{name} がインストールされていません - スキップ")
            return True

        try:
            # パッケージリスト更新
            self.logger.info(f"{name} パッケージリストを更新中...")
            self.run_command(["sudo", "apt", "update"])
            self.logger.success(f"{name} パッケージリスト更新完了")

            # 更新可能パッケージ数確認
            upgradable_count = self.check_updates() or 0
            self.logger.info(f"更新可能パッケージ数: {upgradable_count}")

            if upgradable_count > 0:
                # パッケージアップグレード
                self.logger.info(f"{name} パッケージをアップグレード中...")
                self.run_command(["sudo", "apt", "upgrade", "-y"])
                self.logger.success(f"{name} パッケージアップグレード完了")
            else:
                self.logger.info("更新可能パッケージがないため、アップグレードをスキップします")

            # 不要パッケージ削除
            self.logger.info(f"{name} 不要なパッケージを削除中...")
            result = self.run_command(["sudo", "apt", "autoremove", "-y"], check=False)
            if result.returncode == 0:
                self.logger.success(f"{name} 不要パッケージ削除完了")
            else:
                self.logger.warning(f"{name} 不要パッケージ削除で問題が発生しました")

            # クリーンアップ
            self.run_command(["sudo", "apt", "autoclean"], check=False)

            self.logger.success(f"{name} 更新完了")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"{name} 更新で問題が発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{name} 更新中に予期しないエラー: {e}")
            return False
