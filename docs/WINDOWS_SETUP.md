# Windows環境セットアップガイド

sysupをWindows環境で使用するためのセットアップガイドです。

## 前提条件

- Windows 10/11
- PowerShell 5.1以上
- Python 3.11以上
- **Rust開発用** (オプション): Microsoft C++ Build Tools
  - Cargoパッケージのビルドに必要
  - [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/) からインストール

## インストール手順

### 1. Scoopのインストール

ScoopはWindows用のコマンドラインパッケージマネージャです。

```powershell
# PowerShellを管理者権限で起動
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```

### 2. Pythonのインストール（Scoop経由）

```powershell
scoop install python
```

または、[公式サイト](https://www.python.org/downloads/)からインストーラーをダウンロードしてインストールします。

### 3. uvのインストール

```powershell
# Scoop経由
scoop install uv

# または、PowerShell経由
irm https://astral.sh/uv/install.ps1 | iex
```

### 4. sysupのインストール

```powershell
# uvで
uv tool install git+https://github.com/scottlz0310/sysup.git

# pipxで
pipx install git+https://github.com/scottlz0310/sysup.git
```

## 設定

### 設定ファイルの作成

```powershell
# 設定ディレクトリを作成
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.config\sysup"

# サンプル設定をコピー
Copy-Item config\sysup.windows.toml.example "$env:USERPROFILE\.config\sysup\sysup.toml"

# 設定ファイルを編集
notepad "$env:USERPROFILE\.config\sysup\sysup.toml"
```

### 推奨設定（Windows）

```toml
[updaters]
scoop = true
npm = true
pipx = true
uv = true
rustup = true
cargo = true

[general]
parallel_updates = true

[logging]
dir = "~\\AppData\\Local\\sysup"
```

## 使い方

### 基本的な使い方

```powershell
# 全ての有効な更新を実行
sysup

# ドライラン（実際には更新しない）
sysup --dry-run

# 利用可能なupdaterを一覧表示
sysup --list
```

### 実行例

```powershell
PS> sysup --list

利用可能なUpdater
  ✓ Scoop: 有効
  ✓ npm: 有効
  ✓ pipx: 有効
  ✓ uv tool: 有効
  ✓ Rustup: 有効
  ✓ Cargo: 有効
  ✗ APT: 利用不可
  ✗ Snap: 利用不可
```

## 対応パッケージマネージャ

### Windows環境で利用可能

- **Scoop** - Windows標準パッケージマネージャ
- **npm** - Node.jsグローバルパッケージ（Node.js公式版またはScoop版）
- **pipx** - Python CLIツール
- **uv tool** - Python CLIツール（uvによる管理）
- **Rustup** - Rustツールチェーン
- **Cargo** - Rustパッケージ
- **Gem** - Ruby gems

#### Node.jsのインストール方法

```powershell
# Scoop経由（推奨）
scoop install nodejs-lts

# または公式インストーラー
# https://nodejs.org/ からダウンロードしてインストール
```

#### Rust開発環境のセットアップ

Cargoパッケージをビルドするには、Microsoft C++ Build Toolsが必要です：

```powershell
# Visual Studio Build Toolsを手動インストール
# https://visualstudio.microsoft.com/downloads/
# "Build Tools for Visual Studio 2022" をダウンロード
# 「C++によるデスクトップ開発」を選択してインストール
```

**注意**: Build Toolsがインストールされていない場合、Cargo updaterは自動的にスキップされます。

### Windows環境で利用不可（自動的に無効化）

- **APT** - Linux専用
- **Snap** - Linux専用
- **Flatpak** - Linux専用
- **Firmware** - Linux専用

## トラブルシューティング

### Scoopが見つからない

PowerShellを再起動してください。または、以下のコマンドでパスを確認：

```powershell
$env:Path
```

### 実行ポリシーエラー

PowerShellの実行ポリシーを変更してください：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### パスが通らない

環境変数PATHに以下を追加してください：

- `%USERPROFILE%\scoop\shims`
- `%USERPROFILE%\.local\bin`

### Cargoパッケージのビルドエラー

`link.exe not found` エラーが発生する場合：

1. **Visual Studio Build Toolsをインストール**
   - https://visualstudio.microsoft.com/downloads/
   - "Build Tools for Visual Studio 2022" をダウンロード
   - 「C++によるデスクトップ開発」を選択

2. **回避策**: Build Toolsをインストールしない場合、設定ファイルでCargo updaterを無効化：

```toml
[updaters]
cargo = false
```

## 制限事項

### 未対応機能

- **WSL統合** - Windows環境では利用不可
- **デスクトップ通知** - 現在未実装
- **自動実行設定** - 現在未実装

### 今後の対応予定（v0.6.0）

- **nvm-windows** - Node Version Manager for Windows
- **PowerShell Gallery** - PowerShellモジュール管理
- **winget** - Windows Package Manager（オプション）

## 参考リンク

- [Scoop公式サイト](https://scoop.sh/)
- [uv公式ドキュメント](https://docs.astral.sh/uv/)
- [sysup GitHub](https://github.com/scottlz0310/sysup)
