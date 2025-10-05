"""通知機能のテスト"""

from sysup.core.notification import Notifier


def test_notifier_availability():
    """通知機能の利用可能性テスト"""
    # 利用可能かどうかをチェック（環境依存）
    is_available = Notifier.is_available()
    assert isinstance(is_available, bool)


def test_send_notification_returns_bool():
    """通知送信が真偽値を返すことのテスト"""
    result = Notifier.send("Test", "Test message")
    assert isinstance(result, bool)


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
