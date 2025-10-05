"""WSL統合機能のテスト"""

import tempfile
from pathlib import Path

from sysup.core.wsl import WSLIntegration


def test_get_shell_rc_file():
    """シェルRCファイル取得のテスト"""
    rc_file = WSLIntegration.get_shell_rc_file()
    assert rc_file is not None
    assert rc_file.name in [".bashrc", ".zshrc"]


def test_is_auto_run_configured():
    """自動実行設定確認のテスト"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".bashrc", delete=False) as f:
        f.write("# test\nsysup --auto-run\n")
        rc_file = Path(f.name)

    try:
        assert WSLIntegration.is_auto_run_configured(rc_file) is True
    finally:
        rc_file.unlink()


def test_is_auto_run_not_configured():
    """自動実行未設定確認のテスト"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".bashrc", delete=False) as f:
        f.write("# test\necho hello\n")
        rc_file = Path(f.name)

    try:
        assert WSLIntegration.is_auto_run_configured(rc_file) is False
    finally:
        rc_file.unlink()
