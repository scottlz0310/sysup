"""sysup自身の更新機能.

このモジュールはsysup自身のバージョンチェックと自動更新機能を提供します。
"""

import os
import subprocess
import sys
from pathlib import Path

from .logging import SysupLogger


class SelfUpdater:
    """sysup自身の更新を管理するクラス."""

    def __init__(self, logger: SysupLogger, cache_dir: Path):
        """SelfUpdaterを初期化する.

        Args:
            logger: ロガーインスタンス.
            cache_dir: キャッシュディレクトリのパス.

        """
        self.logger = logger
        self.cache_dir = cache_dir

    def update_self(self) -> bool:
        """sysup自身を更新する.

        Returns:
            更新された場合True、既に最新の場合False.

        """
        try:
            result = subprocess.run(
                ["uv", "tool", "upgrade", "sysup"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                self.logger.debug(f"sysup更新チェック失敗: {result.stderr}")
                return False

            # 出力から更新されたかを判断
            output = result.stdout + result.stderr
            if "Updated" in output or "Installed" in output:
                self.logger.info("✓ sysupが更新されました")
                return True
            else:
                self.logger.debug("sysupは既に最新です")
                return False
        except Exception as e:
            self.logger.debug(f"sysup更新エラー: {e}")
            return False

    def restart_self(self) -> None:
        """更新後にsysupを再実行する.

        現在のプロセスを新しいバージョンで置き換えます。
        この関数は戻りません。

        """
        self.logger.info("更新されたsysupで再実行中...")
        os.execv(sys.executable, [sys.executable, "-m", "sysup.cli", *sys.argv[1:]])

    def check_and_update(self) -> bool:
        """sysup自身を更新し、更新された場合は再実行する.

        Returns:
            更新が実行された場合True（実際には再実行されるため戻らない）.

        """
        if self.update_self():
            self.restart_self()  # この関数は戻らない
            return True
        return False
