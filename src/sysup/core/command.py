"""コマンド実行の補助ユーティリティ.

Windows では `.cmd`/`.bat`/`.ps1` のラッパーが PATH 上に存在することがあり、
`subprocess.run(["tool", ...])` だと直接起動できず失敗するケースがあるため、
実行可能な形に解決したコマンド列を返します。
"""

from __future__ import annotations

import shutil
from pathlib import Path

from .platform import is_windows


def resolve_command(command: list[str]) -> list[str]:
    """実行可能な形にコマンド列を解決して返す.

    Args:
        command: 実行するコマンドのリスト.

    Returns:
        解決済みのコマンドリスト.

    """
    if not command:
        return command

    if not is_windows():
        return command

    resolved = shutil.which(command[0])
    if not resolved:
        return command

    suffix = Path(resolved).suffix.lower()
    if suffix in {".cmd", ".bat"}:
        return ["cmd.exe", "/c", resolved, *command[1:]]
    if suffix == ".ps1":
        return [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            resolved,
            *command[1:],
        ]
    return [resolved, *command[1:]]
