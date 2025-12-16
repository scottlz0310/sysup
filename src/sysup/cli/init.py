"""sysup init コマンド実装.

初期セットアップウィザードを提供するモジュールです。
richを使用した対話型メニューで、ユーザーが簡単にsysupを設定できます。
"""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import ClassVar

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from sysup.core.command import resolve_command
from sysup.core.config import SysupConfig

console = Console()


class PackageManagerDetector:
    """パッケージマネージャを検出するクラス."""

    # 各パッケージマネージャのコマンド名
    MANAGERS: ClassVar[dict[str, str]] = {
        "apt": "apt",
        "snap": "snap",
        "flatpak": "flatpak",
        "pipx": "pipx",
        "uv": "uv",
        "npm": "npm",
        "nvm": "node",
        "rustup": "rustup",
        "cargo": "cargo",
        "gem": "gem",
        "brew": "brew",
        "scoop": "scoop",
        "firmware": "fwupdmgr",
    }

    PROBE_COMMANDS: ClassVar[dict[str, list[str]]] = {
        "apt": ["apt", "--version"],
        "snap": ["snap", "--version"],
        "flatpak": ["flatpak", "--version"],
        "pipx": ["pipx", "--version"],
        "uv": ["uv", "--version"],
        "npm": ["npm", "--version"],
        "nvm": ["node", "--version"],
        "rustup": ["rustup", "--version"],
        "cargo": ["cargo", "--version"],
        "gem": ["gem", "--version"],
        "brew": ["brew", "--version"],
        "scoop": ["scoop", "--version"],
        "firmware": ["fwupdmgr", "--version"],
    }

    @classmethod
    def get_available_managers(cls) -> dict[str, bool]:
        """利用可能なパッケージマネージャを検出.

        Returns:
            各マネージャ名と利用可能性のマッピング.

        """
        available: dict[str, bool] = {}
        for name, command in cls.MANAGERS.items():
            if shutil.which(command) is None:
                available[name] = False
                continue

            probe = cls.PROBE_COMMANDS.get(name, [command, "--version"])
            available[name] = cls._probe_runnable(probe)
        return available

    @staticmethod
    def _probe_runnable(command: list[str]) -> bool:
        """実際にコマンドが起動できるかを軽く確認する."""
        try:
            resolved = resolve_command(command)
            result = subprocess.run(resolved, capture_output=True, text=True, timeout=5, check=False)
            return result.returncode == 0
        except Exception:
            return False

    @classmethod
    def get_manager_description(cls, name: str) -> str:
        """パッケージマネージャの説明を取得.

        Args:
            name: マネージャ名.

        Returns:
            説明文.

        """
        descriptions = {
            "apt": "Debian/Ubuntu パッケージマネージャ",
            "snap": "Snapパッケージマネージャ",
            "flatpak": "Flatpakパッケージマネージャ",
            "pipx": "Python CLIアプリケーション管理",
            "uv": "Pythonパッケージ・プロジェクト管理",
            "npm": "Node.jsパッケージマネージャ",
            "nvm": "Node.jsバージョンマネージャ",
            "rustup": "Rustツールチェーンマネージャ",
            "cargo": "Cargoパッケージマネージャ",
            "gem": "Rubygemsパッケージマネージャ",
            "brew": "Homebrewパッケージマネージャ",
            "scoop": "Scoopパッケージマネージャ",
            "firmware": "ファームウェア更新",
        }
        return descriptions.get(name, name)


def show_header() -> None:
    """ウィザードのヘッダーを表示."""
    console.print(
        Panel(
            "[bold cyan]sysup 初期セットアップウィザード[/bold cyan]",
            style="cyan",
            expand=False,
        )
    )
    console.print("ようこそ！このウィザードで sysup の初期セットアップを行います。\n")


def check_existing_config() -> Path | None:
    """既存設定ファイルをチェック.

    Returns:
        設定ファイルパス、またはNoneが存在しない場合.

    """
    config_paths = [
        Path.home() / ".config" / "sysup" / "sysup.toml",
        Path.home() / ".sysup.toml",
        Path("/etc/sysup/sysup.toml"),
    ]

    for path in config_paths:
        if path.exists():
            return path

    return None


