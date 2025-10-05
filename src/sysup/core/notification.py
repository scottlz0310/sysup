"""デスクトップ通知機能"""

import platform
import subprocess


class Notifier:
    """デスクトップ通知を送信するクラス"""

    @staticmethod
    def is_available() -> bool:
        """通知機能が利用可能かチェック"""
        system = platform.system()

        if system == "Linux":
            # notify-sendの存在確認
            try:
                subprocess.run(["which", "notify-send"], capture_output=True, check=True, timeout=5)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                return False
        elif system == "Darwin":  # macOS
            # osascriptは標準で利用可能
            return True
        else:
            return False

    @staticmethod
    def send(title: str, message: str, urgency: str = "normal", icon: str | None = None) -> bool:
        """デスクトップ通知を送信

        Args:
            title: 通知のタイトル
            message: 通知のメッセージ
            urgency: 緊急度 (low/normal/critical)
            icon: アイコン名またはパス

        Returns:
            成功した場合True
        """
        system = platform.system()

        try:
            if system == "Linux":
                return Notifier._send_linux(title, message, urgency, icon)
            elif system == "Darwin":
                return Notifier._send_macos(title, message)
            else:
                return False
        except Exception:
            return False

    @staticmethod
    def _send_linux(title: str, message: str, urgency: str, icon: str | None) -> bool:
        """Linux (notify-send) で通知を送信"""
        cmd = ["notify-send"]

        # 緊急度
        cmd.extend(["-u", urgency])

        # アイコン
        if icon:
            cmd.extend(["-i", icon])
        else:
            # デフォルトアイコン
            if "成功" in message or "完了" in message:
                cmd.extend(["-i", "dialog-information"])
            elif "エラー" in message or "失敗" in message:
                cmd.extend(["-i", "dialog-error"])
            elif "警告" in message:
                cmd.extend(["-i", "dialog-warning"])

        # タイトルとメッセージ
        cmd.extend([title, message])

        result = subprocess.run(cmd, capture_output=True, timeout=5)
        return result.returncode == 0

    @staticmethod
    def _send_macos(title: str, message: str) -> bool:
        """macOS (osascript) で通知を送信"""
        script = f'display notification "{message}" with title "{title}"'
        result = subprocess.run(["osascript", "-e", script], capture_output=True, timeout=5)
        return result.returncode == 0

    @staticmethod
    def send_success(title: str, message: str) -> bool:
        """成功通知を送信"""
        return Notifier.send(title, message, urgency="normal", icon="dialog-information")

    @staticmethod
    def send_error(title: str, message: str) -> bool:
        """エラー通知を送信"""
        return Notifier.send(title, message, urgency="critical", icon="dialog-error")

    @staticmethod
    def send_warning(title: str, message: str) -> bool:
        """警告通知を送信"""
        return Notifier.send(title, message, urgency="normal", icon="dialog-warning")
