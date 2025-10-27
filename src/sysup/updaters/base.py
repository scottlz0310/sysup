"""Updaterベースクラス.

このモジュールはすべてのupdaterが継承する抽象基底クラスを定義します。
各パッケージマネージャのupdaterはこのクラスを継承し、
必要なメソッドを実装します。
"""

import subprocess
from abc import ABC, abstractmethod

from ..core.logging import SysupLogger
from ..core.platform import is_windows


class BaseUpdater(ABC):
    """Updaterベースクラス.

    すべてのupdaterが継承する抽象基底クラスです。
    更新処理の共通インターフェースと便利なヘルパーメソッドを提供します。

    Attributes:
        logger: ロガーインスタンス.
        dry_run: ドライランモードフラグ. Trueの場合、実際のコマンドは実行されない.

    """

    def __init__(self, logger: SysupLogger, dry_run: bool = False):
        """BaseUpdaterを初期化する.

        Args:
            logger: ロガーインスタンス.
            dry_run: ドライランモード. デフォルトはFalse.

        """
        self.logger = logger
        self.dry_run = dry_run

    @abstractmethod
    def get_name(self) -> str:
        """updaterの表示名を返す.

        Returns:
            updaterの名前(例: "APT", "Homebrew").

        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """コマンドが利用可能かチェックする.

        パッケージマネージャのコマンドがシステムにインストールされているかを確認します。

        Returns:
            コマンドが利用可能な場合True、そうでない場合False.

        """
        pass

    @abstractmethod
    def perform_update(self) -> bool:
        """更新を実行する.

        パッケージマネージャの更新処理を実行します。
        このメソッドは各updaterで実装する必要があります。

        Returns:
            更新成功時True、失敗時False.

        """
        pass

    def check_updates(self) -> int | None:
        """更新可能なパッケージ数を返す.

        このメソッドはオプションであり、実装しなくても構いません。

        Returns:
            更新可能なパッケージ数. 不明な場合はNone.

        """
        return None

    def pre_update(self) -> bool:
        """更新前処理を実行する.

        このメソッドはオプションであり、必要に応じてオーバーライドできます。

        Returns:
            前処理成功時True、失敗時False.

        """
        return True

    def post_update(self) -> bool:
        """更新後処理を実行する.

        このメソッドはオプションであり、必要に応じてオーバーライドできます。

        Returns:
            後処理成功時True、失敗時False.

        """
        return True

    def run_command(self, command: list[str], check: bool = True, timeout: int = 300) -> subprocess.CompletedProcess:
        """コマンドを実行するヘルパーメソッド.

        dry_runモードの場合、実際にはコマンドを実行せずログに出力するのみです。

        Args:
            command: 実行するコマンドのリスト.
            check: コマンド失敗時に例外を発生させるかどうか. デフォルトはTrue.
            timeout: タイムアウト秒数. デフォルトは300秒.

        Returns:
            コマンド実行結果のCompletedProcessオブジェクト.

        Raises:
            subprocess.CalledProcessError: コマンドが非ゼロステータスで終了した場合(checkがTrueのとき).
            subprocess.TimeoutExpired: コマンドがタイムアウトした場合.

        """
        self.logger.debug(f"実行コマンド: {' '.join(command)}")

        if self.dry_run:
            self.logger.info(f"[DRY RUN] {' '.join(command)}")
            return subprocess.CompletedProcess(command, 0, "", "")

        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=check)
            if result.stdout:
                self.logger.debug(f"標準出力: {result.stdout.strip()}")
            if result.stderr:
                self.logger.debug(f"標準エラー: {result.stderr.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            self.logger.error(f"コマンド実行エラー: {' '.join(command)}")
            self.logger.error(f"エラー出力: {e.stderr}")
            raise
        except subprocess.TimeoutExpired:
            self.logger.error(f"コマンドタイムアウト: {' '.join(command)}")
            raise

    def command_exists(self, command: str) -> bool:
        """コマンドが存在するかチェックする.

        Args:
            command: チェックするコマンド名.

        Returns:
            コマンドが存在する場合True、そうでない場合False.

        """
        try:
            if is_windows():
                result = subprocess.run(["where", command], capture_output=True, timeout=5)
            else:
                result = subprocess.run(["which", command], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
