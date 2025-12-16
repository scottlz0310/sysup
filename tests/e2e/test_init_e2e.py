"""sysup init コマンドの E2E テスト.

対話型CLI（TTY/キー入力）のテストをE2Eで担保する。
pexpect を使用して実際のターミナル操作をシミュレートする。
"""

import sys
import time

import pytest

# Windows ではこのテストモジュール全体をスキップ
pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="E2E tests with PTY are not supported on Windows",
)

# pexpect は Windows 以外でのみインポート
if sys.platform != "win32":
    import pexpect


class TestInitInteractive:
    """init コマンドの対話型テスト（TTYモード）."""

    def test_init_wizard_complete_flow(self, pexpect_spawn, temp_home):
        """init ウィザードを最後まで完了するE2Eテスト."""
        child = pexpect_spawn(["init"], timeout=60)

        # ヘッダーの確認
        child.expect("sysup 初期セットアップウィザード", timeout=30)

        # 工程1: システム環境の確認（検出処理があるのでタイムアウトを長めに）
        # 工程2への遷移を待つ（工程1は自動で進む）
        child.expect("工程 2/5", timeout=60)

        # 対話モードでqまたはEnterを押して確定
        time.sleep(0.5)
        child.send("q")

        # 工程3: 実行モード選択
        child.expect("工程 3/5", timeout=10)
        # デフォルト（1=標準モード）を選択
        child.sendline("1")

        # 工程4: 詳細設定
        child.expect("工程 4/5", timeout=10)
        # デフォルト（2=デフォルト値を使用）を選択
        child.sendline("2")

        # 工程5: 完了確認
        child.expect("工程 5/5", timeout=10)
        child.expect("セットアップが完了しました", timeout=10)

        child.expect(pexpect.EOF, timeout=10)

        # 設定ファイルが生成されたことを確認
        config_file = temp_home / ".config" / "sysup" / "sysup.toml"
        assert config_file.exists(), f"Config file should exist at {config_file}"

        # 設定ファイルの内容を確認
        content = config_file.read_text()
        assert "[updaters]" in content
        assert "[auto_run]" in content
        assert "[logging]" in content

    def test_init_wizard_auto_run_mode(self, pexpect_spawn, temp_home):
        """自動実行モードを選択するE2Eテスト."""
        child = pexpect_spawn(["init"], timeout=60)

        child.expect("sysup 初期セットアップウィザード", timeout=30)

        # 工程2を待つ（工程1は自動）
        child.expect("工程 2/5", timeout=60)
        time.sleep(0.5)
        child.send("q")

        # 工程3: 自動実行モード（2）を選択
        child.expect("工程 3/5", timeout=10)
        child.sendline("2")

        # 工程4: デフォルト
        child.expect("工程 4/5", timeout=10)
        child.sendline("2")

        # 完了
        child.expect("セットアップが完了しました", timeout=10)
        child.expect(pexpect.EOF, timeout=10)

        # 設定ファイルの内容確認
        config_file = temp_home / ".config" / "sysup" / "sysup.toml"
        content = config_file.read_text()
        assert 'mode = "enabled"' in content

    def test_init_wizard_custom_settings(self, pexpect_spawn, temp_home):
        """詳細設定をカスタマイズするE2Eテスト."""
        child = pexpect_spawn(["init"], timeout=60)

        child.expect("sysup 初期セットアップウィザード", timeout=30)

        # 工程2を待つ
        child.expect("工程 2/5", timeout=60)
        time.sleep(0.5)
        child.send("q")

        # 工程3: 標準モード
        child.expect("工程 3/5", timeout=10)
        child.sendline("1")

        # 工程4: 詳細設定を行う（1）
        child.expect("工程 4/5", timeout=10)
        child.sendline("1")

        # ログレベル: DEBUG（1）
        child.expect("ログレベル", timeout=10)
        child.sendline("1")

        # 並列実行: はい（1）
        child.expect("並列実行", timeout=10)
        child.sendline("1")

        # バックアップ: いいえ（2）
        child.expect("バックアップ", timeout=10)
        child.sendline("2")

        # 通知: いいえ（2）
        child.expect("通知", timeout=10)
        child.sendline("2")

        # 完了
        child.expect("セットアップが完了しました", timeout=10)
        child.expect(pexpect.EOF, timeout=10)

        # 設定ファイルの内容確認
        config_file = temp_home / ".config" / "sysup" / "sysup.toml"
        content = config_file.read_text()
        assert 'level = "DEBUG"' in content
        assert "parallel_updates = true" in content
        assert "enabled = false" in content  # backup or notification

    @pytest.mark.skip(reason="Ctrl+C handling is environment-dependent and unstable in CI")
    def test_init_wizard_keyboard_interrupt(self, pexpect_spawn, temp_home):
        """Ctrl+Cでキャンセルするテスト."""
        child = pexpect_spawn(["init"], timeout=60)

        child.expect("sysup 初期セットアップウィザード", timeout=30)

        # 少し待ってからCtrl+Cを送信
        time.sleep(1)
        child.sendcontrol("c")

        # キャンセルメッセージの確認
        child.expect("セットアップをキャンセルしました", timeout=10)
        child.expect(pexpect.EOF, timeout=10)

        # 設定ファイルが生成されていないことを確認
        config_file = temp_home / ".config" / "sysup" / "sysup.toml"
        assert not config_file.exists()

    def test_init_wizard_arrow_key_navigation(self, pexpect_spawn, temp_home):
        """矢印キーでの選択操作テスト."""
        child = pexpect_spawn(["init"], timeout=60)

        child.expect("sysup 初期セットアップウィザード", timeout=30)

        # 工程2: updater選択画面を待つ
        child.expect("工程 2/5", timeout=60)
        time.sleep(0.5)

        # 下矢印で移動
        child.send("\x1b[B")  # Down arrow
        time.sleep(0.1)
        child.send("\x1b[B")  # Down arrow
        time.sleep(0.1)

        # スペースでトグル
        child.send(" ")
        time.sleep(0.1)

        # 上矢印で戻る
        child.send("\x1b[A")  # Up arrow
        time.sleep(0.1)

        # qで確定
        child.send("q")

        # 残りの工程を進める
        child.expect("工程 3/5", timeout=10)
        child.sendline("1")

        child.expect("工程 4/5", timeout=10)
        child.sendline("2")

        child.expect("セットアップが完了しました", timeout=10)
        child.expect(pexpect.EOF, timeout=10)


