#!/usr/bin/env python3
import os
import csv
import requests
from typing import List, Dict, Optional

API_KEY = os.getenv("YOUTUBE_API_KEY")

# === НАСТРОЙКИ ПОИСКА ===
PUBLISHED_AFTER = "2025-11-10T00:00:00Z"   # начало диапазона (UTC)
PUBLISHED_BEFORE = "2025-11-16T23:59:00Z"  # конец диапазона (UTC)

QUERIES = [
    "бусификация",
    "тцк",
    "хватают людей",
    "ТЦК хватают людей",
    "военкомат хватает людей",
    "военкомат хватают людей Украина",
    "побег через границу Украина",
    "бегут через лес Украина военкомат",
]

REGION_CODE = None # "UA"        # Украина
RELEVANCE_LANGUAGE = None # "ru"  # или "uk", или None

SHORT_ONLY = False        # True -> стараться ловить только короткие видео (похожи на шортсы)
MAX_RESULTS_PER_QUERY = 200  # общее кол-во видео на один запрос (будет пагинация)
OUTPUT_CSV = "youtube_violations_ua.csv"

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


def search_youtube(
    query: str,
    published_after: str,
    published_before: str,
    max_results_total: int = 1111,
    short_only: bool = False,
    region_code: Optional[str] = None,
    relevance_language: Optional[str] = None,
) -> List[Dict]:
    results: List[Dict] = []
    next_page_token: Optional[str] = None

    while True:
        if len(results) >= max_results_total:
            break

        params = {
            "part": "snippet",
            "type": "video",
            "order": "date",
            "maxResults": 50,  # максимум за один запрос
            "publishedAfter": published_after,
            "publishedBefore": published_before,
            "q": query,
            "key": API_KEY,
        }

        if short_only:
            params["videoDuration"] = "short"

        if region_code:
            params["regionCode"] = region_code

        if relevance_language:
            params["relevanceLanguage"] = relevance_language

        if next_page_token:
            params["pageToken"] = next_page_token

        resp = requests.get(SEARCH_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            snip = item["snippet"]
            results.append(
                {
                    "query": query,
                    "publishedAt": snip.get("publishedAt", ""),
                    "title": snip.get("title", ""),
                    "description": snip.get("description", ""),
                    "channelTitle": snip.get("channelTitle", ""),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                }
            )

            if len(results) >= max_results_total:
                break

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return results


def main():
    all_rows: List[Dict] = []

    for q in QUERIES:
        print(f"Ищу по запросу: {q!r}")
        videos = search_youtube(
            query=q,
            published_after=PUBLISHED_AFTER,
            published_before=PUBLISHED_BEFORE,
            max_results_total=MAX_RESULTS_PER_QUERY,
            short_only=SHORT_ONLY,
            region_code=REGION_CODE,
            relevance_language=RELEVANCE_LANGUAGE,
        )
        print(f"  найдено: {len(videos)} видео")
        all_rows.extend(videos)

    # Убираем дубли (по URL)
    unique = {}
    for row in all_rows:
        unique[row["url"]] = row
    rows = list(unique.values())

    fieldnames = [
        "query",
        "publishedAt",
        "title",
        "channelTitle",
        "url",
        "description",
    ]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nГотово. Записано {len(rows)} уникальных видео в файл: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
