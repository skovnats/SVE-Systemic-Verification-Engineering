#!/usr/bin/env python
import argparse
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

# === базовая неделя 0 ===
BASE_YEAR = 2025
BASE_ISO_WEEK = 47           # 2025KW47
BASE_MONDAY = date.fromisocalendar(BASE_YEAR, BASE_ISO_WEEK, 1)

# === циклы ===
@dataclass
class Cycle:
    idx: int
    start: date
    end: date

CYCLES = [
    Cycle(1, date(2025, 11, 23), date(2026, 3, 14)),
    Cycle(2, date(2026, 3, 15), date(2026, 7, 2)),
    Cycle(3, date(2026, 7, 3), date(2026, 10, 21)),
    Cycle(4, date(2026, 10, 22), date(2027, 2, 10)),
]

ORDINAL = {1: "first", 2: "second", 3: "third", 4: "fourth"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Create weekly report structure for week ±n (base 2025KW47)."
    )
    p.add_argument("n", type=int, help="week offset n >= 0 from base week 2025KW47")
    return p.parse_args()


def detect_cycle(d: date) -> Cycle:
    for c in CYCLES:
        if c.start <= d <= c.end:
            return c
    return CYCLES[0]


def iso_week_label(d: date) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}KW{w:02d}"


def fmt_dmy(d: date) -> str:
    return d.strftime("%d.%m.%Y")


def fmt_long_no_dow(d: date) -> str:
    # "October 27, 2025"
    return d.strftime("%B %d, %Y")


def build_readme(
    n: int,
    kw_minus: str,
    kw_plus: str,
    week_minus_num: int,
    week_plus_num: int,
    monday_minus: date,
    sunday_minus: date,
    monday_plus: date,
    sunday_plus: date,
    cycle: Cycle,
) -> str:
    cycle_label = f"Cycle {cycle.idx}"
    cycle_range_str = f"{fmt_dmy(cycle.start)} - {fmt_dmy(cycle.end)}"
    cycle_ordinal = ORDINAL.get(cycle.idx, str(cycle.idx))

    year_minus = monday_minus.year
    year_plus = monday_plus.year

    return f"""# Week `±{n}`: `{kw_minus}` & `{kw_plus}` - {cycle_label} (111 Days: {cycle_range_str})
**Date Week {week_minus_num}:** {year_minus}: {monday_minus.strftime('%A')}, {fmt_long_no_dow(monday_minus)} - {sunday_minus.strftime('%A')}, {fmt_long_no_dow(sunday_minus)}\\
**Date Week {week_plus_num}:** {year_plus}: {monday_plus.strftime('%A')}, {fmt_long_no_dow(monday_plus)} - {sunday_plus.strftime('%A')}, {fmt_long_no_dow(sunday_plus)}

---

## **Weekly Note for {cycle_label} ({cycle_range_str}x111 Days: {cycle_range_str})**

**Throughout the entire {cycle_ordinal} cycle, I will continue to attach the same official response I received from the institution.**

Until clear, public answers to the original questions appear on the official website, I will operate under the assumption that this document reflects the institution’s current and unchanged position at this level.

Each week, new materials —
**video evidence, transcripts, AI analysis, meta-analysis** —
will be placed **side by side** with this **same, unchanged official response**,
**without** any commentary, interpretation, or judgement from my side.

This method ensures:

* **Full transparency** — nothing is added, removed, or modified.
* **Methodological stability** — one fixed point of reference across all weeks.
* **Institutional clarity** — the official response remains authoritative unless officially updated.
* **Moral neutrality** — the materials speak entirely for themselves.

The purpose of the {cycle_ordinal} cycle is not to argue, but to:

* **document**,
* **compare**,
* **observe**,

using a **stable and unaltered institutional baseline**.


**Official Response — [MFA Position (Level {cycle_label})](https://github.com/skovnats/SVE-Systemic-Verification-Engineering/tree/master/Community/19112025_Berlin_Bundestag_SoloPerformance/reports#hierarchy-escalation-table-111-day-increments):** 
* [PDF of the Response](https://github.com/skovnats/SVE-Systemic-Verification-Engineering/blob/master/Community/19112025_Berlin_Bundestag_SoloPerformance/mails/responses_from_Auswaertiges_Amt_DE/20112025/Beantwortung%20Ihrer%20Anfrage_%20Menschenrechtsverletzungen%20in%20der%20Ukraine%20%5B759bc4c4-387d-49e7-9e16-9a2b56c9da0e%5D%20-%20artiom.kovnatsky%40gmail.com%20-%20Gmail.pdf)
* [Attached Ticket](https://github.com/skovnats/SVE-Systemic-Verification-Engineering/blob/master/Community/19112025_Berlin_Bundestag_SoloPerformance/mails/responses_from_Auswaertiges_Amt_DE/20112025/Ticket%20759bc4c4-387d-49e7-9e16-9a2b56c9da0e.pdf)

**Link to full AI & meta-AI analysis:**
[https://github.com/skovnats/SVE-Systemic-Verification-Engineering/tree/master/Community/19112025_Berlin_Bundestag_SoloPerformance/mails/responses_from_Auswaertiges_Amt_DE/20112025](https://github.com/skovnats/SVE-Systemic-Verification-Engineering/tree/master/Community/19112025_Berlin_Bundestag_SoloPerformance/mails/responses_from_Auswaertiges_Amt_DE/20112025)


### See [QUESTIONS.md](https://github.com/skovnats/SVE-Systemic-Verification-Engineering/blob/master/Community/19112025_Berlin_Bundestag_SoloPerformance/QUESTIONS.md) – these 3+1 questions remain unanswered.

#### See [CODE OF CONDUCT](https://github.com/skovnats/SVE-Systemic-Verification-Engineering/blob/master/Community/19112025_Berlin_Bundestag_SoloPerformance/CODE_OF_CONDUCT.md).
---


## Report

### [**Cases registered:**](https://github.com/skovnats/SVE-Systemic-Verification-Engineering/blob/master/Community/19112025_Berlin_Bundestag_SoloPerformance/reports/REPORTS.md#ak1984-list)
1. AK1984-Human-19, `id=18` (``)



### [Video](video):
1. ``

### [Transcripts (AI+Semi-Manual)](srt):
1. ``

### [Metadata](metadata):
1. [{kw_minus}.csv](metadata/{kw_minus}.csv)
2. [{kw_plus}.csv](metadata/{kw_plus}.csv)


These lists of videos for Week `±{n}` are provided *as is*.
Due to limited personal resources (full-time job, family responsibilities), this collection is necessarily partial.
Please forward the material to the relevant committees for independent review and completion.
"""


