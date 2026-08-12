#!/usr/bin/env python3
"""
x_backup.py — Backup all your X (Twitter) posts + images to beautiful PDFs.

Структура папок:
  twitter_backup/
    2024-03/
      2024-03-15_10-30_thread_abc12345/
        thread.pdf
        images/
          media_key1.jpg
      2024-03-20_14-00_tweet_def67890/
        tweet.pdf
        images/

Setup:
  1. Создай .env (см. .env.example) с ключами X API
  2. pip install -r requirements.txt
  3. python x_backup.py --username YOUR_USERNAME

Нужен X API "Basic" ($100/мес) или "Free" tier с OAuth 1.0a.
Лимит X API: до 3 200 последних твитов на аккаунт.
"""

import os
import sys
import re
import json
import time
import argparse
import requests
import textwrap
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Optional

import tweepy
from PIL import Image as PILImage
from fpdf import FPDF, XPos, YPos
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

# ╔══════════════════════════════════════════════════════════════╗
# ║                     CONFIGURATION                            ║
# ╚══════════════════════════════════════════════════════════════╝

BEARER_TOKEN  = os.getenv("X_BEARER_TOKEN",  "")
API_KEY       = os.getenv("X_API_KEY",       "")
API_SECRET    = os.getenv("X_API_SECRET",    "")
ACCESS_TOKEN  = os.getenv("X_ACCESS_TOKEN",  "")
ACCESS_SECRET = os.getenv("X_ACCESS_SECRET", "")
X_ACCOUNT = os.getenv("X_ACCOUNT", "")

# X API limits
RESULTS_PER_PAGE = 100   # max per request
DEFAULT_MAX_PAGES = 32   # 32 × 100 = 3 200 (hard API limit)

# PDF palette — Twitter/X brand colours
C_BLUE   = (29,  161, 242)   # #1DA1F2 — X blue
C_BLACK  = (15,  20,  25)    # #0F1419 — X near-black
C_GRAY   = (83,  100, 113)   # #536471 — X secondary text
C_BORDER = (207, 217, 222)   # #CFD9DE — X separator
C_BG     = (247, 249, 249)   # #F7F9F9 — X light background
C_WHITE  = (255, 255, 255)

# ╔══════════════════════════════════════════════════════════════╗
# ║                     FONT HANDLING                            ║
# ║  Нужен Unicode-шрифт для кириллицы.                         ║
# ║  Скрипт пробует найти DejaVu/Liberation на системе,         ║
# ║  иначе просит поставить вручную.                             ║
# ╚══════════════════════════════════════════════════════════════╝

FONT_LOCAL_DIR = Path(__file__).parent / "fonts"

