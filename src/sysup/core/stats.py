"""統計情報管理モジュール.

このモジュールは更新処理の実行統計を記録・管理する機能を提供します。
成功・失敗・スキップした更新の記録、実行時間の計測、統計サマリーの表示を行います。
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .logging import SysupLogger


@dataclass
class UpdateStats:
    """更新統計情報.

    更新処理の実行結果を集計するためのデータクラスです。

    Attributes:
        start_time: 更新処理の開始時刻(Unix時刻).
        end_time: 更新処理の終了時刻(Unix時刻). 未完了の場合None.
        success_count: 成功した更新の数.
        failure_count: 失敗した更新の数.
        skip_count: スキップした更新の数.
        successful_updaters: 成功したupdaterのリスト.
        failed_updaters: 失敗したupdaterと理由の辞書.
        skipped_updaters: スキップしたupdaterと理由の辞書.

    """

    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    success_count: int = 0
    failure_count: int = 0
    skip_count: int = 0
    successful_updaters: list[str] = field(default_factory=list)
    failed_updaters: dict[str, str] = field(default_factory=dict)
    skipped_updaters: dict[str, str] = field(default_factory=dict)

    def record_success(self, updater: str) -> None:
        """成功を記録する.

        Args:
            updater: 成功したupdaterの名前.

        """
        self.successful_updaters.append(updater)
        self.success_count += 1

    def record_failure(self, updater: str, reason: str = "不明なエラー") -> None:
        """失敗を記録する.

        Args:
            updater: 失敗したupdaterの名前.
            reason: 失敗の理由. デフォルトは"不明なエラー".

        """
        self.failed_updaters[updater] = reason
        self.failure_count += 1

    def record_skip(self, updater: str, reason: str = "利用不可") -> None:
        """スキップを記録する.

        Args:
            updater: スキップしたupdaterの名前.
            reason: スキップの理由. デフォルトは"利用不可".

        """
        self.skipped_updaters[updater] = reason
        self.skip_count += 1

    def finish(self) -> None:
        """統計情報を完了する.

        終了時刻を記録します。
        """
        self.end_time = time.time()

    @property
    def duration(self) -> float:
        """実行時間を秒単位で返す.

        Returns:
            開始時刻から終了時刻(または現在時刻)までの秒数.

        """
        end = self.end_time or time.time()
        return end - self.start_time

    @property
    def duration_formatted(self) -> str:
        """フォーマットされた実行時間を返す.

        Returns:
            "N分M秒"または"M秒"の形式の文字列.

        """
        duration = int(self.duration)
        minutes = duration // 60
        seconds = duration % 60

        if minutes > 0:
            return f"{minutes}分{seconds}秒"
        else:
            return f"{seconds}秒"


class StatsManager:
    """統計情報管理クラス.

    更新処理の統計を収集・表示・保存するマネージャークラスです。

    Attributes:
        logger: ロガーインスタンス.
        stats: 統計情報を保持するUpdateStatsインスタンス.

    """

    def __init__(self, logger: SysupLogger):
        """StatsManagerを初期化する.

        Args:
            logger: ロガーインスタンス.

        """
        self.logger = logger
        self.stats = UpdateStats()

    def record_success(self, updater: str) -> None:
        """成功を記録する.

        Args:
            updater: 成功したupdaterの名前.

        """
        self.stats.record_success(updater)

    def record_failure(self, updater: str, reason: str = "不明なエラー") -> None:
        """失敗を記録する.

        Args:
            updater: 失敗したupdaterの名前.
            reason: 失敗の理由. デフォルトは"不明なエラー".

        """
        self.stats.record_failure(updater, reason)

    def record_skip(self, updater: str, reason: str = "利用不可") -> None:
        """スキップを記録する.

        Args:
            updater: スキップしたupdaterの名前.
            reason: スキップの理由. デフォルトは"利用不可".

        """
        self.stats.record_skip(updater, reason)

    def show_summary(self) -> None:
        """統計サマリーを表示する.

        更新処理の実行結果を整形してコンソールに表示します。
        """
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

    def save_to_log(self, log_dir: Path) -> None:
        """統計情報をログファイルに保存する.

        Args:
            log_dir: ログディレクトリのパス.

        """
        log_file = log_dir / "update.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_dir.mkdir(parents=True, exist_ok=True)

        with open(log_file, "a", encoding="utf-8") as f:
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
