from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime


class NewsItem:
    """ニュース記事を表すデータクラス"""
    def __init__(self, title: str, url: str, published_date: datetime,
                 source: str, description: str = "", score: int = 0):
        self.title = title
        self.url = url
        self.published_date = published_date
        self.source = source
        self.description = description
        self.score = score  # サイト固有のスコア（HNのポイントなど）

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "url": self.url,
            "published_date": self.published_date.isoformat(),
            "source": self.source,
            "description": self.description,
            "score": self.score
        }


class NewsFetcher(ABC):
    """ニュースフェッチャーの基底クラス"""

    @abstractmethod
    def fetch(self) -> List[NewsItem]:
        """ニュースを取得する"""
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """ソース名を返す"""
        pass
