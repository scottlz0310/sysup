# sysup init コマンド仕様書

## 概要

`sysup init` は初期セットアップを行う対話型メニューです。このコマンドは新規ユーザーが sysup を最初に使う際に、必要な設定を効率的に進めるためのツールです。

**実装技術スタック:**
- Click: CLIフレームワーク
- rich: 対話型UIとテーブル表示

## 1. コマンド仕様

### 実行コマンド

```bash
sysup init
```

### 動作フロー

#### ステップ1: 既存設定の確認

- 設定ファイル（`~/.config/sysup/sysup.toml`）の有無をチェック
- **存在しない場合**: 新規セットアップモードへ進む
- **存在する場合**: 下記の選択肢を提示

#### ステップ2: 既存設定検出時の処理

```text
既存の設定ファイルを検出しました:
~/.config/sysup/sysup.toml

1. セットアップを続行（既存設定を更新）
2. セットアップをスキップ（現在の設定を使用）
3. 設定をリセット（デフォルトからやり直し）
選択: _
```

各選択肢の動作：

- **1. 続行**: 既存値を引き継いで更新ウィザード開始
  - 各工程で現在値を表示
  - 変更したい項目のみ修正可能
  - 変更なしでスキップも可能

- **2. スキップ**: セットアップウィザードを終了
  - 既存設定ファイルを使用

- **3. リセット**: 既存設定をバックアップしてから新規セットアップ開始
  - 既存ファイルは `sysup.toml.bak` として保存
  - すべての工程を新規セットアップ同様に実行

### 出力例
```
╔════════════════════════════════════════╗
║   sysup 初期セットアップウィザード    ║
╚════════════════════════════════════════╝

ようこそ！このウィザードで sysup の初期セットアップを行います。

[1/5] システム環境の確認
      OS: Linux
      パッケージマネージャ: apt, npm, rustup
      ✓ 検出完了

[2/5] 実行モードの選択
      1. 標準モード（対話的）
      2. 自動実行モード（スケジュール実行）
      3. スキップ
      選択: 2

[3/5] 更新対象の選択
      有効なパッケージマネージャ:
      ✓ apt (Debian/Ubuntu)
      ✓ npm (Node.js)
      ✓ rustup (Rust)
      - pipx (Python - インストール未検出)

      有効にするマネージャを選択 (スペース=トグル, Enter=確定):

[4/5] 詳細設定
      1. ログ設定
      2. バックアップ設定
      3. 通知設定
      4. 並列実行設定
      5. スキップ
      選択: 1

      ログレベル: INFO / DEBUG / WARNING / ERROR
      選択: INFO

[5/5] セットアップ完了
      生成された設定ファイル:
      ~/.config/sysup/sysup.toml

      次のコマンドで実行できます:
      sysup          # 通常実行
      sysup --list   # インストール済みマネージャ確認
```

## 2. セットアップ工程

### 工程 1: システム環境の確認

自動検出する項目:
- **OS検出**: Linux / macOS / Windows(WSL)
- **利用可能なパッケージマネージャ**: 実際にインストール済みのマネージャを検出
  - Linux: apt, snap, flatpak, pipx, npm, rustup, cargo, gem, nvm, uv
  - macOS: brew, npm, rustup, cargo, gem, nvm, pipx, uv
  - Windows: scoop, npm, rustup, cargo, gem, pipx, uv

### 工程 2: 実行モードの選択

ユーザーに選択肢を提示:
1. **標準モード**: 通常、必要に応じて確認プロンプトを表示
2. **自動実行モード**: cron/Task Scheduler での定期実行を想定。確認プロンプトなし
3. **スキップ**: デフォルト値を使用（標準モード）

設定値: `general.dry_run`, `auto_run.mode`

### 工程 3: 更新対象の選択

利用可能なパッケージマネージャの一覧から選択:

