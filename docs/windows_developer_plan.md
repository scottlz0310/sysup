## 🎯 開発環境特化のWindows対応計画（修正版）

### 対象パッケージマネージャの再定義

**Linux/macOS版との対応関係:**

| Linux/macOS | Windows対応 | 優先度 | 備考 |
|------------|-----------|-------|------|
| APT/Snap | ❌ なし | - | システムパッケージマネージャ |
| Homebrew | ⚠️ あり（非推奨） | 低 | Windows版は不安定 |
| **npm** | ✅ 同一 | **最高** | クロスプラットフォーム |
| **nvm** | ⚠️ nvm-windows | **高** | 別実装だが同等機能 |
| **pipx** | ✅ 同一 | **最高** | Python CLI管理 |
| **uv tool** | ✅ 同一 | **最高** | 既に対応済み |
| **Rustup** | ✅ 同一 | **最高** | クロスプラットフォーム |
| **Cargo** | ✅ 同一 | **最高** | Rust開発必須 |
| **Gem** | ✅ 同一 | 中 | Ruby開発者向け |
| Flatpak | ❌ なし | - | Linuxアプリ配布 |
| Firmware | ❌ なし | - | Linux専用 |
| - | **Scoop** | **最高** | **Windows開発者の標準** |
| - | PowerShell Gallery | 中 | PowerShell開発者向け |
| - | winget | 低 | 一般向け、開発ツール少ない |
| - | Chocolatey | 低 | 管理者権限必須、重い |

---

## 📋 修正された実装方針

### Phase 1: 開発環境コア対応（v0.5.0）

**最優先実装（クロスプラットフォーム対応済み）:**

```python
# これらは既にLinux/macOSで動作しているので、
# Windowsでのコマンド実行確認のみで対応完了
```

1. **✅ npm** - `npm update -g` (Windows/Linux/macOS同一)
2. **✅ pipx** - `pipx upgrade-all` (同一)
3. **✅ uv tool** - `uv tool upgrade --all` (同一)
4. **✅ Rustup** - `rustup update` (同一)
5. **✅ Cargo** - `cargo install-update -a` (同一)

**Windows固有実装:**

6. **🆕 Scoop** - Windows開発者の事実上の標準

```python
# src/sysup/updaters/scoop.py
from sysup.updaters.base import BaseUpdater

class ScoopUpdater(BaseUpdater):
    """Scoop package manager updater.
    
    Scoop is the most popular package manager for Windows developers.
    Supports: Git, Python, Node.js, Go, Rust, etc.
    
    Requirements:
        - PowerShell 5.1+
        - Scoop installed (https://scoop.sh)
    """
    
    def __init__(self):
        super().__init__("scoop", "Scoop")
    
    def is_available(self) -> bool:
        """Check if Scoop is available."""
        if not is_windows():
            return False
        return self.command_exists("scoop")
    
    def update(self) -> bool:
        """Update Scoop and all installed packages."""
        steps = [
            ("Scoopを更新中", "scoop update"),
            ("パッケージを更新中", "scoop update *"),
            ("クリーンアップ中", "scoop cleanup *"),
        ]
        
        for message, command in steps:
            self.log_info(message)
            if not self.run_command(command):
                return False
        
        return True
```

**中優先度（開発者によっては必要）:**

7. **nvm-windows** - Node.jsバージョン管理（nvmとは別実装）

```python
# src/sysup/updaters/nvm_windows.py
class NvmWindowsUpdater(BaseUpdater):
    """nvm-windows updater.
    
    Note: This is different from nvm on Linux/macOS.
    Windows version: https://github.com/coreybutler/nvm-windows
    """
    
    def is_available(self) -> bool:
        if not is_windows():
            return False
        # nvm-windowsは `nvm version` で確認
        return self.command_exists("nvm")
    
    def update(self) -> bool:
        """Update Node.js versions managed by nvm-windows."""
        # nvm-windows自体の更新は手動
        # インストール済みNode.jsバージョンの一覧と最新版への案内
        self.log_info("nvm-windows自体の更新は手動で行ってください")
        self.log_info("最新版: https://github.com/coreybutler/nvm-windows/releases")
        return True
```

### Phase 2: オプション機能（v0.6.0）

**低優先度（必要に応じて実装）:**

8. **PowerShell Gallery** - PowerShell開発者向け
9. **Gem** - Ruby開発者向け（既存実装の動作確認のみ）
10. **winget** - 念のため実装（開発ツールは少ない）

**実装しない:**
- ❌ Chocolatey - 管理者権限必須、Scoopで十分
- ❌ Microsoft Store - 開発環境に不要
- ❌ Windows Update - リスク高、開発ツール対象外

---

## 🔧 実装の簡素化

### 既存コードの再利用率を最大化

