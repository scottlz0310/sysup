"""sysup CLI インターフェース"""

import atexit
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import click
from rich.console import Console

from . import __version__
from .core.backup import BackupManager
from .core.checks import SystemChecker
from .core.config import SysupConfig
from .core.logging import SysupLogger
from .core.notification import Notifier
from .core.stats import StatsManager
from .core.wsl import WSLIntegration
from .updaters.apt import AptUpdater
from .updaters.base import BaseUpdater
from .updaters.brew import BrewUpdater
from .updaters.cargo import CargoUpdater
from .updaters.firmware import FirmwareUpdater
from .updaters.flatpak import FlatpakUpdater
from .updaters.gem import GemUpdater
from .updaters.npm import NpmUpdater
from .updaters.nvm import NvmUpdater
from .updaters.pipx import PipxUpdater
from .updaters.rustup import RustupUpdater
from .updaters.snap import SnapUpdater
from .updaters.uv import UvUpdater


@click.command()
@click.option("--config", "-c", type=click.Path(exists=True, path_type=Path), help="設定ファイルのパス")
@click.option("--dry-run", is_flag=True, help="実際には更新せず、何が更新されるか表示")
@click.option("--auto-run", is_flag=True, help="自動実行モード（対話なし）")
@click.option("--force", is_flag=True, help="今日既に実行済みでも強制実行")
@click.option("--list", "list_updaters", is_flag=True, help="利用可能なupdaterを一覧表示")
@click.option("--setup-wsl", is_flag=True, help="WSL自動実行をセットアップ")
@click.version_option(version=__version__, prog_name="sysup")
def main(config: Path | None, dry_run: bool, auto_run: bool, force: bool, list_updaters: bool, setup_wsl: bool) -> None:
    """システムと各種パッケージマネージャを統合的に更新するツール"""

    # 設定読み込み
    try:
        sysup_config = SysupConfig.load_config(config)
    except Exception as e:
        click.echo(f"設定ファイル読み込みエラー: {e}", err=True)
        sys.exit(1)

    # ドライランモードの設定
    if dry_run:
        sysup_config.general.dry_run = True

    # ロガー初期化
    logger = SysupLogger(sysup_config.get_log_dir(), sysup_config.logging.level, sysup_config.logging.retention_days)

    # システムチェッカー初期化
    checker = SystemChecker(logger, sysup_config.get_cache_dir())

    # プロセスロックチェック
    if not checker.check_process_lock():
        sys.exit(1)

    # 終了時にロックファイルをクリーンアップ
    atexit.register(checker.cleanup_lock)

    # WSLセットアップ
    if setup_wsl:
        setup_wsl_integration(logger, sysup_config)
        return

    # updater一覧表示
    if list_updaters:
        show_available_updaters(logger, sysup_config)
        return

    # メイン処理
    try:
        run_updates(logger, sysup_config, checker, auto_run, force)
    except KeyboardInterrupt:
        logger.warning("ユーザーによって中断されました")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        sys.exit(1)


def setup_wsl_integration(logger: SysupLogger, config: SysupConfig) -> None:
    """WSL統合をセットアップ"""
    logger.section("WSL統合セットアップ")

    if not WSLIntegration.is_wsl():
        logger.error("WSL環境ではありません")
        return

    logger.info("WSL環境を検出しました")

    # 現在の設定を確認
    rc_file = WSLIntegration.get_shell_rc_file()
    if rc_file:
        logger.info(f"シェル設定ファイル: {rc_file}")

        if WSLIntegration.is_auto_run_configured(rc_file):
            logger.info("自動実行は既に設定されています")

            if click.confirm("設定を削除しますか？"):
                success, message = WSLIntegration.setup_wsl_integration("disabled")
                if success:
                    logger.success(message)
                else:
                    logger.error(message)
            return

    # 自動実行モードを選択
    logger.info("\n自動実行モードを選択してください:")
    logger.info("  1. 有効化（sudo認証なし）")
    logger.info("  2. 有効化（sudo認証あり）")
    logger.info("  3. キャンセル")

    choice = click.prompt("選択", type=int, default=1)

    if choice == 1:
        mode = "enabled"
    elif choice == 2:
        mode = "enabled_with_auth"
    else:
        logger.info("キャンセルしました")
        return

    # セットアップ実行
    success, message = WSLIntegration.setup_wsl_integration(mode)
    if success:
        logger.success(message)
        logger.info("\n次回のシェル起動時から自動実行が有効になります")
        logger.info("今すぐ有効にするには: source " + str(rc_file))
    else:
        logger.error(message)