```
有効にするパッケージマネージャを選択してください (スペース: トグル, Enter: 確定):
  [x] apt
  [ ] snap
  [x] npm
  [x] rustup
  [ ] pipx
  ...
```

設定値: `updaters.*`

実装詳細:
- Checkbox UIは richの `Prompt.ask()` またはカスタム実装
- または、数字入力 (1-5: トグル, q: 確定) なども検討

### 工程 4: 詳細設定（オプション）

以下のいずれかを設定:

#### 4.1 ログ設定
- ログレベル: INFO / DEBUG / WARNING / ERROR
- 保持日数: 30日（デフォルト）
設定値: `logging.level`, `logging.retention_days`

#### 4.2 バックアップ設定
- バックアップを有効化するか
- バックアップ保持数: 10個（デフォルト）
設定値: `backup.enabled`, `backup.dir`

#### 4.3 通知設定
- デスクトップ通知を有効化するか
- 成功時に通知するか
- エラー時に通知するか
設定値: `notification.enabled`, `notification.on_success`, `notification.on_error`

#### 4.4 並列実行設定
- 複数パッケージマネージャの並列実行を有効化するか
設定値: `general.parallel_updates`

### 工程 5: セットアップ完了

生成された設定ファイルの確認:
- 保存先: `~/.config/sysup/sysup.toml`
- 生成内容の表示
- 次のステップの案内

## 3. 設定ファイルの処理

### 新規セットアップ時

- `~/.config/sysup/` ディレクトリを作成（存在しない場合）
- `~/.config/sysup/sysup.toml` を新規作成
- ユーザーに通知して完了

### 既存設定更新時

#### 続行を選択した場合

- 既存ファイルを読み込み
- ユーザーの更新入力を受け取る
- 既存ファイルを上書き（自動バックアップなし）

#### リセットを選択した場合

- 既存ファイルを `~/.config/sysup/sysup.toml.bak` にリネーム
- 新規セットアップを実行
- ユーザーに通知: 「既存設定は sysup.toml.bak に保存されています」

## 4. ファイル構成

### 生成ファイル

```text
~/.config/sysup/sysup.toml          # 設定ファイル
~/.config/sysup/sysup.toml.bak      # バックアップ（リセット時）
```

### サンプル設定ファイル

```toml
[updaters]
apt = true
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
on_warning = false

[general]
parallel_updates = false
dry_run = false
cache_dir = "~/.cache/sysup"
```

## 4. エラーハンドリング

### 権限エラー
- `~/.config/sysup` ディレクトリ作成失敗時:
  ```
  エラー: 設定ディレクトリを作成できません: ~/.config/sysup
  理由: 権限がありません
  ```

### キャンセル
- Ctrl+C 入力時:
  ```
  セットアップをキャンセルしました
  後でセットアップするには: sysup init
  ```

## 5. デフォルト値

`sysup init` を実行していなくても、`SysupConfig.load_config()` がデフォルト値を使用するため、動作に支障はありません。

## 6. 実装上の留意点

- **既存設定の上書き**: 既に設定ファイルが存在する場合、ウィザードで警告して確認を取る
- **バックアップ**: 既存設定ファイルは `sysup.toml.bak` として自動バックアップ
- **パッケージマネージャ検出**: `which` コマンドまたは `shutil.which()` を使用
- **プログレッシブディスクロージャー**: 詳細設定は "詳細設定を行いますか？" で確認

## 7. テスト計画

- [ ] システム検出テスト（各OS、各パッケージマネージャ）
- [ ] UI/UXテスト（選択肢の遷移、キャンセル処理）
- [ ] 設定ファイル生成テスト（TOML形式の正合性）
- [ ] エラーハンドリングテスト（権限エラー、ディスク満杯など）

## 8. 今後の拡張

- インタラクティブなチェックボックスUI (blessed, questionary など)
- WSL環境での自動実行設定
- クラウド連携（複数マシン間の設定同期）
