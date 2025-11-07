import feedparser
from datetime import datetime
from typing import List
from .base import NewsFetcher, NewsItem


class ZDNetFetcher(NewsFetcher):
    """ZDNet JapanのRSSフィードからニュースを取得"""

    RSS_URL = "https://feeds.japan.zdnet.com/rss/zdnet/all.rdf"

    @property
    def source_name(self) -> str:
        return "ZDNet Japan"

    def fetch(self) -> List[NewsItem]:
        try:
            feed = feedparser.parse(self.RSS_URL)
            news_items = []

            for entry in feed.entries[:20]:
                # published_parsed がない場合は updated_parsed または現在時刻を使用
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])
                else:
                    published = datetime.now()

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
