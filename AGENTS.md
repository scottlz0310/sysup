# Repository Guidelines

## 日本語でのやり取りとドキュメント
- 本リポジトリでのやり取り（Issue/PR/レビュー/コメント）は日本語を原則とします。
- 新規・更新ドキュメントは日本語で作成してください（コード内のAPI名やCLI出力は原文のままで可）。

## Project Structure & Module Organization
- `src/sysup/` がパッケージルート。`cli/` はCLIエントリポイント、`core/` は設定・ログ・実行基盤、`updaters/` はパッケージマネージャ連携。
- `tests/` はpytestテスト一式（例: `tests/test_updaters/`）。
- `config/` にサンプル設定 `config/sysup.toml.example`、`docs/` に利用/貢献ガイド。
- `archive/` は過去資料であり実行コードには含めない。

## Build, Test, and Development Commands
- `make bootstrap`: `uv` 仮想環境作成、開発依存の導入、pre-commitの導入。
- `make lint` / `make format`: Ruffによるlint/format。
- `make typecheck`: basedpyrightによる型チェック。
- `make test` / `make cov`: pytest実行（`--cov=src` でカバレッジ）。
- `make security`: banditによるセキュリティスキャン。
- `make pre-commit-run`: 全pre-commitフック実行。
- 直実行の例: `uv run pytest`, `uv run ruff check .`, `uv run ruff format .`, `uv run basedpyright`。

## Coding Style & Naming Conventions
- PEP 8準拠、インデントはスペース4、行長は120文字。
- Ruffで整形（ダブルクォート）とlintを実施。
- 全関数に型ヒント、公開APIにはGoogleスタイルDocstringを必須。
- テストの命名: `tests/test_*.py`, `Test*`, `test_*`。
- セッション完了時はコード品質をチェックしてからコミット。

## Testing Guidelines
- フレームワークはpytest（厳格設定は `pyproject.toml` を参照）。
- カバレッジ閾値は80%以上（`pytest-cov` で強制）。
- Updaterの新規テストは `tests/test_updaters/` に追加し、挙動中心で記述。

## Commit & Pull Request Guidelines
- コミットメッセージはConventional Commits（例: `feat:`, `fix:`, `chore(pre-commit):`, `test:`）。
- ブランチ名は `feature/*`, `fix/*`, `docs/*`。`main` は安定版。
- PRは変更内容の説明、関連Issueへのリンク、テスト/ドキュメント更新の有無を明記。最低限 lint/typecheck/test を実行（`make check` 推奨）。

## Security & Configuration Tips
- 設定ファイルは `~/.config/sysup/sysup.toml`。`config/sysup.toml.example` を起点に作成。
- 脆弱性報告は `SECURITY.md` の手順に従う。
