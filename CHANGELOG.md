# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- 自動実行機能（WSL対応）
- バックアップ機能
- 並列更新オプション
- 通知機能
- ログローテーション

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

[Unreleased]: https://github.com/scottlz0310/sysup/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/scottlz0310/sysup/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/scottlz0310/sysup/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/scottlz0310/sysup/releases/tag/v0.1.0
