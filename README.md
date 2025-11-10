# Daily Tech News Bot

毎日技術ニュースを収集し、Claude AIで分析してGitHub Issueに通知するボットです。

## 特徴

- 複数の技術ニュースサイトから自動収集（TechCrunch, Hacker News, ITmedia, ZDNet Japan, 日経xTECH, Publickey）
- Claude AIによる話題性の評価と記事選定
- 2-3行の簡潔な要約とユーモアあるコメント生成
- 重複ニュースの自動除外
- GitHub Issueでのリッチな通知（Markdown形式）
- GitHub Actionsで平日朝9時に自動実行

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-username/daily-tech-news.git
cd daily-tech-news
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env.example`をコピーして`.env`を作成し、必要な値を設定します:

```bash
cp .env.example .env
```

`.env`ファイルを編集:

```env
ANTHROPIC_API_KEY=your_claude_api_key_here
GITHUB_TOKEN=your_github_token_here
GITHUB_REPOSITORY=owner/repo
```

#### Claude API キーの取得方法

1. [Anthropic Console](https://console.anthropic.com/)にアクセス
2. アカウントを作成またはログイン
3. API Keysページで新しいキーを生成
4. 生成されたキーを`.env`の`ANTHROPIC_API_KEY`に設定

#### GitHub Tokenの取得方法（ローカル実行用）

1. [GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens)にアクセス
2. "Generate new token" → "Generate new token (classic)"を選択
3. Note（説明）を入力（例: "Daily Tech News Bot"）
4. "repo"スコープにチェック
5. "Generate token"をクリック
6. 生成されたトークンを`.env`の`GITHUB_TOKEN`に設定
7. `GITHUB_REPOSITORY`には`owner/repo`形式でリポジトリを指定（例: `your-username/daily-tech-news`）

**注意**: GitHub Actionsでは自動的に`GITHUB_TOKEN`が利用できるため、ローカルでのテスト実行時のみPersonal Access Tokenが必要です。

### 4. ローカルでのテスト実行

```bash
python main.py
```

## ローカルcronでの自動実行設定（推奨）

**注意**: 社内のBedrockプロキシは社外（GitHub Actions）からアクセスできないため、ローカルのcronで実行する必要があります。

### 1. cron実行スクリプトの確認

既に `/tmp/cron_job.sh` にcron実行用のスクリプトがあります:

```bash
#!/bin/bash
cd /Users/kkatagir/IdeaProjects/test/daily-tech-news
/Users/kkatagir/.pyenv/versions/3.12.4/bin/python main.py >> logs/cron.log 2>&1
```

### 2. ログディレクトリの作成

```bash
mkdir -p logs
```

### 3. crontabの設定

現在の設定（6時間ごとに実行）:
```bash
0 */6 * * * /bin/bash /tmp/cron_job.sh
```

設定を確認:
```bash
crontab -l
```

設定を編集する場合:
```bash
crontab -e
```

### 4. 実行スケジュールの変更例

```bash
# 6時間ごと（0:00, 6:00, 12:00, 18:00）
0 */6 * * * /bin/bash /tmp/cron_job.sh

# 平日の午前9時のみ
0 9 * * 1-5 /bin/bash /tmp/cron_job.sh

# 毎日午前9時
0 9 * * * /bin/bash /tmp/cron_job.sh
```

### 5. ログの確認

```bash
tail -f logs/cron.log
```

## 実行スケジュール

- **自動実行**: 6時間ごと（0:00, 6:00, 12:00, 18:00）
- **手動実行**: `python main.py` でいつでも実行可能
- **ログ確認**: `logs/cron.log` で実行履歴を確認可能

## プロジェクト構成

```
daily-tech-news/
├── .github/
│   └── workflows/
│       └── daily-news.yml      # GitHub Actionsワークフロー
├── src/
│   ├── fetchers/
│   │   ├── __init__.py
│   │   ├── base.py             # フェッチャーの基底クラス
│   │   ├── techcrunch.py       # TechCrunchフェッチャー
│   │   ├── hackernews.py       # Hacker Newsフェッチャー
│   │   ├── itmedia.py          # ITmediaフェッチャー
│   │   ├── zdnet.py            # ZDNet Japanフェッチャー
│   │   ├── nikkei_xtech.py     # 日経xTECHフェッチャー
│   │   └── publickey.py        # Publickeyフェッチャー
│   ├── ai_analyzer.py          # Claude AI分析・要約
│   ├── history_manager.py      # 履歴管理
│   └── github_notifier.py      # GitHub Issue通知
├── data/
│   └── history.json            # 通知済みニュースの履歴
├── main.py                     # メインスクリプト
├── requirements.txt            # Python依存関係
├── .env.example                # 環境変数のサンプル
├── .gitignore
└── README.md
```

## 動作フロー

1. **ニュース収集**: 各サイトのRSS/APIから最新ニュースを取得
2. **重複チェック**: 過去に通知済みのニュースを除外
3. **AI評価**: Claude AIが話題性を評価して上位5件を選定
4. **要約生成**: 各ニュースを2-3行で要約し、ユーモアあるコメントを生成
5. **GitHub Issue作成**: Markdown形式でリッチなニュースダイジェストIssueを作成
6. **履歴更新**: 通知したニュースをhistory.jsonに記録

## カスタマイズ

### ニュースソースの追加

`src/fetchers/`に新しいフェッチャークラスを追加し、`main.py`の`fetchers`リストに追加します。

### 通知件数の変更

`main.py`の`analyzer.rank_news(new_news, top_n=5)`の`top_n`パラメータを変更します。

### 実行時間の変更

`.github/workflows/daily-news.yml`のcron設定を変更します（UTC時間で指定）。

例: 午前10時(JST) = 午前1時(UTC)
```yaml
- cron: '0 1 * * 1-5'
```

## トラブルシューティング

### ニュースが取得できない

- 各サイトのRSS/APIのURLが変更されていないか確認
- ネットワーク接続を確認
- フェッチャーのタイムアウト設定を調整

### Claude APIエラー

- APIキーが正しく設定されているか確認
- APIの利用制限に達していないか確認
- [Anthropic Console](https://console.anthropic.com/)でアカウント状況を確認

### GitHub Issueが作成されない

- `GITHUB_TOKEN`の権限が正しく設定されているか確認（Settings > Actions > General > Workflow permissions）
- リポジトリ名が正しいか確認（`owner/repo`形式）
- Actions実行ログでエラーメッセージを確認

### GitHub Actionsが実行されない

- リポジトリのActionsが有効になっているか確認
- cron設定がUTC時間で正しいか確認
- Secretsが正しく設定されているか確認（`ANTHROPIC_API_KEY`のみ）

## ライセンス

MIT License

## 貢献

Issue やPull Requestを歓迎します！
