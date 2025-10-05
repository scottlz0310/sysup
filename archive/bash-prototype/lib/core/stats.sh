#!/bin/bash
# lib/core/stats.sh - 統計情報管理

# 統計情報を格納する連想配列
declare -A STATS_SUCCESS=()
declare -A STATS_FAILED=()
declare -A STATS_SKIPPED=()

# 統計情報の初期化
init_stats() {
    STATS_SUCCESS=()
    STATS_FAILED=()
    STATS_SKIPPED=()
    STATS_START_TIME=$(date +%s)
}

# 成功を記録
record_success() {
    local updater="$1"
    STATS_SUCCESS["$updater"]=1
}

# 失敗を記録
record_failure() {
    local updater="$1"
    local reason="${2:-不明なエラー}"
    STATS_FAILED["$updater"]="$reason"
}

# スキップを記録
record_skip() {
    local updater="$1"
    local reason="${2:-利用不可}"
    STATS_SKIPPED["$updater"]="$reason"
}

# 統計サマリーを表示
show_update_summary() {
    local end_time=$(date +%s)
    local duration=$((end_time - STATS_START_TIME))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    show_section "更新サマリー"
    
    # 成功した更新
    local success_count=${#STATS_SUCCESS[@]}
    if [[ $success_count -gt 0 ]]; then
        success "成功: $success_count 件"
        for updater in "${!STATS_SUCCESS[@]}"; do
            echo "  ✓ $updater"
        done
    fi
    
    # 失敗した更新
    local failed_count=${#STATS_FAILED[@]}
    if [[ $failed_count -gt 0 ]]; then
        error "失敗: $failed_count 件"
        for updater in "${!STATS_FAILED[@]}"; do
            echo "  ✗ $updater: ${STATS_FAILED[$updater]}"
        done
    fi
    
    # スキップした更新
    local skipped_count=${#STATS_SKIPPED[@]}
    if [[ $skipped_count -gt 0 ]]; then
        info "スキップ: $skipped_count 件"
        for updater in "${!STATS_SKIPPED[@]}"; do
            echo "  - $updater: ${STATS_SKIPPED[$updater]}"
        done
    fi
    
    # 実行時間
    if [[ $minutes -gt 0 ]]; then
        info "実行時間: ${minutes}分${seconds}秒"
    else
        info "実行時間: ${seconds}秒"
    fi
    
    # 総合結果
    local total_count=$((success_count + failed_count))
    if [[ $total_count -eq 0 ]]; then
        warning "実行された更新はありませんでした"
    elif [[ $failed_count -eq 0 ]]; then
        success "全ての更新が正常に完了しました"
    else
        warning "$failed_count 件の更新で問題が発生しました"
    fi
}

# 統計情報をログファイルに保存
save_stats_to_log() {
    local log_file="${SYSUP_LOG_DIR:-$HOME/.local/share/sysup}/update.log"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    mkdir -p "$(dirname "$log_file")"
    
    {
        echo "=== Update Summary - $timestamp ==="
        echo "Success: ${#STATS_SUCCESS[@]} items"
        for updater in "${!STATS_SUCCESS[@]}"; do
            echo "  SUCCESS: $updater"
        done
        
        echo "Failed: ${#STATS_FAILED[@]} items"
        for updater in "${!STATS_FAILED[@]}"; do
            echo "  FAILED: $updater - ${STATS_FAILED[$updater]}"
        done
        
        echo "Skipped: ${#STATS_SKIPPED[@]} items"
        for updater in "${!STATS_SKIPPED[@]}"; do
            echo "  SKIPPED: $updater - ${STATS_SKIPPED[$updater]}"
        done
        
        echo "Duration: $(($(date +%s) - STATS_START_TIME)) seconds"
        echo ""
    } >> "$log_file"
}