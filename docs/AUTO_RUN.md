# 自動実行設定ガイド

sysupを定期的に自動実行する方法を説明します。

## 目次

- [WSL（Windows Subsystem for Linux）での設定](#wslwindows-subsystem-for-linuxでの設定)
- [Ubuntu（ネイティブ）での設定](#ubuntuネイティブでの設定)
- [トラブルシューティング](#トラブルシューティング)

## WSL（Windows Subsystem for Linux）での設定

WSL環境では、起動時に自動実行する設定が便利です。

### 方法1: .bashrcでの自動実行（推奨）

WSL起動時に自動的にsysupを実行します。

#### 1. インストール

```bash
# uvでインストール
uv tool install git+https://github.com/scottlz0310/sysup.git

# または pipxで
pipx install git+https://github.com/scottlz0310/sysup.git
```

#### 2. .bashrcに追加

```bash
# .bashrcを編集
vim ~/.bashrc

# 以下を末尾に追加
# sysup自動実行（WSL起動時）
if [[ -n "$WSL_DISTRO_NAME" ]]; then
    # 今日まだ実行していない場合のみ実行
    if command -v sysup >/dev/null 2>&1; then
        # バックグラウンドで実行
        (sysup --auto-run 2>&1 | logger -t sysup) &
        disown
    fi
fi
```

#### 3. 設定を反映

```bash
source ~/.bashrc
```

### 方法2: Windows タスクスケジューラ（高度）

Windows側からWSLを定期実行します。

#### 1. PowerShellスクリプト作成

`C:\Scripts\run-sysup.ps1`を作成：

```powershell
# WSLでsysupを実行
wsl -d Ubuntu -u $env:USERNAME -- bash -c "sysup --auto-run"
```

#### 2. タスクスケジューラ設定

1. タスクスケジューラを開く
2. 「基本タスクの作成」
3. トリガー: 毎日、午前9時
4. 操作: プログラムの開始
   - プログラム: `powershell.exe`
   - 引数: `-ExecutionPolicy Bypass -File C:\Scripts\run-sysup.ps1`

## Ubuntu（ネイティブ）での設定

ネイティブUbuntu環境では、cronまたはsystemdタイマーを使用します。

### 方法1: cron（シンプル）

#### 1. インストール

```bash
# uvでインストール
uv tool install git+https://github.com/scottlz0310/sysup.git

# または pipxで
pipx install git+https://github.com/scottlz0310/sysup.git
```

#### 2. crontabを編集

```bash
crontab -e

# 以下を追加（毎日午前9時に実行）
0 9 * * * /home/$USER/.local/bin/sysup --auto-run >> /home/$USER/.local/share/sysup/cron.log 2>&1
```

**注意:** パスは環境に応じて調整してください。

#### 3. cronログの確認

```bash
tail -f ~/.local/share/sysup/cron.log
```

### 方法2: systemd timer（推奨）

より柔軟な設定が可能です。

#### 1. サービスファイル作成

`~/.config/systemd/user/sysup.service`を作成：

```ini
[Unit]
Description=System Package Update Service
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=%h/.local/bin/sysup --auto-run
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

#### 2. タイマーファイル作成

`~/.config/systemd/user/sysup.timer`を作成：

```ini
[Unit]
Description=Run sysup daily
Requires=sysup.service

[Timer]
OnCalendar=daily
OnBootSec=5min
Persistent=true

[Install]
WantedBy=timers.target
```

#### 3. タイマーを有効化

```bash
# systemdをリロード
systemctl --user daemon-reload

# タイマーを有効化
systemctl --user enable sysup.timer

# タイマーを開始
systemctl --user start sysup.timer

# 状態確認
systemctl --user status sysup.timer
systemctl --user list-timers
```

#### 4. ログ確認

```bash
# サービスログを確認
journalctl --user -u sysup.service -f

# 最新の実行ログ
journalctl --user -u sysup.service -n 50
```

### 方法3: anacron（不定期起動のマシン向け）

ラップトップなど、常時起動していないマシンに適しています。

#### 1. anacronをインストール

```bash
sudo apt install anacron
```

#### 2. anacrontabを編集

```bash
sudo vim /etc/anacrontab

# 以下を追加（1日に1回実行）
1  5  sysup.daily  /home/$USER/.local/bin/sysup --auto-run
```

## sudo権限の設定

自動実行では対話的にパスワードを入力できないため、sudo権限の設定が必要です。

### オプション1: sudoタイムアウトの延長

```bash
sudo visudo

# 以下を追加（60分間有効）
Defaults timestamp_timeout=60
```

### オプション2: 特定コマンドのパスワード不要化（非推奨）

セキュリティリスクがあるため、慎重に検討してください。sysupが実行するコマンドに絞って許可する例です。

```bash
# /etc/sudoers.d に専用ファイルを作成（構文チェック付き）
sudo visudo -f /etc/sudoers.d/apt-snap-nopasswd

# 以下を追加（YOUR_USERNAMEを実際のユーザー名に置換）
# sudoers内では$USERは展開されません
YOUR_USERNAME ALL=(ALL) NOPASSWD: /usr/bin/apt update, /usr/bin/apt upgrade -y, /usr/bin/apt autoremove -y, /usr/bin/apt autoclean, /usr/bin/snap refresh
```

**補足:**
- sysupは`apt`を使用します。`apt-get`を使う運用なら、同様に`/usr/bin/apt-get ...`を追加してください。
- ファイルの権限は`0440`が推奨です（`visudo -f`で作成すれば問題ありません）。

### オプション3: 事前認証（WSL推奨）

WSL起動時にsudo認証を行います。

```bash
# .bashrcに追加
if [[ -n "$WSL_DISTRO_NAME" ]]; then
    # sudo認証（バックグラウンドで）
    sudo -v
fi
```

## 設定ファイルのカスタマイズ

自動実行用の設定ファイルを作成することをお勧めします。

```bash
# 設定ディレクトリ作成
mkdir -p ~/.config/sysup

# 設定ファイル作成
cat > ~/.config/sysup/sysup.toml << 'EOF'
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
scoop = true

[logging]
dir = "~/.local/share/sysup"
level = "INFO"

[general]
dry_run = false
cache_dir = "~/.cache/sysup"
EOF
```

## トラブルシューティング

### 自動実行が動作しない

#### 1. パスの確認

```bash
# sysupのパスを確認
which sysup

# パスが正しいか確認
ls -la ~/.local/bin/sysup
```

#### 2. 権限の確認

```bash
# 実行権限があるか確認
ls -la $(which sysup)

# 必要に応じて権限付与
chmod +x ~/.local/bin/sysup
```

#### 3. ログの確認

```bash
# sysupのログを確認
tail -f ~/.local/share/sysup/sysup_*.log

# systemdの場合
journalctl --user -u sysup.service -f

# cronの場合
tail -f ~/.local/share/sysup/cron.log
```

### sudo権限エラー

```bash
# sudo権限をテスト
sudo -n true && echo "OK" || echo "NG"

# sudoタイムアウトを確認
sudo -l | grep timestamp_timeout
```

### 日次実行チェックをリセット

```bash
# 日次実行チェックをリセット
rm ~/.cache/sysup/daily_run

# 強制実行
sysup --force
```

## ベストプラクティス

1. **テスト実行**: 自動実行設定前に手動で`sysup --auto-run`をテスト
2. **ログ監視**: 初回は数日間ログを確認
3. **通知設定**: 重要な更新は通知を設定（今後実装予定）
4. **バックアップ**: 重要なシステムは定期的にバックアップ
5. **段階的導入**: まずドライランモードでテスト

## 関連ドキュメント

- [README](../README.md) - プロジェクト概要
- [USAGE](USAGE.md) - 詳細な使用方法
- [実装計画書](implement/sysup-implementation-plan.md) - 開発計画
