#!/usr/bin/env python3
"""
Aggregate all REPORT.md tables under a root folder into FINAL_REPORT.md.

Key feature:
- Integrates ALL existing columns from sub-reports (union of columns).
- Preserves column order by first appearance across reports.
- Adds:
    Source Folder
    Source Report
    signed (default false)
    indexed_for_reference_in_courts (default true)

Usage:
  python3 aggregate_reports.py
  python3 aggregate_reports.py /path/to/root
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("path", nargs="?", default=".", help="Root folder to scan (default: pwd)")
    p.add_argument("--report-name", default="REPORT.md", help="Report filename to search for (default: REPORT.md)")
    p.add_argument("--output", default="FINAL_REPORT.md", help="Output filename (written in root folder)")
    return p.parse_args()


def split_md_row(line: str) -> List[str]:
    """
    Minimal markdown row splitter supporting escaped pipes (\|).
    Row format: | a | b | c |
    """
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return []
    s = s[1:-1]  # strip outer pipes

    cells: List[str] = []
    cur: List[str] = []
    esc = False
    for ch in s:
        if esc:
            cur.append(ch)
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == "|":
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    cells.append("".join(cur).strip())
    return cells


def is_separator_row(cells: List[str]) -> bool:
    # typical: --- / :---: etc
    if not cells:
        return False
    for c in cells:
        t = c.replace(":", "").replace("-", "").strip()
        if t != "":
            return False
    return True


def parse_first_md_table(report_path: Path) -> Tuple[List[str], List[List[str]]]:
    """
    Find and parse the first markdown table in the file.
    Returns (header, rows). If no table found, returns ([], []).
    """
    lines = report_path.read_text(encoding="utf-8", errors="replace").splitlines()

    header: List[str] = []
    rows: List[List[str]] = []

    state = "SEARCH_HEADER"  # SEARCH_HEADER -> SEARCH_SEPARATOR -> READ_ROWS

    for line in lines:
        cells = split_md_row(line)
        if not cells:
            # if we already started reading rows, stop on first non-table line
            if state == "READ_ROWS" and rows:
                break
            continue

        if state == "SEARCH_HEADER":
            header = cells
            state = "SEARCH_SEPARATOR"
            continue

        if state == "SEARCH_SEPARATOR":
            if is_separator_row(cells):
                state = "READ_ROWS"
            else:
                # Not a real table; reset and keep searching
                header = []
                rows = []
                state = "SEARCH_HEADER"
            continue

        if state == "READ_ROWS":
            rows.append(cells)

    if not header or not rows:
        return [], []
    return header, rows


def normalize_row(row: List[str], n: int) -> List[str]:
    if len(row) < n:
        return row + [""] * (n - len(row))
    if len(row) > n:
        return row[:n]
    return row


def md_escape(text: str) -> str:
    return text.replace("|", r"\|")


def write_final_report(out_path: Path, rows: List[Dict[str, str]], columns: List[str]) -> None:
    lines = ["# FINAL REPORT", ""]
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("|" + "|".join(["---"] * len(columns)) + "|")

    for r in rows:
        lines.append("| " + " | ".join(md_escape(r.get(c, "")) for c in columns) + " |")

    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"ERROR: not a directory: {root}")

    report_paths = sorted(p for p in root.rglob(args.report_name) if p.is_file())

    print(f"Root: {root}")
    print(f"Found {len(report_paths)} report(s).")
    for i, p in enumerate(report_paths, 1):
        print(f"  [{i}/{len(report_paths)}] {p.relative_to(root)}")

    # Column order strategy:
    # 1) Start with provenance columns
    # 2) Then append columns from each report header in order of first appearance
    # 3) End with the two final control columns (if not already present)
    base_cols = ["Source Folder", "Source Report"]
    tail_cols = ["signed", "indexed_for_reference_in_courts"]

    col_order: List[str] = []
    seen = set()

    def add_col(c: str) -> None:
        if c not in seen:
            seen.add(c)
            col_order.append(c)

    for c in base_cols:
        add_col(c)

    aggregated: List[Dict[str, str]] = []

    for rp in report_paths:
        header, data_rows = parse_first_md_table(rp)
        if not header or not data_rows:
            print(f"  - SKIP (no parseable table): {rp.relative_to(root)}")
            continue

        # register header columns (keep their order)
        for c in header:
            add_col(c)

        for row in data_rows:
            row_n = normalize_row(row, len(header))
            d = {header[i]: row_n[i] for i in range(len(header))}

            d["Source Folder"] = str(rp.parent.relative_to(root))
            d["Source Report"] = str(rp.relative_to(root))

            # defaults (only if not already present)
            d.setdefault("signed", "false")
            d.setdefault("indexed_for_reference_in_courts", "true")

            aggregated.append(d)

    for c in tail_cols:
        add_col(c)

    out_path = root / args.output
    write_final_report(out_path, aggregated, col_order)

    print(f"\nDone. Wrote: {out_path}")
    print(f"Total aggregated rows: {len(aggregated)}")
    print(f"Total columns: {len(col_order)}")


if __name__ == "__main__":
    main()