def handle_existing_config(config_path: Path) -> bool:
    """既存設定ファイルが見つかった場合の処理.

    Args:
        config_path: 既存設定ファイルのパス.

    Returns:
        Trueの場合はセットアップ継続、Falseの場合は中止.

    """
    console.print(
        Panel(
            f"既存の設定ファイルを検出しました:\n[yellow]{config_path}[/yellow]",
            style="yellow",
        )
    )

    console.print("\n以下のいずれかを選択してください:")
    console.print("  1. セットアップを続行（既存設定を更新）")
    console.print("  2. セットアップをスキップ（現在の設定を使用）")
    console.print("  3. 設定をリセット（デフォルトからやり直し）")

    choice = Prompt.ask("\n選択", choices=["1", "2", "3"], default="1")

    if choice == "1":
        console.print("[blue]既存設定を引き継いでセットアップを続行します[/blue]\n")
        return True
    elif choice == "2":
        console.print("[green]✓ 既存設定を使用して終了します。sysup をお使いください！[/green]")
        return False
    else:  # choice == "3"
        # バックアップ作成
        backup_path = config_path.parent / "sysup.toml.bak"
        shutil.copy2(config_path, backup_path)
        console.print(f"[blue]既存設定を {backup_path} に保存してリセットします[/blue]\n")
        return True


def step1_detect_system() -> dict[str, bool]:
    """工程1: システム環境の確認.

    Returns:
        利用可能なパッケージマネージャのマッピング.

    """
    console.print("[bold]工程 1/5: システム環境の確認[/bold]")

    available = PackageManagerDetector.get_available_managers()

    # 利用可能なマネージャのみを表示
    available_list = [name for name, is_available in available.items() if is_available]

    if available_list:
        console.print("✓ 以下のパッケージマネージャを検出しました:")
        for name in available_list:
            console.print(f"  • {name} ({PackageManagerDetector.get_manager_description(name)})")
    else:
        console.print("[yellow]⚠ パッケージマネージャが見つかりませんでした[/yellow]")

    console.print("[green]✓ 検出完了[/green]\n")
    return available


def step2_select_mode() -> str:
    """工程2: 実行モードの選択.

    Returns:
        選択されたモード ('disabled' または 'enabled').

    """
    console.print("[bold]工程 2/5: 実行モードの選択[/bold]")
    console.print("sysupの動作モードを選択してください:")
    console.print("  1. 標準モード（対話的、手動実行用）")
    console.print("  2. 自動実行モード（cronやスケジューラで定期実行用）")
    console.print("  3. スキップ（後で設定）")

    choice = Prompt.ask("\n選択", choices=["1", "2", "3"], default="1")

    if choice == "1":
        console.print("[blue]標準モードを選択しました[/blue]\n")
        return "disabled"
    elif choice == "2":
        console.print("[blue]自動実行モードを選択しました[/blue]\n")
        return "enabled"
    else:  # choice == "3"
        console.print("[blue]スキップしました（デフォルト: 標準モード）[/blue]\n")
        return "disabled"


