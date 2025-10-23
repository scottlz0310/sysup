"""WSL統合機能のテスト"""

import os
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

from sysup.core.wsl import WSLIntegration


def test_is_wsl_true():
    """WSL環境判定 - WSLの場合のテスト"""
    with patch("builtins.open", mock_open(read_data="Linux version 5.10.0-microsoft-standard")):
        assert WSLIntegration.is_wsl() is True


def test_is_wsl_false():
    """WSL環境判定 - WSLでない場合のテスト"""
    with patch("builtins.open", mock_open(read_data="Linux version 5.10.0-generic")):
        assert WSLIntegration.is_wsl() is False


def test_is_wsl_file_not_found():
    """WSL環境判定 - /proc/versionが存在しない場合のテスト"""
    with patch("builtins.open", side_effect=FileNotFoundError()):
        assert WSLIntegration.is_wsl() is False


def test_get_shell_rc_file():
    """シェルRCファイル取得のテスト"""
    rc_file = WSLIntegration.get_shell_rc_file()
    assert rc_file is not None
    assert rc_file.name in [".bashrc", ".zshrc"]


def test_get_shell_rc_file_zsh():
    """シェルRCファイル取得 - zshの場合のテスト"""
    with patch.dict(os.environ, {"SHELL": "/bin/zsh"}):
        rc_file = WSLIntegration.get_shell_rc_file()
        assert rc_file is not None
        assert rc_file.name == ".zshrc"


def test_get_shell_rc_file_bash():
    """シェルRCファイル取得 - bashの場合のテスト"""
    with patch.dict(os.environ, {"SHELL": "/bin/bash"}):
        rc_file = WSLIntegration.get_shell_rc_file()
        assert rc_file is not None
        assert rc_file.name == ".bashrc"


def test_get_shell_rc_file_unknown():
    """シェルRCファイル取得 - 不明なシェルの場合のテスト"""
    with patch.dict(os.environ, {"SHELL": "/bin/fish"}):
        rc_file = WSLIntegration.get_shell_rc_file()
        assert rc_file is not None
        assert rc_file.name == ".bashrc"  # デフォルトはbashrc


def test_get_shell_rc_file_no_shell_env():
    """シェルRCファイル取得 - SHELL環境変数がない場合のテスト"""
    home_dir = str(Path.home())
    env_vars = {"HOME": home_dir, "USERPROFILE": home_dir}
    with patch.dict(os.environ, env_vars, clear=True):
        rc_file = WSLIntegration.get_shell_rc_file()
        assert rc_file is not None
        assert rc_file.name == ".bashrc"  # デフォルトはbashrc


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


def test_is_auto_run_configured_file_not_exists():
    """自動実行設定確認 - ファイルが存在しない場合のテスト"""
    rc_file = Path("/tmp/nonexistent_rc_file")
    assert WSLIntegration.is_auto_run_configured(rc_file) is False


def test_is_auto_run_configured_read_error():
    """自動実行設定確認 - 読み込みエラーの場合のテスト"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".bashrc", delete=False) as f:
        rc_file = Path(f.name)

    try:
        # ファイルを読み込めないようにする
        rc_file.chmod(0o000)
        assert WSLIntegration.is_auto_run_configured(rc_file) is False
    finally:
        rc_file.chmod(0o644)
        rc_file.unlink()


def test_add_auto_run_to_rc_enabled():
    """RC ファイルへの自動実行追加 - enabledモードのテスト"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".bashrc", delete=False, encoding="utf-8") as f:
        f.write("# existing content\n")
        rc_file = Path(f.name)

    try:
        result = WSLIntegration.add_auto_run_to_rc(rc_file, mode="enabled")
        assert result is True

        content = rc_file.read_text(encoding="utf-8")
        assert "sysup --auto-run" in content
        assert "# sysup - システム自動更新" in content
    finally:
        rc_file.unlink(missing_ok=True)
        backup_file = rc_file.with_suffix(rc_file.suffix + ".sysup.bak")
        backup_file.unlink(missing_ok=True)


