import requests
from typing import List, Dict
from datetime import datetime
from .fetchers.base import NewsItem


class GitHubNotifier:
    """GitHub Issueを作成して日次ニュースを通知"""

    # ソースごとの絵文字マッピング
    SOURCE_EMOJIS = {
        "TechCrunch": "🚀",
        "Hacker News": "📙",
        "ITmedia": "🇯🇵",
        "ZDNet Japan": "📰",
        "日経xTECH": "📈",
        "Publickey": "🔑",
    }

    def __init__(self, github_token: str, repo_owner: str, repo_name: str):
        """
        Args:
            github_token: GitHub Personal Access Token or GITHUB_TOKEN
            repo_owner: リポジトリのオーナー名
            repo_name: リポジトリ名
        """
        self.github_token = github_token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"

    def send_daily_digest(self, news_items: List[Dict]):
        """
        日次ニュースダイジェストをGitHub Issueとして作成
        news_items: NewsItemとその要約・コメントを含む辞書のリスト
        """
        today = datetime.now().strftime('%Y年%m月%d日')

        if not news_items:
            self._create_no_news_issue(today)
            return

        # Issueのタイトルと本文を生成
        title = f"📰 技術ニュースダイジェスト - {today}"
        body = self._build_issue_body(news_items, today)

        # GitHub Issueを作成
        try:
            response = requests.post(
                self.api_url,
                json={
                    "title": title,
                    "body": body,
                    "labels": ["daily-news", "automated"]
                },
                headers={
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=10
            )
            response.raise_for_status()
            issue_url = response.json().get('html_url')
            print(f"Successfully created GitHub Issue: {issue_url}")
            print(f"  ({len(news_items)} news items)")
        except Exception as e:
            print(f"Error creating GitHub Issue: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Response: {e.response.text}")

    def _build_issue_body(self, news_items: List[Dict], today: str) -> str:
        """Issue本文をMarkdownで生成"""
        lines = [
            f"# 📰 本日の技術ニュースダイジェスト",
            f"",
            f"**日付:** {today}  ",
            f"**件数:** {len(news_items)}件",
            f"",
            f"---",
            f""
        ]

        for idx, item in enumerate(news_items, 1):
            news_item = item['news']
            summary = item.get('summary', '要約なし')
            comment = item.get('comment', '')
            emoji = self.SOURCE_EMOJIS.get(news_item.source, "🔗")

            lines.extend([
                f"## {idx}. {news_item.title}",
                f"",
                f"{emoji} **ソース:** {news_item.source}  ",
                f"🔗 **リンク:** {news_item.url}",
                f"",
                f"### 📝 要約",
                f"{summary}",
                f""
            ])

            if comment:
                lines.extend([
                    f"### 💬 コメント",
                    f"> {comment}",
                    f""
                ])

            if idx < len(news_items):
                lines.extend([f"---", f""])

        lines.extend([
            f"---",
            f"",
            f"🤖 *Powered by Claude AI*"
        ])

        return "\n".join(lines)

    def _create_no_news_issue(self, today: str):
        """ニュースが取得できなかった場合のIssue"""
        title = f"ℹ️ 本日のニュース - {today}"
        body = f"""# ℹ️ 本日のニュース

**日付:** {today}

本日は新しいニュースがありませんでした。

---

🤖 *Powered by Claude AI*
"""

        try:
            response = requests.post(
                self.api_url,
                json={
                    "title": title,
                    "body": body,
                    "labels": ["daily-news", "automated", "no-news"]
                },
                headers={
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=10
            )
            response.raise_for_status()
            print(f"Created no-news issue: {response.json().get('html_url')}")
        except Exception as e:
            print(f"Error creating no-news issue: {e}")
