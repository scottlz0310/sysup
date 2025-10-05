"""Updaterベースクラス"""

import subprocess
from abc import ABC, abstractmethod
from typing import Optional

from ..core.logging import SysupLogger


class BaseUpdater(ABC):
    """Updaterベースクラス"""
    
    def __init__(self, logger: SysupLogger, dry_run: bool = False):
        self.logger = logger
        self.dry_run = dry_run
    
    @abstractmethod
    def get_name(self) -> str:
        """表示名を返す"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """コマンドが利用可能かチェック"""
        pass
    
    @abstractmethod
    def perform_update(self) -> bool:
        """更新実行（成功: True, 失敗: False）"""
        pass
    
    def check_updates(self) -> Optional[int]:
        """更新可能なパッケージ数を返す（オプション）"""
        return None
    
    def pre_update(self) -> bool:
        """更新前処理（オプション）"""
        return True
    
    def post_update(self) -> bool:
        """更新後処理（オプション）"""
        return True
    
    def run_command(self, command: list[str], check: bool = True, timeout: int = 300) -> subprocess.CompletedProcess:
        """コマンド実行のヘルパーメソッド"""
        if self.dry_run:
            self.logger.info(f"[DRY RUN] {' '.join(command)}")
            return subprocess.CompletedProcess(command, 0, "", "")
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"コマンド実行エラー: {' '.join(command)}")
            self.logger.error(f"エラー出力: {e.stderr}")
            raise
        except subprocess.TimeoutExpired:
            self.logger.error(f"コマンドタイムアウト: {' '.join(command)}")
            raise
    
    def command_exists(self, command: str) -> bool:
        """コマンドが存在するかチェック"""
        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False