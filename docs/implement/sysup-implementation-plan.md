# sysup 実装計画書

## プロジェクト概要

**プロジェクト名:** sysup
**目的:** システムと各種パッケージマネージャを統合的に更新するツール
**言語:** Python 3.11+
**現状:** `up.sh` (Bashスクリプト) から、Pythonベースのモジュール化されたツールへ移行

---

## ディレクトリ構成

```
sysup/
├── src/
│   └── sysup/
│       ├── __init__.py
│       ├── cli.py              # CLIエントリーポイント
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py       # 設定管理（Pydantic）
│       │   ├── logging.py      # ログ機能（Rich）
│       │   ├── checks.py       # 事前チェック
│       │   └── stats.py        # 統計情報管理
│       └── updaters/
│           ├── __init__.py
│           ├── base.py         # Updaterベースクラス
│           ├── apt.py          # APTパッケージ管理
│           ├── snap.py         # Snapパッケージ管理
│           ├── flatpak.py      # Flatpakパッケージ管理
│           ├── pipx.py         # pipx管理ツール
│           ├── npm.py          # npmグローバルパッケージ
│           ├── nvm.py          # Node Version Manager
│           ├── rustup.py       # Rust toolchain
│           ├── cargo.py        # Cargoパッケージ
│           ├── gem.py          # Ruby gems
│           ├── brew.py         # Homebrew
│           └── firmware.py     # ファームウェア更新
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_checks.py
│   └── test_updaters/
│       └── test_apt.py
├── config/
│   └── sysup.toml.example      # 設定ファイルのサンプル
├── docs/
│   ├── implement/
│   │   └── sysup-implementation-plan.md
│   ├── USAGE.md
│   └── CONTRIBUTING.md
├── archive/
│   ├── up.sh                   # 元のBashスクリプト
│   └── bash-prototype/         # Bashプロトタイプ
├── pyproject.toml              # プロジェクト設定
├── README.md
├── LICENSE
└── CHANGELOG.md
```

---

## 実装フェーズ

### Phase 1: 基盤構築 ✅ 完了

#### 1.1 リポジトリセットアップ ✅
- [x] GitHubリポジトリ作成
- [x] LICENSE選定（MIT）
- [x] .gitignore作成（Python用）
- [x] README.md初期版作成
- [x] pyproject.toml作成

#### 1.2 コア機能の実装 ✅
- [x] `src/sysup/core/config.py` 作成
  - Pydanticベースの設定管理
  - TOML形式の設定ファイル読み込み
  - デフォルト値設定
- [x] `src/sysup/core/logging.py` 作成
  - Richベースの美しいログ出力
  - ログ関数（success, info, warning, error）
  - プログレスバー表示
  - セクション表示
- [x] `src/sysup/core/checks.py` 作成
  - check_disk_space
  - check_network
  - check_daily_run
  - check_reboot_required
  - check_sudo_available
  - check_process_lock（多重実行防止）
- [x] `src/sysup/core/stats.py` 作成
  - 統計情報の収集と表示
  - show_summary
  - save_to_log

#### 1.3 設定ファイル設計 ✅
```toml
# config/sysup.toml.example

[updaters]
apt = true
snap = true
flatpak = false
pipx = true
npm = true
nvm = true
rustup = true
cargo = true
gem = false
brew = true
firmware = false

[auto_run]
mode = "disabled"  # disabled/enabled/enabled_with_auth

[logging]
dir = "~/.local/share/sysup"
retention_days = 30
level = "INFO"

[backup]
dir = "~/.local/share/sysup/backups"
enabled = true

[general]
parallel_updates = false
dry_run = false
cache_dir = "~/.cache/sysup"
```

---

### Phase 2: Updaterモジュール実装 ✅ 完了

#### 2.1 標準インターフェース定義 ✅

各updaterは`BaseUpdater`を継承し、以下のメソッドを実装：

```python
from abc import ABC, abstractmethod

class BaseUpdater(ABC):
    @abstractmethod
    def get_name(self) -> str:
        """表示名を返す"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """コマンドが利用可能かチェック"""
        pass

    @abstractmethod
    def perform_update(self) -> bool:
        """更新実行（成功: True, 失敗: False）"""
        pass

    def check_updates(self) -> Optional[int]:
        """更新可能なパッケージ数を返す（オプション）"""
        return None

    def pre_update(self) -> bool:
        """更新前処理（オプション）"""
        return True

    def post_update(self) -> bool:
        """更新後処理（オプション）"""
        return True
```