def test_add_auto_run_to_rc_enabled_with_auth():
    """RC ファイルへの自動実行追加 - enabled_with_authモードのテスト"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".bashrc", delete=False, encoding="utf-8") as f:
        f.write("# existing content\n")
        rc_file = Path(f.name)

    try:
        result = WSLIntegration.add_auto_run_to_rc(rc_file, mode="enabled_with_auth")
        assert result is True

        content = rc_file.read_text(encoding="utf-8")
        assert "sysup --auto-run" in content
    finally:
        rc_file.unlink(missing_ok=True)
        backup_file = rc_file.with_suffix(rc_file.suffix + ".sysup.bak")
        backup_file.unlink(missing_ok=True)


def test_add_auto_run_to_rc_already_configured():
    """RC ファイルへの自動実行追加 - 既に設定済みの場合のテスト"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".bashrc", delete=False) as f:
        f.write("# test\nsysup --auto-run\n")
        rc_file = Path(f.name)

    try:
        result = WSLIntegration.add_auto_run_to_rc(rc_file, mode="enabled")
        assert result is True
    finally:
        rc_file.unlink()


def test_add_auto_run_to_rc_new_file():
    """RC ファイルへの自動実行追加 - 新規ファイルの場合のテスト"""
    with tempfile.TemporaryDirectory() as tmpdir:
        rc_file = Path(tmpdir) / ".bashrc"

        result = WSLIntegration.add_auto_run_to_rc(rc_file, mode="enabled")
        assert result is True

        content = rc_file.read_text(encoding="utf-8")
        assert "sysup --auto-run" in content


def test_remove_auto_run_from_rc():
    """RC ファイルからの自動実行削除のテスト"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".bashrc", delete=False, encoding="utf-8") as f:
        f.write(
            """# some content
# sysup - システム自動更新
# WSLログイン時に自動実行（週1回）
if [ -z "${SYSUP_RAN:-}" ]; then
    export SYSUP_RAN=1
    sysup --auto-run 2>/dev/null || true
fi
# more content
"""
        )
        rc_file = Path(f.name)

    try:
        result = WSLIntegration.remove_auto_run_from_rc(rc_file)
        assert result is True

        content = rc_file.read_text()
        assert "sysup --auto-run" not in content
        assert "# some content" in content
        assert "# more content" in content
    finally:
        rc_file.unlink()


def test_remove_auto_run_from_rc_file_not_exists():
    """RC ファイルからの自動実行削除 - ファイルが存在しない場合のテスト"""
    rc_file = Path("/tmp/nonexistent_rc_file")
    result = WSLIntegration.remove_auto_run_from_rc(rc_file)
    assert result is True


def test_setup_wsl_integration_not_wsl():
    """WSL統合セットアップ - WSL環境でない場合のテスト"""
    with patch.object(WSLIntegration, "is_wsl", return_value=False):
        success, message = WSLIntegration.setup_wsl_integration()
        assert success is False
        assert "WSL環境ではありません" in message


def test_setup_wsl_integration_enabled():
    """WSL統合セットアップ - enabledモードのテスト"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".bashrc", delete=False, encoding="utf-8") as f:
        f.write("# existing content\n")
        rc_file = Path(f.name)

    try:
        with patch.object(WSLIntegration, "is_wsl", return_value=True):
            with patch.object(WSLIntegration, "get_shell_rc_file", return_value=rc_file):
                success, message = WSLIntegration.setup_wsl_integration(mode="enabled")
                assert success is True
                assert "自動実行設定を追加しました" in message
    finally:
        rc_file.unlink(missing_ok=True)
        backup_file = rc_file.with_suffix(rc_file.suffix + ".sysup.bak")
        backup_file.unlink(missing_ok=True)


def test_setup_wsl_integration_disabled():
    """WSL統合セットアップ - disabledモードのテスト"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".bashrc", delete=False, encoding="utf-8") as f:
        f.write("# sysup - システム自動更新\nsysup --auto-run\nfi\n")
        rc_file = Path(f.name)

    try:
        with patch.object(WSLIntegration, "is_wsl", return_value=True):
            with patch.object(WSLIntegration, "get_shell_rc_file", return_value=rc_file):
                success, message = WSLIntegration.setup_wsl_integration(mode="disabled")
                assert success is True
                assert "自動実行設定を削除しました" in message
    finally:
        rc_file.unlink()


def test_setup_wsl_integration_no_rc_file():
    """WSL統合セットアップ - RCファイルが取得できない場合のテスト"""
    with patch.object(WSLIntegration, "is_wsl", return_value=True):
        with patch.object(WSLIntegration, "get_shell_rc_file", return_value=None):
            success, message = WSLIntegration.setup_wsl_integration()
            assert success is False
            assert "シェルRCファイルが見つかりません" in message
