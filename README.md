# sysup

システムと各種パッケージマネージャを統合的に更新するツール

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Coverage](https://img.shields.io/badge/coverage-87.41%25-brightgreen.svg)](https://github.com/scottlz0310/sysup)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-brightgreen.svg)](https://github.com/scottlz0310/sysup)

## 概要

`sysup`は、複数のパッケージマネージャを一括で更新できるPython製のCLIツールです。
APT、Snap、Homebrew、npm、Rustupなど、11種類のパッケージマネージャに対応しています。

### 特徴

- 🚀 **統合更新**: 複数のパッケージマネージャを一度に更新
- 🎨 **美しい出力**: Richライブラリによる見やすいターミナル表示
- ⚙️ **柔軟な設定**: TOML形式の設定ファイルで細かくカスタマイズ
- 🔒 **安全性**: 多重実行防止、日次実行チェック、ドライランモード
- 📊 **統計情報**: 更新結果のサマリー表示とログ保存
- 🔔 **デスクトップ通知**: 更新完了時に通知を表示
- 💾 **バックアップ**: 更新前にパッケージリストを自動バックアップ
- 🐧 **WSL統合**: WSL環境での自動実行設定
- ⚡ **並列更新**: 複数のパッケージマネージャを同時に更新

### 対応パッケージマネージャ

- **APT** - Debian/Ubuntu系パッケージマネージャ
- **Snap** - Ubuntuスナップパッケージ
- **Homebrew** - macOS/Linuxパッケージマネージャ
- **npm** - Node.jsグローバルパッケージ
- **nvm** - Node Version Manager
- **pipx** - Python CLIツール
- **uv tool** - Python CLIツール（uvによる管理）
- **Rustup** - Rustツールチェーン
- **Cargo** - Rustパッケージ
- **Flatpak** - Linuxアプリケーション配布
- **Gem** - Ruby gems
- **Firmware** - ファームウェア更新（fwupdmgr）

### 対応環境

- **Linux** (Ubuntu, Debian, Fedora等)
- **macOS** (Homebrew経由)
- **WSL** (Windows Subsystem for Linux)

> **注意**: Windows ネイティブ環境は現在サポートされていません。Windows用パッケージマネージャ（Scoop、Chocolatey、winget等）への対応は将来的な拡張として検討中です。

## インストール

### 前提条件

- Python 3.11以上
- uv または pipx
- Linux、macOS、またはWSL環境

### GitHubから直接インストール（推奨）

```bash
# uvで
uv tool install git+https://github.com/scottlz0310/sysup.git

# pipxで
pipx install git+https://github.com/scottlz0310/sysup.git
```

### ローカル開発モード

```bash
git clone https://github.com/scottlz0310/sysup.git
cd sysup
uv venv --python 3.13
uv pip install -e .
```

## 使い方

### 基本的な使い方

```bash
# 全ての有効な更新を実行
sysup

# ドライラン（実際には更新しない）
sysup --dry-run

# 今日既に実行済みでも強制実行
sysup --force

# 利用可能なupdaterを一覧表示
sysup --list

# ヘルプ表示
sysup --help

# WSL自動実行をセットアップ
sysup --setup-wsl
```

### 新機能（v0.4.0）

#### 品質向上

- ✅ **テストカバレッジ87.41%達成**（目標80%超過）
- ✅ **全公開APIにDocstring整備**（Googleスタイル）
- ✅ **CodeQL自動スキャン導入**
- ✅ **Secret Scanning + Push Protection有効化**
- ✅ **Dependabot依存関係管理**
- ✅ **SECURITY.md作成**（脆弱性報告方針）
- ✅ **CI/CDカバレッジゲート有効化**（80%閾値）

詳細は [CHANGELOG](CHANGELOG.md) を参照してください。

### v0.3.0の機能

#### WSL自動実行設定

WSL環境でログイン時に自動的にシステム更新を実行できます：

```bash
# WSL自動実行をセットアップ
sysup --setup-wsl
```

詳細は [WSL自動実行設定ガイド](docs/WSL_SETUP.md) を参照してください。

#### デスクトップ通知

更新完了時にデスクトップ通知を表示します（Linux/macOS）。

```toml
[notification]
enabled = true
on_success = true
on_error = true
on_warning = false
```

#### バックアップ機能

更新前にパッケージリストをJSON形式でバックアップします。

```toml
[backup]
dir = "~/.local/share/sysup/backups"
enabled = true
```

バックアップは `~/.local/share/sysup/backups/` に保存されます。

#### 並列更新

複数のパッケージマネージャを同時に更新して高速化：

```toml
[general]
parallel_updates = true
```

#### ログローテーション

古いログファイルを自動的に削除します：

```toml
[logging]
retention_days = 30  # 30日以上古いログを削除
```

### 設定ファイル

設定ファイルは `~/.config/sysup/sysup.toml` に配置します。

```bash
# 設定ディレクトリを作成
mkdir -p ~/.config/sysup

# サンプルをコピー
cp config/sysup.toml.example ~/.config/sysup/sysup.toml

# 編集
vim ~/.config/sysup/sysup.toml
```

```toml
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

[logging]
dir = "~/.local/share/sysup"
level = "INFO"

[general]
dry_run = false
cache_dir = "~/.cache/sysup"
```

設定ファイルのサンプルは `config/sysup.toml.example` を参照してください。

## 実行例

```bash
$ sysup --dry-run

╔════════════════════════════════════════╗
║     sysup システム更新                ║
╚════════════════════════════════════════╝

=== システムチェック ===
ℹ ディスク容量: 923.7GB 利用可能
ℹ ネットワーク接続: OK

=== パッケージ更新 ===
ステップ 1/7: APTを更新中 (14%)
ℹ APT パッケージリストを更新中...
✓ APT パッケージリスト更新完了
...

=== 更新サマリー ===
✓ 成功: 7 件
ℹ 実行時間: 45秒
✓ 全ての更新が正常に完了しました
```

## トラブルシューティング

### sudo権限が必要

一部のupdater（APT、Snapなど）はsudo権限が必要です。事前に`sudo -v`で認証しておくとスムーズです。

### Cargoパッケージの更新ができない

Cargoパッケージを更新するには`cargo-update`が必要です：

```bash
# 依存関係をインストール（Ubuntu/Debian）
sudo apt install build-essential pkg-config libssl-dev

# cargo-updateをインストール
cargo install cargo-update
```

#### `libgit2.so.1.9` が見つからないエラー

`cargo install-update -a` 実行時に `error while loading shared libraries: libgit2.so.1.9: cannot open shared object file` が表示される場合、`libgit2` の共有ライブラリが不足しています。Ubuntu/Debian 系であれば以下で解決できます：

```bash
sudo apt install libgit2-1.9
```

### nvmが検出されない

nvmをgit経由でインストールすることを推奨します：

```bash
# 公式インストールスクリプト
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# シェルを再起動
source ~/.bashrc
```

### 特定のupdaterを無効化したい

設定ファイル（`~/.config/sysup/sysup.toml`）で該当するupdaterを`false`に設定してください。

### ログの確認

ログは `~/.local/share/sysup/` に保存されます。

## 開発

### 開発環境のセットアップ

```bash
git clone https://github.com/scottlz0310/sysup.git
cd sysup
uv venv --python 3.13
uv pip install -e ".[dev]"
```

### テスト実行

```bash
uv run pytest
```

### コード品質チェック

```bash
# Linter
uv run ruff check .

# Formatter
uv run ruff format .

# 型チェック
uv run mypy .
```

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) を参照してください。

## 貢献

貢献を歓迎します！詳細は [CONTRIBUTING.md](docs/CONTRIBUTING.md) を参照してください。

## 関連ドキュメント

- [使い方ガイド](docs/USAGE.md) - 詳細な使用方法
- [自動実行設定ガイド](docs/AUTO_RUN.md) - WSL/Ubuntuでの自動実行設定
- [実装計画書](docs/implement/sysup-implementation-plan.md) - 開発計画
- [CHANGELOG](CHANGELOG.md) - 変更履歴

## 作者

scottlz0310

## 謝辞

元のBashスクリプト `up.sh` からPython版への移行プロジェクトです。
