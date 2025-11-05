import json
import os
from typing import List, Set
from datetime import datetime, timedelta
from .fetchers.base import NewsItem


class HistoryManager:
    """過去に通知したニュースのURLを記録・管理するクラス"""

    def __init__(self, history_file: str = "data/history.json"):
        self.history_file = history_file
        self.history = self._load_history()

    def _load_history(self) -> dict:
        """履歴ファイルを読み込み"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
                return {"notified_urls": {}}
        return {"notified_urls": {}}

    def _save_history(self):
        """履歴をファイルに保存"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def is_notified(self, url: str) -> bool:
        """指定されたURLが過去に通知済みかチェック"""
        return url in self.history["notified_urls"]

    def add_notified(self, url: str):
        """通知済みURLを追加"""
        self.history["notified_urls"][url] = datetime.now().isoformat()
        self._save_history()

    def filter_new_news(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """未通知のニュースのみをフィルタリング"""
        return [item for item in news_items if not self.is_notified(item.url)]

    def cleanup_old_entries(self, days: int = 30):
        """
        指定日数より古い履歴エントリを削除
        （データベースが大きくなりすぎないように）
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        notified_urls = self.history["notified_urls"]

        urls_to_remove = []
        for url, date_str in notified_urls.items():
            try:
                date = datetime.fromisoformat(date_str)
                if date < cutoff_date:
                    urls_to_remove.append(url)
            except:
                continue

        for url in urls_to_remove:
            del notified_urls[url]

        if urls_to_remove:
            self._save_history()
            print(f"Cleaned up {len(urls_to_remove)} old history entries")
