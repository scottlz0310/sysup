"""sysup CLI インターフェース"""

import sys
import atexit
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from .core.config import SysupConfig
from .core.logging import SysupLogger
from .core.checks import SystemChecker
from .core.stats import StatsManager
from .updaters.apt import AptUpdater
from .updaters.snap import SnapUpdater
from .updaters.brew import BrewUpdater
from .updaters.npm import NpmUpdater
from .updaters.pipx import PipxUpdater
from .updaters.rustup import RustupUpdater
from .updaters.cargo import CargoUpdater
from .updaters.flatpak import FlatpakUpdater
from .updaters.gem import GemUpdater
from .updaters.nvm import NvmUpdater
from .updaters.firmware import FirmwareUpdater


@click.command()
@click.option("--config", "-c", type=click.Path(exists=True, path_type=Path), help="設定ファイルのパス")
@click.option("--dry-run", is_flag=True, help="実際には更新せず、何が更新されるか表示")
@click.option("--auto-run", is_flag=True, help="自動実行モード（対話なし）")
@click.option("--force", is_flag=True, help="今日既に実行済みでも強制実行")
@click.option("--list", "list_updaters", is_flag=True, help="利用可能なupdaterを一覧表示")
@click.version_option(version="0.1.0", prog_name="sysup")
def main(
    config: Optional[Path],
    dry_run: bool,
    auto_run: bool,
    force: bool,
    list_updaters: bool
) -> None:
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
    logger = SysupLogger(sysup_config.get_log_dir(), sysup_config.logging.level)
    
    # システムチェッカー初期化
    checker = SystemChecker(logger, sysup_config.get_cache_dir())
    
    # プロセスロックチェック
    if not checker.check_process_lock():
        sys.exit(1)
    
    # 終了時にロックファイルをクリーンアップ
    atexit.register(checker.cleanup_lock)
    
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


def show_available_updaters(logger: SysupLogger, config: SysupConfig) -> None:
    """利用可能なupdaterを一覧表示"""
    logger.section("利用可能なUpdater")
    
    updaters = [
        ("apt", AptUpdater(logger, config.general.dry_run)),
        ("snap", SnapUpdater(logger, config.general.dry_run)),
        ("brew", BrewUpdater(logger, config.general.dry_run)),
        ("npm", NpmUpdater(logger, config.general.dry_run)),
        ("pipx", PipxUpdater(logger, config.general.dry_run)),
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


def run_updates(
    logger: SysupLogger,
    config: SysupConfig,
    checker: SystemChecker,
    auto_run: bool,
    force: bool
) -> None:
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
    updaters = []
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


if __name__ == "__main__":
    main()