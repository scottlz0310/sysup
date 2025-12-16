"""設定モジュールのテスト"""

import tempfile
from pathlib import Path

from sysup.core.config import SysupConfig


def test_default_config():
    """デフォルト設定のテスト"""
    config = SysupConfig()

    assert config.updaters.apt is True
    assert config.updaters.snap is True
    assert config.updaters.flatpak is True
    assert config.auto_run.mode == "disabled"
    assert config.logging.level == "INFO"
    assert config.backup.enabled is True


def test_load_config_from_file():
    """ファイルからの設定読み込みテスト"""
    config_data = """
[updaters]
apt = false
snap = true

[auto_run]
mode = "enabled"

[logging]
level = "DEBUG"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(config_data)
        config_path = Path(f.name)

    try:
        config = SysupConfig.load_config(config_path)

        assert config.updaters.apt is False
        assert config.updaters.snap is True
        assert config.auto_run.mode == "enabled"
        assert config.logging.level == "DEBUG"
    finally:
        config_path.unlink()


def test_is_updater_enabled():
    """updater有効チェックのテスト"""
    config = SysupConfig()

    assert config.is_updater_enabled("apt") is True
    assert config.is_updater_enabled("flatpak") is True
    assert config.is_updater_enabled("nonexistent") is False


def test_path_expansion():
    """パス展開のテスト"""
    config = SysupConfig()

    log_dir = config.get_log_dir()
    assert log_dir.is_absolute()
    assert "~" not in str(log_dir)
