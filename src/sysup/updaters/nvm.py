"""Node Version Manager (nvm) updater."""

import subprocess
from pathlib import Path

from .._typing_compat import override
from .base import BaseUpdater


class NvmUpdater(BaseUpdater):
    """Node Version Manager (nvm) updater."""

    @override
    def get_name(self) -> str:
        """Updater名を取得."""
        return "nvm"

    @override
    def is_available(self) -> bool:
        """nvmが利用可能かチェック."""
        # nvmはシェル関数なので、bashシェル経由で確認
        try:
            result = subprocess.run(
                ["bash", "-c", "source ~/.nvm/nvm.sh 2>/dev/null && command -v nvm"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0 and result.stdout.strip() == "nvm"
        except Exception:
            return False

    @override
    def perform_update(self) -> bool:
        """nvm更新実行."""
        name = self.get_name()

        if not self.is_available():
            self.logger.info(f"{name} がインストールされていません - スキップ")
            return True

        try:
            nvm_dir = Path.home() / ".nvm"

            # gitリポジトリか確認
            if not (nvm_dir / ".git").exists():
                self.logger.info(f"{name} はgitリポジトリではありません - 更新をスキップ")
                return True

            # nvmの更新はgit pullで行う
            self.logger.info(f"{name} を更新中...")

            # nvmディレクトリでgit pullを実行
            if not self.dry_run:
                result = subprocess.run(["git", "pull"], cwd=str(nvm_dir), capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    self.logger.success(f"{name} 更新完了")
                    return True
                else:
                    self.logger.warning(f"{name} 更新で問題が発生しました")
                    return False
            else:
                self.logger.info(f"[DRY RUN] git pull in {nvm_dir}")
                return True

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"{name} 更新で問題が発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{name} 更新中に予期しないエラー: {e}")
            return False
