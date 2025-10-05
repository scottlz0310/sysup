# sysup 実装計画書

## プロジェクト概要

**プロジェクト名:** sysup  
**目的:** システムと各種パッケージマネージャを統合的に更新するツール  
**現状:** `up.sh` という単一スクリプトから、モジュール化されたリポジトリへ移行

---

## ディレクトリ構成

```
sysup/
├── sysup                       # メインエントリーポイント
├── lib/
│   ├── core/
│   │   ├── common.sh          # 共通関数（ログ、メッセージ表示）
│   │   ├── checks.sh          # 事前チェック（disk, network等）
│   │   ├── stats.sh           # 統計情報管理
│   │   └── config.sh          # 設定ファイル読み込み
│   └── updaters/
│       ├── apt.sh             # APTパッケージ管理
│       ├── snap.sh            # Snapパッケージ管理
│       ├── flatpak.sh         # Flatpakパッケージ管理
│       ├── pipx.sh            # pipx管理ツール
│       ├── npm.sh             # npmグローバルパッケージ
│       ├── nvm.sh             # Node Version Manager
│       ├── node.sh            # Node.jsバージョン設定
│       ├── rustup.sh          # Rust toolchain
│       ├── cargo.sh           # Cargoパッケージ
│       ├── gem.sh             # Ruby gems
│       ├── brew.sh            # Homebrew
│       └── firmware.sh        # ファームウェア更新
├── config/
│   └── sysup.conf.example     # 設定ファイルのサンプル
├── install.sh                  # インストールスクリプト
├── uninstall.sh               # アンインストールスクリプト
├── tests/                      # テストスクリプト（将来的に）
├── docs/                       # ドキュメント
│   ├── USAGE.md               # 使い方ガイド
│   └── CONTRIBUTING.md        # 貢献ガイド
├── README.md
├── LICENSE
└── CHANGELOG.md
```

---

## 実装フェーズ

### Phase 1: 基盤構築（Week 1-2）

#### 1.1 リポジトリセットアップ
- [ ] GitHubリポジトリ作成
- [ ] LICENSE選定（MIT推奨）
- [ ] .gitignore作成
- [ ] README.md初期版作成

#### 1.2 コア機能の抽出
- [ ] `lib/core/common.sh` 作成
  - ログ関数（log_message, success, info, warning, error）
  - プログレスバー（show_progress）
  - 確認プロンプト（confirm）
  - 色定義
- [ ] `lib/core/checks.sh` 作成
  - check_disk_space
  - check_network
  - check_daily_run
  - check_reboot_required
- [ ] `lib/core/stats.sh` 作成
  - 統計情報の収集と表示
  - show_update_summary
- [ ] `lib/core/config.sh` 作成
  - 設定ファイル読み込み
  - デフォルト値設定

#### 1.3 設定ファイル設計
```bash
# config/sysup.conf.example

# === 更新対象の有効/無効 ===
ENABLE_APT=true
ENABLE_SNAP=true
ENABLE_FLATPAK=false
ENABLE_PIPX=true
ENABLE_NPM=true
ENABLE_NVM=true
ENABLE_RUSTUP=true
ENABLE_CARGO=true
ENABLE_GEM=false
ENABLE_BREW=true
ENABLE_FIRMWARE=false

# === 自動実行設定 ===
AUTO_RUN_MODE="disabled"  # disabled/enabled/enabled_with_auth

# === ログ設定 ===
LOG_DIR="$HOME/logs"
LOG_RETENTION_DAYS=30

# === バックアップ設定 ===
BACKUP_DIR="$HOME/backups"
ENABLE_BACKUP=true

# === その他 ===
PARALLEL_UPDATES=false  # 将来的な並列実行機能
```

---

### Phase 2: Updaterモジュール実装（Week 3-4）

#### 2.1 標準インターフェース定義

各updaterは以下の関数を実装する必要があります：

```bash
# 必須関数
is_available()      # コマンドが利用可能かチェック
get_name()          # 表示名を返す
perform_update()    # 更新実行（成功: 0, 失敗: 1）

# オプション関数
check_updates()     # 更新可能なパッケージ数を返す
pre_update()        # 更新前処理
post_update()       # 更新後処理
```

