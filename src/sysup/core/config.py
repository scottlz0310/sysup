"""設定管理モジュール.

このモジュールはsysupの設定ファイルの読み込みと管理を行います。
TOMLフォーマットの設定ファイルをサポートし、各種updaterの有効/無効設定、
ログ設定、バックアップ設定、通知設定などを管理します。
"""

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class UpdaterConfig(BaseModel):
    """各updaterの有効/無効設定.

    各パッケージマネージャのupdaterを有効にするかどうかを制御します。

    Attributes:
        apt: APTパッケージマネージャ(Debian/Ubuntu)を有効にする.
        snap: Snapパッケージマネージャを有効にする.
        flatpak: Flatpakパッケージマネージャを有効にする.
        pipx: pipxパッケージマネージャを有効にする.
        uv: uv toolパッケージマネージャを有効にする.
        npm: npmパッケージマネージャを有効にする.
        nvm: nvmバージョンマネージャを有効にする.
        rustup: Rustupツールチェーンマネージャを有効にする.
        cargo: Cargoパッケージマネージャを有効にする.
        gem: Rubygemsパッケージマネージャを有効にする.
        brew: Homebrewパッケージマネージャを有効にする.
        firmware: ファームウェア更新を有効にする.

    """

    apt: bool = True
    snap: bool = True
    flatpak: bool = False
    pipx: bool = True
    uv: bool = True
    npm: bool = True
    nvm: bool = True
    rustup: bool = True
    cargo: bool = True
    gem: bool = False
    brew: bool = True
    firmware: bool = False


class AutoRunConfig(BaseModel):
    """自動実行設定.

    sysupの自動実行モードを設定します。

    Attributes:
        mode: 自動実行モード. 'disabled', 'enabled', 'enabled_with_auth'のいずれか.

    """

    mode: str = Field(default="disabled", pattern="^(disabled|enabled|enabled_with_auth)$")


class LoggingConfig(BaseModel):
    """ログ設定.

    ログファイルの保存場所、保持期間、ログレベルを設定します。

    Attributes:
        dir: ログディレクトリのパス. デフォルトは'~/.local/share/sysup'.
        retention_days: ログファイルの保持日数. デフォルトは30日.
        level: ログレベル. 'DEBUG', 'INFO', 'WARNING', 'ERROR'のいずれか.

    """

    dir: str = "~/.local/share/sysup"
    retention_days: int = 30
    level: str = "INFO"


class BackupConfig(BaseModel):
    """バックアップ設定.

    パッケージリストのバックアップに関する設定を管理します。

    Attributes:
        dir: バックアップディレクトリのパス. デフォルトは'~/.local/share/sysup/backups'.
        enabled: バックアップを有効にするかどうか. デフォルトはTrue.

    """

    dir: str = "~/.local/share/sysup/backups"
    enabled: bool = True


class NotificationConfig(BaseModel):
    """通知設定.

    デスクトップ通知の有効化と通知条件を設定します。

    Attributes:
        enabled: 通知機能を有効にするかどうか. デフォルトはTrue.
        on_success: 成功時に通知するかどうか. デフォルトはTrue.
        on_error: エラー時に通知するかどうか. デフォルトはTrue.
        on_warning: 警告時に通知するかどうか. デフォルトはFalse.

    """

    enabled: bool = True
    on_success: bool = True
    on_error: bool = True
    on_warning: bool = False


class GeneralConfig(BaseModel):
    """一般設定.

    sysupの動作全般に関する設定を管理します。

    Attributes:
        parallel_updates: 並列更新を有効にするかどうか. デフォルトはFalse.
        dry_run: ドライランモード(実際には実行しない). デフォルトはFalse.
        cache_dir: キャッシュディレクトリのパス. デフォルトは'~/.cache/sysup'.

    """

    parallel_updates: bool = False
    dry_run: bool = False
    cache_dir: str = "~/.cache/sysup"


class SysupConfig(BaseSettings):
    """sysup設定クラス.

    sysupのすべての設定を統合的に管理するメインの設定クラスです。
    TOMLファイルから設定を読み込み、各種機能で利用されます。

    Attributes:
        updaters: 各updaterの有効/無効設定.
        auto_run: 自動実行の設定.
        logging: ログ出力の設定.
        backup: バックアップの設定.
        notification: デスクトップ通知の設定.
        general: 一般的な動作設定.

    Examples:
        デフォルト設定で初期化:
            >>> config = SysupConfig()

        設定ファイルから読み込み:
            >>> config = SysupConfig.load_config(Path("~/.config/sysup/sysup.toml"))

    """

    updaters: UpdaterConfig = Field(default_factory=UpdaterConfig)
    auto_run: AutoRunConfig = Field(default_factory=AutoRunConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    backup: BackupConfig = Field(default_factory=BackupConfig)
    notification: NotificationConfig = Field(default_factory=NotificationConfig)
    general: GeneralConfig = Field(default_factory=GeneralConfig)

    @classmethod
    def load_config(cls, config_path: Path | None = None) -> "SysupConfig":
        """設定ファイルを読み込む.

        TOMLフォーマットの設定ファイルを読み込んでSysupConfigインスタンスを生成します。
        config_pathが指定されない場合、デフォルトの検索パスから設定ファイルを探します。

        Args:
            config_path: 設定ファイルのパス. Noneの場合はデフォルトパスを検索.

        Returns:
            読み込まれた設定を持つSysupConfigインスタンス.
            設定ファイルが見つからない場合はデフォルト設定を返す.

        Examples:
            >>> config = SysupConfig.load_config()  # デフォルトパスから検索
            >>> config = SysupConfig.load_config(Path("./sysup.toml"))  # 指定パス

        """
        if config_path is None:
            # 設定ファイルの検索パス
            config_paths = [
                Path.home() / ".config" / "sysup" / "sysup.toml",
                Path.home() / ".sysup.toml",
                Path("/etc/sysup/sysup.toml"),
            ]

            for path in config_paths:
                if path.exists():
                    config_path = path
                    break

        if config_path and config_path.exists():
            with open(config_path, "rb") as f:
                from typing import Any

                config_data: dict[str, Any] = tomllib.load(f)  # type: ignore
            return cls(**config_data)  # type: ignore

        # デフォルト設定を返す
        return cls()

    def get_log_dir(self) -> Path:
        """ログディレクトリのPathオブジェクトを返す.

        Returns:
            ログディレクトリの絶対パス. チルダ(~)は展開される.

        """
        return Path(self.logging.dir).expanduser()

    def get_backup_dir(self) -> Path:
        """バックアップディレクトリのPathオブジェクトを返す.

        Returns:
            バックアップディレクトリの絶対パス. チルダ(~)は展開される.

        """
        return Path(self.backup.dir).expanduser()

    def get_cache_dir(self) -> Path:
        """キャッシュディレクトリのPathオブジェクトを返す.

        Returns:
            キャッシュディレクトリの絶対パス. チルダ(~)は展開される.

        """
        return Path(self.general.cache_dir).expanduser()

    def is_updater_enabled(self, updater_name: str) -> bool:
        """指定されたupdaterが有効かチェックする.

        Args:
            updater_name: チェックするupdaterの名前(例: 'apt', 'brew').

        Returns:
            updaterが有効な場合True、無効または存在しない場合False.

        Examples:
            >>> config = SysupConfig()
            >>> config.is_updater_enabled("apt")
            True

        """
        return getattr(self.updaters, updater_name, False)
