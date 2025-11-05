import requests
from datetime import datetime
from typing import List
from .base import NewsFetcher, NewsItem


class HackerNewsFetcher(NewsFetcher):
    """Hacker NewsのAPIからニュースを取得"""

    API_BASE = "https://hacker-news.firebaseio.com/v0"

    @property
    def source_name(self) -> str:
        return "Hacker News"

    def fetch(self) -> List[NewsItem]:
        try:
            # トップストーリーのIDを取得
            response = requests.get(f"{self.API_BASE}/topstories.json", timeout=10)
            story_ids = response.json()[:30]  # 上位30件

            news_items = []
            for story_id in story_ids:
                story_response = requests.get(f"{self.API_BASE}/item/{story_id}.json", timeout=10)
                story = story_response.json()

                if story and story.get('type') == 'story' and story.get('url'):
                    published = datetime.fromtimestamp(story['time'])
                    news_items.append(NewsItem(
                        title=story['title'],
                        url=story['url'],
                        published_date=published,
                        source=self.source_name,
                        description=story.get('text', ''),
                        score=story.get('score', 0)
                    ))

            return news_items
        except Exception as e:
            print(f"Error fetching from {self.source_name}: {e}")
            return []
