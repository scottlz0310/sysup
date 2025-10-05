#!/bin/bash

# ===================================================================
# インテリジェント システム更新スクリプト
# 作成日: $(date +%Y-%m-%d)
# ===================================================================

set -euo pipefail  # エラー時に即座に停止

# 設定
LOG_DIR="$HOME/logs"
LOG_FILE="$LOG_DIR/system_update_$(date +%Y%m%d_%H%M%S).log"
BACKUP_DIR="$HOME/backups/$(date +%Y%m%d_%H%M%S)"
LOCK_FILE="/tmp/system_update.lock"
AUTO_RUN_FLAG="$HOME/.system_update_auto_run"
LAST_RUN_DATE_FILE="$HOME/.last_system_update_date"

# 統計情報
START_TIME=$(date +%s)
UPDATED_PACKAGES=0
REMOVED_PACKAGES=0
SNAP_UPDATES=0
ADDITIONAL_UPDATES=()

# 色付きメッセージ用の定数
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ===================================================================
# ユーティリティ関数
# ===================================================================

# ログとコンソールに同時出力
log_message() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# 成功メッセージ
success() {
    echo -e "${GREEN}✓${NC} $*"
    log_message "SUCCESS" "$*"
}

# 情報メッセージ
info() {
    echo -e "${BLUE}ℹ${NC} $*"
    log_message "INFO" "$*"
}

# 警告メッセージ
warning() {
    echo -e "${YELLOW}⚠${NC} $*"
    log_message "WARNING" "$*"
}

# エラーメッセージ
error() {
    echo -e "${RED}✗${NC} $*" >&2
    log_message "ERROR" "$*"
}

# プログレスバー
show_progress() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((current * width / total))
    local remaining=$((width - completed))
    
    printf "\r${CYAN}進捗:${NC} ["
    printf "%*s" "$completed" "" | tr ' ' '='
    printf "%*s" "$remaining" "" | tr ' ' '-'
    printf "] %d%% (%d/%d)" "$percentage" "$current" "$total"
}

# 確認プロンプト
confirm() {
    local message="$1"
    echo -e "${YELLOW}$message${NC} (y/N): "
    read -r response
    case "$response" in
        [yY][eE][sS]|[yY])
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# 今日既に実行されたかチェック
check_daily_run() {
    local today=$(date +%Y-%m-%d)
    
    if [[ -f "$LAST_RUN_DATE_FILE" ]]; then
        local last_run_date=$(cat "$LAST_RUN_DATE_FILE" 2>/dev/null || echo "")
        if [[ "$last_run_date" == "$today" ]]; then
            return 1  # 今日既に実行済み
        fi
    fi
    return 0  # 今日未実行
}

# 実行日付を記録
record_run_date() {
    echo "$(date +%Y-%m-%d)" > "$LAST_RUN_DATE_FILE"
}

# WSL自動実行の設定
setup_auto_run() {
    local bashrc="$HOME/.bashrc"
    local auto_run_code='
# WSL初回起動時のシステム更新自動実行
if [[ -n "$WSL_DISTRO_NAME" ]] && [[ -f "$HOME/up.sh" ]]; then
    if [[ ! -f "$HOME/.system_update_auto_run" ]] || [[ "$(cat "$HOME/.system_update_auto_run" 2>/dev/null)" != "enabled" ]]; then
        echo "🚀 WSL初回起動時のシステム更新自動実行が有効になりました"
        echo "   無効にする場合は: echo \"disabled\" > ~/.system_update_auto_run"
        echo "enabled" > "$HOME/.system_update_auto_run"
    fi
    
    if [[ "$(cat "$HOME/.system_update_auto_run" 2>/dev/null)" == "enabled" ]]; then
        if bash "$HOME/up.sh" --check-auto-run; then
            echo "🔄 システム更新を自動実行しています..."
            bash "$HOME/up.sh" --auto-run &
            disown
        fi
    fi
fi'
    
    if ! grep -q "WSL初回起動時のシステム更新自動実行" "$bashrc" 2>/dev/null; then
        echo "$auto_run_code" >> "$bashrc"
        info "自動実行設定を.bashrcに追加しました"
        info "次回のWSL起動時から自動更新が有効になります"
    fi
}

