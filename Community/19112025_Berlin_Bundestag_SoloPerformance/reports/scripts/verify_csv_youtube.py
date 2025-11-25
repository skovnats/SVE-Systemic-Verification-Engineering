#!/usr/bin/env python3
import csv
import requests
from urllib.parse import urlparse, parse_qs
from typing import List, Dict

API_KEY = "ВСТАВЬ_СВОЙ_API_KEY"

INPUT_CSV = "youtube_violations_ua.csv"
OUTPUT_CSV = "youtube_violations_ua_verified.csv"

VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def extract_video_id(url: str) -> str:
    """
    Поддерживает:
    - https://www.youtube.com/watch?v=ID
    - https://youtu.be/ID
    - с параметрами &t= и т.п.
    """
    parsed = urlparse(url)

    # стандартный формат ?v=ID
    qs = parse_qs(parsed.query).get("v")
    if qs:
        return qs[0]

    # короткий формат youtu.be/ID
    if parsed.netloc in ("youtu.be", "www.youtu.be"):
        return parsed.path.strip("/")

    return ""


def chunk_list(lst: List[str], size: int) -> List[List[str]]:
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def fetch_videos_metadata(video_ids: List[str]) -> Dict[str, Dict]:
    """
    Запрашиваем метаданные для списка ID (до 50 за раз).
    Возвращает dict: video_id -> данные.
    """
    result: Dict[str, Dict] = {}

    for chunk in chunk_list(video_ids, 50):
        params = {
            "part": "snippet,contentDetails,statistics,status",
            "id": ",".join(chunk),
            "key": API_KEY,
        }

        resp = requests.get(VIDEOS_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("items", []):
            vid = item["id"]
            result[vid] = item

    return result


def main():
    rows_input = []

    # 1) читаем входной CSV
    with open(INPUT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get("url", "").strip()
            vid = extract_video_id(url)
            row["video_id"] = vid
            rows_input.append(row)

    # отфильтруем только те, у кого есть ID
    video_ids = sorted({r["video_id"] for r in rows_input if r["video_id"]})

    print(f"Всего видео с ID: {len(video_ids)}")
    if not video_ids:
        print("Нет валидных видео ID. Проверь INPUT_CSV.")
        return

    # 2) дергаем YouTube Data API
    metadata_by_id = fetch_videos_metadata(video_ids)

    # 3) готовим выходной CSV
    # поля исходного CSV + поля проверки
    base_fields = list(rows_input[0].keys())
    extra_fields = [
        "found_in_api",
        "uploadStatus",
        "privacyStatus",
        "license",
        "duration",
        "definition",
        "viewCount",
        "likeCount",
        "dislikeCount",  # сейчас не отдается публично, останется пустым
    ]
    fieldnames = base_fields + extra_fields

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows_input:
            vid = row.get("video_id", "")
            meta = metadata_by_id.get(vid)

            out = dict(row)  # копия исходной строки

            if not vid or not meta:
                # не найдено / удалено / приватное
                out.update(
                    {
                        "found_in_api": 0,
                        "uploadStatus": "",
                        "privacyStatus": "",
                        "license": "",
                        "duration": "",
                        "definition": "",
                        "viewCount": "",
                        "likeCount": "",
                        "dislikeCount": "",
                    }
                )
            else:
                snippet = meta.get("snippet", {})
                content = meta.get("contentDetails", {})
                stats = meta.get("statistics", {})
                status = meta.get("status", {})

                out.update(
                    {
                        "found_in_api": 1,
                        "uploadStatus": status.get("uploadStatus", ""),
                        "privacyStatus": status.get("privacyStatus", ""),
                        "license": status.get("license", ""),
                        "duration": content.get("duration", ""),  # ISO8601 (PT1M23S)
                        "definition": content.get("definition", ""),
                        "viewCount": stats.get("viewCount", ""),
                        "likeCount": stats.get("likeCount", ""),
                        "dislikeCount": stats.get("dislikeCount", ""),
                    }
                )

                # при желании можно перезаписать заголовок/описание более свежими
                # out["title"] = snippet.get("title", row.get("title", ""))
                # out["description"] = snippet.get("description", row.get("description", ""))

            writer.writerow(out)

    print(f"Готово. Результат: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
