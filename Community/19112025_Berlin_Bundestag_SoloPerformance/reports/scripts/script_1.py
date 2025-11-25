import requests
from datetime import datetime

API_KEY = "ВСТАВЬ_СВОЙ_API_KEY"

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


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
    # Пример: диапазон дат
    published_after = "2024-01-01T00:00:00Z"
    published_before = "2024-02-01T00:00:00Z"

    # Ключевые слова (рус.)
    queries = [
        "тцк",
        "хватают людей",
        "военкомат хватает людей",
    ]

    for q in queries:
        print(f"\n=== Результаты для запроса: {q!r} ===")
        videos = search_youtube(
            query=q,
            published_after=published_after,
            published_before=published_before,
            max_results=20,
            short_only=True,  # ставь False, если нужны вообще все видео
        )
        for v in videos:
            print(f"{v['publishedAt']} | {v['title']} | {v['url']}")
