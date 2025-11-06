import os
from typing import List, Dict
from anthropic import AnthropicBedrock
from .fetchers.base import NewsItem


class AIAnalyzer:
    """Claude APIを使ってニュースを分析・要約するクラス"""

    def __init__(self, api_key: str):
        # 環境変数でBedrockプロキシが指定されている場合はそちらを使う
        use_bedrock = os.getenv("CLAUDE_CODE_USE_BEDROCK") == "1"
        bedrock_base_url = os.getenv("ANTHROPIC_BEDROCK_BASE_URL")

        if use_bedrock and bedrock_base_url:
            # LINE社内Bedrockプロキシを使用
            self.client = AnthropicBedrock(
                aws_access_key=os.getenv("AWS_ACCESS_KEY_ID", "anything_is_fine"),
                aws_secret_key=os.getenv("AWS_SECRET_ACCESS_KEY", "anything_is_fine"),
                aws_session_token=api_key,  # セッショントークンをここに渡す
                aws_region=os.getenv("AWS_REGION", "us-east-1"),
                base_url=bedrock_base_url
            )
        else:
            # 通常のAnthropic APIを使用
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)

    def rank_news(self, news_items: List[NewsItem], top_n: int = 5) -> List[NewsItem]:
        """
        全ニュースをClaude AIに評価させて、話題性の高い上位N件を選定
        """
        if not news_items:
            return []

        # ニュース情報を文字列化
        news_list_text = self._format_news_for_ranking(news_items)

        prompt = f"""以下は本日収集した技術ニュースのリストです。
これらの中から、ソフトウェア開発者にとって最も話題性が高く、重要と思われるニュース記事を{top_n}件選んでください。

選定基準:
- 技術トレンドとして注目されているか
- ソフトウェア開発に影響を与える内容か
- 業界で話題になっている可能性が高いか
- 新規性や革新性があるか
- 日本語記事を優先するが、英語でも重要な内容であれば含める

{news_list_text}

選んだニュースのインデックス番号を、重要度の高い順にJSON形式で返してください。
フォーマット: {{"selected_indices": [1, 5, 12, ...]}}
"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # レスポンスからインデックスを抽出
            import json
            response_text = message.content[0].text

            # JSONブロックを抽出（```json ... ``` の場合も対応）
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            result = json.loads(response_text)
            selected_indices = result.get("selected_indices", [])

            # インデックスに対応するニュースを返す
            selected_news = []
            for idx in selected_indices[:top_n]:
                if 0 <= idx < len(news_items):
                    selected_news.append(news_items[idx])

            return selected_news

        except Exception as e:
            print(f"Error ranking news with AI: {e}")
            # フォールバック: 最初のN件を返す
            return news_items[:top_n]

    def summarize_and_comment(self, news_item: NewsItem) -> Dict[str, str]:
        """
        ニュース記事を2-3行で要約し、ユーモアある一言コメントを生成
        """
        prompt = f"""以下のニュース記事を分析してください:

タイトル: {news_item.title}
URL: {news_item.url}
ソース: {news_item.source}
説明: {news_item.description[:500]}

このニュースについて以下を生成してください:
1. 要約: 2-3行で記事の内容を簡潔にまとめる
2. コメント: ユーモアを含んだ一言コメント（軽いツッコミや面白い視点）

JSON形式で返してください:
{{"summary": "要約文", "comment": "コメント文"}}
"""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            response_text = message.content[0].text

            # JSONブロックを抽出
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            result = json.loads(response_text)

            return {
                "summary": result.get("summary", news_item.description[:200]),
                "comment": result.get("comment", "これは注目ですね!")
            }

        except Exception as e:
            print(f"Error summarizing news with AI: {e}")
            return {
                "summary": news_item.description[:200] if news_item.description else "詳細は記事をご覧ください。",
                "comment": "チェックしておきたいニュースです!"
            }

    def _format_news_for_ranking(self, news_items: List[NewsItem]) -> str:
        """ニュースリストをテキスト形式にフォーマット"""
        formatted = []
        for idx, item in enumerate(news_items):
            formatted.append(
                f"[{idx}] タイトル: {item.title}\n"
                f"    ソース: {item.source}\n"
                f"    URL: {item.url}\n"
                f"    日時: {item.published_date.strftime('%Y-%m-%d %H:%M')}\n"
                f"    説明: {item.description[:200]}...\n"
            )
        return "\n".join(formatted)
