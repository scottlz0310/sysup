#!/bin/bash
# lib/core/common.sh - 共通関数

# 色定義
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m' # No Color

# ログ関数
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] [$level] $message"
}

success() {
    log_message "${GREEN}SUCCESS${NC}" "${GREEN}$1${NC}"
}

info() {
    log_message "${BLUE}INFO${NC}" "$1"
}

warning() {
    log_message "${YELLOW}WARNING${NC}" "${YELLOW}$1${NC}"
}

error() {
    log_message "${RED}ERROR${NC}" "${RED}$1${NC}"
}

# プログレスバー
show_progress() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((current * width / total))
    
    printf "\r["
    for ((i=0; i<completed; i++)); do printf "="; done
    for ((i=completed; i<width; i++)); do printf " "; done
    printf "] %d%% (%d/%d)" $percentage $current $total
    
    if [[ $current -eq $total ]]; then
        echo
    fi
}

# 確認プロンプト
confirm() {
    local message="$1"
    local default="${2:-n}"
    
    if [[ "$default" == "y" ]]; then
        local prompt="$message (Y/n): "
    else
        local prompt="$message (y/N): "
    fi
    
    read -p "$prompt" -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    elif [[ $REPLY =~ ^[Nn]$ ]]; then
        return 1
    else
        # デフォルト値を使用
        [[ "$default" == "y" ]] && return 0 || return 1
    fi
}

# セクション表示
show_section() {
    local title="$1"
    echo
    echo -e "${CYAN}=== $title ===${NC}"
}

# エラー時の終了
die() {
    error "$1"
    exit 1
}