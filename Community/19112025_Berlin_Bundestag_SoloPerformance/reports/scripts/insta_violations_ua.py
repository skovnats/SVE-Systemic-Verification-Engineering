#!/usr/bin/env python3
import sys
import os
import csv
import time
import instaloader
from datetime import date, datetime, timedelta

# === НАСТРОЙКИ ===
# 1. Впишите сюда данные вашего ТЕХНИЧЕСКОГО аккаунта
INSTA_USER=os.getenv("INSTA_USER")
INSTA_PASS=os.getenv("INSTA_PASS")

TARGET_ACCOUNTS = [
    "artem__dmytruk",
    "voenkomat_bespredell",
    "busifikator",
    "tck_pidary"
]

BASE_MONDAY = date.fromisocalendar(2025, 47, 1)

def get_week_range_from_k(k: int):
    monday = BASE_MONDAY + timedelta(weeks=k)
    sunday = monday + timedelta(days=6)
    year, week, _ = monday.isocalendar()
    kw_label = f"{year}KW{week:02d}"
    start_dt = datetime.combine(monday, datetime.min.time())
    end_dt = datetime.combine(sunday, datetime.max.time())
    return kw_label, start_dt, end_dt

def main():
    try:
        K = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    except ValueError:
        K = 0

    kw_label, start_dt, end_dt = get_week_range_from_k(K)
    output_csv = f"insta_{kw_label}.csv"

    print(f"Week: {kw_label} | {start_dt.date()} ... {end_dt.date()}")

    # Инициализация
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False, 
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    # === АВТОРИЗАЦИЯ ===
    print(f"🔐 Вход в аккаунт {INSTA_USER}...")
    try:
        # Пытаемся загрузить сессию, если она была сохранена ранее
        L.load_session_from_file(INSTA_USER)
    except FileNotFoundError:
        # Если сессии нет, логинимся паролем
        try:
            L.login(INSTA_USER, INSTA_PASS)
        except instaloader.TwoFactorAuthRequiredException:
            # Если включена 2FA, скрипт попросит код в консоли
            code = input("Введите код 2FA: ")
            L.two_factor_login(code)
        except Exception as e:
            print(f"❌ Ошибка входа: {e}")
            sys.exit(1)

    all_results = []

    for username in TARGET_ACCOUNTS:
        print(f"\n🔍 Проверяю аккаунт: {username}...")
        
        try:
            profile = instaloader.Profile.from_username(L.context, username)
        except Exception as e:
            print(f"❌ Не удалось получить профиль {username}: {e}")
            continue

        posts = profile.get_posts()
        count_found = 0

        try:
            for post in posts:
                post_date = post.date
                
                if post_date > end_dt:
                    continue 
                
                if post_date < start_dt:
                    print(f"   -> Старые посты ({post_date.date()}), стоп.")
                    break 

                if not post.is_video:
                    continue

                print(f"   ✅ {post_date} | {post.shortcode}")

                all_results.append({
                    "username": username,
                    "publishedAt": post_date,
                    "shortcode": post.shortcode,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "caption": (post.caption or "")[:300].replace("\n", " "),
                    "likes": post.likes,
                    "comments": post.comments,
                    "video_duration": post.video_duration,
                    "video_view_count": post.video_view_count
                })
                count_found += 1
                
                # ВАЖНО: Пауза, чтобы не забанили
                time.sleep(4) 

        except Exception as e:
            print(f"⚠️ Ошибка при чтении постов (возможно лимит запросов): {e}")
            time.sleep(60) # Ждем минуту если ошибка

        time.sleep(10) # Пауза между аккаунтами

    keys = ["username", "publishedAt", "video_duration", "video_view_count", "likes", "comments", "url", "caption"]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\n🏁 Готово! Файл: {output_csv}")

if __name__ == "__main__":
    main()