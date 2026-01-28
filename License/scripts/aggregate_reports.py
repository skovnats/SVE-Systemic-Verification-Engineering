#!/usr/bin/env python3
"""
Aggregate REPORT.md files from all subfolders into one FINAL_REPORT.md.

- Recursively scans for REPORT.md
- Parses the markdown table inside each report
- Produces a single combined table with extra columns:
    signed (default: false)
    indexed_for_reference_in_courts (default: true)

Usage:
  python3 aggregate_reports.py                 # uses current working directory
  python3 aggregate_reports.py /path/to/root   # scans this folder recursively

Output:
  FINAL_REPORT.md in the root folder used.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("path", nargs="?", default=".", help="Root folder to scan (default: pwd)")
    p.add_argument(
        "--report-name",
        default="REPORT.md",
        help="Report filename to search for (default: REPORT.md)",
    )
    p.add_argument(
        "--output",
        default="FINAL_REPORT.md",
        help="Output filename (written in root folder)",
    )
    return p.parse_args()


def split_md_row(line: str) -> List[str]:
    """
    Very small markdown table parser: handles \| escaped pipes.
    Assumes row looks like: | a | b | c |
    """
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return []
    s = s[1:-1]  # strip outer pipes

    cells: List[str] = []
    cur = []
    esc = False
    for ch in s:
        if esc:
            cur.append(ch)  # keep escaped char without backslash
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


def parse_report_table(report_path: Path) -> Tuple[List[str], List[List[str]]]:
    """
    Returns (header, rows). If no table found, returns ([], []).
    """
    lines = report_path.read_text(encoding="utf-8", errors="replace").splitlines()

    header: List[str] = []
    rows: List[List[str]] = []

    in_table = False
    saw_header = False

    for line in lines:
        if "|" not in line:
            if in_table and rows:
                break
            continue

        cells = split_md_row(line)
        if not cells:
            continue

        # First table row: header
        if not in_table:
            header = cells
            in_table = True
            saw_header = True
            continue

        # Second row: separator (---)
        if saw_header and is_separator_row(cells):
            continue

        # Data rows
        if in_table:
            # Stop if row length doesn't match and looks like a new table elsewhere
            # (keep it simple; pad/truncate later)
            rows.append(cells)

    if not header or not rows:
        return ([], [])
    return (header, rows)


def normalize_row(row: List[str], n: int) -> List[str]:
    if len(row) < n:
        return row + [""] * (n - len(row))
    if len(row) > n:
        return row[:n]
    return row


def md_escape(text: str) -> str:
    return text.replace("|", r"\|")


def write_final_report(
    out_path: Path,
    rows: List[Dict[str, str]],
    columns: List[str],
) -> None:
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
    print(f"Found {len(report_paths)} report(s):")
    for i, p in enumerate(report_paths, 1):
        print(f"  [{i}/{len(report_paths)}] {p.relative_to(root)}")

    aggregated: List[Dict[str, str]] = []

    # We’ll build a union of columns across all REPORTs, but keep a stable preferred order.
    preferred = [
        "Source Folder",
        "Source Report",
        "File",
        "File SHA-256",
        "OTS_1",
        "OTS_1 SHA-256",
        "OTS_1 Verify",
        "OTS_2",
        "OTS_2 SHA-256",
        "OTS_2 Verify",
        "OTS_3",
        "OTS_3 SHA-256",
        "OTS_3 Verify",
        "signed",
        "indexed_for_reference_in_courts",
    ]
    seen_cols = set(preferred)

    for rp in report_paths:
        header, rows = parse_report_table(rp)
        if not header or not rows:
            print(f"  - SKIP (no table found): {rp.relative_to(root)}")
            continue

        # Map each row to dict by header
        for row in rows:
            row_n = normalize_row(row, len(header))
            d = {header[i]: row_n[i] for i in range(len(header))}

            # Add provenance
            d["Source Folder"] = str(rp.parent.relative_to(root))
            d["Source Report"] = str(rp.relative_to(root))

            # Add requested columns (defaults)
            d["signed"] = "false"
            d["indexed_for_reference_in_courts"] = "true"

            # Track any new columns from input reports
            for col in d.keys():
                if col not in seen_cols:
                    seen_cols.add(col)

            aggregated.append(d)

    # Final column order:
    # - start with preferred
    # - then append any extra columns discovered (stable sorted)
    extra_cols = sorted(c for c in seen_cols if c not in preferred)
    final_columns = preferred + extra_cols

    out_path = root / args.output
    write_final_report(out_path, aggregated, final_columns)

    print(f"\nDone. Wrote: {out_path}")
    print(f"Total aggregated rows: {len(aggregated)}")


if __name__ == "__main__":
    main()
