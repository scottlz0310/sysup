"""ログ機能モジュール"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler
from rich.text import Text


class SysupLogger:
    """sysup専用ロガー"""
    
    def __init__(self, log_dir: Path, level: str = "INFO"):
        self.log_dir = log_dir
        self.console = Console()
        self.logger = self._setup_logger(level)
        
    def _setup_logger(self, level: str) -> logging.Logger:
        """ロガーのセットアップ"""
        logger = logging.getLogger("sysup")
        logger.setLevel(getattr(logging, level.upper()))
        
        # 既存のハンドラーをクリア
        logger.handlers.clear()
        
        # コンソールハンドラー（Rich使用）
        console_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=False,
            markup=True
        )
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
        
        # ファイルハンドラー
        self.log_dir.mkdir(parents=True, exist_ok=True)
        log_file = self.log_dir / f"sysup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def success(self, message: str) -> None:
        """成功メッセージ"""
        self.console.print(f"[green]✓[/green] {message}")
        self.logger.info(f"SUCCESS: {message}")
    
    def info(self, message: str) -> None:
        """情報メッセージ"""
        self.console.print(f"[blue]ℹ[/blue] {message}")
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """警告メッセージ"""
        self.console.print(f"[yellow]⚠[/yellow] {message}")
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """エラーメッセージ"""
        self.console.print(f"[red]✗[/red] {message}", style="bold red")
        self.logger.error(message)
    
    def section(self, title: str) -> None:
        """セクション表示"""
        self.console.print(f"\n[cyan]=== {title} ===[/cyan]")
        self.logger.info(f"SECTION: {title}")
    
    def progress_step(self, current: int, total: int, message: str) -> None:
        """プログレス表示"""
        percentage = int((current / total) * 100)
        self.console.print(f"[cyan]ステップ {current}/{total}:[/cyan] {message} ({percentage}%)")
        self.logger.info(f"STEP {current}/{total}: {message}")


def get_logger(log_dir: Optional[Path] = None, level: str = "INFO") -> SysupLogger:
    """ロガーインスタンスを取得"""
    if log_dir is None:
        log_dir = Path.home() / ".local" / "share" / "sysup"
    
    return SysupLogger(log_dir, level)