"""Node Version Manager (nvm) updater"""

import subprocess
import os
from pathlib import Path
from typing import Optional

from .base import BaseUpdater


class NvmUpdater(BaseUpdater):
    """Node Version Manager (nvm) updater"""
    
    def get_name(self) -> str:
        return "nvm"
    
    def is_available(self) -> bool:
        # nvmはシェル関数なので、nvmディレクトリの存在で確認
        nvm_dir = Path.home() / ".nvm"
        return nvm_dir.exists() and (nvm_dir / "nvm.sh").exists()
    
    def perform_update(self) -> bool:
        """nvm更新実行"""
        name = self.get_name()
        
        if not self.is_available():
            self.logger.info(f"{name} がインストールされていません - スキップ")
            return True
        
        try:
            nvm_dir = Path.home() / ".nvm"
            
            # nvmの更新はgit pullで行う
            self.logger.info(f"{name} を更新中...")
            
            # nvmディレクトリでgit pullを実行
            result = subprocess.run(
                ["git", "pull"],
                cwd=str(nvm_dir),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.logger.success(f"{name} 更新完了")
                return True
            else:
                self.logger.warning(f"{name} 更新で問題が発生しました")
                return False
            
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"{name} 更新で問題が発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{name} 更新中に予期しないエラー: {e}")
            return False