"""設定管理モジュール"""

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class UpdaterConfig(BaseModel):
    """各updaterの設定"""

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
    """自動実行設定"""

    mode: str = Field(default="disabled", pattern="^(disabled|enabled|enabled_with_auth)$")


class LoggingConfig(BaseModel):
    """ログ設定"""

    dir: str = "~/.local/share/sysup"
    retention_days: int = 30
    level: str = "INFO"


class BackupConfig(BaseModel):
    """バックアップ設定"""

    dir: str = "~/.local/share/sysup/backups"
    enabled: bool = True


class NotificationConfig(BaseModel):
    """通知設定"""

    enabled: bool = True
    on_success: bool = True
    on_error: bool = True
    on_warning: bool = False


class GeneralConfig(BaseModel):
    """一般設定"""

    parallel_updates: bool = False
    dry_run: bool = False
    cache_dir: str = "~/.cache/sysup"


class SysupConfig(BaseSettings):
    """sysup設定クラス"""

    updaters: UpdaterConfig = Field(default_factory=UpdaterConfig)
    auto_run: AutoRunConfig = Field(default_factory=AutoRunConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    backup: BackupConfig = Field(default_factory=BackupConfig)
    notification: NotificationConfig = Field(default_factory=NotificationConfig)
    general: GeneralConfig = Field(default_factory=GeneralConfig)

    @classmethod
    def load_config(cls, config_path: Path | None = None) -> "SysupConfig":
        """設定ファイルを読み込み"""
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
                config_data = tomllib.load(f)
            return cls(**config_data)

        # デフォルト設定を返す
        return cls()

    def get_log_dir(self) -> Path:
        """ログディレクトリのPathオブジェクトを返す"""
        return Path(self.logging.dir).expanduser()

    def get_backup_dir(self) -> Path:
        """バックアップディレクトリのPathオブジェクトを返す"""
        return Path(self.backup.dir).expanduser()

    def get_cache_dir(self) -> Path:
        """キャッシュディレクトリのPathオブジェクトを返す"""
        return Path(self.general.cache_dir).expanduser()

    def is_updater_enabled(self, updater_name: str) -> bool:
        """指定されたupdaterが有効かチェック"""
        return getattr(self.updaters, updater_name, False)