# Пути к шрифтам на разных ОС
_FONT_CANDIDATES = {
    "regular": [
        # Linux (Debian/Ubuntu)
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf"),
        # Linux (Liberation — часто есть по умолчанию)
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        Path("/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf"),
        # macOS
        Path("/Library/Fonts/Arial Unicode MS.ttf"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
        # Windows
        Path("C:/Windows/Fonts/arial.ttf"),
        # Локальная папка ./fonts/
        FONT_LOCAL_DIR / "DejaVuSans.ttf",
        FONT_LOCAL_DIR / "LiberationSans-Regular.ttf",
        FONT_LOCAL_DIR / "arial.ttf",
    ],
    "bold": [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        Path("/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf"),
        Path("/Library/Fonts/Arial Bold.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
        FONT_LOCAL_DIR / "DejaVuSans-Bold.ttf",
        FONT_LOCAL_DIR / "LiberationSans-Bold.ttf",
        FONT_LOCAL_DIR / "arialbd.ttf",
    ],
}


def find_fonts() -> tuple[Optional[Path], Optional[Path]]:
    """
    Ищет Unicode-шрифт (regular + bold).
    Если не нашёл — пробует поставить через apt (Linux only).
    Возвращает (regular_path, bold_path) или (None, None).
    """
    reg = next((p for p in _FONT_CANDIDATES["regular"] if p.exists()), None)
    bld = next((p for p in _FONT_CANDIDATES["bold"]    if p.exists()), None)

    if reg:
        return reg, bld or reg   # bold fallback = regular

    # Попытка auto-install на Ubuntu/Debian
    try:
        import subprocess
        result = subprocess.run(
            ["apt-get", "install", "-y", "fonts-dejavu-core"],
            capture_output=True, timeout=60,
        )
        if result.returncode == 0:
            return find_fonts()   # рекурсивная проверка после установки
    except Exception:
        pass

    return None, None


# ╔══════════════════════════════════════════════════════════════╗
# ║                     X API CLIENT                             ║
# ╚══════════════════════════════════════════════════════════════╝

def make_client() -> tweepy.Client:
    if not BEARER_TOKEN:
        sys.exit(
            "\n❌  X_BEARER_TOKEN не задан. "
            "Создай файл .env (пример в .env.example) и повтори.\n"
        )
    return tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY       or None,
        consumer_secret=API_SECRET or None,
        access_token=ACCESS_TOKEN  or None,
        access_token_secret=ACCESS_SECRET or None,
        wait_on_rate_limit=True,
    )


def get_user_id(client: tweepy.Client, username: str) -> str:
    user_auth = bool(API_KEY and ACCESS_TOKEN)
    try:
        resp = client.get_user(username=username, user_auth=user_auth)
    except tweepy.errors.TweepyException as e:
        sys.exit(f"\n❌  Не удалось найти пользователя @{username}: {e}\n")
    if not resp.data:
        sys.exit(f"\n❌  Пользователь @{username} не найден.\n")
    return str(resp.data.id)


# ╔══════════════════════════════════════════════════════════════╗
# ║                     FETCH TWEETS                             ║
# ╚══════════════════════════════════════════════════════════════╝

def fetch_tweets(
    client: tweepy.Client,
    user_id: str,
    max_pages: int = DEFAULT_MAX_PAGES,
) -> tuple[list, dict]:
    """
    Скачивает все твиты пользователя (до max_pages * 100).
    Возвращает: (tweets_list, media_map {media_key -> media_obj}).
    
    Как конвейер на почте: каждый "вагон" (page) содержит
    до 100 писем (tweets) + вложения (media).
    """
    tweets    : list = []
    media_map : dict = {}
    user_auth = bool(API_KEY and ACCESS_TOKEN)

    paginator = tweepy.Paginator(
        client.get_users_tweets,
        id=user_id,
        tweet_fields=[
            "created_at",
            "text",
            "conversation_id",
            "in_reply_to_user_id",
            "attachments",
            "public_metrics",
        ],
        expansions=["attachments.media_keys"],
        media_fields=[
            "url",
            "preview_image_url",
            "type",
            "width",
            "height",
            "media_key",
        ],
        max_results=RESULTS_PER_PAGE,
        user_auth=user_auth,
        limit=max_pages,
    )

    for page in paginator:
        if page.data:
            tweets.extend(page.data)
        if page.includes and "media" in page.includes:
            for m in page.includes["media"]:
                media_map[m.media_key] = m

    return tweets, media_map


# ╔══════════════════════════════════════════════════════════════╗
# ║                  THREAD GROUPING                             ║
# ╚══════════════════════════════════════════════════════════════╝

def group_into_threads(tweets: list) -> dict[str, list]:
    """
    Группирует твиты по conversation_id.
    Это как сортировка писем по стопкам: все части одного разговора
    лежат в одной стопке, отсортированной по времени.
    """
    groups: dict[str, list] = defaultdict(list)
    for t in tweets:
        cid = str(getattr(t, "conversation_id", None) or t.id)
        groups[cid].append(t)

    # Хронологический порядок внутри каждого треда
    for cid in groups:
        groups[cid].sort(
            key=lambda t: t.created_at if t.created_at else datetime.min
        )
    return dict(groups)


# ╔══════════════════════════════════════════════════════════════╗
# ║                  IMAGE DOWNLOAD                              ║
# ╚══════════════════════════════════════════════════════════════╝

def download_image(url: str, dest: Path) -> Optional[Path]:
    """Скачивает одно изображение. Пропускает, если уже есть."""
    if dest.exists():
        return dest
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        dest.write_bytes(r.content)
        # Проверяем, что это валидное изображение
        with PILImage.open(dest) as im:
            im.verify()
        return dest
    except Exception as e:
        dest.unlink(missing_ok=True)
        return None


def download_thread_media(
    tweets: list,
    media_map: dict,
    img_dir: Path,
) -> dict[str, Path]:
    """
    Скачивает все изображения треда.
    Возвращает {media_key -> local_path}.
    """
    img_dir.mkdir(parents=True, exist_ok=True)
    local: dict[str, Path] = {}

    for tweet in tweets:
        if not (tweet.attachments and tweet.attachments.get("media_keys")):
            continue
        for mk in tweet.attachments["media_keys"]:
            if mk in local:
                continue
            m = media_map.get(mk)
            if not m:
                continue
            url = getattr(m, "url", None) or getattr(m, "preview_image_url", None)
            if not url:
                continue
            dest = img_dir / f"{mk}.jpg"
            path = download_image(url, dest)
            if path:
                local[mk] = path

    return local


# ╔══════════════════════════════════════════════════════════════╗
# ║                  PDF GENERATION                              ║
# ╚══════════════════════════════════════════════════════════════╝

class TweetPDF(FPDF):
    """
    Генерирует PDF в стиле X/Twitter.
    Как блокнот с фирменным оформлением, куда мы вклеиваем
    каждый пост и его картинки.
    """

    # mm margins
    MARGIN_H = 14
    MARGIN_V = 14

    def __init__(self, username: str, font_r: Optional[Path], font_b: Optional[Path]):
        super().__init__("P", "mm", "A4")
        self.username = username
        self._has_unicode = False
        self._setup_fonts(font_r, font_b)
        self.set_auto_page_break(auto=True, margin=self.MARGIN_V + 8)
        self.set_margins(self.MARGIN_H, self.MARGIN_V, self.MARGIN_H)

    # ── Fonts ────────────────────────────────────────────────────

    def _setup_fonts(self, font_r: Optional[Path], font_b: Optional[Path]):
        if font_r and font_r.exists():
            try:
                self.add_font("X", style="",  fname=str(font_r))
                self.add_font("X", style="B", fname=str(font_b or font_r))
                self._has_unicode = True
            except Exception as e:
                tqdm.write(f"  ⚠  Не удалось загрузить шрифт: {e}")

    def _f(self, size: float, bold: bool = False):
        """Устанавливает шрифт (Unicode если есть, иначе Helvetica)."""
        if self._has_unicode:
            self.set_font("X", "B" if bold else "", size)
        else:
            self.set_font("Helvetica", "B" if bold else "", size)

    # ── Page chrome ──────────────────────────────────────────────

    def header(self):
        # Синяя полоса сверху
        self.set_fill_color(*C_BLUE)
        self.rect(0, 0, 210, 10, "F")

        self._f(8.5, bold=True)
        self.set_text_color(*C_WHITE)
        self.set_y(1.5)
        self.set_x(self.MARGIN_H)
        self.cell(0, 7, f"@{self.username}  ·  X (Twitter) Backup", align="L")

        ts_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        self.set_y(1.5)
        self.cell(0, 7, f"{ts_now}  ", align="R")
        self.ln(11)

    def footer(self):
        self.set_y(-13)
        self.set_draw_color(*C_BORDER)
        self.set_line_width(0.2)
        self.line(self.MARGIN_H, self.get_y(), 210 - self.MARGIN_H, self.get_y())
        self._f(7.5)
        self.set_text_color(*C_GRAY)
        self.cell(0, 8, f"Страница {self.page_no()}", align="C")

    # ── Thread / Tweet header ────────────────────────────────────

    def add_document_header(self, tweets: list, is_thread: bool):
        first  = tweets[0]
        dt_str = ""
        if first.created_at:
            dt_str = first.created_at.strftime("%d %B %Y  ·  %H:%M UTC")

        kind   = "Тред" if is_thread else "Твит"
        n_str  = f"  ({len(tweets)} сообщений)" if is_thread else ""

        # Фоновая плашка
        y0 = self.get_y()
        self.set_fill_color(*C_BG)
        self.rect(self.MARGIN_H - 1, y0, 210 - 2 * self.MARGIN_H + 2, 14, "F")

        self._f(13, bold=True)
        self.set_text_color(*C_BLUE)
        self.set_y(y0 + 2)
        self.cell(0, 8, f"{kind}{n_str}", ln=False)

        self._f(9)
        self.set_text_color(*C_GRAY)
        self.cell(0, 8, f"  {dt_str}", ln=True)

        # Синяя разделительная черта
        self.set_draw_color(*C_BLUE)
        self.set_line_width(0.6)
        self.line(self.MARGIN_H, self.get_y() + 1, 210 - self.MARGIN_H, self.get_y() + 1)
        self.ln(7)

    # ── Single tweet block ───────────────────────────────────────

    def add_tweet(self, tweet, local_imgs: dict[str, Path], num: int = 0):
        """Рендерит один пост (часть треда или самостоятельный твит)."""

        # Бейдж с номером (только для тредов)
        if num > 0:
            self._f(8, bold=True)
            self.set_fill_color(*C_BLUE)
            self.set_text_color(*C_WHITE)
            self.cell(14, 5.5, f" #{num}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1.5)

        # Метаданные: время + метрики
        ts = ""
        if tweet.created_at:
            ts = tweet.created_at.strftime("%Y-%m-%d  %H:%M UTC")

        m       = tweet.public_metrics or {}
        likes   = m.get("like_count",    0)
        rts     = m.get("retweet_count", 0)
        replies = m.get("reply_count",   0)
        views   = m.get("impression_count", "—")

        self._f(8)
        self.set_text_color(*C_GRAY)
        meta = f"{ts}    Лайки: {likes}   RT: {rts}   Ответы: {replies}   Просмотры: {views}"
        self.multi_cell(0, 5, meta, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

        # Текст поста
        self._f(10.5)
        self.set_text_color(*C_BLACK)
        text = clean_text(tweet.text or "")
        self.multi_cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

        # Изображения
        if tweet.attachments and tweet.attachments.get("media_keys"):
            for mk in tweet.attachments["media_keys"]:
                img_path = local_imgs.get(mk)
                if img_path and img_path.exists():
                    self._embed_image(img_path)

        # Горизонтальная черта-разделитель
        self.set_draw_color(*C_BORDER)
        self.set_line_width(0.2)
        y = self.get_y()
        self.line(self.MARGIN_H, y, 210 - self.MARGIN_H, y)
        self.ln(7)

    def _embed_image(self, img_path: Path):
        """Вставляет изображение с авто-масштабированием под ширину страницы."""
        MAX_W_MM = 160.0
        MAX_H_MM = 100.0
        PX_TO_MM = 0.264583   # при 96 DPI

        try:
            with PILImage.open(img_path) as im:
                w_px, h_px = im.size

            # Масштаб: вписать в MAX_W × MAX_H, сохраняя пропорции
            w_mm = w_px * PX_TO_MM
            h_mm = h_px * PX_TO_MM
            scale = min(MAX_W_MM / w_mm, MAX_H_MM / h_mm, 1.0)
            w_mm *= scale
            h_mm *= scale

            # Перевернуть страницу, если не влезает
            if self.get_y() + h_mm + 5 > self.h - 22:
                self.add_page()

            # Серая рамка вокруг картинки
            brd = 1.0
            self.set_fill_color(*C_BORDER)
            self.rect(self.MARGIN_H - brd, self.get_y(), w_mm + 2 * brd, h_mm + 2 * brd, "F")
            self.image(
                str(img_path),
                x=self.MARGIN_H,
                y=self.get_y() + brd,
                w=w_mm,
                h=h_mm,
            )
            self.set_y(self.get_y() + h_mm + 2 * brd + 3)
            self.ln(2)

        except Exception as e:
            self._f(8)
            self.set_text_color(*C_GRAY)
            self.cell(0, 5, f"[изображение: {img_path.name}]", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1)


# ── Helpers ──────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Нормализует текст для PDF: убирает null-байты, нормализует переносы строк."""
    text = text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Убираем управляющие символы кроме \n и \t
    text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return text


def render_pdf(
    thread_tweets : list,
    local_imgs    : dict[str, Path],
    out_path      : Path,
    username      : str,
    font_r        : Optional[Path],
    font_b        : Optional[Path],
):
    is_thread = len(thread_tweets) > 1
    pdf = TweetPDF(username, font_r, font_b)
    pdf.add_page()
    pdf.add_document_header(thread_tweets, is_thread)

    for i, tweet in enumerate(thread_tweets, 1):
        num = i if is_thread else 0
        pdf.add_tweet(tweet, local_imgs, num)

    pdf.output(str(out_path))


# ╔══════════════════════════════════════════════════════════════╗
# ║                         MAIN                                 ║
# ╚══════════════════════════════════════════════════════════════╝

def main():
    ap = argparse.ArgumentParser(
        description="X (Twitter) → PDF backup. Скачивает все твиты и сохраняет в PDF.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python x_backup.py --username myaccount
  python x_backup.py --username myaccount --only-threads
  python x_backup.py --username myaccount --no-images --out /tmp/backup
        """,
    )
    ap.add_argument("--username",     required=True,
                    help="X-никнейм без @")
    ap.add_argument("--out",          default="twitter_backup",
                    help="Папка для сохранения (default: twitter_backup/)")
    ap.add_argument("--only-threads", action="store_true",
                    help="Сохранять только треды (игнорировать одиночные твиты)")
    ap.add_argument("--no-images",    action="store_true",
                    help="Пропустить скачивание картинок")
    ap.add_argument("--max-pages",    type=int, default=DEFAULT_MAX_PAGES,
                    help=f"Макс. страниц API (1 стр. = 100 твитов, default: {DEFAULT_MAX_PAGES})")
    args = ap.parse_args()

    out_root = Path(args.out)

    print(f"\n  ╔══ X Backup ══ @{args.username} ══╗")
    print(  "  ║")

    # ── Шрифты ──────────────────────────────────────────────────
    print("  ║  🔤  Поиск Unicode-шрифта (нужен для кириллицы) …")
    font_r, font_b = find_fonts()
    if font_r:
        print(f"  ║  ✓   Шрифт: {font_r.name}")
    else:
        print("  ║  ⚠   Unicode-шрифт не найден. Кириллица может не отображаться.")
        print("  ║      Решение:")
        print("  ║        sudo apt-get install fonts-dejavu-core  (Linux)")
        print("  ║        или положи DejaVuSans.ttf в папку ./fonts/")

    # ── Авторизация ──────────────────────────────────────────────
    print("  ║  🔑  Авторизация в X API …")
    client  = make_client()
    user_id = get_user_id(client, args.username)
    print(f"  ║  ✓   User ID: {user_id}")

    # ── Скачивание ───────────────────────────────────────────────
    limit = args.max_pages * RESULTS_PER_PAGE
    print(f"  ║  📥  Скачивание твитов (лимит: {limit}, ждём rate limit'ов …)")
    tweets, media_map = fetch_tweets(client, user_id, args.max_pages)
    print(f"  ║  ✓   Скачано: {len(tweets)} твитов, {len(media_map)} медиа")

    # ── Группировка в треды ──────────────────────────────────────
    threads   = group_into_threads(tweets)
    n_threads = sum(1 for v in threads.values() if len(v) > 1)
    n_singles = len(threads) - n_threads
    print(f"  ║  🧵  {n_threads} тредов  +  {n_singles} одиночных твитов")
    print("  ║")
    print("  ║  💾  Сохранение PDF …\n")

    # ── Сохранение ───────────────────────────────────────────────
    saved = skipped = errors = 0

    for conv_id, items in tqdm(
        threads.items(), desc="  Прогресс", unit="разговор"
    ):
        if args.only_threads and len(items) == 1:
            skipped += 1
            continue

        first = items[0]
        dt    = first.created_at if first.created_at else datetime.utcnow()

        # Структура папок: out/YYYY-MM/YYYY-MM-DD_HH-MM_[thread|tweet]_XXXXXXXX/
        is_thread  = len(items) > 1
        kind       = "thread" if is_thread else "tweet"
        ts_str     = dt.strftime("%Y-%m-%d_%H-%M")
        conv_short = str(conv_id)[-8:]
        conv_dir   = out_root / dt.strftime("%Y-%m") / f"{ts_str}_{kind}_{conv_short}"
        img_dir    = conv_dir / "images"

        try:
            conv_dir.mkdir(parents=True, exist_ok=True)

            # Скачиваем медиа
            local_imgs: dict[str, Path] = {}
            if not args.no_images:
                local_imgs = download_thread_media(items, media_map, img_dir)

            # Генерируем PDF
            pdf_path = conv_dir / f"{ts_str}_{kind}.pdf"
            render_pdf(items, local_imgs, pdf_path, args.username, font_r, font_b)
            saved += 1

        except Exception as e:
            tqdm.write(f"\n  ⚠  Ошибка conv {conv_short}: {e}")
            errors += 1

    # ── Итог ─────────────────────────────────────────────────────
    print(f"""
  ╠══ Готово! ══╣
  ║  ✅ Сохранено:  {saved}
  ║  ⏭  Пропущено: {skipped}
  ║  ❌ Ошибок:    {errors}
  ║
  ║  📁 Папка: {out_root.resolve()}
  ║  📐 Схема: {out_root}/ГГГГ-ММ/ДАТА_тип_ID/
  ╚══════════════╝
""")


if __name__ == "__main__":
    main()
