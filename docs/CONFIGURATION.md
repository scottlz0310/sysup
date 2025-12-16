# sysup 設定ガイド

sysup の設定方法を詳しく説明します。

## 目次

- [クイックスタート](#クイックスタート)
- [初期セットアップウィザード](#初期セットアップウィザード)
- [手動による設定](#手動による設定)
- [設定ファイルの詳細](#設定ファイルの詳細)
- [例](#例)
- [よくある質問](#よくある質問)

## クイックスタート

最も簡単な方法は、対話型ウィザードを使うことです：

```bash
sysup init
```

このコマンドで、5つの工程を通じて設定を行えます。既に設定ファイルがある場合は、更新か新規作成かを選択できます。

## 初期セットアップウィザード

### ウィザードを実行する

```bash
sysup init
```

### 工程1: システム環境の確認

このステップでは sysup が自動的にシステムを調査し、利用可能なパッケージマネージャを検出します。

```
工程 1/5: システム環境の確認
✓ 以下のパッケージマネージャを検出しました:
  • apt (Debian/Ubuntu パッケージマネージャ)
  • npm (Node.jsパッケージマネージャ)
  • rustup (Rustツールチェーンマネージャ)
✓ 検出完了
```

### 工程2: 更新対象パッケージマネージャの選択

工程1で検出できたマネージャのみをデフォルトで有効化し、不要なものを無効化します：

```
工程 2/5: 更新対象パッケージマネージャの選択
矢印キーで移動、スペースでトグル、Enter または q で確定:
```

**操作方法：**

- 矢印キーで移動、スペースでトグル、`Enter` または `q` で確定
- 対話入力が利用できない環境では「数字入力でトグル」方式にフォールバックします

### 工程3: 実行モードの選択

sysup をどのように使用するかを選択します：

```
工程 3/5: 実行モードの選択
sysupの動作モードを選択してください:
  1. 標準モード（対話的、手動実行用）
  2. 自動実行モード（cronやスケジューラで定期実行用）
  3. スキップ（後で設定）

選択 [1]:
```

**選択肢の説明：**

- **標準モード**: 通常の手動実行時に確認プロンプトを表示
- **自動実行モード**: cron や Task Scheduler で定期実行する場合（確認プロンプトなし）
- **スキップ**: デフォルト値（標準モード）を使用

### 工程4: 詳細設定

詳細設定を行うかどうか選択します：

```
工程 4/5: 詳細設定
詳細設定を行いますか?
  1. はい（詳細設定を行う）
  2. いいえ（デフォルト値を使用）

選択 [2]: 1
```

「はい」を選択した場合、以下の設定が可能です：

#### ログレベル

```
ログレベルを選択してください:
  1. DEBUG (詳細）
  2. INFO (通常)
  3. WARNING (警告以上)
  4. ERROR (エラーのみ)

選択 [2]:
```

#### 並列実行

```
複数のパッケージマネージャを並列実行しますか?
  1. はい
  2. いいえ（逐次実行）

選択 [2]:
```

#### バックアップ

```
パッケージリストをバックアップしますか?
  1. はい
  2. いいえ

選択 [1]:
```

#### 通知

```
デスクトップ通知を有効にしますか?
  1. はい
  2. いいえ

選択 [1]:
```

### 工程5: セットアップ完了

設定ファイルが生成され、内容が表示されます：

```
工程 5/5: セットアップ完了
✓ 設定ファイルを生成しました
  保存先: /home/user/.config/sysup/sysup.toml

生成された設定:
[updaters]
apt = false
snap = false
flatpak = false
pipx = true
...

✓ セットアップが完了しました！

次のコマンドで実行できます:
  sysup              # システムを更新
  sysup --list       # インストール済みマネージャを確認
  sysup init         # 設定を変更する場合
```

## 手動による設定

設定ファイルを手動で作成することもできます。

### 設定ファイルの場所

sysup は以下の場所を優先順で探します：

1. `-c` オプションで指定した場所
2. `~/.config/sysup/sysup.toml` - **推奨**
3. `~/.sysup.toml`
4. `/etc/sysup/sysup.toml` - システム全体設定

### ディレクトリ作成

```bash
mkdir -p ~/.config/sysup
```

### TOML ファイルの作成

`~/.config/sysup/sysup.toml` を作成して、以下の内容を入力します：

```toml
[updaters]
# パッケージマネージャの有効/無効 (true/false)
apt = true
snap = true
flatpak = true
pipx = true
uv = true
npm = true
nvm = true
rustup = true
cargo = true
gem = true
brew = true
firmware = true
scoop = true

[auto_run]
# 自動実行モード: disabled | enabled | enabled_with_auth
mode = "disabled"

[logging]
# ログファイルの保存先
dir = "~/.local/share/sysup"
# ログファイルの保持日数
retention_days = 30
# ログレベル: DEBUG | INFO | WARNING | ERROR
level = "INFO"

[backup]
# バックアップディレクトリ
dir = "~/.local/share/sysup/backups"
# バックアップを有効にするか
enabled = true

[notification]
# デスクトップ通知を有効にするか
enabled = true
# 成功時に通知するか
on_success = true
# エラー時に通知するか
on_error = true
# 警告時に通知するか（実験的）
on_warning = false

[general]
# 複数のマネージャを並列実行するか
parallel_updates = false
# ドライランモード（実際には実行しない）
dry_run = false
# キャッシュディレクトリ
cache_dir = "~/.cache/sysup"
```

## 設定ファイルの詳細

### updaters セクション

各パッケージマネージャの有効/無効を制御します。

| キー | 説明 | デフォルト | 対応環境 |
|------|------|----------|--------|
| `apt` | APT (Debian/Ubuntu) | true | Linux |
| `snap` | Snap packages | true | Linux |
| `flatpak` | Flatpak | true | Linux |
| `pipx` | pipx (Python CLIツール) | true | Linux/macOS/Windows |
| `uv` | uv tool | true | Linux/macOS/Windows |
| `npm` | npm (Node.js) | true | Linux/macOS/Windows |
| `nvm` | nvm (Node Version Manager) | true | Linux/macOS/Windows |
| `rustup` | Rustup | true | Linux/macOS/Windows |
| `cargo` | Cargo | true | Linux/macOS/Windows |
| `gem` | Ruby gems | true | Linux/macOS/Windows |
| `brew` | Homebrew | true | macOS/Linux |
| `firmware` | ファームウェア更新 | true | Linux |
| `scoop` | Scoop | true | Windows |

### auto_run セクション

自動実行の設定を制御します。

| キー | 値 | 説明 |
|------|-----|------|
| `mode` | `disabled` | 自動実行なし（デフォルト） |
|  | `enabled` | 自動実行（sudo認証なし） |
|  | `enabled_with_auth` | 自動実行（sudo認証あり） |

### logging セクション

ログファイルの設定を制御します。

| キー | 説明 | デフォルト |
|------|------|----------|
| `dir` | ログディレクトリ | `~/.local/share/sysup` |
| `retention_days` | ログ保持日数 | 30 |
| `level` | ログレベル | INFO |

**ログレベルの選択肢：**
- `DEBUG` - 詳細なデバッグ情報を出力
- `INFO` - 通常の操作情報を出力（推奨）
- `WARNING` - 警告以上を出力
- `ERROR` - エラーのみ出力

### backup セクション

バックアップの設定を制御します。

| キー | 説明 | デフォルト |
|------|------|----------|
| `dir` | バックアップディレクトリ | `~/.local/share/sysup/backups` |
| `enabled` | バックアップ有効 | true |

バックアップはパッケージリストのスナップショットを保存し、更新前の状態に戻す際に使用できます。

### notification セクション

デスクトップ通知の設定を制御します。

| キー | 説明 | デフォルト |
|------|------|----------|
| `enabled` | 通知を有効にするか | true |
| `on_success` | 成功時に通知 | true |
| `on_error` | エラー時に通知 | true |
| `on_warning` | 警告時に通知（実験的） | false |

### general セクション

一般設定を制御します。

| キー | 説明 | デフォルト |
|------|------|----------|
| `parallel_updates` | 並列実行 | false |
| `dry_run` | ドライラン | false |
| `cache_dir` | キャッシュディレクトリ | `~/.cache/sysup` |

**parallel_updates について：**
- `true` の場合、複数のパッケージマネージャを同時に実行（高速）
- `false` の場合、順序通り実行（安定的）

## 例

### 例1: 最小限の設定

APT だけを更新する場合：

```toml
[updaters]
apt = true
snap = false
flatpak = false
pipx = false
uv = false
npm = false
nvm = false
rustup = false
cargo = false
gem = false
brew = false
firmware = false

[auto_run]
mode = "disabled"

[logging]
dir = "~/.local/share/sysup"
retention_days = 30
level = "INFO"

[backup]
dir = "~/.local/share/sysup/backups"
enabled = false

[notification]
enabled = false

[general]
parallel_updates = false
dry_run = false
cache_dir = "~/.cache/sysup"
```

### 例2: フル構成

すべてのマネージャを有効にし、並列実行する場合：

```toml
[updaters]
apt = true
snap = true
flatpak = true
pipx = true
uv = true
npm = true
nvm = true
rustup = true
cargo = true
gem = true
brew = true
firmware = true

[auto_run]
mode = "enabled"

[logging]
dir = "~/.local/share/sysup"
retention_days = 30
level = "DEBUG"

[backup]
dir = "~/.local/share/sysup/backups"
enabled = true

[notification]
enabled = true
on_success = true
on_error = true
on_warning = true

[general]
parallel_updates = true
dry_run = false
cache_dir = "~/.cache/sysup"
```

### 例3: 開発環境用

Python/Node.js/Rust だけを更新する場合：

```toml
[updaters]
apt = false
snap = false
flatpak = false
pipx = true
uv = true
npm = true
nvm = true
rustup = true
cargo = true
gem = false
brew = false
firmware = false

[auto_run]
mode = "disabled"

[logging]
dir = "~/.local/share/sysup"
retention_days = 30
level = "INFO"

[backup]
dir = "~/.local/share/sysup/backups"
enabled = true

[notification]
enabled = true
on_success = true
on_error = true

[general]
parallel_updates = true
dry_run = false
cache_dir = "~/.cache/sysup"
```

## よくある質問

### Q: 設定ファイルが見つかりません

A: デフォルトの検索パスが以下の通りです。いずれかの場所に配置してください：

```bash
# 推奨の場所
~/.config/sysup/sysup.toml

# または
~/.sysup.toml
/etc/sysup/sysup.toml  # システム全体設定（管理者権限が必要）
```

または `-c` オプションで明示的に指定できます：

```bash
sysup update -c ~/my-config.toml
```

### Q: 特定のパッケージマネージャが見つかりません

A: sysup は `which` コマンドで各マネージャのインストール状態を確認します。

確認方法：

```bash
# インストール状態を確認
which apt
which npm
which rustup

# sysupで利用可能なマネージャを確認
sysup update --list
```

未検出の場合は、先にパッケージマネージャをインストールしてください。

### Q: ウィザードで設定をやり直したいです

A: 再度 `sysup init` を実行してください：

```bash
sysup init
```

既存の設定ファイルを検出して、以下の選択肢が表示されます：

```
既存の設定ファイルを検出しました:
~/.config/sysup/sysup.toml

1. セットアップを続行（既存設定を更新）
2. セットアップをスキップ（現在の設定を使用）
3. 設定をリセット（デフォルトからやり直し）

選択:
```

**3. リセット** を選択すると、既存設定が `sysup.toml.bak` に保存された上で新規セットアップが開始されます。

### Q: デフォルト設定で実行できますか？

A: はい。設定ファイルがない場合、sysup はデフォルト設定で実行されます：

```bash
sysup update
```

設定ファイルを作成せずに実行したい場合：

```bash
# ドライランで動作確認
sysup update --dry-run

# リスト表示
sysup update --list
```

### Q: 並列実行で問題が発生しました

A: 一部のマネージャは並列実行に対応していない可能性があります。`parallel_updates = false` に設定して逐次実行にしてください：

```toml
[general]
parallel_updates = false
```

### Q: ログファイルの場所は？

A: ログは以下のディレクトリに保存されます：

```bash
# デフォルト場所
~/.local/share/sysup/

# または設定ファイルで指定した dir
```

確認方法：

```bash
# ログファイル一覧を表示
ls -la ~/.local/share/sysup/
```

### Q: バックアップはどこに保存されますか？

A: バックアップはデフォルトで以下の場所に保存されます：

```bash
~/.local/share/sysup/backups/

# または設定ファイルで指定した dir
```

確認方法：

```bash
ls -la ~/.local/share/sysup/backups/
```

### Q: 設定ファイルをリセットしたいです

A: 設定ファイルを削除してから、再度ウィザードを実行してください：

```bash
# 既存設定を削除
rm ~/.config/sysup/sysup.toml

# ウィザードを実行（新規作成）
sysup init
```

**警告**: ファイルを削除する前に、必要に応じてバックアップを取ってください。

### Q: 複数の環境で同じ設定を使いたいです

A: 以下の方法があります：

**方法1: ホームディレクトリに配置**
```bash
cp ~/.config/sysup/sysup.toml ~/sysup.toml
scp ~/sysup.toml user@remote-host:~/.config/sysup/
```

**方法2: 明示的に指定**
```bash
sysup update -c /shared/path/sysup.toml
```

**方法3: シンボリックリンク**
```bash
ln -s /shared/path/sysup.toml ~/.config/sysup/sysup.toml
```