class TestInitExistingConfig:
    """既存設定ファイルがある場合のテスト."""

    def test_init_with_existing_config_continue(self, pexpect_spawn, temp_home):
        """既存設定がある場合に続行を選択するテスト."""
        # 既存の設定ファイルを作成
        config_dir = temp_home / ".config" / "sysup"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "sysup.toml"
        config_file.write_text("[general]\ndry_run = false\n")

        child = pexpect_spawn(["init"], timeout=60)

        child.expect("sysup 初期セットアップウィザード", timeout=30)

        # 既存設定の検出
        child.expect("既存の設定ファイルを検出しました", timeout=10)

        # 続行（1）を選択
        child.sendline("1")

        # ウィザード続行
        child.expect("工程 1/5", timeout=10)
        child.expect("検出完了", timeout=30)

        # 残りの工程を完了
        child.expect("工程 2/5", timeout=10)
        child.sendline("\r")

        child.expect("工程 3/5", timeout=10)
        child.sendline("1")

        child.expect("工程 4/5", timeout=10)
        child.sendline("2")

        child.expect("セットアップが完了しました", timeout=10)
        child.expect(pexpect.EOF, timeout=10)

    def test_init_with_existing_config_skip(self, pexpect_spawn, temp_home):
        """既存設定がある場合にスキップを選択するテスト."""
        # 既存の設定ファイルを作成
        config_dir = temp_home / ".config" / "sysup"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "sysup.toml"
        original_content = "[general]\ndry_run = false\n"
        config_file.write_text(original_content)

        child = pexpect_spawn(["init"], timeout=60)

        child.expect("sysup 初期セットアップウィザード", timeout=30)
        child.expect("既存の設定ファイルを検出しました", timeout=10)

        # スキップ（2）を選択
        child.sendline("2")

        child.expect("既存設定を使用して終了します", timeout=10)
        child.expect(pexpect.EOF, timeout=10)

        # 設定ファイルが変更されていないことを確認
        assert config_file.read_text() == original_content

    def test_init_with_existing_config_reset(self, pexpect_spawn, temp_home):
        """既存設定がある場合にリセットを選択するテスト."""
        # 既存の設定ファイルを作成
        config_dir = temp_home / ".config" / "sysup"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "sysup.toml"
        original_content = "[general]\ndry_run = true\n"
        config_file.write_text(original_content)

        child = pexpect_spawn(["init"], timeout=60)

        child.expect("sysup 初期セットアップウィザード", timeout=30)
        child.expect("既存の設定ファイルを検出しました", timeout=10)

        # リセット（3）を選択
        child.sendline("3")

        # バックアップが作成されることを確認
        child.expect("バックアップ|リセットします", timeout=10)

        # ウィザード続行
        child.expect("工程 1/5", timeout=10)
        child.expect("検出完了", timeout=30)

        # 残りの工程を完了
        child.expect("工程 2/5", timeout=10)
        child.sendline("\r")

        child.expect("工程 3/5", timeout=10)
        child.sendline("1")

        child.expect("工程 4/5", timeout=10)
        child.sendline("2")

        child.expect("セットアップが完了しました", timeout=10)
        child.expect(pexpect.EOF, timeout=10)

        # バックアップファイルが作成されたことを確認
        backup_file = config_dir / "sysup.toml.bak"
        assert backup_file.exists()
        assert backup_file.read_text() == original_content


