# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- 統合テスト・E2Eテストの整備
- SBOM生成の自動化
- 構造化ログの導入

## [0.5.2] - 2025-10-23

### Fixed
- **pre-commit**: ruff-formatが変更した場合にexit 1で終了するように修正
  - `fail_fast: true`を追加してコミットを中断

## [0.5.1] - 2025-10-23

### Fixed
- **Windows CI**: Windows環境でのCI実行時間を大幅改善（22分→数分）
  - `check_sudo_available()`でWindows環境をスキップ
  - テストで全updaterをモック化してハングを防止
  - `pytest-timeout`導入（5分タイムアウト）
- **CI/CD**: `uv sync --all-groups`に変更（PEP 735対応）
- **GemUpdater**: Windows環境での利用可能性判定を修正
  - `is_windows()`ガードを追加してWindows環境で自動無効化
- **エンコーディング**: WSL関連ファイルでUTF-8を明示的に指定

### Changed
- pytest実行時に`-vv`オプションを追加（詳細な出力）
- Windows環境でもカバレッジ収集を有効化

## [0.5.0] - 2025-10-22

### Added
- **Windows対応**: Windows環境での基本対応完了
  - プラットフォーム検出機能（`is_windows()`, `is_unix()`, `get_platform()`）
  - Scoop updater実装（Windows標準パッケージマネージャ）
  - BaseUpdater拡張（Windows環境での`where`コマンド対応）
  - Linux専用updaterのWindows環境での自動無効化（APT, Snap, Flatpak, Firmware）
- **テスト**: Windows対応テスト追加（13テストケース）
  - test_platform.py（プラットフォーム検出）
  - test_scoop.py（Scoop updater）
  - 既存updaterテストにWindows無効化テスト追加
- **CI/CD**: Windows環境追加（windows-latest）
  - マトリクステスト: Ubuntu/macOS/Windows × Python 3.11/3.12/3.13
  - Scoop自動インストール追加

### Changed
- pyproject.tomlに`Operating System :: Microsoft :: Windows`追加

### Documentation
- README.md更新（Windows対応明記）
- config/sysup.windows.toml.example作成（Windows用設定サンプル）
- docs/WINDOWS_SETUP.md作成（Windows環境セットアップガイド）

## [0.4.0] - 2025-10-09

### Added
- **品質向上**: テストカバレッジ87.41%達成（目標80%超過）
- **セキュリティ**: CodeQL自動スキャン導入
- **セキュリティ**: Secret Scanning + Push Protection有効化
- **セキュリティ**: Dependabot依存関係管理導入
- **セキュリティ**: SECURITY.md作成（脆弱性報告方針）
- **ドキュメント**: 全公開APIにDocstring整備（Googleスタイル）
- **CI/CD**: カバレッジゲート有効化（80%閾値）
- **CI/CD**: マトリクステスト（Ubuntu/macOS × Python 3.11/3.12/3.13）
- **テスト**: 227テストケース追加（6つの新規テストファイル）
  - test_additional_updaters.py（9種類のupdater）
  - test_apt.py（APT updater）
  - test_brew.py（Homebrew updater）
  - test_checks.py（システムチェック機能）
  - test_stats.py（統計情報管理）
  - test_uv.py（uv tool updater）

### Changed
- 開発ステータス: Alpha → Beta
- pre-commit設定強化（ruff, mypy, bandit）
- mypy strict相当の型チェック設定

### Documentation
- SECURITY_SETUP.md追加（セキュリティ機能セットアップガイド）
- QUALITY_IMPROVEMENT_PLAN.md更新（v0.4.0完了）
- README.md更新（品質バッジ追加）

### Fixed
- CargoUpdaterのエラーハンドリングテスト修正

## [0.3.0] - 2025-10-05

### Added
- WSL統合機能（`--setup-wsl`コマンド）
  - WSL環境の自動検出
  - .bashrc/.zshrcへの自動実行設定追加
  - 対話形式のセットアップウィザード
- デスクトップ通知機能
  - Linux（notify-send）対応
  - macOS（osascript）対応
  - 成功/エラー/警告の通知
- バックアップ機能
  - 更新前にパッケージリストをJSON形式でバックアップ
  - 全11種類のパッケージマネージャに対応
  - 古いバックアップの自動削除（最新10件を保持）
- 並列更新オプション
  - `parallel_updates`設定で有効化
  - ThreadPoolExecutorで最大4並列実行
- ログローテーション機能
  - `retention_days`設定で保持期間を指定
  - 古いログファイルの自動削除

### Changed
- 設定ファイルに`[notification]`セクション追加
- ロガー初期化時にログローテーションを自動実行

### Documentation
- WSL_SETUP.md追加（WSL自動実行設定ガイド）
- README.mdに新機能の説明追加
- USAGE.mdに新機能セクション追加

## [0.2.1] - 2025-10-05

### Fixed
- nvmの検出方法を改善（bashシェル経由でnvm関数の存在を直接確認）
- cargoの利用可能性判定を緩和（cargo-install-updateは実行時にチェック）

### Changed
- nvmがgitリポジトリでない場合は更新をスキップするように変更

## [0.2.0] - 2025-01-05

### Added
- 全11種類のupdater実装完了
  - APT, Snap, Homebrew, npm, nvm, pipx, Rustup, Cargo, Flatpak, Gem, Firmware
- 高優先度updater（APT, Snap, Homebrew）
- 中優先度updater（npm, nvm, pipx, Rustup, Cargo）
- 低優先度updater（Flatpak, Gem, Firmware）
- 完全なドキュメント整備
  - README.md
  - USAGE.md
  - CONTRIBUTING.md
  - CHANGELOG.md

### Changed
- PyPI公開計画を削除、GitHubインストール方式に変更

## [0.1.0] - 2025-01-05

### Added
- 初回リリース
- コア機能実装
  - Pydanticベースの設定管理（TOML形式）
  - Richベースの美しいログ出力
  - システムチェック機能（ディスク、ネットワーク、sudo）
  - 統計情報管理
  - 再起動チェック
  - プロセスロック（多重実行防止）
  - 日次実行チェック
  - ドライランモード
- APT updater実装
- Clickベースのコマンドラインインターフェース
- 基本的なテスト（設定モジュール）
- プロジェクト設定（pyproject.toml）
- ライセンス（MIT）

### Changed
- Bashスクリプト（up.sh）からPython版への移行

[Unreleased]: https://github.com/scottlz0310/sysup/compare/v0.5.2...HEAD
[0.5.2]: https://github.com/scottlz0310/sysup/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/scottlz0310/sysup/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/scottlz0310/sysup/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/scottlz0310/sysup/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/scottlz0310/sysup/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/scottlz0310/sysup/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/scottlz0310/sysup/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/scottlz0310/sysup/releases/tag/v0.1.0
