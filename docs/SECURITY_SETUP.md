# セキュリティ機能セットアップガイド

## Secret Scanning有効化手順

GitHubのSecret Scanningを有効化することで、コミット履歴やPRに含まれる機密情報（APIキー、トークン、パスワードなど）を自動検出できます。

### 前提条件

- **Publicリポジトリ**: 無料で利用可能
- **Privateリポジトリ**: GitHub Advanced Security（有料）が必要

### 有効化手順

1. **リポジトリ設定にアクセス**
   ```
   https://github.com/scottlz0310/sysup/settings
   ```

2. **Security & analysisセクションに移動**
   - 左サイドバーの「Security & analysis」をクリック

3. **Secret scanningを有効化**
   - 「Secret scanning」セクションで「Enable」をクリック
   - 「Secret scanning alerts」を有効化

4. **Push protectionを有効化（推奨）**
   - 「Push protection」で「Enable」をクリック
   - これにより、機密情報を含むコミットのpushが自動的にブロックされます

### 確認方法

有効化後、以下で検出結果を確認できます：

```
https://github.com/scottlz0310/sysup/security/secret-scanning
```

### 検出される機密情報の例

- AWS Access Key
- GitHub Personal Access Token
- Google API Key
- Slack Token
- SSH Private Key
- Database Connection String
- など200種類以上のパターン

### 誤検出への対応

誤検出（False Positive）の場合：

1. アラートページで「Close as」→「False positive」を選択
2. `.github/secret_scanning.yml`でカスタムパターンを除外（必要に応じて）

### CI/CDとの統合

Secret Scanningは自動的に以下のタイミングで実行されます：

- コミットのpush時
- Pull Request作成時
- 履歴スキャン（有効化時に過去のコミットも検査）

### 参考リンク

- [GitHub Secret Scanning公式ドキュメント](https://docs.github.com/en/code-security/secret-scanning)
- [Push Protection](https://docs.github.com/en/code-security/secret-scanning/push-protection-for-repositories-and-organizations)

---

## その他のセキュリティ機能

### CodeQL（既に有効化済み）

自動的にコード脆弱性をスキャンします。

確認先：
```
https://github.com/scottlz0310/sysup/security/code-scanning
```

### Dependabot（既に有効化済み）

依存関係の脆弱性を自動検出し、更新PRを作成します。

確認先：
```
https://github.com/scottlz0310/sysup/security/dependabot
```

### Security Policy（既に作成済み）

脆弱性報告方法を定義しています。

参照先：[SECURITY.md](../SECURITY.md)

---

**最終更新**: 2025-10-09
