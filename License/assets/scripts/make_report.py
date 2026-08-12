#!/usr/bin/env python3
"""
Scan a folder for *.md files, PREPROCESS them (add line numbers if missing),
compute SHA-256, create 3 OpenTimestamps receipts/proofs, attempt upgrade+verify,
and write REPORT.md with extra registry columns.

New columns in REPORT.md:
- prefix (folder name)
- file_index_in_folder (1..N)
- date_added_to_registry (kept stable across reruns)

Outputs (per input file):
  <name>_1.ots, <name>_2.ots, <name>_3.ots
  REPORT.md

Usage:
  python3 make_report.py                # uses current working directory
  python3 make_report.py /path/to/dir
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional

CALENDARS = [
    ("1", "https://a.pool.opentimestamps.org"),
    ("2", "https://b.pool.opentimestamps.org"),
    ("3", "https://a.pool.eternitywall.com"),
]

LINE_NUM_WIDTH = 5  # 00001:
LINE_NUM_SEP = ": "


def now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path, buf_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(buf_size), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_ots_cli() -> str:
    ots = shutil.which("ots")
    if not ots:
        raise SystemExit(
            "ERROR: 'ots' CLI not found.\n"
            "Install it with: pip install opentimestamps-client\n"
            "Then ensure your PATH includes the 'ots' executable."
        )
    return ots


def run_cmd(cmd: List[str], cwd: Path) -> Tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def stamp_with_calendar(ots: str, file_path: Path, calendar_url: str, out_path: Path) -> None:
    """
    Runs: ots stamp -c <calendar> -m 1 <file>
    which creates <file>.ots next to the file; then we move it to out_path.
    """
    default_proof = file_path.with_name(file_path.name + ".ots")

    if out_path.exists() and out_path.stat().st_size > 0:
        return

    if default_proof.exists():
        default_proof.unlink()

    code, out, err = run_cmd(
        [ots, "stamp", "-c", calendar_url, "-m", "1", str(file_path.name)],
        cwd=file_path.parent,
    )
    if code != 0:
        raise SystemExit(
            f"ERROR stamping {file_path.name} via {calendar_url}\n"
            f"stdout:\n{out}\n\nstderr:\n{err}"
        )

    if not default_proof.exists():
        raise SystemExit(f"ERROR: expected proof not created: {default_proof.name}")

    default_proof.replace(out_path)


def try_upgrade(ots: str, proof_path: Path) -> str:
    code, out, err = run_cmd([ots, "upgrade", str(proof_path.name)], cwd=proof_path.parent)
    if code == 0 and out:
        return out
    if code == 0 and not out:
        return "Upgraded (no output)"
    return f"UPGRADE_ERROR: {err or out or 'unknown'}"


def try_verify(ots: str, proof_path: Path, target_file: Path) -> str:
    """
    Try:
      1) ots verify <proof> -f <target>
      2) fallback: temporary copy named <target>.ots and plain ots verify
    """
    code, out, err = run_cmd(
        [ots, "verify", str(proof_path.name), "-f", str(target_file.name)],
        cwd=proof_path.parent,
    )
    if code == 0:
        return out or "Verified (no output)"

    tmp = target_file.with_name(target_file.name + ".ots")
    try:
        if tmp.exists():
            tmp.unlink()
        shutil.copy2(proof_path, tmp)

        code2, out2, err2 = run_cmd([ots, "verify", str(tmp.name)], cwd=proof_path.parent)
        if code2 == 0:
            return out2 or "Verified (no output)"
        return f"VERIFY_ERROR: {err2 or out2 or err or out or 'unknown'}"
    finally:
        if tmp.exists():
            tmp.unlink()


def classify_verify_output(s: str) -> str:
    s_low = s.lower()
    if "success!" in s_low:
        return "SUCCESS"
    if "pending confirmation" in s_low:
        return "PENDING"
    if s_low.startswith("verify_error"):
        return "ERROR"
    return "UNKNOWN"


def md_escape(text: str) -> str:
    return text.replace("|", r"\|")


# ---------------------------
# Preprocessing: smart line numbers
# ---------------------------

LINE_FMT = "[{num:04d}] "

_CODEBLOCK_RE = re.compile(r"^```")
_TABLE_RE = re.compile(r"^\s*\|")
_LIST_RE = re.compile(r"^\s*([-*+]|\d+\.)\s+")
_HEADER_RE = re.compile(r"^\s*#{1,6}\s+")

_EXISTING_NUM_RE = re.compile(r"^\s*(\[\d{1,6}\]|\d{1,6}[:.)])\s+")


def has_nice_line_numbers(text: str) -> bool:
    """
    Detect already nicely formatted numbers like [0001]
    """
    lines = [l for l in text.splitlines() if l.strip()]
    if len(lines) < 5:
        return False
    hits = sum(1 for l in lines[:20] if re.match(r"^\[\d{4,6}\]\s+", l))
    return hits >= max(3, int(0.6 * min(20, len(lines))))


def add_or_fix_line_numbers(md_path: Path) -> bool:
    """
    Add or normalize line numbers without breaking Markdown.
    Returns True if file was modified.
    """
    original = md_path.read_text(encoding="utf-8", errors="replace")

    # If already nicely numbered → skip
    if has_nice_line_numbers(original):
        return False

    lines = original.splitlines(keepends=True)
    out = []
    in_codeblock = False
    counter = 1
    changed = False

    for line in lines:
        stripped = line.lstrip()

        # Toggle code block
        if _CODEBLOCK_RE.match(stripped):
            in_codeblock = not in_codeblock
            out.append(line)
            continue

        # Never touch code blocks, tables, headers, lists, empty lines
        if (
            in_codeblock
            or not stripped.strip()
            or _TABLE_RE.match(stripped)
            or _HEADER_RE.match(stripped)
            or _LIST_RE.match(stripped)
        ):
            out.append(line)
            continue

        # Remove ugly existing numbering if present
        new_line = re.sub(_EXISTING_NUM_RE, "", line)
        prefix = LINE_FMT.format(num=counter)
        out.append(prefix + new_line.lstrip())
        counter += 1
        changed = True

    if changed:
        md_path.write_text("".join(out), encoding="utf-8")

    return changed


def add_line_numbers_if_missing(md_path: Path) -> bool:
    """
    If file doesn't appear to have line numbers, rewrite it with:
      00001: <original line>
    Returns True if file changed.
    """
    original = md_path.read_text(encoding="utf-8", errors="replace")
    if has_line_numbers(original):
        return False

    lines = original.splitlines(keepends=True)
    out_lines = []
    for i, line in enumerate(lines, start=1):
        prefix = f"{i:0{LINE_NUM_WIDTH}d}{LINE_NUM_SEP}"
        out_lines.append(prefix + line)

    md_path.write_text("".join(out_lines), encoding="utf-8")
    return True


# ---------------------------
# Existing registry parsing
# ---------------------------

def _split_md_row(line: str) -> List[str]:
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return []
    s = s[1:-1]
    cells: List[str] = []
    cur = []
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


def _is_sep_row(cells: List[str]) -> bool:
    if not cells:
        return False
    for c in cells:
        t = c.replace(":", "").replace("-", "").strip()
        if t != "":
            return False
    return True


def load_existing_dates(report_path: Path) -> Dict[str, str]:
    """
    If REPORT.md exists, parse table and return {File -> date_added_to_registry}.
    """
    if not report_path.exists():
        return {}

    txt = report_path.read_text(encoding="utf-8", errors="replace").splitlines()
    header: Optional[List[str]] = None
    file_col = None
    date_col = None
    in_table = False
    out: Dict[str, str] = {}

    for line in txt:
        cells = _split_md_row(line)
        if not cells:
            continue
        if header is None:
            header = cells
            in_table = True
            continue
        if in_table and _is_sep_row(cells):
            # separator
            continue
        if in_table and header:
            # data row
            if file_col is None:
                # determine indices once
                try:
                    file_col = header.index("File")
                except ValueError:
                    return {}
                try:
                    date_col = header.index("date_added_to_registry")
                except ValueError:
                    # older report: no column
                    return {}

            if len(cells) <= max(file_col, date_col):
                continue

            fname = cells[file_col]
            date_added = cells[date_col]
            if fname and date_added:
                out[fname] = date_added

    return out


# ---------------------------
# Report writing
# ---------------------------

def write_report(rows: List[Dict[str, str]], report_path: Path) -> None:
    cols = [
        "prefix",
        "file_index_in_folder",
        "date_added_to_registry",
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
    ]

    lines = ["# REPORT", "", "| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]

    for r in rows:
        line = (
            f"| {md_escape(r['prefix'])} | {md_escape(r['file_index_in_folder'])} | {md_escape(r['date_added_to_registry'])} | "
            f"{md_escape(r['file'])} | `{r['file_sha256']}` | "
            f"{md_escape(r['ots1_name'])} | `{r['ots1_sha256']}` | {md_escape(r['ots1_verify'])} | "
            f"{md_escape(r['ots2_name'])} | `{r['ots2_sha256']}` | {md_escape(r['ots2_verify'])} | "
            f"{md_escape(r['ots3_name'])} | `{r['ots3_sha256']}` | {md_escape(r['ots3_verify'])} |"
        )
        lines.append(line)

    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("path", nargs="?", default=".", help="Folder to scan + write outputs (default: pwd)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    target_dir = Path(args.path).expanduser().resolve()

    if not target_dir.exists() or not target_dir.is_dir():
        raise SystemExit(f"ERROR: not a directory: {target_dir}")

    ots = ensure_ots_cli()

    report_path = target_dir / "REPORT.md"
    existing_dates = load_existing_dates(report_path)

    md_files = sorted(p for p in target_dir.glob("*.md") if p.is_file() and p.name != "REPORT.md")
    total = len(md_files)

    print(f"Folder: {target_dir}")
    print(f"Found {total} markdown file(s).")

    # Preprocess: add line numbers if missing
    changed = 0
    for i, f in enumerate(md_files, start=1):
        did = add_or_fix_line_numbers(f)
        if did:
            changed += 1
            print(f"[preprocess] Added line numbers: {f.name}")
    if changed:
        print(f"[preprocess] Updated {changed}/{total} file(s).")

    prefix = target_dir.name
    rows: List[Dict[str, str]] = []

    for i, f in enumerate(md_files, start=1):
        print(f"\n[{i}/{total}] {f.name}")

        # stable date_added if already in report
        date_added = existing_dates.get(f.name) or now_iso_utc()

        file_digest = sha256_file(f)
        row: Dict[str, str] = {
            "prefix": prefix,
            "file_index_in_folder": str(i),
            "date_added_to_registry": date_added,
            "file": f.name,
            "file_sha256": file_digest,
        }

        for idx, cal_url in CALENDARS:
            out_proof = target_dir / f"{f.stem}_{idx}.ots"
            print(f"  - stamping _{idx}.ots via {cal_url}")
            stamp_with_calendar(ots, f, cal_url, out_proof)

            print(f"    upgrading: {out_proof.name}")
            _ = try_upgrade(ots, out_proof)

            print(f"    verifying: {out_proof.name}")
            verify_out = try_verify(ots, out_proof, f)
            status = classify_verify_output(verify_out)

            row[f"ots{idx}_name"] = out_proof.name
            row[f"ots{idx}_sha256"] = sha256_file(out_proof)
            row[f"ots{idx}_verify"] = status

        rows.append(row)

    write_report(rows, report_path)

    print(f"\nDone. Wrote {report_path} for {len(rows)} file(s).")
    print("If verify status is PENDING, rerun later (hours+) to get SUCCESS once confirmed on-chain.")


if __name__ == "__main__":
    main()
