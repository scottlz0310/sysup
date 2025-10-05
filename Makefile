.PHONY: bootstrap lint format typecheck test cov security clean install pre-commit

# 開発環境のセットアップ
bootstrap:
	uv venv --python 3.13
	uv pip install -e ".[dev]"
	pre-commit install

# Linter実行
lint:
	uv run ruff check .

# Formatter実行
format:
	uv run ruff format .

# 型チェック
typecheck:
	uv run mypy src/sysup

# テスト実行
test:
	uv run pytest -v

# カバレッジ付きテスト
cov:
	uv run pytest --cov=src --cov-report=term-missing --cov-report=html

# セキュリティチェック
security:
	uv run bandit -r src/sysup -c pyproject.toml

# 全チェック実行
check: lint typecheck test security

# クリーンアップ
clean:
	rm -rf .venv
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf build
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# インストール
install:
	uv pip install -e .

# pre-commitフックのインストール
pre-commit:
	pre-commit install

# pre-commitフックの実行
pre-commit-run:
	pre-commit run --all-files