class TestInitNonTTY:
    """非TTYモード（パイプ入力）でのテスト.

    注意: 非TTYモードでのinit実行は、Prompt.askのEOF処理により
    完全なE2Eテストが難しい。これらのテストは統合テストとして
    別途test_init_command.pyで実装されている。
    """

    @pytest.mark.skip(reason="Non-TTY mode requires special handling for EOF in Prompt.ask")
    def test_init_non_tty_mode(self, run_cli, temp_home):
        """非TTYモードでのフォールバック動作テスト."""
        # パイプ入力で init を実行
        # 選択: q(updater確定), 1(標準モード), 2(デフォルト設定)
        input_text = "q\n1\n2\n"

        result = run_cli(["init"], input_text=input_text, timeout=60)

        # 正常終了を確認
        assert result.returncode == 0

        # 設定ファイルが生成されたことを確認
        config_file = temp_home / ".config" / "sysup" / "sysup.toml"
        assert config_file.exists()

    @pytest.mark.skip(reason="Non-TTY mode requires special handling for EOF in Prompt.ask")
    def test_init_non_tty_toggle_updaters(self, run_cli, temp_home):
        """非TTYモードでupdaterをトグルするテスト."""
        # 1番目をトグル、qで確定、標準モード、デフォルト設定
        input_text = "1\nq\n1\n2\n"

        result = run_cli(["init"], input_text=input_text, timeout=60)

        assert result.returncode == 0

        config_file = temp_home / ".config" / "sysup" / "sysup.toml"
        assert config_file.exists()


class TestInitHelp:
    """init コマンドのヘルプテスト."""

    def test_init_help(self, run_cli, temp_home):
        """init --help のテスト."""
        result = run_cli(["init", "--help"])

        assert result.returncode == 0
        assert "init" in result.stdout or "セットアップ" in result.stdout
