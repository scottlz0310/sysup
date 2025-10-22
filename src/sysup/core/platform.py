"""プラットフォーム検出モジュール。

Windows、Linux、macOSなどのプラットフォームを検出する機能を提供します。
"""

import platform


def is_windows() -> bool:
    """Windows環境かどうかを判定します。

    Returns:
        bool: Windows環境の場合True、それ以外はFalse
    """
    return platform.system() == "Windows"


def is_unix() -> bool:
    """Unix系環境（Linux/macOS）かどうかを判定します。

    Returns:
        bool: Unix系環境の場合True、それ以外はFalse
    """
    return platform.system() in ("Linux", "Darwin")


def get_platform() -> str:
    """現在のプラットフォーム名を取得します。

    Returns:
        str: プラットフォーム名（"Windows", "Linux", "Darwin"など）
    """
    return platform.system()
