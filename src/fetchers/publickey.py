import feedparser
from datetime import datetime
from typing import List
from .base import NewsFetcher, NewsItem


class PublickeyFetcher(NewsFetcher):
    """PublickeyのRSSフィードからニュースを取得"""

    RSS_URL = "https://www.publickey1.jp/atom.xml"

    @property
    def source_name(self) -> str:
        return "Publickey"

    def fetch(self) -> List[NewsItem]:
        try:
            feed = feedparser.parse(self.RSS_URL)
            news_items = []

            for entry in feed.entries[:20]:
                published = datetime(*entry.published_parsed[:6])
                news_items.append(NewsItem(
                    title=entry.title,
                    url=entry.link,
                    published_date=published,
                    source=self.source_name,
                    description=entry.get('summary', '')
                ))

            return news_items
        except Exception as e:
            print(f"Error fetching from {self.source_name}: {e}")
            return []
