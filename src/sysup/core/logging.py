"""ログ機能モジュール.

このモジュールはsysupのログ出力機能を提供します。
Richライブラリを使用した美しいコンソール出力と、
ファイルへのログ記録を統合的に管理します。
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler


class SysupLogger:
    """sysup専用ロガー.

    コンソール出力とファイル出力を統合したロガークラスです。
    Richライブラリを使用した美しい出力と、古いログの自動削除機能を持ちます。

    Attributes:
        log_dir: ログファイルの保存ディレクトリ.
        retention_days: ログファイルの保持日数.
        console: Richのコンソールインスタンス.
        logger: Pythonの標準ロガーインスタンス.

    """

    def __init__(self, log_dir: Path, level: str = "INFO", retention_days: int = 30):
        """SysupLoggerを初期化する.

        Args:
            log_dir: ログファイルの保存ディレクトリ.
            level: ログレベル. デフォルトは"INFO".
            retention_days: ログファイルの保持日数. デフォルトは30日.

        """
        self.log_dir: Path = log_dir
        self.retention_days: int = retention_days
        self.console: Console = Console()
        self.logger: logging.Logger = self._setup_logger(level)
        self._rotate_logs()

    def _setup_logger(self, level: str) -> logging.Logger:
        """ロガーをセットアップする.

        Args:
            level: ログレベル文字列.

        Returns:
            設定済みのロガーインスタンス.

        """
        logger = logging.getLogger("sysup")
        logger.setLevel(getattr(logging, level.upper()))  # type: ignore

        # 既存のハンドラーをクリア
        logger.handlers.clear()

        # コンソールハンドラー（Rich使用）
        console_handler = RichHandler(console=self.console, show_time=True, show_path=False, markup=True)
        console_handler.setLevel(getattr(logging, level.upper()))  # type: ignore
        logger.addHandler(console_handler)

        # ファイルハンドラー
        self.log_dir.mkdir(parents=True, exist_ok=True)
        log_file = self.log_dir / f"sysup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        return logger

    def _rotate_logs(self) -> None:
        """古いログファイルを削除する.

        保持日数を超えたログファイルを自動的に削除します。
        """
        if not self.log_dir.exists():
            return

        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        for log_file in self.log_dir.glob("sysup_*.log"):
            try:
                # ファイル名から日付を抽出 (sysup_YYYYMMDD_HHMMSS.log)
                file_date_str = log_file.stem.split("_")[1]
                file_date = datetime.strptime(file_date_str, "%Y%m%d")

                if file_date < cutoff_date:
                    log_file.unlink()
                    self.logger.debug(f"古いログファイルを削除: {log_file}")
            except (ValueError, IndexError):
                # ファイル名が予期した形式でない場合はスキップ
                continue
            except Exception as e:
                self.logger.debug(f"ログファイル削除エラー: {e}")
                continue

    def success(self, message: str) -> None:
        """成功メッセージを出力する.

        Args:
            message: 出力するメッセージ.

        """
        self.console.print(f"[green]✓[/green] {message}")
        self.logger.info(f"SUCCESS: {message}")

    def info(self, message: str) -> None:
        """情報メッセージを出力する.

        Args:
            message: 出力するメッセージ.

        """
        self.console.print(f"[blue]ℹ[/blue] {message}")
        self.logger.info(message)

    def debug(self, message: str) -> None:
        """デバッグメッセージを出力する.

        Args:
            message: 出力するメッセージ.

        """
        self.console.print(f"[dim]🔍 {message}[/dim]")
        self.logger.debug(message)

    def warning(self, message: str) -> None:
        """警告メッセージを出力する.

        Args:
            message: 出力するメッセージ.

        """
        self.console.print(f"[yellow]⚠[/yellow] {message}")
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """エラーメッセージを出力する.

        Args:
            message: 出力するメッセージ.

        """
        self.console.print(f"[red]✗[/red] {message}", style="bold red")
        self.logger.error(message)

    def section(self, title: str) -> None:
        """セクションタイトルを表示する.

        Args:
            title: セクションのタイトル.

        """
        self.console.print(f"\n[cyan]=== {title} ===[/cyan]")
        self.logger.info(f"SECTION: {title}")

    def progress_step(self, current: int, total: int, message: str) -> None:
        """進捗ステップを表示する.

        Args:
            current: 現在のステップ番号.
            total: 全ステップ数.
            message: 表示するメッセージ.

        """
        percentage = int((current / total) * 100)
        self.console.print(f"[cyan]ステップ {current}/{total}:[/cyan] {message} ({percentage}%)")
        self.logger.info(f"STEP {current}/{total}: {message}")

    def close(self) -> None:
        """ロガーのハンドラーをクローズする.

        Windows環境でファイルロックを解放するために使用します.
        """
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)


def get_logger(log_dir: Path | None = None, level: str = "INFO") -> SysupLogger:
    """ロガーインスタンスを取得する.

    Args:
        log_dir: ログディレクトリのパス. Noneの場合はデフォルトパス.
        level: ログレベル. デフォルトは"INFO".

    Returns:
        設定済みのSysupLoggerインスタンス.

    Examples:
        >>> logger = get_logger()
        >>> logger.info("情報メッセージ")

    """
    if log_dir is None:
        log_dir = Path.home() / ".local" / "share" / "sysup"

    return SysupLogger(log_dir, level)
