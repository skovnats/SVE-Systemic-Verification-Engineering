#!/usr/bin/env python3
"""
Scan current folder for *.md files, compute SHA-256, create OpenTimestamps proof (.ots),
and write REPORT.md with a table.

Requirements:
  - Python 3.8+
  - OpenTimestamps client installed and on PATH:
      pip install opentimestamps-client
    (provides: ots)

Usage:
  python3 make_report.py
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple


def sha256_file(path: Path, buf_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(buf_size)
            if not chunk:
                break
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


def make_ots_proof(ots_cli: str, file_path: Path, proof_path: Path) -> None:
    # Create proof only if missing (idempotent)
    if proof_path.exists() and proof_path.stat().st_size > 0:
        return

    # ots stamp <file> creates <file>.ots
    try:
        subprocess.run(
            [ots_cli, "stamp", str(file_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise SystemExit(
            f"ERROR: failed to create timestamp proof for {file_path.name}\n"
            f"stdout:\n{e.stdout}\n\nstderr:\n{e.stderr}"
        ) from e

    if not proof_path.exists():
        raise SystemExit(
            f"ERROR: expected proof file not found after stamping: {proof_path.name}"
        )


def md_escape(text: str) -> str:
    # Escape pipes for markdown tables
    return text.replace("|", r"\|")


def write_report(rows: List[Tuple[str, str, str]], report_path: Path) -> None:
    lines = []
    lines.append("# REPORT\n")
    lines.append("")
    lines.append("| File | SHA-256 | Timestamp Proof (.ots) |")
    lines.append("|---|---|---|")
    for fname, digest, ots_name in rows:
        lines.append(f"| {md_escape(fname)} | `{digest}` | {md_escape(ots_name)} |")
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    here = Path(__file__).resolve().parent
    os.chdir(here)

    ots_cli = ensure_ots_cli()

    md_files = sorted(
        [p for p in here.glob("*.md") if p.is_file() and p.name != "REPORT.md"]
    )

    rows: List[Tuple[str, str, str]] = []
    for p in md_files:
        digest = sha256_file(p)
        proof = p.with_name(p.name + ".ots")  # e.g. foo.md.ots
        make_ots_proof(ots_cli, p, proof)
        rows.append((p.name, digest, proof.name))

    write_report(rows, here / "REPORT.md")
    print(f"Done. Wrote REPORT.md for {len(rows)} file(s).")


if __name__ == "__main__":
    main()
