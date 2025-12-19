# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- SBOM生成の自動化
- 構造化ログの導入

## [0.10.0] - 2025-12-19

### Added
- **pnpm updater**: pnpmグローバルツール更新機能を追加
  - `pnpm update -g` でグローバルパッケージを更新
  - Windows/Linux/macOS対応
  - `sysup init` での自動検出に対応
  - パッケージリストのバックアップ機能に対応
  - npmからpnpmへの移行基盤を整備

### Changed
- **対応パッケージマネージャ数**: 13種類から14種類に拡大
- **README**: pnpm対応を追記、インストール手順をv0.10.0に更新

## [0.9.0] - 2025-12-16

### Added
- **E2Eテスト整備**: pexpectを使用した対話型CLI（init コマンド）のE2Eテストを追加
  - TTYモードでの矢印キー操作、スペースでのトグル、qキーでの確定をテスト
  - 既存設定ファイルの検出・続行・スキップ・リセット処理をテスト
  - Ctrl+Cでのキャンセル処理をテスト
- **統合テスト**: updateコマンドの統合テストを追加
  - --help, --version, --list, --dry-run オプションのテスト
  - 不正な設定ファイルでのエラーハンドリングテスト

### Changed
- **テスト戦略**: 対話型CLI（TTY/キー入力）のテストはE2Eで担保し、ユニットテストは仕様が固まるまで最小限にする方針を実装

### Changed
- **init コマンド**: 工程2で検出済みupdaterを選択（デフォルトは検出済みのみ有効）、工程3で実行モード選択に変更。TTYでは矢印キー移動+スペースでトグル、非TTYでは番号入力トグルにフォールバック。
- **検出精度**: `--version` 等の軽い実行を含めて「実際に起動できるか」を検出に反映。

## [0.8.2] - 2025-12-15

### Fixed
- **Windows（Scoop実行）**: `.cmd/.ps1` ラッパーを直接実行した際に `WinError 2` になるケースに対応し、`scoop update` / `scoop update *` / `scoop cleanup *` が実行できるように改善。

## [0.8.1] - 2025-12-15

### Fixed
- **init コマンド（Windows/Scoop）**: `sysup init` の検出・選択・設定ファイル生成に `scoop` を追加し、`src/sysup/updaters/scoop.py` と整合するように修正。

### Changed
- **改行コードの統一**: `.gitattributes` と `.editorconfig` を追加し、`mixed-line-ending` フック（`--fix=lf`）と `git add` の挙動が衝突しにくいよう LF に統一。

## [0.8.0] - 2025-12-14

### Added
- **uv updater**: `uv self update` を `uv tool upgrade --all` の前に自動実行し、uv本体とツール群の両方を常に最新状態に維持。スタンドアロン以外のインストールでは警告のみで処理を継続し、順序を保証する回帰テストも追加。

### Changed
- **型ヒント互換レイヤー**: `_typing_compat` モジュールを新設し、25ファイル超にわたって型ヒントを整理。Python 3.13/3.14 での `typing_extensions` 依存や互換性課題を吸収できるようになりました。
- **開発体験**: タイプチェックを basedpyright へ全面移行し（pyproject/Makefile/CI/ドキュメント更新）、pre-commit と GitHub Actions を最新の ruff v0.14.9・basedpyright 1.36.1・actions/checkout v6・Python 3.14.2 へ更新。Renovate 設定もプリセット中心に再構成し、保守トラフィックを削減。

### Fixed
- **初期セットアップメッセージ**: `sysup init` 完了時に `sysup update` / `sysup update --list` へ誘導するよう文言を修正。
- **uv.lock の取り扱い**: `.gitignore` から除外してリポジトリに含め、依存ピン留めが誤って外れないようにしました。

## [0.7.1] - 2025-11-05

### Added

- **Python モジュールエントリーポイント**: `__main__.py` 追加
  - `python -m sysup.cli` での実行をサポート

### Fixed

- **セルフアップデート機能**: 無限ループと再実行エラーを修正
  - `uv tool upgrade` の "Nothing to upgrade" メッセージを正しく処理
  - インストール済み `sysup` コマンドを `which` で検索して再実行
  - フォールバック時は `python -m sysup.cli.cli` で実行
- **例外処理**: より具体的な例外型を使用 (`Exception` → `subprocess.TimeoutExpired, OSError`)
- **subprocess.run**: `check=False` パラメータを明示的に指定

### Changed

- **テスト**: `test_self_update.py` を新しい実装に合わせて全面更新（6件の修正）
- **コード品質**: pre-commit フック全てをパス（ruff, basedpyright, bandit, pytest）
- **テストカバレッジ**: 85.81% 維持（目標80%超え、279テスト全て成功）

## [0.7.0] - 2025-11-05

### Added
- **init コマンド**: 対話的セットアップウィザード実装
  - システム環境自動検出
  - パッケージマネージャ選択UI
  - 実行モード（標準/自動実行）選択
  - 詳細設定（ログレベル、並列実行、バックアップ、通知）
  - 設定ファイル自動生成
  - 既存設定の上書き保護
- **Pre-commit 強化**: CI で実行されるすべてのチェックをローカルで実行可能に
  - pytest フック追加（テスト実行）
  - ruff（リント・フォーマット）
  - basedpyright（型チェック）
  - bandit（セキュリティチェック）

### Changed
- **CLI リファクタリング**: cli.py をパッケージ構造に変更
  - src/sysup/cli/__init__.py
  - src/sysup/cli/cli.py
  - src/sysup/cli/init.py
- **ドキュメント更新**: INIT_COMMAND_SPEC.md, CONFIGURATION.md 追加
- **コード品質**: 不要なインポート削除、フォーマット統一

### Fixed
- ruff リント警告の修正
- コードフォーマットの統一

## [0.6.0] - 2025-01-24

### Added
- **セルフアップデート機能**: sysup実行時に自動的に最新版に更新
  - 起動毎に`uv tool upgrade sysup`を実行
  - 更新された場合は自動的に再実行
  - `--no-self-update`オプションでスキップ可能
  - リリース前のpush版にも対応

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
- pre-commit設定強化（ruff, basedpyright, bandit）
- basedpyright strict相当の型チェック設定

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

[Unreleased]: https://github.com/scottlz0310/sysup/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/scottlz0310/sysup/compare/v0.8.2...v0.9.0
[0.8.2]: https://github.com/scottlz0310/sysup/compare/v0.8.1...v0.8.2
[0.8.1]: https://github.com/scottlz0310/sysup/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/scottlz0310/sysup/compare/v0.7.1...v0.8.0
[0.7.1]: https://github.com/scottlz0310/sysup/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/scottlz0310/sysup/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/scottlz0310/sysup/compare/v0.5.2...v0.6.0
[0.5.2]: https://github.com/scottlz0310/sysup/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/scottlz0310/sysup/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/scottlz0310/sysup/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/scottlz0310/sysup/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/scottlz0310/sysup/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/scottlz0310/sysup/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/scottlz0310/sysup/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/scottlz0310/sysup/releases/tag/v0.1.0
