# Windows対応計画書

## 概要

sysupプロジェクトのWindows対応について、拡張案と新規プロジェクト案を検討した結果、**拡張案（現プロジェクトにWindows対応を追加）**を採用する。

## 検討結果

### 拡張案（推奨）

**メリット：**
- 既存のアーキテクチャ（BaseUpdater、設定管理、ログ、通知等）を活用
- 統一されたCLIインターフェース
- 開発・保守コストの効率化
- ユーザーにとって単一ツールで完結

**デメリット：**
- プラットフォーム固有の複雑性増加
- Linux/macOS特化の設計（`which`コマンド、`/var/run/`等）の修正が必要
- テストマトリクスの複雑化

### 新規プロジェクト案（不採用）

**メリット：**
- Windows固有の最適化（PowerShell、レジストリ、Windows API等）
- シンプルな設計・テスト
- 独立したリリースサイクル

**デメリット：**
- 重複開発（設定管理、ログ、CLI等）
- ユーザーが複数ツールを管理
- 機能の一貫性維持が困難

## 採用理由

1. **アーキテクチャの優秀性**: 現在のBaseUpdaterパターンは拡張性が高く、Windows updaterも容易に追加可能

2. **Windows固有パッケージマネージャの対応可能性**:
   - Scoop、Chocolatey、winget、Windows Update
   - Microsoft Store、PowerShell Gallery
   - これらも既存のupdaterパターンで実装可能

3. **プラットフォーム検出の実装が比較的簡単**

4. **段階的移行が可能**

## 実装方針

### Phase 1: プラットフォーム基盤整備

1. **プラットフォーム検出モジュールの追加**
   ```python
   # src/sysup/core/platform.py
   import platform

   def is_windows() -> bool:
       return platform.system() == "Windows"

   def is_linux() -> bool:
       return platform.system() == "Linux"

   def is_macos() -> bool:
       return platform.system() == "Darwin"
   ```

2. **BaseUpdaterの拡張**
   - `command_exists()`メソッドのWindows対応（`where`コマンド使用）
   - PowerShellコマンド実行サポート

3. **SystemCheckerのWindows対応**
   - ディスク容量チェック（Windows API使用）
   - ネットワークチェック（`ping`コマンドの差異対応）
   - 管理者権限チェック（UAC対応）

### Phase 2: Windows Updater実装

優先順位順に実装：

1. **winget** - Windows Package Manager（Microsoft公式）
2. **Chocolatey** - 最も普及しているサードパーティ
3. **Scoop** - 開発者向けパッケージマネージャ
4. **PowerShell Gallery** - PowerShellモジュール
5. **Microsoft Store** - UWPアプリ
6. **Windows Update** - システム更新

### Phase 3: Windows固有機能

1. **レジストリ操作**（必要に応じて）
2. **Windowsサービス管理**
3. **Windows固有の通知システム**
4. **WSL統合の強化**

## 技術的考慮事項

### プラットフォーム固有の修正が必要な箇所

1. **checks.py**
   - `check_reboot_required()`: Windows再起動フラグの確認
   - `check_sudo_available()`: 管理者権限チェックに変更

2. **base.py**
   - `command_exists()`: `which` → `where`コマンド対応
   - PowerShellコマンド実行サポート

3. **pyproject.toml**
   - classifiersにWindows追加：`"Operating System :: Microsoft :: Windows"`

### テスト戦略

- GitHub ActionsでWindows環境のテストマトリクス追加
- Windows固有のmockテスト実装
- 段階的なカバレッジ目標設定

## マイルストーン

### v0.5.0: Windows基盤
- プラットフォーム検出
- BaseUpdaterのWindows対応
- SystemCheckerのWindows対応
- winget updater実装

### v0.6.0: 主要Windows Updater
- Chocolatey updater
- Scoop updater
- PowerShell Gallery updater

### v0.7.0: Windows固有機能
- Microsoft Store updater
- Windows Update統合
- Windows固有通知

## リスク評価

**高リスク:**
- Windows環境でのテスト不足
- 管理者権限の複雑性

**中リスク:**
- 既存Linux/macOS機能への影響
- CI/CDパイプラインの複雑化

**対策:**
- 段階的実装とテスト
- プラットフォーム固有コードの分離
- 既存機能の回帰テスト強化

## 結論

現在のsysupプロジェクトの高品質なアーキテクチャ（87.41%カバレッジ、厳格な型チェック）を活用し、Windows対応を段階的に実装することで、統一されたマルチプラットフォーム対応のシステム更新ツールを実現する。
