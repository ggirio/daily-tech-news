#!/usr/bin/env python3
"""
Daily Tech News Bot
毎日技術ニュースを収集し、Claude AIで分析してSlackに通知する
"""
import os
import sys
from dotenv import load_dotenv

from src.fetchers import (
    TechCrunchFetcher,
    HackerNewsFetcher,
    ITmediaFetcher,
    ZDNetFetcher,
    NikkeiXTechFetcher,
    PublickeyFetcher
)
from src.ai_analyzer import AIAnalyzer
from src.history_manager import HistoryManager
from src.slack_notifier import SlackNotifier


def main():
    """メイン処理"""
    # 環境変数を読み込み
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    if not api_key:
        print("Error: ANTHROPIC_API_KEY is not set")
        sys.exit(1)

    if not webhook_url:
        print("Error: SLACK_WEBHOOK_URL is not set")
        sys.exit(1)

    print("=" * 60)
    print("Daily Tech News Bot - Starting")
    print("=" * 60)

    # 各コンポーネントを初期化
    fetchers = [
        TechCrunchFetcher(),
        HackerNewsFetcher(),
        ITmediaFetcher(),
        ZDNetFetcher(),
        NikkeiXTechFetcher(),
        PublickeyFetcher()
    ]

    analyzer = AIAnalyzer(api_key)
    history = HistoryManager()
    notifier = SlackNotifier(webhook_url)

    # 古い履歴をクリーンアップ（30日より古いものを削除）
    history.cleanup_old_entries(days=30)

    # Step 1: 全サイトからニュースを収集
    print("\n[Step 1] Fetching news from all sources...")
    all_news = []
    for fetcher in fetchers:
        print(f"  - Fetching from {fetcher.source_name}...", end=" ")
        try:
            news = fetcher.fetch()
            all_news.extend(news)
            print(f"✓ ({len(news)} items)")
        except Exception as e:
            print(f"✗ Error: {e}")

    print(f"\nTotal fetched: {len(all_news)} news items")

    # Step 2: 既に通知済みのニュースを除外
    print("\n[Step 2] Filtering out already notified news...")
    new_news = history.filter_new_news(all_news)
    print(f"New news items: {len(new_news)} (filtered out {len(all_news) - len(new_news)} duplicates)")

    if not new_news:
        print("\n[Result] No new news to report today.")
        notifier.send_daily_digest([])
        return

    # Step 3: Claude AIで話題性の高いニュースを選定（最大5件）
    print("\n[Step 3] Ranking news with Claude AI...")
    top_news = analyzer.rank_news(new_news, top_n=5)
    print(f"Selected top {len(top_news)} news items")

    # Step 4: 各ニュースを要約してコメントを生成
    print("\n[Step 4] Generating summaries and comments...")
    news_with_analysis = []

    for idx, news_item in enumerate(top_news, 1):
        print(f"  [{idx}/{len(top_news)}] Analyzing: {news_item.title[:50]}...")
        try:
            analysis = analyzer.summarize_and_comment(news_item)
            news_with_analysis.append({
                'news': news_item,
                'summary': analysis['summary'],
                'comment': analysis['comment']
            })
            # 履歴に追加
            history.add_notified(news_item.url)
        except Exception as e:
            print(f"    Error analyzing news: {e}")
            # エラーでも記事自体は送信
            news_with_analysis.append({
                'news': news_item,
                'summary': news_item.description[:200] if news_item.description else "詳細は記事をご覧ください。",
                'comment': "注目のニュースです!"
            })
            history.add_notified(news_item.url)

    # Step 5: Slackに通知
    print("\n[Step 5] Sending digest to Slack...")
    notifier.send_daily_digest(news_with_analysis)

    print("\n" + "=" * 60)
    print(f"Daily Tech News Bot - Completed ({len(news_with_analysis)} news sent)")
    print("=" * 60)


if __name__ == "__main__":
    main()
