#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path
from datetime import datetime

# ---- patterns ----
CODEBLOCK_RE = re.compile(r"^\s*```")
TABLE_RE = re.compile(r"^\s*\|")
HEADER_RE = re.compile(r"^\s*#{1,6}\s+")
BULLET_RE = re.compile(r"^\s*[-*+]\s+")
ORDERED_LIST_RE = re.compile(r"^\s*\d+\.\s+")  # keep real markdown lists

# Bad line-number prefixes we want to REMOVE from originals
PREFIX_00001_COLON = re.compile(r"^\s*\d{1,7}\s*:\s+")
PREFIX_BRACKET = re.compile(r"^\s*\[\d{1,7}\]\s+")
PREFIX_NUM_PAREN_DOT = re.compile(r"^\s*\d{1,7}\s*[.)]\s+")

MOJIBAKE_HINT_RE = re.compile(r"[Ãâ€]")

def normalize_text_best_effort(s: str) -> str:
    # Fix classic "UTF-8 bytes decoded as Latin-1" mojibake
    if MOJIBAKE_HINT_RE.search(s):
        try:
            fixed = s.encode("latin-1").decode("utf-8")
            return fixed
        except Exception:
            return s
    return s

def should_strip_num_prefix(line: str) -> bool:
    """
    Strip only if it looks like our artificial numbering, and NOT a real markdown list.
    """
    if HEADER_RE.match(line) or TABLE_RE.match(line) or BULLET_RE.match(line) or ORDERED_LIST_RE.match(line):
        return False
    if PREFIX_BRACKET.match(line):
        return True
    if PREFIX_00001_COLON.match(line):
        return True
    # 1) / 1. can be list; we already excluded ordered-list "1. " above,
    # but "1) " is safe to remove if it's everywhere (we treat per-line here)
    if PREFIX_NUM_PAREN_DOT.match(line) and not ORDERED_LIST_RE.match(line):
        return True
    return False

def strip_prefix(line: str) -> str:
    line2 = PREFIX_BRACKET.sub("", line)
    line2 = PREFIX_00001_COLON.sub("", line2)
    # Strip 1) / 1. only if not markdown ordered list
    if not ORDERED_LIST_RE.match(line2):
        line2 = PREFIX_NUM_PAREN_DOT.sub("", line2)
    return line2

def make_court_copy_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    out = []
    for i, line in enumerate(lines, start=1):
        out.append(f"[{i:04d}] {line}")
    return "\n".join(out) + "\n"

def fix_one_md(path: Path, make_court_copy: bool) -> tuple[bool, bool]:
    """
    Returns (original_changed, court_written)
    """
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="replace")

    text = normalize_text_best_effort(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = text.split("\n")
    out_lines = []
    in_code = False
    changed = False

    for line in lines:
        if CODEBLOCK_RE.match(line):
            in_code = not in_code
            out_lines.append(line)
            continue

        if in_code:
            out_lines.append(line)
            continue

        # keep tables/headers/lists as-is (except mojibake already fixed)
        if HEADER_RE.match(line) or TABLE_RE.match(line) or BULLET_RE.match(line) or ORDERED_LIST_RE.match(line):
            out_lines.append(line)
            continue

        if should_strip_num_prefix(line):
            new_line = strip_prefix(line)
            if new_line != line:
                changed = True
            out_lines.append(new_line)
        else:
            out_lines.append(line)

    fixed = "\n".join(out_lines)
    if not fixed.endswith("\n"):
        fixed += "\n"

    if fixed != text:
        changed = True

    if changed:
        path.write_text(fixed, encoding="utf-8")

    court_written = False
    if make_court_copy:
        court_path = path.with_name(path.stem + "_COURT.md")
        court_text = make_court_copy_text(fixed)
        court_path.write_text(court_text, encoding="utf-8")
        court_written = True

    return changed, court_written

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".", help="Root folder to scan (recursive)")
    ap.add_argument("--court", action="store_true", help="Also write *_COURT.md copies with [0001] numbering")
    ap.add_argument("--dry-run", action="store_true", help="Do not modify files; just print what would change")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"Not a directory: {root}")

    md_files = sorted(
        p for p in root.rglob("*.md")
        if p.is_file() and p.name != "REPORT.md" and not p.name.endswith("_COURT.md")
    )

    print(f"Root: {root}")
    print(f"Found {len(md_files)} .md files")
    changed_cnt = 0
    court_cnt = 0

    for i, p in enumerate(md_files, 1):
        if args.dry_run:
            # simulate by reading + processing, but don't write
            raw = p.read_bytes()
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("utf-8", errors="replace")
            text = normalize_text_best_effort(text).replace("\r\n", "\n").replace("\r", "\n")
            # quick check: mojibake or prefixes exist
            would_change = bool(MOJIBAKE_HINT_RE.search(text) or any(
                should_strip_num_prefix(line) for line in text.split("\n") if line
            ))
            if would_change:
                print(f"[{i}/{len(md_files)}] WOULD FIX: {p}")
                changed_cnt += 1
            continue

        orig_changed, court_written = fix_one_md(p, make_court_copy=args.court)
        if orig_changed:
            print(f"[{i}/{len(md_files)}] FIXED: {p}")
            changed_cnt += 1
        if court_written:
            court_cnt += 1

    print("\nDone.")
    print(f"Originals fixed: {changed_cnt}")
    if args.court:
        print(f"Court copies written: {court_cnt}")

if __name__ == "__main__":
    main()
