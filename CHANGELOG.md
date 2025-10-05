# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- テストスイートの充実
- CI/CD設定（GitHub Actions）

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

[Unreleased]: https://github.com/scottlz0310/sysup/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/scottlz0310/sysup/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/scottlz0310/sysup/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/scottlz0310/sysup/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/scottlz0310/sysup/releases/tag/v0.1.0
