import requests
from typing import List, Dict
from datetime import datetime
from .fetchers.base import NewsItem


class SlackNotifier:
    """Slack Block Kitを使ってリッチな通知を送信"""

    # ソースごとの絵文字マッピング
    SOURCE_EMOJIS = {
        "TechCrunch": ":rocket:",
        "Hacker News": ":orange_book:",
        "ITmedia": ":jp:",
        "ZDNet Japan": ":newspaper:",
        "日経xTECH": ":chart_with_upwards_trend:",
        "Publickey": ":key:",
    }

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_daily_digest(self, news_items: List[Dict]):
        """
        日次ニュースダイジェストをSlackに送信
        news_items: NewsItemとその要約・コメントを含む辞書のリスト
        """
        if not news_items:
            self._send_no_news_message()
            return

        blocks = self._build_header_block()

        for idx, item in enumerate(news_items, 1):
            news_item = item['news']
            summary = item.get('summary', '要約なし')
            comment = item.get('comment', '')

            blocks.extend(self._build_news_block(idx, news_item, summary, comment))
            # ニュース間の区切り
            if idx < len(news_items):
                blocks.append({"type": "divider"})

        blocks.extend(self._build_footer_block())

        payload = {
            "blocks": blocks
        }

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            print(f"Successfully sent digest to Slack ({len(news_items)} news items)")
        except Exception as e:
            print(f"Error sending to Slack: {e}")

    def _build_header_block(self) -> List[Dict]:
        """ヘッダーブロックを生成"""
        today = datetime.now().strftime('%Y年%m月%d日')
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f":newspaper: 本日の技術ニュースダイジェスト",
                    "emoji": True
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f":calendar: {today} | 今日の注目ニュースをお届けします"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]

    def _build_news_block(self, index: int, news_item: NewsItem,
                          summary: str, comment: str) -> List[Dict]:
        """個別ニュースのブロックを生成"""
        emoji = self.SOURCE_EMOJIS.get(news_item.source, ":link:")

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{index}. <{news_item.url}|{news_item.title}>*\n{emoji} _{news_item.source}_"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":memo: *要約*\n{summary}"
                }
            }
        ]

        if comment:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f":speech_balloon: _{comment}_"
                    }
                ]
            })

        return blocks

    def _build_footer_block(self) -> List[Dict]:
        """フッターブロックを生成"""
        return [
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": ":robot_face: Powered by Claude AI | 良い一日を!"
                    }
                ]
            }
        ]

    def _send_no_news_message(self):
        """ニュースが取得できなかった場合のメッセージ"""
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": ":information_source: 本日のニュース",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "本日は新しいニュースがありませんでした。"
                    }
                }
            ]
        }

        try:
            requests.post(self.webhook_url, json=payload, timeout=10)
        except Exception as e:
            print(f"Error sending no-news message to Slack: {e}")