# ディスク容量チェック
check_disk_space() {
    local required_space=1000000  # 1GB in KB
    local available_space=$(df / | awk 'NR==2 {print $4}')
    
    if [[ $available_space -lt $required_space ]]; then
        error "ディスク容量が不足しています（必要: 1GB, 利用可能: $(($available_space/1024))MB）"
        return 1
    fi
}

# ネットワーク接続チェック
check_network() {
    if ! ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        error "インターネット接続が確認できません"
        return 1
    fi
}

# システム情報取得
get_system_info() {
    echo "=== システム情報 ==="
    echo "OS: $(lsb_release -d | cut -f2)"
    echo "カーネル: $(uname -r)"
    echo "アップタイム: $(uptime -p)"
    echo "メモリ使用量: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
    echo "ディスク使用量: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')"
    echo "更新可能パッケージ数: $(apt list --upgradable 2>/dev/null | wc -l)"
    echo
}

# 重要ファイルのバックアップ
backup_critical_files() {
    info "重要な設定ファイルをバックアップしています..."
    
    mkdir -p "$BACKUP_DIR"
    
    local files_to_backup=(
        "/etc/apt/sources.list"
        "/etc/apt/sources.list.d/"
        "/etc/fstab"
        "/etc/hosts"
        "/etc/hostname"
        "$HOME/.bashrc"
        "$HOME/.profile"
    )
    
    for file in "${files_to_backup[@]}"; do
        if [[ -e "$file" ]]; then
            cp -r "$file" "$BACKUP_DIR/" 2>/dev/null || true
        fi
    done
    
    success "バックアップ完了: $BACKUP_DIR"
}

# パッケージ更新前のクリーンアップ
pre_update_cleanup() {
    info "更新前のクリーンアップを実行しています..."
    
    # キャッシュクリーンアップ
    sudo apt autoclean
    
    # 破損したパッケージの修復
    sudo apt --fix-broken install -y
    
    success "クリーンアップ完了"
}

# メイン更新処理
perform_system_update() {
    local total_steps=7
    local current_step=0
    
    echo -e "\n${PURPLE}=== システム更新を開始します ===${NC}\n"
    
    # ステップ1: パッケージリスト更新
    ((current_step++))
    show_progress $current_step $total_steps
    echo -e "\n${CYAN}ステップ $current_step/$total_steps: パッケージリストを更新しています...${NC}"
    if sudo apt update; then
        success "パッケージリスト更新完了"
    else
        error "パッケージリスト更新に失敗しました"
        return 1
    fi
    
    # ステップ2: 更新可能パッケージの確認
    ((current_step++))
    show_progress $current_step $total_steps
    echo -e "\n${CYAN}ステップ $current_step/$total_steps: 更新可能パッケージを確認しています...${NC}"
    # ヘッダー行を除いた行数で判定
    local upgradable_count=$(apt list --upgradable 2>/dev/null | tail -n +2 | wc -l)
    info "更新可能パッケージ数: $upgradable_count"
    
    if [[ $upgradable_count -eq 0 ]]; then
        success "すべてのパッケージが最新です"
        info "パッケージの更新は不要ですが、クリーンアップとSnapパッケージの更新は続行します"
    fi
    
    # ステップ3: パッケージアップグレード
    ((current_step++))
    show_progress $current_step $total_steps
    echo -e "\n${CYAN}ステップ $current_step/$total_steps: パッケージをアップグレードしています...${NC}"
    if [[ $upgradable_count -gt 0 ]]; then
        if sudo apt upgrade -y; then
            UPDATED_PACKAGES=$upgradable_count
            success "パッケージアップグレード完了"
        else
            error "パッケージアップグレードに失敗しました"
            return 1
        fi
    else
        info "更新可能パッケージがないため、アップグレードをスキップします"
        success "パッケージアップグレード完了（スキップ）"
    fi
    
    # ステップ4: 不要パッケージ削除
    ((current_step++))
    show_progress $current_step $total_steps
    echo -e "\n${CYAN}ステップ $current_step/$total_steps: 不要なパッケージを削除しています...${NC}"
    local removable_count=$(apt autoremove --dry-run 2>/dev/null | grep -c '^Remv' || echo 0)
    if sudo apt autoremove -y; then
        REMOVED_PACKAGES=$removable_count
        success "不要パッケージ削除完了"
    else
        warning "不要パッケージ削除で問題が発生しました"
    fi
    
    # ステップ5: Snapパッケージ更新
    ((current_step++))
    show_progress $current_step $total_steps
    echo -e "\n${CYAN}ステップ $current_step/$total_steps: Snapパッケージを更新しています...${NC}"
    if command -v snap >/dev/null 2>&1; then
        local snap_count=$(snap list 2>/dev/null | wc -l)
        if sudo snap refresh; then
            SNAP_UPDATES=$((snap_count - 1))  # ヘッダー行を除く
            success "Snapパッケージ更新完了"
        else
            warning "Snapパッケージ更新で問題が発生しました"
        fi
    else
        info "Snapがインストールされていません - スキップ"
    fi
    
    # 追加パッケージ管理システムの更新
    update_additional_packages
    
    # ステップ7: 最終クリーンアップ
    ((current_step++))
    show_progress $current_step $total_steps
    echo -e "\n${CYAN}ステップ $current_step/$total_steps: 最終クリーンアップを実行しています...${NC}"
    sudo apt autoremove -y
    sudo apt autoclean
    success "最終クリーンアップ完了"
    
    echo
}

