# 貢献ガイド

sysupへの貢献に興味を持っていただきありがとうございます！

## 目次

- [開発環境のセットアップ](#開発環境のセットアップ)
- [コーディング規約](#コーディング規約)
- [新しいUpdaterの追加](#新しいupdaterの追加)
- [テストの書き方](#テストの書き方)
- [プルリクエストのガイドライン](#プルリクエストのガイドライン)

## 開発環境のセットアップ

### 前提条件

- Python 3.11以上
- uv（推奨）または pip
- Git

### セットアップ手順

```bash
# リポジトリをクローン
git clone https://github.com/scottlz0310/sysup.git
cd sysup

# 仮想環境を作成
uv venv --python 3.13

# 開発用依存関係を含めてインストール
uv pip install -e ".[dev]"

# 動作確認
uv run sysup --help
```

## コーディング規約

### Python スタイルガイド

- **PEP 8**に準拠
- 行長: 120文字まで
- インデント: スペース4つ

### ツール

#### Ruff（Linter/Formatter）

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# 自動修正
uv run ruff check --fix .
```

#### Mypy（型チェック）

```bash
uv run mypy .
```

### 型ヒント

全ての関数に型ヒントを付けてください：

```python
def get_name(self) -> str:
    """表示名を返す"""
    return "Example"

def perform_update(self) -> bool:
    """更新実行"""
    return True
```

### Docstring

全ての公開関数・クラスにDocstringを付けてください：

```python
def example_function(param: str) -> bool:
    """
    関数の説明

    Args:
        param: パラメータの説明

    Returns:
        成功した場合True、失敗した場合False
    """
    pass
```

## 新しいUpdaterの追加

### 1. Updaterファイルの作成

`src/sysup/updaters/`に新しいファイルを作成します：

```python
# src/sysup/updaters/example.py
"""Exampleパッケージマネージャupdater"""

import subprocess
from typing import Optional

from .base import BaseUpdater


class ExampleUpdater(BaseUpdater):
    """Exampleパッケージマネージャupdater"""

    def get_name(self) -> str:
        return "Example"

    def is_available(self) -> bool:
        return self.command_exists("example")

    def perform_update(self) -> bool:
        """Example更新実行"""
        name = self.get_name()

        if not self.is_available():
            self.logger.info(f"{name} がインストールされていません - スキップ")
            return True

        try:
            self.logger.info(f"{name} を更新中...")
            self.run_command(["example", "update"])
            self.logger.success(f"{name} 更新完了")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.warning(f"{name} 更新で問題が発生しました: {e}")
            return False
        except Exception as e:
            self.logger.error(f"{name} 更新中に予期しないエラー: {e}")
            return False
```

### 2. 設定ファイルに追加

`config/sysup.toml.example`に設定項目を追加：

```toml
[updaters]
example = true  # 新しいupdater
```

### 3. 設定クラスに追加

`src/sysup/core/config.py`の`UpdaterConfig`に追加：

```python
class UpdaterConfig(BaseModel):
    """各updaterの設定"""
    example: bool = True  # 新しいupdater
```

### 4. CLIに統合

`src/sysup/cli.py`にインポートと登録を追加：

```python
from .updaters.example import ExampleUpdater

# show_available_updatersに追加
updaters = [
    ...
    ("example", ExampleUpdater(logger, config.general.dry_run)),
]

# run_updatesに追加
if config.is_updater_enabled("example"):
    updaters.append(("example", ExampleUpdater(logger, config.general.dry_run)))
```

### 5. テストの作成

`tests/test_updaters/test_example.py`を作成：

```python
"""Exampleupdaterのテスト"""

import pytest
from sysup.updaters.example import ExampleUpdater
from sysup.core.logging import SysupLogger


def test_get_name():
    """名前取得のテスト"""
    logger = SysupLogger(Path("/tmp"), "INFO")
    updater = ExampleUpdater(logger, dry_run=True)
    assert updater.get_name() == "Example"
```

## テストの書き方

### テストの実行

```bash
# 全テスト実行
uv run pytest

# カバレッジ付き
uv run pytest --cov=src --cov-report=term-missing

# 特定のテストのみ
uv run pytest tests/test_config.py
```

### テストの構造

```python
def test_function_name():
    """テストの説明"""
    # Arrange（準備）
    expected = "expected_value"

    # Act（実行）
    result = function_to_test()

    # Assert（検証）
    assert result == expected
```

## プルリクエストのガイドライン

### ブランチ戦略

- `main`: 安定版
- `feature/*`: 新機能
- `fix/*`: バグ修正
- `docs/*`: ドキュメント更新

### コミットメッセージ

Conventional Commitsに従ってください：

```
feat: 新機能の追加
fix: バグ修正
docs: ドキュメント更新
refactor: リファクタリング
test: テスト追加・修正
chore: ビルド・ツール関連
```

例：
```
feat: Exampleupdaterを追加

- ExampleUpdater実装
- 設定ファイルに追加
- テスト追加
```

### プルリクエストの作成

1. **Forkとクローン**
   ```bash
   git clone https://github.com/YOUR_USERNAME/sysup.git
   ```

2. **ブランチ作成**
   ```bash
   git checkout -b feature/add-example-updater
   ```

3. **変更とコミット**
   ```bash
   git add .
   git commit -m "feat: Exampleupdaterを追加"
   ```

4. **プッシュ**
   ```bash
   git push origin feature/add-example-updater
   ```

5. **プルリクエスト作成**
   - GitHubでプルリクエストを作成
   - 変更内容を明確に説明
   - 関連するIssueがあればリンク

### プルリクエストのチェックリスト

- [ ] コードがPEP 8に準拠している
- [ ] 型ヒントが付いている
- [ ] Docstringが付いている
- [ ] テストが追加されている
- [ ] テストが全て通る
- [ ] Ruffでlint/formatが通る
- [ ] Mypyで型チェックが通る
- [ ] ドキュメントが更新されている（必要な場合）

## コードレビュー

プルリクエストは以下の観点でレビューされます：

- **機能性**: 意図した通りに動作するか
- **コード品質**: 読みやすく保守しやすいか
- **テスト**: 適切にテストされているか
- **ドキュメント**: 必要なドキュメントが更新されているか
- **パフォーマンス**: 不要な処理がないか

## 質問・サポート

- **Issue**: バグ報告や機能要望は[GitHub Issues](https://github.com/scottlz0310/sysup/issues)へ
- **Discussion**: 質問や議論は[GitHub Discussions](https://github.com/scottlz0310/sysup/discussions)へ

## ライセンス

貢献されたコードはMITライセンスの下で公開されます。

## 謝辞

貢献していただきありがとうございます！