#### 2.2 優先度順での実装

**高優先度（必須）:**
- [ ] `apt.sh` - 最も重要なシステムパッケージ
- [ ] `snap.sh`
- [ ] `brew.sh` - よく使われる

**中優先度:**
- [ ] `npm.sh`
- [ ] `pipx.sh`
- [ ] `rustup.sh`
- [ ] `cargo.sh`

**低優先度:**
- [ ] `flatpak.sh`
- [ ] `gem.sh`
- [ ] `nvm.sh`
- [ ] `node.sh`
- [ ] `firmware.sh`

#### 2.3 各updaterのテンプレート

```bash
#!/bin/bash
# lib/updaters/example.sh

# パッケージマネージャが利用可能かチェック
is_available() {
    command -v example >/dev/null 2>&1
}

# 表示名
get_name() {
    echo "Example Package Manager"
}

# 更新可能なパッケージ数を取得（オプション）
check_updates() {
    example list-outdated 2>/dev/null | wc -l
}

# 更新実行
perform_update() {
    local name=$(get_name)
    
    if ! is_available; then
        info "$name がインストールされていません - スキップ"
        return 0
    fi
    
    info "$name を更新中..."
    
    if example update 2>/dev/null; then
        success "$name 更新完了"
        return 0
    else
        warning "$name 更新で問題が発生しました"
        return 1
    fi
}
```

---

### Phase 3: メインスクリプト実装（Week 5）

#### 3.1 sysupメインスクリプト

```bash
#!/bin/bash
# sysup - システム更新統合ツール

set -euo pipefail

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/sysup"
CONFIG_FILE="$CONFIG_DIR/sysup.conf"

# コアライブラリ読み込み
source "$LIB_DIR/core/common.sh"
source "$LIB_DIR/core/checks.sh"
source "$LIB_DIR/core/stats.sh"
source "$LIB_DIR/core/config.sh"

# 設定読み込み
load_config

# メイン処理
main() {
    # 引数解析
    parse_arguments "$@"
    
    # 事前チェック
    perform_pre_checks
    
    # 更新実行
    run_updates
    
    # サマリー表示
    show_summary
    
    # 再起動チェック
    check_reboot_if_needed
}

# 更新実行
run_updates() {
    local updaters=()
    
    # 有効なupdaterを収集
    for updater_file in "$LIB_DIR/updaters"/*.sh; do
        source "$updater_file"
        
        local updater_name=$(basename "$updater_file" .sh)
        local enable_var="ENABLE_${updater_name^^}"
        
        if [[ "${!enable_var:-false}" == "true" ]] && is_available; then
            updaters+=("$updater_file")
        fi
    done
    
    # 更新実行
    local total=${#updaters[@]}
    local current=0
    
    for updater_file in "${updaters[@]}"; do
        ((current++))
        source "$updater_file"
        
        show_progress $current $total
        perform_update
    done
}

main "$@"
```

---

### Phase 4: インストール/アンインストール（Week 6）

#### 4.1 install.sh

```bash
#!/bin/bash
# install.sh

set -e

INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/sysup"

echo "=== sysup インストール ==="

# シンボリックリンク作成
sudo ln -sf "$(pwd)/sysup" "$INSTALL_DIR/sysup"
echo "✓ $INSTALL_DIR/sysup に配置しました"

# 設定ディレクトリ作成
mkdir -p "$CONFIG_DIR"

# 設定ファイルコピー（存在しない場合のみ）
if [[ ! -f "$CONFIG_DIR/sysup.conf" ]]; then
    cp config/sysup.conf.example "$CONFIG_DIR/sysup.conf"
    echo "✓ 設定ファイルを作成しました: $CONFIG_DIR/sysup.conf"
else
    echo "ℹ 既存の設定ファイルを保持します"
fi

# 実行権限付与
chmod +x sysup
chmod +x lib/core/*.sh
chmod +x lib/updaters/*.sh

echo ""
echo "インストール完了！"
echo "使い方: sysup --help"
```

#### 4.2 uninstall.sh