# 追加パッケージ管理システムの更新
update_additional_packages() {
    info "追加パッケージ管理システムを更新しています..."
    local updated_systems=()
    local skipped_systems=()
    
    # Flatpak更新
    if command -v flatpak >/dev/null 2>&1; then
        info "Flatpakパッケージを更新中..."
        if flatpak update -y 2>/dev/null; then
            success "Flatpak更新完了"
            updated_systems+=("Flatpak")
        else
            warning "Flatpak更新で問題が発生しました"
        fi
    else
        skipped_systems+=("Flatpak")
    fi
    
    # pipx更新（Python CLIアプリケーション）
    if command -v pipx >/dev/null 2>&1; then
        info "pipxパッケージを更新中..."
        if pipx upgrade-all 2>/dev/null; then
            success "pipx更新完了"
            updated_systems+=("pipx")
        else
            warning "pipx更新で問題が発生しました"
        fi
    else
        skipped_systems+=("pipx")
    fi
    
    # npm更新（グローバルパッケージ）
    if command -v npm >/dev/null 2>&1; then
        info "npmパッケージを更新中..."
        if npm update -g 2>/dev/null; then
            success "npm更新完了"
            updated_systems+=("npm")
        else
            warning "npm更新で問題が発生しました"
        fi
    else
        skipped_systems+=("npm")
    fi
    
    # Rust環境のPATH設定
    if [[ -f "$HOME/.cargo/env" ]]; then
        source "$HOME/.cargo/env"
    fi
    
    # Homebrew環境のPATH設定
    if [[ -x "/home/linuxbrew/.linuxbrew/bin/brew" ]]; then
        eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    fi
    
    # Rustup更新（Rustツールチェーン）
    if command -v rustup >/dev/null 2>&1; then
        info "Rustupを更新中..."
        if rustup update 2>/dev/null; then
            success "Rustup更新完了"
            updated_systems+=("rustup")
        else
            warning "Rustup更新で問題が発生しました"
        fi
    else
        skipped_systems+=("rustup")
    fi
    
    # cargo更新
    if command -v cargo >/dev/null 2>&1; then
        if command -v cargo-install-update >/dev/null 2>&1; then
            info "cargoパッケージを更新中..."
            if cargo install-update -a 2>/dev/null; then
                success "cargo更新完了"
                updated_systems+=("cargo")
            else
                warning "cargo更新で問題が発生しました"
            fi
        else
            info "cargo-install-updateがインストールされていません - cargoパッケージ更新をスキップ"
        fi
    else
        skipped_systems+=("cargo")
    fi
    
    # gem更新
    if command -v gem >/dev/null 2>&1; then
        info "gemパッケージを更新中..."
        if gem update --user-install 2>/dev/null; then
            success "gem更新完了"
            updated_systems+=("gem")
        else
            warning "gem更新で問題が発生しました"
        fi
    else
        skipped_systems+=("gem")
    fi
    
    # Homebrew更新
    if command -v brew >/dev/null 2>&1; then
        info "Homebrewパッケージを更新中..."
        # Homebrewのパッケージリストを更新
        if brew update 2>/dev/null; then
            # アップグレード可能なパッケージがあるかチェック
            local outdated_count=$(brew outdated --quiet | wc -l)
            if [[ $outdated_count -gt 0 ]]; then
                info "更新可能なHomebrewパッケージ: $outdated_count 個"
                if brew upgrade 2>/dev/null; then
                    success "Homebrew更新完了"
                    updated_systems+=("Homebrew")
                else
                    warning "Homebrew更新で問題が発生しました"
                fi
            else
                info "すべてのHomebrewパッケージが最新です"
                success "Homebrew更新完了（更新なし）"
                updated_systems+=("Homebrew")
            fi
            # クリーンアップも実行
            brew cleanup 2>/dev/null || true
        else
            warning "Homebrewの更新チェックで問題が発生しました"
        fi
    else
        skipped_systems+=("Homebrew")
    fi
    
    # ファームウェア更新
    if command -v fwupdmgr >/dev/null 2>&1; then
        info "ファームウェアを確認中..."
        if fwupdmgr refresh 2>/dev/null && fwupdmgr update -y 2>/dev/null; then
            success "ファームウェア更新完了"
            updated_systems+=("firmware")
        else
            info "ファームウェア更新なし"
        fi
    else
        skipped_systems+=("firmware")
    fi
    
    # 結果を統計に保存
    ADDITIONAL_UPDATES=("${updated_systems[@]}")
    
    if [[ ${#skipped_systems[@]} -gt 0 ]]; then
        info "スキップされたパッケージ管理システム: ${skipped_systems[*]}"
    fi
}

# 再起動が必要かチェック
check_reboot_required() {
    if [[ -f /var/run/reboot-required ]]; then
        warning "システムの再起動が必要です"
        if [[ -f /var/run/reboot-required.pkgs ]]; then
            echo "再起動が必要なパッケージ:"
            sed 's/^/  - /' < /var/run/reboot-required.pkgs
        fi
        echo
        if confirm "今すぐ再起動しますか？"; then
            info "5秒後に再起動します..."
            sleep 5
            sudo reboot
        else
            warning "後で手動で再起動してください"
        fi
    else
        success "再起動は不要です"
    fi
}

# 更新サマリー表示
show_update_summary() {
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    echo -e "\n${PURPLE}╔════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║            更新サマリー                ║${NC}"
    echo -e "${PURPLE}╚════════════════════════════════════════╝${NC}\n"
    
    echo -e "${CYAN}📊 実行統計:${NC}"
    echo "   実行時間: ${minutes}分${seconds}秒"
    echo "   開始時刻: $(date -d @$START_TIME '+%Y-%m-%d %H:%M:%S')"
    echo "   終了時刻: $(date '+%Y-%m-%d %H:%M:%S')"
    echo
    
    echo -e "${CYAN}📦 パッケージ更新:${NC}"
    echo "   更新されたパッケージ: $UPDATED_PACKAGES 個"
    echo "   削除されたパッケージ: $REMOVED_PACKAGES 個"
    echo "   Snapパッケージ: $SNAP_UPDATES 個"
    if [[ ${#ADDITIONAL_UPDATES[@]} -gt 0 ]]; then
        echo "   追加パッケージ管理システム: ${ADDITIONAL_UPDATES[*]}"
    else
        echo "   追加パッケージ管理システム: なし"
    fi
    echo
    
    echo -e "${CYAN}💾 システム情報:${NC}"
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}')
    local memory_usage=$(free -h | awk '/^Mem:/ {print $3 "/" $2}')
    echo "   ディスク使用量: $disk_usage"
    echo "   メモリ使用量: $memory_usage"
    echo
    
    echo -e "${CYAN}📁 ファイル:${NC}"
    echo "   ログファイル: $LOG_FILE"
    if [[ -d "$BACKUP_DIR" ]]; then
        echo "   バックアップ: $BACKUP_DIR"
    fi
    echo
    
    # 再起動が必要かどうかの状態
    if [[ -f /var/run/reboot-required ]]; then
        echo -e "${YELLOW}⚠ 注意: システムの再起動が必要です${NC}"
    else
        echo -e "${GREEN}✓ 再起動は不要です${NC}"
    fi
    
    echo -e "\n${GREEN}🎉 システム更新が正常に完了しました！${NC}"
}

# ===================================================================
# メイン実行部
# ===================================================================

main() {
    local auto_run=false
    local check_auto_run=false
    
    # 自動実行モードの場合の追加セキュリティチェック
    if [[ "${1:-}" == "--auto-run" ]]; then
        # 非インタラクティブ環境では実行しない
        if [[ $- != *i* ]]; then
            error "セキュリティ上の理由により、非インタラクティブ環境では自動実行されません"
            exit 1
        fi
        
        # TTYが利用可能かチェック
        if [[ ! -t 0 ]] || [[ ! -t 1 ]] || [[ ! -t 2 ]]; then
            error "セキュリティ上の理由により、TTYが利用できない環境では自動実行されません"
            exit 1
        fi
        
        # SSH経由でのリモート実行をチェック
        if [[ -n "${SSH_CLIENT:-}" ]] || [[ -n "${SSH_TTY:-}" ]]; then
            warning "SSH経由での自動実行が検出されました"
            if [[ ! -f "$HOME/.allow_ssh_auto_update" ]]; then
                error "SSH経由での自動実行は無効化されています"
                info "有効にする場合は: touch ~/.allow_ssh_auto_update"
                exit 1
            fi
        fi
    fi
    
    # コマンドライン引数の解析
    while [[ $# -gt 0 ]]; do
        case $1 in
            --auto-run)
                auto_run=true
                shift
                ;;
            --check-auto-run)
                check_auto_run=true
                shift
                ;;
            --setup-auto-run)
                setup_auto_run
                exit 0
                ;;
            --disable-auto-run)
                echo "disabled" > "$AUTO_RUN_FLAG"
                echo "自動実行を無効にしました"
                exit 0
                ;;
            --enable-auto-run)
                echo "enabled" > "$AUTO_RUN_FLAG"
                echo "自動実行を有効にしました"
                exit 0
                ;;
            --enable-auto-run-with-auth)
                echo "enabled_with_auth" > "$AUTO_RUN_FLAG"
                echo "事前認証付き自動実行を有効にしました"
                echo "次回WSL起動時にsudoパスワードの入力が求められます"
                exit 0
                ;;
            -h|--help)
                echo "使用方法: $0 [オプション]"
                echo ""
                echo "オプション:"
                echo "  --auto-run              自動実行モード（対話なし）"
                echo "  --check-auto-run        自動実行が必要かチェックのみ"
                echo "  --setup-auto-run        .bashrcに自動実行設定を追加"
                echo "  --enable-auto-run       自動実行を有効化"
                echo "  --enable-auto-run-with-auth  事前認証付き自動実行を有効化"
                echo "  --disable-auto-run      自動実行を無効化"
                echo "  -h, --help              このヘルプを表示"
                echo ""
                echo "自動実行モード:"
                echo "  enabled              : sudo権限がキャッシュされている場合のみ実行"
                echo "  enabled_with_auth    : WSL起動時にsudoパスワードを要求して実行"
                echo "  disabled             : 自動実行を無効化"
                exit 0
                ;;
            *)
                error "不明なオプション: $1"
                exit 1
                ;;
        esac
    done
    
    # 自動実行チェックモード
    if $check_auto_run; then
        local auto_run_mode=$(cat "$AUTO_RUN_FLAG" 2>/dev/null)
        if [[ "$auto_run_mode" != "enabled" ]] && [[ "$auto_run_mode" != "enabled_with_auth" ]]; then
            exit 1  # 自動実行無効
        fi
        if ! check_daily_run; then
            exit 1  # 今日既に実行済み
        fi
        exit 0  # 自動実行可能
    fi
    
    # ロック機能
    if [[ -f "$LOCK_FILE" ]]; then
        error "別のインスタンスが実行中です"
        exit 1
    fi
    trap 'rm -f "$LOCK_FILE"' EXIT
    touch "$LOCK_FILE"
    
    # 初期化
    mkdir -p "$LOG_DIR"
    touch "$LOG_FILE"
    
    echo -e "${PURPLE}╔════════════════════════════════════════╗${NC}"
    if $auto_run; then
        echo -e "${PURPLE}║   自動システム更新 ($(date '+%H:%M'))      ║${NC}"
    else
        echo -e "${PURPLE}║     インテリジェント システム更新      ║${NC}"
    fi
    echo -e "${PURPLE}╚════════════════════════════════════════╝${NC}\n"
    
    # ルート権限チェック
    if [[ $EUID -eq 0 ]]; then
        error "このスクリプトはrootユーザーで実行しないでください"
        exit 1
    fi
    
    # 自動実行モードの場合の特別処理
    if $auto_run; then
        info "自動実行モードで開始します..."
        
        # 今日既に実行されているかチェック
        if ! check_daily_run; then
            info "今日は既にシステム更新が実行済みです"
            exit 0
        fi
        
        # sudoアクセスチェック（パスワード要求なし）
        if ! sudo -n true 2>/dev/null; then
            info "sudo権限がキャッシュされていないため、自動実行をスキップします"
            info "手動でパスワードを入力してシステム更新を実行してください"
            info "または以下のコマンドでsudoタイムアウトを延長できます："
            info "  sudo visudo"
            info "  以下の行を追加: Defaults timestamp_timeout=60  # 60分間有効"
            exit 0
        fi
        
        # sudoタイムアウトを延長（15分）
        sudo -v
        
        # バックアップは作成しない（自動実行時）
        # 確認プロンプトもスキップ
    else
        # 手動実行の場合
        if [[ "$(cat "$AUTO_RUN_FLAG" 2>/dev/null)" != "enabled" ]]; then
            if confirm "WSL初回起動時の自動実行機能を有効にしますか？"; then
                setup_auto_run
                echo
            fi
        fi
        
        # sudoアクセスチェック
        if ! sudo -n true 2>/dev/null; then
            info "sudo権限が必要です。パスワードを入力してください。"
            sudo -v || {
                error "sudo権限が取得できませんでした"
                exit 1
            }
        fi
    fi
    
    # 事前チェック
    info "システムチェックを実行しています..."
    check_disk_space || exit 1
    check_network || exit 1
    
    # 更新前システム情報表示
    info "更新前のシステム情報:"
    get_system_info
    
    # バックアップ作成（手動実行時のみ）
    if ! $auto_run; then
        if confirm "重要ファイルのバックアップを作成しますか？"; then
            backup_critical_files
        fi
    fi
    
    # 更新前クリーンアップ
    pre_update_cleanup
    
    # メイン更新処理
    if perform_system_update; then
        success "システム更新が完了しました"
        record_run_date  # 実行日付を記録
    else
        error "システム更新中にエラーが発生しました"
        exit 1
    fi
    
    # 再起動チェック（自動実行時は再起動しない）
    if ! $auto_run; then
        check_reboot_required
    else
        if [[ -f /var/run/reboot-required ]]; then
            warning "システムの再起動が必要です（後で手動で再起動してください）"
        fi
    fi
    
    # サマリー表示
    show_update_summary
    
    # 完了通知（notify-sendがある場合）
    if command -v notify-send >/dev/null 2>&1; then
        if $auto_run; then
            notify-send "自動システム更新完了" "バックグラウンドでシステムの更新が完了しました" -i software-update-available
        else
            notify-send "システム更新完了" "システムの更新が正常に完了しました" -i software-update-available
        fi
    fi
}

# スクリプト実行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
