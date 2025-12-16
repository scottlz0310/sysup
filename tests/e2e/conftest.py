"""E2E テスト用 conftest."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# pexpect は Windows では利用不可
pexpect_available = sys.platform != "win32"
if pexpect_available:
    try:
        import pexpect

        HAS_PEXPECT = True
    except ImportError:
        HAS_PEXPECT = False
        pexpect = None
else:
    HAS_PEXPECT = False
    pexpect = None

skip_if_no_pexpect = pytest.mark.skipif(
    not HAS_PEXPECT,
    reason="pexpect is not available (Windows or not installed)",
)

skip_on_windows = pytest.mark.skipif(
    sys.platform == "win32",
    reason="E2E tests with PTY are not supported on Windows",
)


@pytest.fixture
def temp_home():
    """一時的なHOMEディレクトリを作成するフィクスチャ."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_home = os.environ.get("HOME")
        os.environ["HOME"] = tmpdir
        # .config ディレクトリを事前に作成
        config_dir = Path(tmpdir) / ".config" / "sysup"
        config_dir.mkdir(parents=True, exist_ok=True)
        try:
            yield Path(tmpdir)
        finally:
            if old_home is not None:
                os.environ["HOME"] = old_home
            else:
                os.environ.pop("HOME", None)


@pytest.fixture
def sysup_command():
    """sysup コマンドのパスを返すフィクスチャ."""
    # uv run sysup を使用
    return ["uv", "run", "sysup"]


@pytest.fixture
def pexpect_spawn(temp_home, sysup_command):
    """pexpect.spawn のラッパーフィクスチャ."""
    if not HAS_PEXPECT:
        pytest.skip("pexpect is not available")

    spawned_processes = []

    def _spawn(args, timeout=30, encoding="utf-8"):
        cmd = " ".join(sysup_command + args)
        env = os.environ.copy()
        env["HOME"] = str(temp_home)
        # 端末サイズを設定（richの出力に影響）
        env["COLUMNS"] = "120"
        env["LINES"] = "40"
        # ANSIエスケープシーケンスを無効化（rich対応）
        env["NO_COLOR"] = "1"
        env["TERM"] = "dumb"
        child = pexpect.spawn(
            cmd,
            timeout=timeout,
            encoding=encoding,
            env=env,
        )
        spawned_processes.append(child)
        return child

    yield _spawn

    # クリーンアップ
    for child in spawned_processes:
        if child.isalive():
            child.terminate(force=True)


@pytest.fixture
def run_cli(temp_home, sysup_command):
    """CLIコマンドを実行するヘルパーフィクスチャ."""
    import subprocess

    def _run(args, input_text=None, timeout=30):
        cmd = sysup_command + args
        env = os.environ.copy()
        env["HOME"] = str(temp_home)
        # ANSIエスケープシーケンスを無効化
        env["NO_COLOR"] = "1"
        env["TERM"] = "dumb"
        result = subprocess.run(
            cmd,
            input=input_text,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return result

    return _run
