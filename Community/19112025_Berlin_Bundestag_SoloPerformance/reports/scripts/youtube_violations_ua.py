#!/usr/bin/env python3
import os
import csv
import requests
from typing import List, Dict, Optional
from datetime import date, timedelta

API_KEY = os.getenv("YOUTUBE_API_KEY")
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

# 🔹 Базовая неделя: 2025KW47 (понедельник)
BASE_MONDAY = date.fromisocalendar(2025, 47, 1)  # 1 = Monday

# 🔹 Смещение по неделям относительно 2025KW47:
#    K = 0  -> 2025KW47
#    K = 1  -> 2025KW48
#    K = -1 -> 2025KW46
K = 0


def get_week_range_from_k(k: int):
    """
    Возвращает:
      kw_label         – строка вида '2025KW47'
      published_after  – начало недели: 'YYYY-MM-DDT00:00:00Z'
      published_before – конец недели:  'YYYY-MM-DDT23:59:59Z'
    """
    monday = BASE_MONDAY + timedelta(weeks=k)
    sunday = monday + timedelta(days=6)

    year, week, _ = monday.isocalendar()
    kw_label = f"{year}KW{week:02d}"

    published_after = monday.strftime("%Y-%m-%dT00:00:00Z")
    published_before = sunday.strftime("%Y-%m-%dT23:59:59Z")

    return kw_label, published_after, published_before


# === НАСТРОЙКИ ПОИСКА ===
QUERIES = [
    "бусификация",
    "тцк",
    "хватают людей",
    "ТЦК хватают людей",
    "военкомат хватают людей Украина",
    "побег через границу Украина",
    "бегут через лес Украина военкомат",
]

REGION_CODE = "UA"          # Украина
RELEVANCE_LANGUAGE = "ru"   # можно сменить на "uk" / "en"
SHORT_ONLY = False          # True -> стараться ловить только короткие видео
MAX_RESULTS_PER_QUERY = 200  # максимум видео на один запрос (с учётом пагинации)


def search_youtube(
    query: str,
    published_after: str,
    published_before: str,
    max_results_total: int = 100,
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
            "maxResults": 50,
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

        if resp.status_code != 200:
            print("STATUS:", resp.status_code)
            print("BODY:", resp.text)
            break

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
    kw_label, published_after, published_before = get_week_range_from_k(K)

    print(f"Week: {kw_label}")
    print(f"PUBLISHED_AFTER:  {published_after}")
    print(f"PUBLISHED_BEFORE: {published_before}")

    output_csv = f"youtube_violations_{kw_label}.csv"
    all_rows: List[Dict] = []

    for q in QUERIES:
        print(f"\nИщу по запросу: {q!r}")
        videos = search_youtube(
            query=q,
            published_after=published_after,
            published_before=published_before,
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

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nГотово. Записано {len(rows)} уникальных видео в файл: {output_csv}")


if __name__ == "__main__":
    main()
