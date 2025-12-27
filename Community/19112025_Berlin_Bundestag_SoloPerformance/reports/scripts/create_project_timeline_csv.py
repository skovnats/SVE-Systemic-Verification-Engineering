#!/usr/bin/env python
import argparse
import csv
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


# ===== базовая неделя 0 =====
BASE_YEAR = 2025
BASE_ISO_WEEK = 47  # 2025KW47
BASE_MONDAY = date.fromisocalendar(BASE_YEAR, BASE_ISO_WEEK, 1)

# ===== 444-дневная шкала (для day_444) =====
DAY1_444 = date(2025, 11, 23)  # day 1

@dataclass(frozen=True)
class Cycle:
    idx: int
    layer: str
    start: date
    end: date

CYCLES = [
    Cycle(1, "Working Level (Ukraine Desk)", date(2025, 11, 23), date(2026, 3, 14)),
    Cycle(2, "Regional / Political Leadership", date(2026, 3, 15), date(2026, 7, 2)),
    Cycle(3, "Federal Foreign Minister", date(2026, 7, 3), date(2026, 10, 21)),
    Cycle(4, "Federal Chancellor", date(2026, 10, 22), date(2027, 2, 10)),
]


def iso_kw(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}KW{w:02d}"


def monday_sunday_from_monday(monday: date) -> tuple[date, date]:
    return monday, monday + timedelta(days=6)


def detect_cycle(d: date) -> Cycle:
    for c in CYCLES:
        if c.start <= d <= c.end:
            return c
    # вне диапазона — всё равно вернём ближайший по смыслу (Cycle 1)
    return CYCLES[0]


def day_444(d: date) -> int:
    # day 1 = 23.11.2025
    return (d - DAY1_444).days + 1


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create master timeline CSV for week ±n reports.")
    p.add_argument(
        "--max-n",
        type=int,
        default=None,
        help="Max n to generate (default: enough to cover until Cycle 4 end).",
    )
    p.add_argument(
        "--out",
        type=str,
        default="project_timeline.csv",
        help="Output CSV name (written to repo root). Default: project_timeline.csv",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    # по умолчанию считаем max_n так, чтобы +n воскресенье дошло до конца Cycle 4
    if args.max_n is None:
        end = CYCLES[-1].end
        # найдём n, при котором воскресенье (+n) >= end
        n = 0
        while True:
            ref_sunday_plus = BASE_MONDAY + timedelta(weeks=n, days=6)
            if ref_sunday_plus >= end:
                args.max_n = n
                break
            n += 1

    scripts_dir = Path(__file__).resolve().parent
    repo_root = scripts_dir.parent
    out_path = repo_root / args.out

    fieldnames = [
        "n",

        "kw_minus", "minus_monday", "minus_sunday",
        "kw_plus", "plus_monday", "plus_sunday",

        "ref_sunday_plus", "ref_kw_plus", "ref_day_444",

        "cycle", "level", "institutional_layer",
        "cycle_start", "cycle_end",
    ]

    rows = []
    for n in range(0, args.max_n + 1):
        minus_monday = BASE_MONDAY - timedelta(weeks=n)
        plus_monday = BASE_MONDAY + timedelta(weeks=n)

        minus_monday, minus_sunday = monday_sunday_from_monday(minus_monday)
        plus_monday, plus_sunday = monday_sunday_from_monday(plus_monday)

        kw_minus = iso_kw(minus_monday)
        kw_plus = iso_kw(plus_monday)

        ref_sunday_plus = plus_sunday  # по твоей поправке
        cycle = detect_cycle(ref_sunday_plus)

        rows.append({
            "n": n,

            "kw_minus": kw_minus,
            "minus_monday": minus_monday.isoformat(),
            "minus_sunday": minus_sunday.isoformat(),

            "kw_plus": kw_plus,
            "plus_monday": plus_monday.isoformat(),
            "plus_sunday": plus_sunday.isoformat(),

            "ref_sunday_plus": ref_sunday_plus.isoformat(),
            "ref_kw_plus": iso_kw(ref_sunday_plus),
            "ref_day_444": day_444(ref_sunday_plus),

            "cycle": f"Cycle {cycle.idx}",
            "level": cycle.idx,  # уровни 1-4 = циклы 1-4
            "institutional_layer": cycle.layer,
            "cycle_start": cycle.start.isoformat(),
            "cycle_end": cycle.end.isoformat(),
        })

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"Created: {out_path} (rows: {len(rows)})")


if __name__ == "__main__":
    main()
