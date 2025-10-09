#!/bin/bash
# lib/core/config.sh - 設定ファイル読み込み

# デフォルト設定値
set_default_config() {
    # 更新対象の有効/無効
    ENABLE_APT=${ENABLE_APT:-true}
    ENABLE_SNAP=${ENABLE_SNAP:-true}
    ENABLE_FLATPAK=${ENABLE_FLATPAK:-false}
    ENABLE_PIPX=${ENABLE_PIPX:-true}
    ENABLE_NPM=${ENABLE_NPM:-true}
    ENABLE_NVM=${ENABLE_NVM:-true}
    ENABLE_RUSTUP=${ENABLE_RUSTUP:-true}
    ENABLE_CARGO=${ENABLE_CARGO:-true}
    ENABLE_GEM=${ENABLE_GEM:-false}
    ENABLE_BREW=${ENABLE_BREW:-true}
    ENABLE_FIRMWARE=${ENABLE_FIRMWARE:-false}

    # 自動実行設定
    AUTO_RUN_MODE=${AUTO_RUN_MODE:-"disabled"}

    # ログ設定
    SYSUP_LOG_DIR=${SYSUP_LOG_DIR:-"$HOME/.local/share/sysup"}
    LOG_RETENTION_DAYS=${LOG_RETENTION_DAYS:-30}

    # バックアップ設定
    SYSUP_BACKUP_DIR=${SYSUP_BACKUP_DIR:-"$HOME/.local/share/sysup/backups"}
    ENABLE_BACKUP=${ENABLE_BACKUP:-true}

    # キャッシュディレクトリ
    SYSUP_CACHE_DIR=${SYSUP_CACHE_DIR:-"$HOME/.cache/sysup"}

    # その他
    PARALLEL_UPDATES=${PARALLEL_UPDATES:-false}
    DRY_RUN=${DRY_RUN:-false}
}

# 設定ファイルを読み込み
load_config() {
    # デフォルト設定を適用
    set_default_config

    # 設定ファイルのパス
    local config_paths=(
        "${SYSUP_CONFIG_FILE:-}"
        "${XDG_CONFIG_HOME:-$HOME/.config}/sysup/sysup.conf"
        "$HOME/.sysup.conf"
        "/etc/sysup/sysup.conf"
    )

    # 設定ファイルを順番に探して読み込み
    for config_file in "${config_paths[@]}"; do
        if [[ -n "$config_file" ]] && [[ -f "$config_file" ]]; then
            info "設定ファイルを読み込み: $config_file"
            # shellcheck source=/dev/null
            source "$config_file"
            return 0
        fi
    done

    info "設定ファイルが見つかりません。デフォルト設定を使用します"
    return 0
}

# 設定値の検証
validate_config() {
    # AUTO_RUN_MODEの検証
    case "$AUTO_RUN_MODE" in
        disabled|enabled|enabled_with_auth)
            ;;
        *)
            warning "無効なAUTO_RUN_MODE: $AUTO_RUN_MODE (disabled/enabled/enabled_with_auth)"
            AUTO_RUN_MODE="disabled"
            ;;
    esac

    # ディレクトリの作成
    mkdir -p "$SYSUP_LOG_DIR" "$SYSUP_BACKUP_DIR" "$SYSUP_CACHE_DIR"

    return 0
}

# 設定値を表示（デバッグ用）
show_config() {
    show_section "現在の設定"

    echo "更新対象:"
    echo "  APT: $ENABLE_APT"
    echo "  Snap: $ENABLE_SNAP"
    echo "  Flatpak: $ENABLE_FLATPAK"
    echo "  pipx: $ENABLE_PIPX"
    echo "  npm: $ENABLE_NPM"
    echo "  nvm: $ENABLE_NVM"
    echo "  Rustup: $ENABLE_RUSTUP"
    echo "  Cargo: $ENABLE_CARGO"
    echo "  Gem: $ENABLE_GEM"
    echo "  Homebrew: $ENABLE_BREW"
    echo "  Firmware: $ENABLE_FIRMWARE"

    echo ""
    echo "その他の設定:"
    echo "  自動実行モード: $AUTO_RUN_MODE"
    echo "  ログディレクトリ: $SYSUP_LOG_DIR"
    echo "  バックアップディレクトリ: $SYSUP_BACKUP_DIR"
    echo "  バックアップ有効: $ENABLE_BACKUP"
    echo "  並列更新: $PARALLEL_UPDATES"
    echo "  ドライラン: $DRY_RUN"
}