def main() -> None:
    args = parse_args()
    n = args.n
    if n < 0:
        raise SystemExit("n must be >= 0")

    # воскресенье недели +n от базовой 2025KW47
    ref_sunday = BASE_MONDAY + timedelta(weeks=n, days=6)
    cycle = detect_cycle(ref_sunday)

    # неделя -n и +n
    monday_minus = BASE_MONDAY - timedelta(weeks=n)
    sunday_minus = monday_minus + timedelta(days=6)

    monday_plus = BASE_MONDAY + timedelta(weeks=n)
    sunday_plus = monday_plus + timedelta(days=6)

    kw_minus = iso_week_label(monday_minus)
    kw_plus = iso_week_label(monday_plus)

    _, week_minus_num, _ = monday_minus.isocalendar()
    _, week_plus_num, _ = monday_plus.isocalendar()

    scripts_dir = Path(__file__).resolve().parent
    root_dir = scripts_dir.parent
    week_dir = root_dir / f"week_+-{n}"
    metadata_dir = week_dir / "metadata"
    srt_dir = week_dir / "srt"
    video_dir = week_dir / "video"

    metadata_dir.mkdir(parents=True, exist_ok=True)
    srt_dir.mkdir(parents=True, exist_ok=True)
    video_dir.mkdir(parents=True, exist_ok=True)

    readme_path = week_dir / "README.md"
    content = build_readme(
        n=n,
        kw_minus=kw_minus,
        kw_plus=kw_plus,
        week_minus_num=week_minus_num,
        week_plus_num=week_plus_num,
        monday_minus=monday_minus,
        sunday_minus=sunday_minus,
        monday_plus=monday_plus,
        sunday_plus=sunday_plus,
        cycle=cycle,
    )
    readme_path.write_text(content, encoding="utf-8")
    print(f"Created structure in: {week_dir}")


if __name__ == "__main__":
    main()