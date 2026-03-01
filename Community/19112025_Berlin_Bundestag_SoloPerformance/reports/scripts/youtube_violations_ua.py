#!/usr/bin/env python3
import os
import sys
import csv
import requests
import isodate
from typing import List, Dict, Optional
from datetime import date, timedelta

'''
python youtube_violations_ua.py -n
python youtube_violations_ua.py n
'''

API_KEY = os.getenv("YOUTUBE_API_KEY")
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

BASE_MONDAY = date.fromisocalendar(2025, 47, 1)

# === НАСТРОЙКИ ===
QUERIES = [
    "бусификация",
    "тцк",
    "тцк беспредел",
    "хватают людей",
    "ТЦК хватают людей",
    "военкомат хватают людей Украина",
    "побег через границу Украина",
    "бегут через лес Украина военкомат",
]

REGION_CODE = "UA"
RELEVANCE_LANGUAGE = "uk"  # Исправлено: API принимает только один язык
MAX_RESULTS_PER_QUERY = 444
MAX_DURATION_MINUTES = 15.0  # Фильтр длительности

def duration_in_minutes(iso_str: str) -> float:
    try:
        if not iso_str: return 0.0
        return isodate.parse_duration(iso_str).total_seconds() / 60
    except:
        return 9999.0

def get_week_range_from_k(k: int):
    monday = BASE_MONDAY + timedelta(weeks=k)
    sunday = monday + timedelta(days=6)
    year, week, _ = monday.isocalendar()
    return f"{year}KW{week:02d}", monday.strftime("%Y-%m-%dT00:00:00Z"), sunday.strftime("%Y-%m-%dT23:59:59Z")

def get_video_durations(video_ids: List[str]) -> Dict[str, float]:
    """Делает доп. запрос, чтобы получить длительность видео"""
    if not video_ids:
        return {}
    
    params = {
        "part": "contentDetails",
        "id": ",".join(video_ids),
        "key": API_KEY,
    }
    resp = requests.get(VIDEOS_URL, params=params)
    data = resp.json()
    
    dur_map = {}
    for item in data.get("items", []):
        try:
            vid = item["id"]
            iso_dur = item["contentDetails"]["duration"]
            dur_map[vid] = duration_in_minutes(iso_dur)
        except: 
            iso_dur = -1
            dur_map[vid] = -1
            continue
    return dur_map

def search_youtube(query: str, published_after: str, published_before: str) -> List[Dict]:
    results = []
    next_page_token = None

    while len(results) < MAX_RESULTS_PER_QUERY:
        params = {
            "part": "snippet",
            "type": "video",
            "order": "date",
            "maxResults": 50,
            "publishedAfter": published_after,
            "publishedBefore": published_before,
            "q": query,
            "key": API_KEY,
            "regionCode": REGION_CODE,
        }
        if RELEVANCE_LANGUAGE:
            params["relevanceLanguage"] = RELEVANCE_LANGUAGE
        if next_page_token:
            params["pageToken"] = next_page_token

        resp = requests.get(SEARCH_URL, params=params)
        
        if resp.status_code != 200:
            print(f"⚠️ Ошибка API {resp.status_code}: {resp.text}")
            break

        data = resp.json()
        items = data.get("items", [])
        if not items:
            break

        # 1. Собираем ID найденных видео
        batch_ids = [item["id"]["videoId"] for item in items]
        
        # 2. Получаем их длительность (отдельный запрос)
        durations = get_video_durations(batch_ids)

        # 3. Фильтруем и сохраняем
        for item in items:
            vid_id = item["id"]["videoId"]
            minutes = durations.get(vid_id, 9999) # Если не нашли, считаем длинным

            if minutes > MAX_DURATION_MINUTES:
                continue

            snip = item["snippet"]
            results.append({
                "query": query,
                "publishedAt": snip.get("publishedAt", ""),
                "title": snip.get("title", ""),
                "description": snip.get("description", "").replace("\n", " "),
                "channelTitle": snip.get("channelTitle", ""),
                "url": f"https://www.youtube.com/watch?v={vid_id}",
                "duration_min": round(minutes, 2)
            })

            if len(results) >= MAX_RESULTS_PER_QUERY:
                break

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return results

def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    kw_label, p_after, p_before = get_week_range_from_k(K)

    print(f"Week: {kw_label} | {p_after} ... {p_before}")
    output_csv = f"{kw_label}.csv"
    
    all_rows = []
    for q in QUERIES:
        print(f"🔍 '{q}'...", end=" ", flush=True)
        videos = search_youtube(q, p_after, p_before)
        print(f"найдено: {len(videos)}")
        all_rows.extend(videos)

    # Убираем дубли
    unique_rows = {r["url"]: r for r in all_rows}.values()

    fieldnames = ["query", "publishedAt", "duration_min", "title", "channelTitle", "url", "description"]
    
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_rows)

    print(f"\n✅ Готово! Файл: {output_csv} ({len(unique_rows)} строк)")

if __name__ == "__main__":
    main()