def step3_select_updaters(available: dict[str, bool]) -> dict[str, bool]:
    """工程3: 更新対象の選択.

    Args:
        available: 利用可能なパッケージマネージャ.

    Returns:
        各マネージャの有効/無効設定.

    """
    console.print("[bold]工程 3/5: 更新対象パッケージマネージャの選択[/bold]")
    console.print("有効にするマネージャを選択してください (数字入力でトグル, Enterで確定):\n")

    # テーブルで選択肢を表示
    table = Table(title="パッケージマネージャ")
    table.add_column("No.", style="cyan")
    table.add_column("状態", style="green")
    table.add_column("マネージャ", style="yellow")
    table.add_column("説明")

    # デフォルト設定を読み込み
    default_config = SysupConfig()
    selected = {}

    managers_list = list(available.keys())
    for i, name in enumerate(managers_list, 1):
        is_enabled = default_config.is_updater_enabled(name)
        is_available = available[name]
        selected[name] = is_enabled

        status = "✓" if selected[name] else " "
        availability = "検出済み" if is_available else "未検出"
        description = PackageManagerDetector.get_manager_description(name)

        table.add_row(str(i), status, name, f"{description} ({availability})")

    console.print(table)

    # トグル入力ループ
    while True:
        console.print(f"\n数字を入力してトグル (1-{len(managers_list)}, q で確定):")
        user_input = Prompt.ask("入力").strip().lower()

        if user_input == "q":
            break

        try:
            idx = int(user_input) - 1
            if 0 <= idx < len(managers_list):
                name = managers_list[idx]
                selected[name] = not selected[name]
                status = "✓" if selected[name] else " "
                if selected[name] and not available[name]:
                    console.print(f"[yellow]⚠ {name} は未検出ですが有効にしました（後でインストール可能）[/yellow]")
                else:
                    console.print(f"[blue]{name}: {status if selected[name] else '無効に変更'}[/blue]")
            else:
                console.print("[red]✗ 無効な選択です[/red]")
        except ValueError:
            console.print("[red]✗ 数字を入力してください[/red]")

    console.print("[green]✓ 選択完了[/green]\n")
    selected_typed: dict[str, bool] = selected
    return selected_typed


def step4_advanced_settings() -> dict[str, bool | str]:
    """工程4: 詳細設定.

    Returns:
        詳細設定オプション.

    """
    console.print("[bold]工程 4/5: 詳細設定[/bold]")
    console.print("詳細設定を行いますか?")
    console.print("  1. はい（詳細設定を行う）")
    console.print("  2. いいえ（デフォルト値を使用）")

    choice = Prompt.ask("\n選択", choices=["1", "2"], default="2")

    settings: dict[str, bool | str] = {
        "parallel_updates": False,
        "log_level": "INFO",
        "backup_enabled": True,
        "notification_enabled": True,
    }

    if choice == "1":
        # ログレベル設定
        console.print("\nログレベルを選択してください:")
        console.print("  1. DEBUG (詳細）")
        console.print("  2. INFO (通常)")
        console.print("  3. WARNING (警告以上)")
        console.print("  4. ERROR (エラーのみ)")

        log_choice = Prompt.ask("選択", choices=["1", "2", "3", "4"], default="2")
        log_levels = {"1": "DEBUG", "2": "INFO", "3": "WARNING", "4": "ERROR"}
        settings["log_level"] = log_levels[log_choice]

        # 並列実行設定
        console.print("\n複数のパッケージマネージャを並列実行しますか?")
        console.print("  1. はい")
        console.print("  2. いいえ（逐次実行）")
        parallel_choice = Prompt.ask("選択", choices=["1", "2"], default="2")
        settings["parallel_updates"] = parallel_choice == "1"

        # バックアップ設定
        console.print("\nパッケージリストをバックアップしますか?")
        console.print("  1. はい")
        console.print("  2. いいえ")
        backup_choice = Prompt.ask("選択", choices=["1", "2"], default="1")
        settings["backup_enabled"] = backup_choice == "1"

        # 通知設定
        console.print("\nデスクトップ通知を有効にしますか?")
        console.print("  1. はい")
        console.print("  2. いいえ")
        notify_choice = Prompt.ask("選択", choices=["1", "2"], default="1")
        settings["notification_enabled"] = notify_choice == "1"

        console.print("[green]✓ 詳細設定完了[/green]\n")
    else:
        console.print("[blue]デフォルト値を使用します[/blue]\n")

    return settings


