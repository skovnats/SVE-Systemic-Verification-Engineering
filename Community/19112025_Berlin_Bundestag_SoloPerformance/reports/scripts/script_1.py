#!/usr/bin/env python3
import os
import requests
from datetime import datetime

API_KEY = os.getenv("YOUTUBE_API_KEY")

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

from datetime import date, timedelta

# Базовая неделя: 2025KW47
BASE_MONDAY = date.fromisocalendar(2025, 47, 1)  # 1 = Monday

def get_week_range_from_k(k: int):
    """
    k = 0  -> 2025KW47
    k = 1  -> следующая неделя
    k = -1 -> предыдущая неделя
    """
    monday = BASE_MONDAY + timedelta(weeks=k)
    sunday = monday + timedelta(days=6)

    year, week, _ = monday.isocalendar()
    kw_label = f"{year}KW{week:02d}"

    published_after = monday.strftime("%Y-%m-%dT00:00:00Z")
    published_before = sunday.strftime("%Y-%m-%dT23:59:59Z")

    return kw_label, published_after, published_before



def search_youtube(
    query: str,
    published_after: str,
    published_before: str,
    max_results: int = 50,
    short_only: bool = False,
):
    """
    query            – строка запроса (ключевые слова)
    published_after  – 'YYYY-MM-DDT00:00:00Z'
    published_before – 'YYYY-MM-DDT00:00:00Z'
    short_only       – если True, пытаемся ловить Shorts (videoDuration=short)
    """
    params = {
        "part": "snippet",
        "type": "video",
        "order": "date",
        "maxResults": max_results,
        "publishedAfter": published_after,
        "publishedBefore": published_before,
        "q": query,
        "key": API_KEY,
    }

    if short_only:
        params["videoDuration"] = "short"  # < 4 минут, часто Shorts

    resp = requests.get(SEARCH_URL, params=params)
    if resp.status_code != 200:
        print("STATUS:", resp.status_code)
        print("BODY:", resp.text)
        resp.raise_for_status()
    data = resp.json()

    results = []
    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        results.append(
            {
                "publishedAt": snippet["publishedAt"],
                "title": snippet["title"],
                "channelTitle": snippet["channelTitle"],
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
        )

    return results


if __name__ == "__main__":
    k = 0  # смещение от 2025KW47; меняешь как хочешь: -2, -1, 0, 1, 2...
    kw_label, PUBLISHED_AFTER, PUBLISHED_BEFORE = get_week_range_from_k(k)

    print(f"Week: {kw_label}")
    print(f"PUBLISHED_AFTER:  {PUBLISHED_AFTER}")
    print(f"PUBLISHED_BEFORE: {PUBLISHED_BEFORE}")

    # дальше используешь PUBLISHED_AFTER / PUBLISHED_BEFORE в запросах
    videos = search_youtube(
        query="тцк",
        published_after=PUBLISHED_AFTER,
        published_before=PUBLISHED_BEFORE,
        max_results_total=MAX_RESULTS_PER_QUERY,
        short_only=SHORT_ONLY,
        region_code=REGION_CODE,
        relevance_language=RELEVANCE_LANGUAGE,
    )

        for v in videos:
            print(f"{v['publishedAt']} | {v['title']} | {v['url']}")