```python
# src/sysup/core/platform.py（最小限のコード）

import platform

def is_windows() -> bool:
    """Windows環境かチェック"""
    return platform.system() == "Windows"

def is_unix() -> bool:
    """Unix系（Linux/macOS）かチェック"""
    return platform.system() in ("Linux", "Darwin")

# これだけでOK！既存のupdaterはis_unix()で判定を追加するだけ
```

### 既存updaterの修正（最小限）

```python
# src/sysup/updaters/apt.py（例）

class AptUpdater(BaseUpdater):
    def is_available(self) -> bool:
        # Windowsでは無効化
        if is_windows():
            return False
        return self.command_exists("apt-get")

# 同様にSnap, Flatpak, Firmwareも is_windows() チェックを追加
```

### BaseUpdaterの拡張（PowerShell対応）

```python
# src/sysup/updaters/base.py

class BaseUpdater:
    def run_command(self, command: str, ...) -> bool:
        """コマンド実行（PowerShell自動対応）"""
        if is_windows() and not command.startswith("powershell"):
            # Windowsでは自動的にPowerShell経由で実行
            command = f'powershell -NoProfile -Command "{command}"'
        
        # 既存のsubprocess.run()処理
        ...
```

---

## 📊 修正されたマイルストーン

### v0.5.0: 開発環境Windows対応（Phase 1）

**実装内容:**
- ✅ プラットフォーム検出（`is_windows()`のみ）
- ✅ BaseUpdaterのPowerShell対応
- ✅ **Scoop updater実装**（新規）
- ✅ 既存updater（npm, pipx, uv, Rustup, Cargo）の動作確認
- ✅ Linux/macOS専用updaterに`is_windows()`ガード追加
- ✅ GitHub Actions Windows環境追加

**期待される成果:**
```bash
# Windowsで実行
PS> sysup --list

利用可能なupdater:
  ✓ scoop     - Scoop package manager
  ✓ npm       - Node.js global packages
  ✓ pipx      - Python CLI tools
  ✓ uv        - UV tool packages
  ✓ rustup    - Rust toolchain
  ✓ cargo     - Rust packages

無効なupdater（このプラットフォームでは利用不可）:
  ✗ apt       - Linux only
  ✗ snap      - Linux only
  ✗ flatpak   - Linux only
  ✗ firmware  - Linux only
```

### v0.6.0: 追加機能（Phase 2・オプション）

**実装内容:**
- nvm-windows updater
- PowerShell Gallery updater
- winget updater（念のため）
- Gem updaterのWindows動作確認

---

## 🧪 簡素化されたテスト戦略

### 既存updaterのテスト

```python
# tests/test_npm.py（例）

def test_npm_available_windows():
    """npmはWindowsでも利用可能"""
    with patch('platform.system', return_value='Windows'):
        updater = NpmUpdater()
        # commandが存在すればTrue
        assert updater.is_available() or not updater.command_exists("npm")

def test_apt_unavailable_windows():
    """APTはWindowsでは無効"""
    with patch('platform.system', return_value='Windows'):
        updater = AptUpdater()
        assert not updater.is_available()
```

### GitHub Actions（簡略版）

```yaml
# .github/workflows/test.yml

strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ['3.11', '3.12', '3.13']

jobs:
  test:
    steps:
      - name: Install Scoop (Windows only)
        if: runner.os == 'Windows'
        run: |
          iwr -useb get.scoop.sh | iex
          scoop install git
      
      - name: Run tests
        run: uv run pytest -v --cov
```

---

## 📝 設定ファイル例（Windows向け）

```toml
# config/sysup.windows.toml.example

[updaters]
# Windows開発環境向け設定
scoop = true          # Windows開発者の標準
npm = true            # Node.js開発
pipx = true           # Python CLIツール
uv = true             # Python開発
rustup = true         # Rust開発
cargo = true          # Rustパッケージ
gem = false           # Ruby開発者のみ

# Windows版があるが非推奨
nvm = true            # nvm-windows
brew = false          # Windows版は不安定

# 低優先度
winget = false        # 開発ツール少ない
powershell_gallery = false  # PowerShell開発者のみ

# Linux/macOS専用（自動的に無効化）
apt = false
snap = false
flatpak = false
firmware = false

[general]
# Windows環境の推奨設定
parallel_updates = true   # 並列更新で高速化
dry_run = false

[logging]
dir = "~\\AppData\\Local\\sysup"  # Windows標準パス
level = "INFO"
```

---

## ✅ 開発環境特化版のメリット

1. **実装コストの大幅削減**
   - Scoop以外は既存コードがほぼそのまま動作
   - PowerShell対応のみ追加

2. **保守性の向上**
   - システムクリティカルな機能（Windows Update等）を扱わない
   - UAC、レジストリ操作が不要

3. **テストの簡素化**
   - npm, pipx, uv等は既にテスト済み
   - Scoopのテストのみ追加

4. **ユースケースの明確化**
   - 開発者向けツールに特化
   - ドキュメント作成が容易