def show_available_updaters(logger: SysupLogger, config: SysupConfig) -> None:
    """利用可能なupdaterを一覧表示"""
    logger.section("利用可能なUpdater")

    updaters = [
        ("apt", AptUpdater(logger, config.general.dry_run)),
        ("snap", SnapUpdater(logger, config.general.dry_run)),
        ("brew", BrewUpdater(logger, config.general.dry_run)),
        ("npm", NpmUpdater(logger, config.general.dry_run)),
        ("pipx", PipxUpdater(logger, config.general.dry_run)),
        ("uv", UvUpdater(logger, config.general.dry_run)),
        ("rustup", RustupUpdater(logger, config.general.dry_run)),
        ("cargo", CargoUpdater(logger, config.general.dry_run)),
        ("flatpak", FlatpakUpdater(logger, config.general.dry_run)),
        ("gem", GemUpdater(logger, config.general.dry_run)),
        ("nvm", NvmUpdater(logger, config.general.dry_run)),
        ("firmware", FirmwareUpdater(logger, config.general.dry_run)),
    ]

    for name, updater in updaters:
        enabled = config.is_updater_enabled(name)
        available = updater.is_available()

        status = "✓" if enabled and available else "✗" if not available else "-"
        status_text = "有効" if enabled and available else "利用不可" if not available else "無効"

        logger.info(f"  {status} {updater.get_name()}: {status_text}")


