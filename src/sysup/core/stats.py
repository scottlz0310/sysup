"""統計情報管理モジュール"""

import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from .logging import SysupLogger


@dataclass
class UpdateStats:
    """更新統計情報"""
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    success_count: int = 0
    failure_count: int = 0
    skip_count: int = 0
    successful_updaters: List[str] = field(default_factory=list)
    failed_updaters: Dict[str, str] = field(default_factory=dict)
    skipped_updaters: Dict[str, str] = field(default_factory=dict)
    
    def record_success(self, updater: str) -> None:
        """成功を記録"""
        self.successful_updaters.append(updater)
        self.success_count += 1
    
    def record_failure(self, updater: str, reason: str = "不明なエラー") -> None:
        """失敗を記録"""
        self.failed_updaters[updater] = reason
        self.failure_count += 1
    
    def record_skip(self, updater: str, reason: str = "利用不可") -> None:
        """スキップを記録"""
        self.skipped_updaters[updater] = reason
        self.skip_count += 1
    
    def finish(self) -> None:
        """統計情報を完了"""
        self.end_time = time.time()
    
    @property
    def duration(self) -> float:
        """実行時間（秒）"""
        end = self.end_time or time.time()
        return end - self.start_time
    
    @property
    def duration_formatted(self) -> str:
        """フォーマットされた実行時間"""
        duration = int(self.duration)
        minutes = duration // 60
        seconds = duration % 60
        
        if minutes > 0:
            return f"{minutes}分{seconds}秒"
        else:
            return f"{seconds}秒"


class StatsManager:
    """統計情報管理クラス"""
    
    def __init__(self, logger: SysupLogger):
        self.logger = logger
        self.stats = UpdateStats()
    
    def record_success(self, updater: str) -> None:
        """成功を記録"""
        self.stats.record_success(updater)
    
    def record_failure(self, updater: str, reason: str = "不明なエラー") -> None:
        """失敗を記録"""
        self.stats.record_failure(updater, reason)
    
    def record_skip(self, updater: str, reason: str = "利用不可") -> None:
        """スキップを記録"""
        self.stats.record_skip(updater, reason)
    
    def show_summary(self) -> None:
        """統計サマリーを表示"""
        self.stats.finish()
        
        self.logger.section("更新サマリー")
        
        # 成功した更新
        if self.stats.success_count > 0:
            self.logger.success(f"成功: {self.stats.success_count} 件")
            for updater in self.stats.successful_updaters:
                self.logger.info(f"  ✓ {updater}")
        
        # 失敗した更新
        if self.stats.failure_count > 0:
            self.logger.error(f"失敗: {self.stats.failure_count} 件")
            for updater, reason in self.stats.failed_updaters.items():
                self.logger.error(f"  ✗ {updater}: {reason}")
        
        # スキップした更新
        if self.stats.skip_count > 0:
            self.logger.info(f"スキップ: {self.stats.skip_count} 件")
            for updater, reason in self.stats.skipped_updaters.items():
                self.logger.info(f"  - {updater}: {reason}")
        
        # 実行時間
        self.logger.info(f"実行時間: {self.stats.duration_formatted}")
        
        # 総合結果
        total_count = self.stats.success_count + self.stats.failure_count
        if total_count == 0:
            self.logger.warning("実行された更新はありませんでした")
        elif self.stats.failure_count == 0:
            self.logger.success("全ての更新が正常に完了しました")
        else:
            self.logger.warning(f"{self.stats.failure_count} 件の更新で問題が発生しました")
    
    def save_to_log(self, log_dir) -> None:
        """統計情報をログファイルに保存"""
        log_file = log_dir / "update.log"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_dir.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"=== Update Summary - {timestamp} ===\n")
            f.write(f"Success: {self.stats.success_count} items\n")
            for updater in self.stats.successful_updaters:
                f.write(f"  SUCCESS: {updater}\n")
            
            f.write(f"Failed: {self.stats.failure_count} items\n")
            for updater, reason in self.stats.failed_updaters.items():
                f.write(f"  FAILED: {updater} - {reason}\n")
            
            f.write(f"Skipped: {self.stats.skip_count} items\n")
            for updater, reason in self.stats.skipped_updaters.items():
                f.write(f"  SKIPPED: {updater} - {reason}\n")
            
            f.write(f"Duration: {int(self.stats.duration)} seconds\n")
            f.write("\n")