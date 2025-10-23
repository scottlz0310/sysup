"""システムチェック機能モジュール.

このモジュールはsysup実行前のシステム状態をチェックする機能を提供します。
ディスク容量、ネットワーク接続、sudo権限、多重実行防止などをチェックします。
"""

import os
import shutil
import subprocess
from datetime import date
from pathlib import Path

from .logging import SysupLogger
from .platform import is_windows


class SystemChecker:
    """システムチェッククラス.

    システム更新前の各種チェック機能を提供します。

    Attributes:
        logger: ロガーインスタンス.
        cache_dir: キャッシュディレクトリのパス.

    """

    def __init__(self, logger: SysupLogger, cache_dir: Path):
        """SystemCheckerを初期化する.

        Args:
            logger: ロガーインスタンス.
            cache_dir: キャッシュディレクトリのパス.

        """
        self.logger = logger
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def check_disk_space(self, min_space_gb: float = 1.0) -> bool:
        """ディスク容量をチェックする.

        Args:
            min_space_gb: 必要な最小空き容量(GB). デフォルトは1.0GB.

        Returns:
            十分な空き容量がある場合True、不足している場合False.

        Raises:
            Exception: ディスク容量の取得に失敗した場合.

        """
        try:
            _total, _used, free = shutil.disk_usage("/")
            free_gb = free / (1024**3)

            if free_gb < min_space_gb:
                self.logger.warning(f"利用可能なディスク容量が少なくなっています: {free_gb:.1f}GB")
                return False

            self.logger.info(f"ディスク容量: {free_gb:.1f}GB 利用可能")
            return True
        except Exception as e:
            self.logger.error(f"ディスク容量チェックエラー: {e}")
            return False

    def check_network(self) -> bool:
        """ネットワーク接続をチェックする.

        複数のDNSサーバーにpingを送信してネットワーク接続を確認します。

        Returns:
            ネットワーク接続が正常な場合True、問題がある場合False.

        """
        test_hosts = ["8.8.8.8", "1.1.1.1"]

        for host in test_hosts:
            try:
                if is_windows():
                    result = subprocess.run(["ping", "-n", "1", "-w", "1000", host], capture_output=True, timeout=3)
                else:
                    result = subprocess.run(["ping", "-c", "1", "-W", "3", host], capture_output=True, timeout=5)
                if result.returncode == 0:
                    self.logger.info("ネットワーク接続: OK")
                    return True
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                continue

        self.logger.warning("ネットワーク接続に問題があります")
        return False

    def check_daily_run(self) -> bool:
        """日次実行チェックを行う.

        最後に実行した日付を記録し、同日の重複実行を防ぎます。

        Returns:
            今日まだ実行されていない場合True、既に実行済みの場合False.

        """
        lock_file = self.cache_dir / "daily_run"
        today = date.today().isoformat()

        if lock_file.exists():
            try:
                last_run = lock_file.read_text().strip()
                if last_run == today:
                    self.logger.info(f"今日は既に実行済みです: {today}")
                    return False
            except Exception as exc:
                self.logger.warning(f"日次実行状態の読み込みに失敗しました: {exc}")

        # 今日の日付を記録
        lock_file.write_text(today)
        return True

    def check_reboot_required(self) -> bool:
        """再起動が必要かチェックする.

        Debian/Ubuntuシステムで再起動が必要かを判定します。

        Returns:
            再起動が必要な場合True、不要な場合False.

        """
        reboot_file = Path("/var/run/reboot-required")
        if reboot_file.exists():
            self.logger.warning("システムの再起動が必要です")

            pkgs_file = Path("/var/run/reboot-required.pkgs")
            if pkgs_file.exists():
                try:
                    packages = pkgs_file.read_text().strip().split("\n")
                    self.logger.info("再起動が必要なパッケージ:")
                    for pkg in packages:
                        self.logger.info(f"  - {pkg}")
                except Exception as exc:
                    self.logger.warning(f"再起動が必要なパッケージ一覧の読み込みに失敗しました: {exc}")
            return True

        return False

    def check_sudo_available(self) -> bool:
        """sudo権限の有無をチェックする.

        パスワードなしでsudoコマンドが実行可能かを確認します。

        Returns:
            sudo権限が利用可能な場合True、そうでない場合False.

        """
        try:
            result = subprocess.run(["sudo", "-n", "true"], capture_output=True, timeout=5)
            if result.returncode != 0:
                self.logger.warning("一部の操作には管理者権限が必要です")
                return False
            return True
        except Exception:
            return False

    def check_process_lock(self) -> bool:
        """プロセスロックをチェックする(多重実行防止).

        sysupが既に実行中でないかをチェックし、ロックファイルを作成します。

        Returns:
            実行可能な場合True、既に実行中の場合False.

        """
        lock_file = self.cache_dir / "sysup.lock"
        pid_file = self.cache_dir / "sysup.pid"

        if lock_file.exists() and pid_file.exists():
            try:
                old_pid = int(pid_file.read_text().strip())
                # プロセスが生きているかチェック
                os.kill(old_pid, 0)
                self.logger.error(f"sysupは既に実行中です (PID: {old_pid})")
                return False
            except (OSError, ValueError):
                # プロセスが存在しない場合は古いロックファイルを削除
                lock_file.unlink(missing_ok=True)
                pid_file.unlink(missing_ok=True)

        # 新しいロックを作成
        pid_file.write_text(str(os.getpid()))
        lock_file.touch()

        return True

    def cleanup_lock(self) -> None:
        """ロックファイルをクリーンアップする.

        プロセス終了時にロックファイルとPIDファイルを削除します。
        """
        lock_file = self.cache_dir / "sysup.lock"
        pid_file = self.cache_dir / "sysup.pid"

        lock_file.unlink(missing_ok=True)
        pid_file.unlink(missing_ok=True)
