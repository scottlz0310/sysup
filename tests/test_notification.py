"""通知機能のテスト"""

from unittest.mock import Mock, patch

from sysup.core.notification import Notifier


def test_notifier_availability():
    """通知機能の利用可能性テスト"""
    # 利用可能かどうかをチェック（環境依存）
    is_available = Notifier.is_available()
    assert isinstance(is_available, bool)


def test_notifier_availability_linux_available():
    """通知機能の利用可能性テスト - Linux (利用可能)"""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            assert Notifier.is_available() is True


def test_notifier_availability_linux_unavailable():
    """通知機能の利用可能性テスト - Linux (利用不可)"""
    import subprocess

    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "which")

            assert Notifier.is_available() is False


def test_notifier_availability_linux_timeout():
    """通知機能の利用可能性テスト - Linux (タイムアウト)"""
    import subprocess

    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("which", 5)

            assert Notifier.is_available() is False


def test_notifier_availability_macos():
    """通知機能の利用可能性テスト - macOS"""
    with patch("platform.system", return_value="Darwin"):
        assert Notifier.is_available() is True


def test_notifier_availability_windows():
    """通知機能の利用可能性テスト - Windows"""
    with patch("platform.system", return_value="Windows"):
        assert Notifier.is_available() is False


def test_send_notification_returns_bool():
    """通知送信が真偽値を返すことのテスト"""
    result = Notifier.send("Test", "Test message")
    assert isinstance(result, bool)


def test_send_linux_success():
    """Linux通知送信 - 成功のテスト"""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = Notifier.send("Test", "Test message")
            assert result is True


def test_send_linux_with_icon():
    """Linux通知送信 - カスタムアイコンのテスト"""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = Notifier.send("Test", "Test message", icon="custom-icon")
            assert result is True


def test_send_linux_auto_icon_success():
    """Linux通知送信 - 自動アイコン選択(成功)のテスト"""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = Notifier.send("Test", "更新成功しました")
            assert result is True


def test_send_linux_auto_icon_error():
    """Linux通知送信 - 自動アイコン選択(エラー)のテスト"""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = Notifier.send("Test", "エラーが発生しました")
            assert result is True


def test_send_linux_auto_icon_warning():
    """Linux通知送信 - 自動アイコン選択(警告)のテスト"""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = Notifier.send("Test", "警告: 注意が必要です")
            assert result is True


def test_send_macos_success():
    """macOS通知送信 - 成功のテスト"""
    with patch("platform.system", return_value="Darwin"):
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = Notifier.send("Test", "Test message")
            assert result is True


def test_send_macos_failure():
    """macOS通知送信 - 失敗のテスト"""
    with patch("platform.system", return_value="Darwin"):
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1
            mock_run.return_value = mock_result

            result = Notifier.send("Test", "Test message")
            assert result is False


def test_send_windows_unsupported():
    """Windows通知送信 - 未サポートのテスト"""
    with patch("platform.system", return_value="Windows"):
        result = Notifier.send("Test", "Test message")
        assert result is False


def test_send_exception_handling():
    """通知送信 - 例外処理のテスト"""
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Unexpected error")

            result = Notifier.send("Test", "Test message")
            assert result is False


def test_send_success_notification():
    """成功通知のテスト"""
    result = Notifier.send_success("Test", "Success message")
    assert isinstance(result, bool)


def test_send_error_notification():
    """エラー通知のテスト"""
    result = Notifier.send_error("Test", "Error message")
    assert isinstance(result, bool)


def test_send_warning_notification():
    """警告通知のテスト"""
    result = Notifier.send_warning("Test", "Warning message")
    assert isinstance(result, bool)