def step5_save_config(
    mode: str,
    updaters: dict[str, bool],
    settings: dict[str, bool | str],
    _existing_config: Path | None,
) -> None:
    """工程5: 設定ファイルの生成と保存.

    Args:
        mode: 実行モード.
        updaters: パッケージマネージャ設定.
        settings: 詳細設定.
        existing_config: 既存設定ファイルパス（更新の場合）.

    """
    console.print("[bold]工程 5/5: セットアップ完了[/bold]")

    # デフォルト設定を作成
    config = SysupConfig()

    # 各設定を更新
    for name, enabled in updaters.items():
        setattr(config.updaters, name, enabled)

    config.auto_run.mode = mode
    config.logging.level = str(settings["log_level"])
    config.general.parallel_updates = bool(settings["parallel_updates"])
    config.backup.enabled = bool(settings["backup_enabled"])
    config.notification.enabled = bool(settings["notification_enabled"])

    # 設定ファイルの保存先を決定
    config_dir = Path.home() / ".config" / "sysup"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "sysup.toml"

    # TOML形式で設定を保存
    toml_content = _generate_toml(config)
    config_file.write_text(toml_content)

    console.print("[green]✓ 設定ファイルを生成しました[/green]")
    console.print(f"  保存先: {config_file}\n")

    # 設定内容を表示
    console.print("[bold]生成された設定:[/bold]")
    console.print(toml_content)

    console.print("\n[bold green]✓ セットアップが完了しました！[/bold green]")
    console.print("\n次のコマンドで実行できます:")
    console.print("  [cyan]sysup update[/cyan]         # システムを更新")
    console.print("  [cyan]sysup update --list[/cyan]  # 利用可能なマネージャを確認")
    console.print("  [cyan]sysup init[/cyan]           # 設定を変更する場合")


def _generate_toml(config: SysupConfig) -> str:
    """SysupConfigをTOML形式の文字列に変換.

    Args:
        config: 設定オブジェクト.

    Returns:
        TOML形式の文字列.

    """
    lines = [
        "[updaters]",
        f"apt = {str(config.updaters.apt).lower()}",
        f"snap = {str(config.updaters.snap).lower()}",
        f"flatpak = {str(config.updaters.flatpak).lower()}",
        f"pipx = {str(config.updaters.pipx).lower()}",
        f"uv = {str(config.updaters.uv).lower()}",
        f"npm = {str(config.updaters.npm).lower()}",
        f"nvm = {str(config.updaters.nvm).lower()}",
        f"rustup = {str(config.updaters.rustup).lower()}",
        f"cargo = {str(config.updaters.cargo).lower()}",
        f"gem = {str(config.updaters.gem).lower()}",
        f"brew = {str(config.updaters.brew).lower()}",
        f"scoop = {str(config.updaters.scoop).lower()}",
        f"firmware = {str(config.updaters.firmware).lower()}",
        "",
        "[auto_run]",
        f'mode = "{config.auto_run.mode}"',
        "",
        "[logging]",
        f'dir = "{config.logging.dir}"',
        f"retention_days = {config.logging.retention_days}",
        f'level = "{config.logging.level}"',
        "",
        "[backup]",
        f'dir = "{config.backup.dir}"',
        f"enabled = {str(config.backup.enabled).lower()}",
        "",
        "[notification]",
        f"enabled = {str(config.notification.enabled).lower()}",
        f"on_success = {str(config.notification.on_success).lower()}",
        f"on_error = {str(config.notification.on_error).lower()}",
        f"on_warning = {str(config.notification.on_warning).lower()}",
        "",
        "[general]",
        f"parallel_updates = {str(config.general.parallel_updates).lower()}",
        f"dry_run = {str(config.general.dry_run).lower()}",
        f'cache_dir = "{config.general.cache_dir}"',
    ]

    return "\n".join(lines)


def init_command() -> None:
    """Sysup init コマンドのメイン処理."""
    try:
        show_header()

        # 既存設定ファイルのチェック
        existing_config = check_existing_config()
        if existing_config:
            if not handle_existing_config(existing_config):
                sys.exit(0)

        # ウィザード実行
        available = step1_detect_system()
        mode = step2_select_mode()
        updaters = step3_select_updaters(available)
        settings = step4_advanced_settings()
        step5_save_config(mode, updaters, settings, existing_config)

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ セットアップをキャンセルしました[/yellow]")
        console.print("後でセットアップするには: [cyan]sysup init[/cyan]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]✗ エラーが発生しました: {e}[/red]")
        sys.exit(1)
