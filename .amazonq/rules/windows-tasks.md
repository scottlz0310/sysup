# Windows対応タスクリスト

## v0.5.0: Windows基本対応

### プラットフォーム検出
- [x] `src/sysup/core/platform.py` 作成
  - [x] `is_windows()` 関数実装
  - [x] `is_unix()` 関数実装
  - [x] `get_platform()` 関数実装（オプション）

### BaseUpdater拡張
- [x] `src/sysup/updaters/base.py` 修正
  - [x] PowerShell自動実行対応（command_exists）
  - [x] Windowsパス処理対応（where/which）
  - [x] エラーハンドリング強化

### Linux専用updater修正
- [x] `src/sysup/updaters/apt.py` - `is_windows()` ガード追加
- [x] `src/sysup/updaters/snap.py` - `is_windows()` ガード追加
- [x] `src/sysup/updaters/flatpak.py` - `is_windows()` ガード追加
- [x] `src/sysup/updaters/firmware.py` - `is_windows()` ガード追加

### Scoop updater実装
- [x] `src/sysup/updaters/scoop.py` 作成
  - [x] `ScoopUpdater` クラス実装
  - [x] `is_available()` 実装
  - [x] `perform_update()` 実装（update, update *, cleanup *）
  - [x] エラーハンドリング

### 既存updater動作確認
- [ ] npm - Windows動作確認
- [ ] pipx - Windows動作確認
- [ ] uv tool - Windows動作確認
- [ ] Rustup - Windows動作確認
- [ ] Cargo - Windows動作確認

### テスト追加
- [x] `tests/test_platform.py` 作成
  - [x] プラットフォーム検出テスト
- [x] `tests/test_scoop.py` 作成
  - [x] Scoop updaterテスト
- [x] 既存updaterテスト修正
  - [x] Windows環境での無効化テスト
  - [x] クロスプラットフォームテスト

### CI/CD
- [x] `.github/workflows/ci.yml` 修正
  - [x] Windows環境追加（windows-latest）
  - [x] Scoopインストール手順追加
  - [x] マトリクステスト確認

### ドキュメント
- [x] `README.md` 更新
  - [x] Windows対応を明記
  - [x] Scoopインストール手順追加
- [x] `config/sysup.windows.toml.example` 作成
- [x] `docs/WINDOWS_SETUP.md` 作成

---

## v0.6.0: 追加機能

### nvm-windows対応
- [ ] `src/sysup/updaters/nvm_windows.py` 作成
  - [ ] nvm-windows検出
  - [ ] 更新案内実装
- [ ] `tests/test_nvm_windows.py` 作成

### PowerShell Gallery対応
- [ ] `src/sysup/updaters/powershell_gallery.py` 作成
  - [ ] PowerShellモジュール更新
- [ ] `tests/test_powershell_gallery.py` 作成

### winget対応（オプション）
- [ ] `src/sysup/updaters/winget.py` 作成
  - [ ] winget更新実装
- [ ] `tests/test_winget.py` 作成

---

## 優先順位

### 最優先（v0.5.0必須）
1. プラットフォーム検出
2. Linux専用updaterガード追加
3. Scoop updater実装
4. CI/CD Windows追加

### 高優先度（v0.5.0推奨）
5. 既存updater動作確認
6. テスト追加
7. ドキュメント更新

### 中優先度（v0.6.0）
8. nvm-windows対応
9. PowerShell Gallery対応

### 低優先度（v0.6.0オプション）
10. winget対応

---

## 実装順序

1. **プラットフォーム検出** → 全ての基盤
2. **Linux専用updaterガード** → 既存機能保護
3. **BaseUpdater拡張** → PowerShell対応
4. **Scoop updater** → Windows標準ツール
5. **テスト追加** → 品質保証
6. **CI/CD** → 自動検証
7. **ドキュメント** → ユーザー案内

---

**作成日**: 2025-10-22
**対象バージョン**: v0.5.0, v0.6.0