```bash
#!/bin/bash
# uninstall.sh

set -e

INSTALL_DIR="/usr/local/bin"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/sysup"

echo "=== sysup アンインストール ==="

# シンボリックリンク削除
if [[ -L "$INSTALL_DIR/sysup" ]]; then
    sudo rm "$INSTALL_DIR/sysup"
    echo "✓ $INSTALL_DIR/sysup を削除しました"
fi

# 設定削除の確認
read -p "設定ファイルも削除しますか？ (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$CONFIG_DIR"
    echo "✓ 設定ファイルを削除しました"
fi

echo "アンインストール完了"
```

---

### Phase 5: ドキュメント整備（Week 7）

#### 5.1 README.md
- プロジェクト説明
- インストール方法
- 基本的な使い方
- 設定例
- トラブルシューティング

#### 5.2 USAGE.md
- 詳細な使用方法
- 全オプションの説明
- 設定ファイルの詳細
- 各updaterの説明

#### 5.3 CONTRIBUTING.md
- 新しいupdaterの追加方法
- コーディング規約
- プルリクエストのガイドライン

---

## 主な機能

### 既存機能の維持
- [x] APT更新（update, upgrade, autoremove）
- [x] Snap更新
- [x] 各種パッケージマネージャ対応
- [x] 自動実行機能（WSL対応）
- [x] バックアップ機能
- [x] 統計情報表示
- [x] 再起動チェック
- [x] ロック機能（多重実行防止）

### 新機能
- [ ] 設定ファイルでの柔軟な制御
- [ ] 個別updaterの有効/無効化
- [ ] ドライランモード（`--dry-run`）
- [ ] 並列更新オプション（将来）
- [ ] 通知機能の改善
- [ ] ログローテーション

---

## コマンドラインインターフェース

```bash
# 基本的な使い方
sysup                          # 全ての有効な更新を実行
sysup --dry-run               # 実際には更新せず、何が更新されるか表示
sysup --only apt,brew         # 特定のupdaterのみ実行
sysup --exclude snap          # 特定のupdaterを除外

# 自動実行関連
sysup --auto-run              # 自動実行モード
sysup --setup-auto-run        # 自動実行を設定
sysup --enable-auto-run       # 自動実行を有効化
sysup --disable-auto-run      # 自動実行を無効化

# 情報表示
sysup --list                  # 利用可能なupdaterを一覧表示
sysup --version               # バージョン情報
sysup --help                  # ヘルプ表示

# その他
sysup --no-backup             # バックアップなしで実行
sysup --force                 # 今日既に実行済みでも強制実行
```

---

## テスト計画

### 手動テスト項目
- [ ] 各updaterの単体テスト
- [ ] 統合テスト（全更新の実行）
- [ ] エラーハンドリング
- [ ] WSL環境での自動実行
- [ ] 設定ファイルの読み込み

### 自動テスト（将来）
- Unit tests for core functions
- Integration tests
- CI/CD setup (GitHub Actions)

---

## マイグレーション戦略

### 既存のup.shからの移行

1. **並行運用期間**
   - 新しいsysupと既存のup.shを両方保持
   - 十分なテスト実施

2. **段階的移行**
   - Phase 1-2完了後、個人環境で試用
   - Phase 3完了後、本格運用開始
   - 問題なければup.shを削除

3. **設定移行**
   - up.shの設定を新しいsysup.confに変換
   - 自動実行設定の移行

---

## リリース計画

### v0.1.0 (Alpha)
- コア機能実装
- APT, Snap, Brew updater

### v0.5.0 (Beta)
- 全updater実装
- ドキュメント整備

### v1.0.0 (Stable)
- 十分なテストと安定性確認
- 公開リリース

---

## 今後の拡張案

- 📊 Web UIでの更新状況確認
- 🔔 より高度な通知システム
- 📦 プラグインシステム（カスタムupdater追加）
- 🔄 ロールバック機能
- 📈 更新履歴のトラッキング
- 🌐 複数マシンの一括管理

---

## 参考資料

- 現在のup.sh: 約600行の充実したスクリプト
- 対応パッケージマネージャ: apt, snap, flatpak, pipx, npm, rustup, cargo, gem, brew, firmware
- WSL自動実行機能: .bashrcとの連携

---

**作成日:** 2025-10-01  
**最終更新:** 2025-10-01  
**バージョン:** 1.0