#### 2.2 優先度順での実装

**高優先度（必須）:** ✅ 完了
- [x] `apt.py` - 最も重要なシステムパッケージ ✅
- [x] `snap.py` ✅
- [x] `brew.py` - よく使われる ✅

**中優先度:** ✅ 完了
- [x] `npm.py` ✅
- [x] `nvm.py` ✅
- [x] `pipx.py` ✅
- [x] `rustup.py` ✅
- [x] `cargo.py` ✅

**低優先度:** ✅ 完了
- [x] `flatpak.py` ✅
- [x] `gem.py` ✅
- [x] `firmware.py` ✅

---

### Phase 3: CLIインターフェース実装 ✅ 完了

#### 3.1 メインCLI ✅

- [x] Clickベースのコマンドラインインターフェース
- [x] 引数解析（--config, --dry-run, --auto-run, --force, --list）
- [x] 事前チェック実行
- [x] 更新実行ループ
- [x] サマリー表示
- [x] 再起動チェック

---

### Phase 4: CI/CD・品質保証 ✅ 完了

#### 4.1 型アノテーション ✅
- [x] 全モジュールに完全な型アノテーションを追加
- [x] mypy strict設定でtype check完全対応
- [x] 23ファイル全て型エラーなし

#### 4.2 CI/CD構築 ✅
- [x] GitHub Actions CI/CDワークフロー追加
  - [x] lint (ruff check/format)
  - [x] type check (mypy)
  - [x] test (pytest) - ubuntu/macos × Python 3.11/3.12/3.13
  - [x] security check (bandit)
  - [x] coverage測定 (pytest-cov)
- [x] pre-commit設定追加
- [x] Makefile追加（開発タスク自動化）

#### 4.3 テスト拡充 ✅
- [x] test_backup.py
- [x] test_logging.py
- [x] test_notification.py
- [x] test_wsl.py
- [x] テストカバレッジ設定（段階的厳格化対応）

#### 4.4 バージョン管理 ✅
- [x] セマンティックバージョニング（SemVer）の適用
- [x] CHANGELOG.mdの更新

---

### Phase 5: インストール/配布

#### 5.1 インストール方法（個人用） ✅

**GitHubから直接インストール（推奨）:**
```bash
# uvで
uv tool install git+https://github.com/scottlz0310/sysup.git

# pipxで
pipx install git+https://github.com/scottlz0310/sysup.git
```

**ローカル開発モード:**
```bash
cd /path/to/sysup
uv pip install -e .
```

#### 5.2 リリース管理（未実装）
- [ ] Gitタグによるリリース管理
- [ ] GitHub Releasesの自動生成
- [ ] リリースノートの自動作成

---

---

### Phase 6: ドキュメント整備 ✅ 完了

#### 6.1 README.md ✅
- [x] プロジェクト説明
- [x] インストール方法
- [x] 基本的な使い方
- [x] 設定例
- [x] トラブルシューティング（Cargo、nvmの追加情報を含む）

#### 6.2 USAGE.md ✅
- [x] 詳細な使用方法
- [x] 全オプションの説明
- [x] 設定ファイルの詳細
- [x] 各updaterの説明（Cargoの依存関係情報を含む）

#### 6.3 CONTRIBUTING.md ✅
- [x] 新しいupdaterの追加方法
- [x] コーディング規約
- [x] プルリクエストのガイドライン

---

## 主な機能

### 実装済み機能 ✅
- [x] 設定ファイル管理（TOML形式、Pydantic）
- [x] Richベースの美しいログ出力
- [x] システムチェック（ディスク、ネットワーク、sudo）
- [x] 統計情報表示
- [x] 再起動チェック
- [x] ロック機能（多重実行防止）
- [x] 日次実行チェック
- [x] ドライランモード
- [x] 全11種類のupdater実装完了
  - APT, Snap, Homebrew, npm, nvm, pipx, Rustup, Cargo, Flatpak, Gem, Firmware

### 実装済み機能（基本） ✅
- [x] 自動実行モード（--auto-run）

### 実装済み機能（v0.3.0） ✅
- [x] WSL統合（.bashrc自動設定、--setup-wslコマンド）
- [x] バックアップ機能（パッケージリストのJSONバックアップ）
- [x] 並列更新オプション（parallel_updates設定）
- [x] デスクトップ通知機能（Linux/macOS対応）
- [x] ログローテーション（retention_days設定）