def run_updates(logger: SysupLogger, config: SysupConfig, checker: SystemChecker, auto_run: bool, force: bool) -> None:
    """更新実行"""

    # ヘッダー表示
    console = Console()
    if auto_run:
        console.print("╔════════════════════════════════════════╗", style="purple")
        console.print("║   自動システム更新                     ║", style="purple")
        console.print("╚════════════════════════════════════════╝", style="purple")
    else:
        console.print("╔════════════════════════════════════════╗", style="purple")
        console.print("║     sysup システム更新                ║", style="purple")
        console.print("╚════════════════════════════════════════╝", style="purple")

    # 統計管理初期化
    stats = StatsManager(logger)

    # 日次実行チェック
    if not force and not checker.check_daily_run():
        logger.info("今日は既にシステム更新が実行済みです")
        if not auto_run:
            if not click.confirm("強制実行しますか？"):
                return

    # バックアップ作成
    if config.backup.enabled:
        backup_manager = BackupManager(config.get_backup_dir(), config.backup.enabled)
        backup_file = backup_manager.create_backup()
        if backup_file:
            logger.info(f"バックアップ作成: {backup_file.name}")
            # 古いバックアップを削除
            deleted = backup_manager.cleanup_old_backups(keep_count=10)
            if deleted > 0:
                logger.info(f"古いバックアップを{deleted}件削除しました")

    # 事前チェック
    logger.section("システムチェック")

    if not checker.check_disk_space():
        if not auto_run and not click.confirm("ディスク容量が不足していますが続行しますか？"):
            return

    if not checker.check_network():
        if not auto_run and not click.confirm("ネットワーク接続に問題がありますが続行しますか？"):
            return

    if not checker.check_sudo_available():
        logger.warning("sudo権限が必要です")
        if auto_run:
            logger.error("自動実行モードではsudo権限が必要です")
            return

    # 更新実行
    logger.section("パッケージ更新")

    # 有効なupdaterを収集
    updaters: list[tuple[str, BaseUpdater]] = []
    if config.is_updater_enabled("apt"):
        updaters.append(("apt", AptUpdater(logger, config.general.dry_run)))
    if config.is_updater_enabled("snap"):
        updaters.append(("snap", SnapUpdater(logger, config.general.dry_run)))
    if config.is_updater_enabled("brew"):
        updaters.append(("brew", BrewUpdater(logger, config.general.dry_run)))
    if config.is_updater_enabled("npm"):
        updaters.append(("npm", NpmUpdater(logger, config.general.dry_run)))
    if config.is_updater_enabled("pipx"):
        updaters.append(("pipx", PipxUpdater(logger, config.general.dry_run)))
    if config.is_updater_enabled("uv"):
        updaters.append(("uv", UvUpdater(logger, config.general.dry_run)))
    if config.is_updater_enabled("rustup"):
        updaters.append(("rustup", RustupUpdater(logger, config.general.dry_run)))
    if config.is_updater_enabled("cargo"):
        updaters.append(("cargo", CargoUpdater(logger, config.general.dry_run)))
    if config.is_updater_enabled("flatpak"):
        updaters.append(("flatpak", FlatpakUpdater(logger, config.general.dry_run)))
    if config.is_updater_enabled("gem"):
        updaters.append(("gem", GemUpdater(logger, config.general.dry_run)))
    if config.is_updater_enabled("nvm"):
        updaters.append(("nvm", NvmUpdater(logger, config.general.dry_run)))
    if config.is_updater_enabled("firmware"):
        updaters.append(("firmware", FirmwareUpdater(logger, config.general.dry_run)))

    if not updaters:
        logger.warning("有効なupdaterがありません")
        return

    total_updaters = len(updaters)

    if config.general.parallel_updates:
        # 並列更新
        logger.info("並列更新モードで実行中...")

        def update_package(item: tuple[str, BaseUpdater]) -> tuple[str, str, str | None]:
            name, updater = item
            if not updater.is_available():
                return (name, "skip", "利用不可")
            try:
                if updater.perform_update():
                    return (name, "success", None)
                else:
                    return (name, "failure", "更新失敗")
            except Exception as e:
                return (name, "failure", str(e))

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(update_package, item): item for item in updaters}

            for i, future in enumerate(as_completed(futures), 1):
                name, status, error = future.result()
                logger.progress_step(i, total_updaters, f"{name}完了")

                if status == "success":
                    stats.record_success(name)
                elif status == "skip":
                    stats.record_skip(name, error or "不明")
                else:
                    stats.record_failure(name, error or "不明")
    else:
        # 逐次更新
        for i, (name, updater) in enumerate(updaters, 1):
            logger.progress_step(i, total_updaters, f"{updater.get_name()}を更新中")

            if not updater.is_available():
                stats.record_skip(name, "利用不可")
                continue

            try:
                if updater.perform_update():
                    stats.record_success(name)
                else:
                    stats.record_failure(name, "更新失敗")
            except Exception as e:
                stats.record_failure(name, str(e))

    # 再起動チェック
    if checker.check_reboot_required():
        if not auto_run and click.confirm("今すぐ再起動しますか？"):
            logger.info("5秒後に再起動します...")
            import time

            time.sleep(5)
            import subprocess

            subprocess.run(["sudo", "reboot"])
        else:
            logger.warning("後で手動で再起動してください")

    # サマリー表示
    stats.show_summary()
    stats.save_to_log(config.get_log_dir())

    logger.success("🎉 システム更新が完了しました！")

    # デスクトップ通知
    if config.notification.enabled and Notifier.is_available():
        success_count = stats.stats.success_count
        failure_count = stats.stats.failure_count

        if failure_count > 0 and config.notification.on_error:
            Notifier.send_error("sysup", f"更新完了: {success_count}件成功, {failure_count}件失敗")
        elif success_count > 0 and config.notification.on_success:
            Notifier.send_success("sysup", f"システム更新が完了しました ({success_count}件)")


if __name__ == "__main__":
    main()
