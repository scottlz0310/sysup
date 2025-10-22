# Windows対応計画（開発環境特化）

## 対象パッケージマネージャ

| Linux/macOS | Windows | 優先度 | 備考 |
|------------|---------|-------|------|
| APT/Snap | ❌ なし | - | Linux専用 |
| Homebrew | ⚠️ あり | 低 | 不安定 |
| **npm** | ✅ 同一 | **最高** | クロスプラットフォーム |
| **nvm** | ⚠️ nvm-windows | **高** | 別実装 |
| **pipx** | ✅ 同一 | **最高** | 既存コード流用可 |
| **uv tool** | ✅ 同一 | **最高** | 既存コード流用可 |
| **Rustup** | ✅ 同一 | **最高** | 既存コード流用可 |
| **Cargo** | ✅ 同一 | **最高** | 既存コード流用可 |
| **Gem** | ✅ 同一 | 中 | Ruby開発者向け |
| Flatpak | ❌ なし | - | Linux専用 |
| Firmware | ❌ なし | - | Linux専用 |
| - | **Scoop** | **最高** | **Windows標準** |
| - | PowerShell Gallery | 中 | PowerShell開発者向け |
| - | winget | 低 | 開発ツール少ない |
| - | Chocolatey | 低 | 管理者権限必須 |

---

## 実装方針

### Phase 1: コア対応（v0.5.0）

**既存コード流用（動作確認のみ）:**
- npm, pipx, uv tool, Rustup, Cargo

**新規実装:**
- Scoop updater（Windows開発者の標準）
- プラットフォーム検出（`is_windows()`）
- BaseUpdaterのPowerShell対応

**既存updater修正:**
- Linux専用updaterに`is_windows()`ガード追加

### Phase 2: 追加機能（v0.6.0）

- nvm-windows updater
- PowerShell Gallery updater
- winget updater（オプション）

**実装しない:**
- Chocolatey（管理者権限必須）
- Windows Update（リスク高）

---

## 実装の簡素化

### プラットフォーム検出

最小限のコード追加：
- `is_windows()`: Windows判定
- `is_unix()`: Linux/macOS判定

### 既存updater修正

Linux専用updaterに1行追加：
```python
def is_available(self) -> bool:
    if is_windows():
        return False
    # 既存のロジック
```

### PowerShell対応

BaseUpdaterで自動対応：
- Windowsでは自動的にPowerShell経由で実行
- 既存updaterの変更不要

---

## マイルストーン

### v0.5.0: Windows基本対応

**実装:**
- プラットフォーム検出
- Scoop updater
- 既存updater動作確認
- GitHub Actions Windows追加

**期待結果:**
```
PS> sysup --list

利用可能:
  ✓ scoop, npm, pipx, uv, rustup, cargo

無効（Linux専用）:
  ✗ apt, snap, flatpak, firmware
```

### v0.6.0: 追加機能

- nvm-windows
- PowerShell Gallery
- winget（オプション）

---

## テスト戦略

### 既存updaterテスト

プラットフォーム別テスト追加：
- Windows: npm, pipx等が利用可能
- Windows: apt, snap等が無効

### CI/CD

GitHub Actions マトリクス拡張：
- OS: ubuntu, macos, **windows**
- Python: 3.11, 3.12, 3.13

---

## 設定例（Windows）

```toml
[updaters]
# Windows開発環境
scoop = true
npm = true
pipx = true
uv = true
rustup = true
cargo = true

# 低優先度
nvm = true
gem = false
winget = false

# Linux専用（自動無効化）
apt = false
snap = false
flatpak = false
firmware = false

[logging]
dir = "~\\AppData\\Local\\sysup"
```

---

## メリット

1. **実装コスト削減**: 既存コードほぼ流用可
2. **保守性向上**: システムクリティカル機能を扱わない
3. **テスト簡素化**: 既存テスト流用可
4. **明確なユースケース**: 開発者向けツール特化

---

**最終更新**: 2025-10-22
