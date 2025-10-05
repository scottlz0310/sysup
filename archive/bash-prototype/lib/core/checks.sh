#!/bin/bash
# lib/core/checks.sh - 事前チェック機能

# ディスク容量チェック
check_disk_space() {
    local min_space_gb=${1:-1}
    local available_gb=$(df / | awk 'NR==2 {printf "%.1f", $4/1024/1024}')
    
    if (( $(echo "$available_gb < $min_space_gb" | bc -l) )); then
        warning "利用可能なディスク容量が少なくなっています: ${available_gb}GB"
        return 1
    fi
    
    info "ディスク容量: ${available_gb}GB 利用可能"
    return 0
}

# ネットワーク接続チェック
check_network() {
    local test_hosts=("8.8.8.8" "1.1.1.1")
    
    for host in "${test_hosts[@]}"; do
        if ping -c 1 -W 3 "$host" >/dev/null 2>&1; then
            info "ネットワーク接続: OK"
            return 0
        fi
    done
    
    warning "ネットワーク接続に問題があります"
    return 1
}

# 日次実行チェック
check_daily_run() {
    local lock_file="${SYSUP_CACHE_DIR:-$HOME/.cache/sysup}/daily_run"
    local today=$(date +%Y-%m-%d)
    
    mkdir -p "$(dirname "$lock_file")"
    
    if [[ -f "$lock_file" ]]; then
        local last_run=$(cat "$lock_file" 2>/dev/null || echo "")
        if [[ "$last_run" == "$today" ]]; then
            info "今日は既に実行済みです: $today"
            return 1
        fi
    fi
    
    echo "$today" > "$lock_file"
    return 0
}

# 再起動が必要かチェック
check_reboot_required() {
    if [[ -f /var/run/reboot-required ]]; then
        warning "システムの再起動が必要です"
        if [[ -f /var/run/reboot-required.pkgs ]]; then
            info "再起動が必要なパッケージ:"
            cat /var/run/reboot-required.pkgs | sed 's/^/  - /'
        fi
        return 0
    fi
    
    return 1
}

# 管理者権限チェック
check_sudo_available() {
    if ! sudo -n true 2>/dev/null; then
        warning "一部の操作には管理者権限が必要です"
        return 1
    fi
    return 0
}

# プロセスロックチェック（多重実行防止）
check_process_lock() {
    local lock_file="${SYSUP_CACHE_DIR:-$HOME/.cache/sysup}/sysup.lock"
    local pid_file="${SYSUP_CACHE_DIR:-$HOME/.cache/sysup}/sysup.pid"
    
    mkdir -p "$(dirname "$lock_file")"
    
    if [[ -f "$lock_file" ]] && [[ -f "$pid_file" ]]; then
        local old_pid=$(cat "$pid_file" 2>/dev/null || echo "")
        if [[ -n "$old_pid" ]] && kill -0 "$old_pid" 2>/dev/null; then
            error "sysupは既に実行中です (PID: $old_pid)"
            return 1
        else
            # 古いロックファイルを削除
            rm -f "$lock_file" "$pid_file"
        fi
    fi
    
    # 新しいロックを作成
    echo $$ > "$pid_file"
    touch "$lock_file"
    
    # 終了時にロックファイルを削除するトラップを設定
    trap 'rm -f "$lock_file" "$pid_file"' EXIT
    
    return 0
}