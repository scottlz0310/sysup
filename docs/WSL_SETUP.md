# sysup 便利な使い方ガイド

このガイドでは、sysupをより便利に使うための設定方法を説明します。

## 概要

sysupは手動実行が基本ですが、エイリアスやショートカットを設定することで、
より簡単に実行できるようになります。

## 推奨設定方法

### 1. エイリアス設定（推奨）

`.bashrc`または`.zshrc`に以下のエイリアスを追加します：

```bash
# sysup - システム更新エイリアス
alias up='sudo -v && sysup'           # 基本的な更新
alias upd='sudo -v && sysup --dry-run' # ドライラン
alias upf='sudo -v && sysup --force'   # 強制実行
alias upl='sysup --list'               # updater一覧
```

**使い方：**
```bash
up    # システム更新を実行
upd   # 何が更新されるか確認
upf   # 今日既に実行済みでも強制実行
upl   # 利用可能なupdaterを表示
```

### 2. シンプルなエイリアス

sudo認証を毎回行いたくない場合：

```bash
alias up='sysup'
```

**注意：** この場合、APTやSnapなどsudo権限が必要なupdaterは実行時にパスワードを求められます。

### 3. 週次リマインダー（オプション）

自動実行の代わりに、週次でリマインダーを表示：

```bash
# .bashrc / .zshrc に追加
if [ -f ~/.cache/sysup/last_reminder ]; then
    LAST_REMINDER=$(cat ~/.cache/sysup/last_reminder)
    DAYS_SINCE=$((( $(date +%s) - LAST_REMINDER ) / 86400))
    if [ $DAYS_SINCE -ge 7 ]; then
        echo "💡 Tip: システム更新を実行しませんか？ 'up' コマンドで実行できます"
        mkdir -p ~/.cache/sysup
        date +%s > ~/.cache/sysup/last_reminder
    fi
else
    mkdir -p ~/.cache/sysup
    date +%s > ~/.cache/sysup/last_reminder
fi
```

## sudo認証の扱い

### 問題点

sysupは以下のupdaterでsudo権限が必要です：
- APT（システムパッケージ）
- Snap
- Firmware

自動実行では、パスワード入力ができないため、これらのupdaterがスキップされます。

### 解決策

**1. 事前にsudo認証（推奨）**
```bash
alias up='sudo -v && sysup'
```
`sudo -v`で事前に認証を更新し、その後sysupを実行します。

**2. sudoersでパスワードなし実行を許可（上級者向け）**
```bash
sudo visudo

# 以下を追加（YOUR_USERNAMEを実際のユーザー名に置換）
YOUR_USERNAME ALL=(ALL) NOPASSWD: /usr/bin/apt-get, /usr/bin/snap
```

**注意：** セキュリティリスクがあるため、個人環境でのみ推奨します。

**3. sudo不要なupdaterのみ使用**
```toml
# ~/.config/sysup/sysup.toml
[updaters]
apt = false      # 無効化
snap = false     # 無効化
firmware = false # 無効化

# sudo不要なupdater
brew = true
npm = true
pipx = true
rustup = true
cargo = true
nvm = true
```

## 便利なワークフロー

### 朝のルーティン

```bash
# 1. 何が更新されるか確認
upd

# 2. 問題なければ実行
up
```

### 週次メンテナンス

```bash
# 月曜日の朝に実行
up

# バックアップを確認
ls -lh ~/.local/share/sysup/backups/

# ログを確認
tail ~/.local/share/sysup/sysup_*.log
```

### トラブル時

```bash
# ドライランで確認
upd

# 利用可能なupdaterを確認
upl

# 設定ファイルを編集
vim ~/.config/sysup/sysup.toml
```

## 設定例

### 最小構成（高速）

```toml
[updaters]
# sudo不要で高速なupdaterのみ
apt = false
snap = false
brew = true
npm = true
pipx = true
rustup = true
cargo = true
nvm = true
flatpak = false
gem = false
firmware = false

[general]
parallel_updates = true
```

### フル構成（全て有効）

```toml
[updaters]
# 全て有効化（sudo認証が必要）
apt = true
snap = true
brew = true
npm = true
pipx = true
rustup = true
cargo = true
nvm = true
flatpak = true
gem = true
firmware = false  # 時間がかかるため無効化推奨

[general]
parallel_updates = true

[backup]
enabled = true

[notification]
enabled = true
```

## トラブルシューティング

### エイリアスが動作しない

**確認事項：**

1. エイリアスが正しく設定されているか確認
   ```bash
   alias | grep up
   ```

2. シェルを再起動
   ```bash
   source ~/.bashrc  # または source ~/.zshrc
   ```

3. sysupがインストールされているか確認
   ```bash
   which sysup
   sysup --version
   ```

### sudo権限エラー

**エラー例：**
```
E: Could not open lock file /var/lib/dpkg/lock-frontend - open (13: Permission denied)
```

**解決策：**

1. エイリアスで事前認証を使用
   ```bash
   alias up='sudo -v && sysup'
   ```

2. または、手動でsudo認証してから実行
   ```bash
   sudo -v
   sysup
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
   flatpak = false   # Flatpakも遅い場合がある
   ```

3. ドライランで確認してから実行
   ```bash
   upd  # 何が更新されるか確認
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

### 推奨ワークフロー

1. **週1回の定期実行**
   - 月曜日の朝に`up`コマンドを実行
   - ドライランで確認してから実行

2. **エイリアスの活用**
   ```bash
   alias up='sudo -v && sysup'
   alias upd='sudo -v && sysup --dry-run'
   ```

3. **設定のカスタマイズ**
   - 使用しないupdaterは無効化
   - 並列更新を有効化
   - バックアップを有効化

### セキュリティ

- **sudo認証は毎回行う**（エイリアスで`sudo -v`を使用）
- sudoersでパスワードなし実行は個人環境のみ
- バックアップ機能を有効にして、問題発生時に復元できるようにする

### パフォーマンス

- **並列更新を有効化**して実行時間を短縮
- **不要なupdaterを無効化**（firmware, flatpak, gemなど）
- **ドライランで事前確認**してから実行
- ログローテーションを設定してディスク容量を節約

### 推奨設定ファイル

```toml
# ~/.config/sysup/sysup.toml
[updaters]
apt = true
snap = true
brew = true
npm = true
pipx = true
rustup = true
cargo = true
nvm = true
flatpak = false
gem = false
firmware = false

[notification]
enabled = true
on_success = true
on_error = true

[backup]
enabled = true

[general]
parallel_updates = true

[logging]
retention_days = 30
```

## 関連ドキュメント

- [README](../README.md) - プロジェクト概要
- [USAGE](USAGE.md) - 詳細な使用方法
- [CONTRIBUTING](CONTRIBUTING.md) - 貢献ガイド
