# WSL自動実行設定ガイド

このガイドでは、WSL（Windows Subsystem for Linux）環境でsysupを自動実行する方法を説明します。

## 概要

WSL統合機能を使用すると、WSLログイン時に自動的にシステム更新を実行できます。
週1回程度の頻度で自動実行されるため、常に最新の状態を保つことができます。

## セットアップ方法

### 1. 自動セットアップ（推奨）

最も簡単な方法は、`--setup-wsl`オプションを使用することです：

```bash
sysup --setup-wsl
```

対話形式で以下を選択できます：

1. **有効化（sudo認証なし）** - 推奨
   - sudo権限が不要な更新のみ実行
   - パスワード入力なしで自動実行

2. **有効化（sudo認証あり）**
   - 全ての更新を実行
   - 初回ログイン時にsudoパスワードが必要

3. **キャンセル**
   - セットアップを中止

### 2. 手動セットアップ

`.bashrc`または`.zshrc`に以下を追加します：

```bash
# sysup - システム自動更新
# WSLログイン時に自動実行（週1回）
if [ -z "${SYSUP_RAN:-}" ]; then
    export SYSUP_RAN=1
    sysup --auto-run 2>/dev/null || true
fi
```

## 動作の仕組み

### 実行タイミング

- WSLシェルの起動時に実行
- 環境変数`SYSUP_RAN`で多重実行を防止
- 日次実行チェックにより、1日1回のみ実行

### 実行内容

1. システムチェック（ディスク容量、ネットワーク）
2. 有効なパッケージマネージャの更新
3. バックアップ作成（有効な場合）
4. 更新結果のログ保存

### 自動実行モード

`--auto-run`フラグが指定されると：

- 対話的なプロンプトなしで実行
- エラーが発生しても処理を継続
- 標準エラー出力を抑制（`2>/dev/null`）

## 設定のカスタマイズ

### 自動実行の無効化

設定ファイル（`~/.config/sysup/sysup.toml`）で制御できます：

```toml
[auto_run]
mode = "disabled"  # 自動実行を無効化
```

または、`.bashrc`/`.zshrc`から該当行を削除します：

```bash
sysup --setup-wsl
# 「設定を削除しますか？」で「y」を選択
```

### 実行頻度の調整

デフォルトでは日次チェックにより1日1回のみ実行されます。
強制的に再実行する場合：

```bash
sysup --force
```

### 特定のupdaterのみ有効化

設定ファイルで不要なupdaterを無効化できます：

```toml
[updaters]
apt = true
snap = true
flatpak = false  # 無効化
pipx = true
npm = true
nvm = true
rustup = true
cargo = true
gem = false      # 無効化
brew = true
firmware = false # 無効化
```

## トラブルシューティング

### 自動実行が動作しない

**確認事項：**

1. WSL環境かどうか確認
   ```bash
   cat /proc/version | grep -i microsoft
   ```

2. sysupがインストールされているか確認
   ```bash
   which sysup
   ```

3. 設定が正しく追加されているか確認
   ```bash
   grep -A5 "sysup" ~/.bashrc
   ```

### sudo権限エラー

**解決策：**

- sudo認証なしモードを使用（推奨）
- または、sudoersファイルでパスワードなし実行を許可

```bash
# sudoersファイルを編集（注意して実行）
sudo visudo

# 以下を追加（YOUR_USERNAMEを実際のユーザー名に置換）
YOUR_USERNAME ALL=(ALL) NOPASSWD: /usr/bin/apt, /usr/bin/snap
```

### 実行が遅い

**解決策：**

1. 並列更新を有効化
   ```toml
   [general]
   parallel_updates = true
   ```

2. 不要なupdaterを無効化
   ```toml
   [updaters]
   firmware = false  # ファームウェア更新は時間がかかる
   ```

### ログの確認

自動実行のログを確認：

```bash
# 最新のログを表示
ls -lt ~/.local/share/sysup/*.log | head -1 | xargs cat

# または
tail -f ~/.local/share/sysup/sysup_*.log
```

## ベストプラクティス

### 推奨設定

```toml
[updaters]
# 高速なupdaterのみ有効化
apt = true
snap = true
brew = true
npm = true
pipx = true
rustup = true
cargo = true
nvm = true

# 時間がかかるものは無効化
flatpak = false
gem = false
firmware = false

[auto_run]
mode = "enabled"  # sudo認証なし

[notification]
enabled = true
on_success = true
on_error = true

[backup]
enabled = true

[general]
parallel_updates = true  # 高速化
```

### セキュリティ

- sudo認証なしモードを使用する場合、APT/Snapは更新されません
- 重要な更新は手動で実行することを推奨
- バックアップ機能を有効にして、問題発生時に復元できるようにする

### パフォーマンス

- 並列更新を有効化して実行時間を短縮
- 不要なupdaterを無効化
- ログローテーションを設定してディスク容量を節約

## 関連ドキュメント

- [README](../README.md) - プロジェクト概要
- [USAGE](USAGE.md) - 詳細な使用方法
- [CONTRIBUTING](CONTRIBUTING.md) - 貢献ガイド
