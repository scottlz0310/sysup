# sysup 使い方ガイド

## 目次

- [基本的な使い方](#基本的な使い方)
- [コマンドラインオプション](#コマンドラインオプション)
- [設定ファイル](#設定ファイル)
- [新機能 (v0.3.0)](#新機能-v030)
- [各Updaterの詳細](#各updaterの詳細)
- [高度な使い方](#高度な使い方)

## 基本的な使い方

### 初回実行

```bash
# 全ての有効なupdaterを実行
sysup
```

初回実行時は、設定ファイルが存在しない場合、デフォルト設定で実行されます。

### ドライラン

実際には更新せず、何が更新されるかを確認：

```bash
sysup --dry-run
```

### 利用可能なupdaterの確認

```bash
sysup --list
```

出力例：
```
=== 利用可能なUpdater ===
  ✓ APT: 有効
  ✓ Snap: 有効
  ✓ Homebrew: 有効
  ✗ Flatpak: 利用不可
  ...
```

## コマンドラインオプション

### 基本オプション

| オプション | 説明 |
|-----------|------|
| `--dry-run` | 実際には更新せず、何が更新されるか表示 |
| `--force` | 今日既に実行済みでも強制実行 |
| `--list` | 利用可能なupdaterを一覧表示 |
| `--version` | バージョン情報を表示 |
| `--help` | ヘルプを表示 |

### 設定オプション

| オプション | 説明 |
|-----------|------|
| `-c, --config PATH` | 設定ファイルのパスを指定 |

### 使用例

```bash
# カスタム設定ファイルを使用
sysup -c ~/my-sysup-config.toml

# ドライランで強制実行
sysup --dry-run --force
```

## 新機能 (v0.3.0)

### WSL自動実行

WSL環境でログイン時に自動的にシステム更新を実行できます。

```bash
# WSL自動実行をセットアップ
sysup --setup-wsl
```

**設定モード:**
- **有効化（sudo認証なし）**: sudo権限が不要な更新のみ実行
- **有効化（sudo認証あり）**: 全ての更新を実行（パスワード入力が必要）

詳細は [WSL自動実行設定ガイド](WSL_SETUP.md) を参照してください。

### デスクトップ通知

更新完了時にデスクトップ通知を表示します。

**対応プラットフォーム:**
- Linux: `notify-send`を使用
- macOS: `osascript`を使用

**設定例:**
```toml
[notification]
enabled = true
on_success = true  # 成功時に通知
on_error = true    # エラー時に通知
on_warning = false # 警告時は通知しない
```

### バックアップ機能

更新前にパッケージリストをJSON形式でバックアップします。

**バックアップ内容:**
- APT, Snap, Homebrew, npm, pipx, Cargo, Flatpak, Gemのパッケージリスト
- タイムスタンプ付きJSONファイル
- 最新10件を保持（古いものは自動削除）

**設定例:**
```toml
[backup]
dir = "~/.local/share/sysup/backups"
enabled = true
```

**バックアップの確認:**
```bash
ls -lt ~/.local/share/sysup/backups/
cat ~/.local/share/sysup/backups/packages_20251005_120000.json
```

### 並列更新

複数のパッケージマネージャを同時に更新して高速化します。

**設定例:**
```toml
[general]
parallel_updates = true
```

**注意事項:**
- 最大4並列で実行
- sudo権限が必要な更新は順次実行を推奨
- ログ出力が混在する可能性があります

### ログローテーション

古いログファイルを自動的に削除します。

**設定例:**
```toml
[logging]
dir = "~/.local/share/sysup"
retention_days = 30  # 30日以上古いログを削除
level = "INFO"
```

**動作:**
- sysup起動時に自動実行
- `retention_days`より古いログを削除
- ディスク容量を節約

## 設定ファイル

### 設定ファイルの場所

設定ファイルは以下の順序で検索されます：

1. `--config`オプションで指定されたパス
2. `~/.config/sysup/sysup.toml`
3. `~/.sysup.toml`
4. `/etc/sysup/sysup.toml`

### 設定ファイルの作成

```bash
# 設定ディレクトリを作成
mkdir -p ~/.config/sysup

# サンプルをコピー
cp config/sysup.toml.example ~/.config/sysup/sysup.toml

# 編集
vim ~/.config/sysup/sysup.toml
```

### 設定項目

#### [updaters] - Updaterの有効/無効

```toml
[updaters]
apt = true          # APTパッケージマネージャ
snap = true         # Snapパッケージ
flatpak = false     # Flatpak（デフォルト無効）
pipx = true         # pipx
npm = true          # npm
nvm = true          # nvm
rustup = true       # Rustup
cargo = true        # Cargo
gem = false         # Gem（デフォルト無効）
brew = true         # Homebrew
firmware = false    # ファームウェア更新（デフォルト無効）
```

#### [logging] - ログ設定

```toml
[logging]
dir = "~/.local/share/sysup"  # ログディレクトリ
retention_days = 30            # ログ保持日数
level = "INFO"                 # ログレベル（DEBUG/INFO/WARNING/ERROR）
```

#### [backup] - バックアップ設定（今後実装予定）

```toml
[backup]
dir = "~/.local/share/sysup/backups"
enabled = true
```

#### [general] - 一般設定

```toml
[general]
parallel_updates = false  # 並列更新（今後実装予定）
dry_run = false          # デフォルトでドライラン
cache_dir = "~/.cache/sysup"
```

## 各Updaterの詳細

### APT

**対象:** Debian/Ubuntu系システム

**実行内容:**
1. パッケージリスト更新（`apt update`）
2. パッケージアップグレード（`apt upgrade -y`）
3. 不要パッケージ削除（`apt autoremove -y`）
4. クリーンアップ（`apt autoclean`）

**必要な権限:** sudo

### Snap

**対象:** Snapパッケージ

**実行内容:**
- 全Snapパッケージの更新（`snap refresh`）

**必要な権限:** sudo

### Homebrew

**対象:** macOS/Linux

**実行内容:**
1. パッケージリスト更新（`brew update`）
2. パッケージアップグレード（`brew upgrade`）
3. クリーンアップ（`brew cleanup`）

**必要な権限:** なし

### npm

**対象:** Node.jsグローバルパッケージ

**実行内容:**
- グローバルパッケージ更新（`npm update -g`）

**必要な権限:** なし（グローバルインストール先による）

### nvm

**対象:** Node Version Manager

**実行内容:**
- nvmの更新（`~/.nvm`ディレクトリでgit pull）

**必要な権限:** なし

### pipx

**対象:** Python CLIツール

**実行内容:**
- 全pipxパッケージの更新（`pipx upgrade-all`）

**必要な権限:** なし

### Rustup

**対象:** Rustツールチェーン

**実行内容:**
- Rustツールチェーンの更新（`rustup update`）

**必要な権限:** なし

### Cargo

**対象:** Rustパッケージ

**実行内容:**
- 全Cargoパッケージの更新（`cargo install-update -a`）

**必要条件:** `cargo-install-update`がインストールされていること

**インストール手順:**
```bash
# Ubuntu/Debianの場合、依存関係をインストール
sudo apt install build-essential pkg-config libssl-dev

# cargo-updateをインストール
cargo install cargo-update
```

**必要な権限:** なし

### Flatpak

**対象:** Flatpakアプリケーション

**実行内容:**
- 全Flatpakパッケージの更新（`flatpak update -y`）

**必要な権限:** なし

### Gem

**対象:** Ruby gems

**実行内容:**
- ユーザーインストールのgem更新（`gem update --user-install`）

**必要な権限:** なし

### Firmware

**対象:** システムファームウェア

**実行内容:**
1. メタデータ更新（`fwupdmgr refresh`）
2. ファームウェア更新（`fwupdmgr update -y`）

**必要な権限:** なし（fwupdmgrが適切に設定されている場合）

## 高度な使い方

### 日次実行チェック

sysupは1日1回のみ実行されるようにチェックします。
強制的に再実行する場合は`--force`オプションを使用してください。

```bash
sysup --force
```

### ログの確認

```bash
# 最新のログを表示
tail -f ~/.local/share/sysup/sysup_*.log

# 更新履歴を確認
cat ~/.local/share/sysup/update.log
```

### 特定のupdaterのみ実行（今後実装予定）

```bash
# APTとSnapのみ実行
sysup --only apt,snap

# Snapを除外して実行
sysup --exclude snap
```

### 自動実行設定（今後実装予定）

WSL環境での自動実行機能は今後実装予定です。

## トラブルシューティング

### sudo権限エラー

**問題:** `sudo権限が必要です`というエラーが表示される

**解決策:**
```bash
# 事前にsudo認証
sudo -v

# その後sysupを実行
sysup
```

### 多重実行エラー

**問題:** `sysupは既に実行中です`というエラーが表示される

**解決策:**
```bash
# ロックファイルを削除
rm ~/.cache/sysup/sysup.lock
rm ~/.cache/sysup/sysup.pid
```

### ディスク容量不足

**問題:** ディスク容量が不足している警告が表示される

**解決策:**
- 不要なファイルを削除してディスク容量を確保
- 警告を無視して続行する場合は、プロンプトで`y`を入力

### ネットワーク接続エラー

**問題:** ネットワーク接続に問題があるという警告が表示される

**解決策:**
- インターネット接続を確認
- プロキシ設定を確認
- 警告を無視して続行する場合は、プロンプトで`y`を入力

## ベストプラクティス

1. **定期的な実行**: 週に1回程度の実行を推奨
2. **ドライランの活用**: 重要な作業前は`--dry-run`で確認
3. **ログの確認**: 問題が発生した場合はログを確認
4. **設定のカスタマイズ**: 使用しないupdaterは無効化して実行時間を短縮

## 関連ドキュメント

- [README](../README.md) - プロジェクト概要
- [実装計画書](implement/sysup-implementation-plan.md) - 開発計画
- [CONTRIBUTING](CONTRIBUTING.md) - 貢献ガイド