---

## コマンドラインインターフェース

```bash
# 基本的な使い方
sysup                          # 全ての有効な更新を実行
sysup --dry-run               # 実際には更新せず、何が更新されるか表示
sysup --force                 # 今日既に実行済みでも強制実行

# 設定
sysup -c /path/to/config.toml # 設定ファイルを指定

# 情報表示
sysup --list                  # 利用可能なupdaterを一覧表示
sysup --version               # バージョン情報
sysup --help                  # ヘルプ表示

# 自動実行関連
sysup --auto-run              # 自動実行モード（対話なし）
```

---

## テスト計画

### 実装済みテスト ✅
- [x] 設定モジュールの基本テスト (test_config.py)
- [x] バックアップ機能テスト (test_backup.py)
- [x] ログ機能テスト (test_logging.py)
- [x] 通知機能テスト (test_notification.py)
- [x] WSL統合テスト (test_wsl.py)
- [x] CI/CD setup (GitHub Actions) ✅

### 今後実装予定（Phase 4以降）
- [ ] 各updaterの単体テスト
- [ ] システムチェック機能テスト (test_checks.py)
- [ ] 統計機能テスト (test_stats.py)
- [ ] 統合テスト
- [ ] エラーハンドリングテスト
- [ ] カバレッジ60%以上（staging目標）

---

## 技術スタック

### 主要ライブラリ
- **click**: CLIフレームワーク
- **rich**: 美しいターミナル出力
- **pydantic**: 設定管理・バリデーション
- **pydantic-settings**: 設定ファイル読み込み

### 開発ツール
- **uv**: 高速パッケージマネージャ
- **ruff**: Linter/Formatter
- **mypy**: 型チェック
- **pytest**: テストフレームワーク

### Python要件
- Python 3.11以上

---

## マイグレーション戦略

### 既存のup.shからの移行

1. **アーカイブ保存** ✅
   - 元のup.shを`archive/up.sh`に保存
   - Bashプロトタイプを`archive/bash-prototype/`に保存

2. **段階的移行**
   - Phase 1-2完了後、個人環境で試用
   - Phase 3完了後、本格運用開始
   - 十分なテスト後、up.shから完全移行

3. **設定移行**
   - Bash形式からTOML形式への変換
   - 自動実行設定の移行（今後実装）

---

## リリース計画

### v0.1.0 (Alpha) ✅ 完了
- コア機能実装完了
- APT updater実装
- 基本的なCLI動作確認

### v0.2.0 (Alpha) ✅ 完了
- 全11種類のupdater実装完了
- 主要パッケージマネージャ対応完了

### v0.2.1 (Alpha) ✅ 完了
- nvm検出方法の改善
- cargo利用可能性判定の修正

### v0.3.0 (Beta) ✅ 現在
- WSL統合機能
- バックアップ機能
- 並列更新オプション
- デスクトップ通知機能
- ログローテーション
- 型アノテーション完全対応
- CI/CD環境整備完了

### v0.4.0 (Beta) - 次回リリース
- Gitタグによるリリース管理
- GitHub Releases自動生成
- 追加テスト実装（updaters, checks, stats）
- カバレッジ向上

### v1.0.0 (Stable)
- 十分なテストと安定性確認
- 個人環境での安定運用
- ドキュメント完備

---

## 今後の拡張案

- 📊 Web UIでの更新状況確認
- 🔔 より高度な通知システム（デスクトップ通知）
- 📦 プラグインシステム（カスタムupdater追加）
- 🔄 ロールバック機能
- 📈 更新履歴のトラッキング
- 🌐 複数マシンの一括管理
- ⚡ 並列更新の実装
- 🐳 Dockerコンテナ対応

---

## 参考資料

- 元のup.sh: 約600行の充実したBashスクリプト（`archive/up.sh`）
- 対応予定パッケージマネージャ: apt, snap, flatpak, pipx, npm, nvm, rustup, cargo, gem, brew, firmware
- WSL自動実行機能: 今後実装予定

---

**作成日:** 2025-01-05
**最終更新:** 2025-10-05
**バージョン:** 3.0 (Python版 v0.3.0)
**現在のフェーズ:** Phase 4 (CI/CD・品質保証) 完了 ✅ → Phase 5 (リリース管理) 未実装
