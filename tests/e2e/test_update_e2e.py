"""sysup update コマンドの E2E テスト.

実際のコマンド実行による統合テストを行う。
"""


class TestUpdateCommand:
    """update コマンドの E2E テスト."""

    def test_update_help(self, run_cli, temp_home):
        """update --help のテスト."""
        result = run_cli(["update", "--help"])

        assert result.returncode == 0
        assert "update" in result.stdout.lower() or "更新" in result.stdout

    def test_update_version(self, run_cli, temp_home):
        """sysup --version のテスト."""
        result = run_cli(["--version"])

        assert result.returncode == 0
        assert "sysup" in result.stdout

    def test_update_list_updaters(self, run_cli, temp_home):
        """update --list でupdater一覧を表示するテスト."""
        # 設定ファイルを作成
        config_dir = temp_home / ".config" / "sysup"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "sysup.toml"
        config_file.write_text("""
[updaters]
apt = true
npm = true
rustup = true

[auto_run]
mode = "disabled"

[logging]
dir = "~/.local/share/sysup/logs"
retention_days = 30
level = "INFO"

[backup]
dir = "~/.local/share/sysup/backups"
enabled = false

[notification]
enabled = false
on_success = false
on_error = true
on_warning = true

[general]
parallel_updates = false
dry_run = false
cache_dir = "~/.cache/sysup"
""")

        result = run_cli(["update", "--list"], timeout=60)

        # プロセスロックの取得に失敗した場合も考慮
        # 成功または「既に実行中」のメッセージ
        assert result.returncode == 0 or "既に実行中" in result.stdout

    def test_update_dry_run(self, run_cli, temp_home):
        """update --dry-run でドライラン実行するテスト."""
        # 設定ファイルを作成
        config_dir = temp_home / ".config" / "sysup"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "sysup.toml"
        config_file.write_text("""
[updaters]
apt = false
snap = false
flatpak = false
pipx = false
uv = false
npm = false
nvm = false
rustup = false
cargo = false
gem = false
brew = false
scoop = false
firmware = false

[auto_run]
mode = "disabled"

[logging]
dir = "~/.local/share/sysup/logs"
retention_days = 30
level = "INFO"

[backup]
dir = "~/.local/share/sysup/backups"
enabled = false

[notification]
enabled = false
on_success = false
on_error = true
on_warning = true

[general]
parallel_updates = false
dry_run = true
cache_dir = "~/.cache/sysup"
""")

        result = run_cli(["update", "--dry-run"], timeout=60)

        # ドライランモードで実行（すべてのupdaterを無効にしているので何も実行されない）
        # プロセスロックの取得に失敗した場合も考慮
        assert result.returncode == 0 or "既に実行中" in result.stdout

    def test_update_invalid_config(self, run_cli, temp_home):
        """不正な設定ファイルでのエラーハンドリングテスト."""
        # 不正な設定ファイルを作成
        config_dir = temp_home / ".config" / "sysup"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "sysup.toml"
        config_file.write_text("invalid toml [[[")

        result = run_cli(["update", "--config", str(config_file)], timeout=30)

        assert result.returncode == 1
        # エラーメッセージはstdoutまたはstderrに出力される
        output = result.stdout + result.stderr
        assert "エラー" in output or "error" in output.lower()


class TestSysupMain:
    """sysup メインコマンドのテスト."""

    def test_main_help(self, run_cli, temp_home):
        """sysup --help のテスト."""
        result = run_cli(["--help"])

        assert result.returncode == 0
        assert "sysup" in result.stdout.lower()
        assert "update" in result.stdout.lower() or "更新" in result.stdout
        assert "init" in result.stdout.lower() or "セットアップ" in result.stdout

    def test_main_no_args(self, run_cli, temp_home):
        """引数なしで実行した場合のテスト."""
        result = run_cli([], timeout=30)

        # ヘルプが表示されるか、何らかのメッセージが出力される
        assert result.returncode == 0 or result.returncode == 2
