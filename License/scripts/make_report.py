#!/usr/bin/env python3
"""
Scan a folder for *.md files, compute SHA-256, create 3 OpenTimestamps receipts/proofs
(using 3 different calendars), attempt upgrade+verify, and write REPORT.md.

Outputs (per input file):
  <name>_1.ots, <name>_2.ots, <name>_3.ots
  REPORT.md

Usage:
  python3 make_report.py                # uses current working directory
  python3 make_report.py /path/to/dir

Notes:
- Fresh stamps are often "Pending confirmation in Bitcoin blockchain" for hours. That’s normal.
- For court-grade, you typically want a *confirmed* attestation (verify shows Success + block).
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

CALENDARS = [
    ("1", "https://a.pool.opentimestamps.org"),
    ("2", "https://b.pool.opentimestamps.org"),
    ("3", "https://a.pool.eternitywall.com"),
]


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
            "Install: pip install opentimestamps-client\n"
            "Ensure 'ots' is on PATH."
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

    # If output exists, skip (idempotent)
    if out_path.exists() and out_path.stat().st_size > 0:
        return

    # If a leftover default proof exists, remove it (avoid picking up stale output)
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
    Verification can require a local Bitcoin node (or specific client options).
    Also, default 'ots verify' infers target filename from proof name, so we try:
      1) ots verify <proof> -f <target>
      2) fallback: temporary copy named <target>.ots and plain ots verify
    """
    # Attempt 1: -f (seen in community docs)
    code, out, err = run_cmd(
        [ots, "verify", str(proof_path.name), "-f", str(target_file.name)],
        cwd=proof_path.parent,
    )
    if code == 0:
        return out or "Verified (no output)"

    # Attempt 2: fallback temp name matching expected convention: <target>.ots
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


def write_report(rows: List[Dict[str, str]], report_path: Path) -> None:
    cols = [
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
            f"| {md_escape(r['file'])} | `{r['file_sha256']}` | "
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

    md_files = sorted(p for p in target_dir.glob("*.md") if p.is_file() and p.name != "REPORT.md")
    total = len(md_files)

    print(f"Folder: {target_dir}")
    print(f"Found {total} markdown file(s).")

    rows: List[Dict[str, str]] = []

    for i, f in enumerate(md_files, start=1):
        print(f"\n[{i}/{total}] {f.name}")
        file_digest = sha256_file(f)
        row: Dict[str, str] = {"file": f.name, "file_sha256": file_digest}

        for idx, cal_url in CALENDARS:
            out_proof = target_dir / f"{f.stem}_{idx}.ots"
            print(f"  - stamping _{idx}.ots via {cal_url}")
            stamp_with_calendar(ots, f, cal_url, out_proof)

            # attempt upgrade (harmless if still pending)
            print(f"    upgrading: {out_proof.name}")
            _ = try_upgrade(ots, out_proof)

            # verify (may be pending / may require local bitcoin node)
            print(f"    verifying: {out_proof.name}")
            verify_out = try_verify(ots, out_proof, f)
            status = classify_verify_output(verify_out)

            row[f"ots{idx}_name"] = out_proof.name
            row[f"ots{idx}_sha256"] = sha256_file(out_proof)
            row[f"ots{idx}_verify"] = status

            # Optional: uncomment if you want full verify text in console
            # print("    verify output:", verify_out.replace("\n", " | "))

        rows.append(row)

    report_path = target_dir / "REPORT.md"
    write_report(rows, report_path)

    print(f"\nDone. Wrote {report_path} for {len(rows)} file(s).")
    print("If verify status is PENDING, rerun later (hours+) to get SUCCESS once confirmed on-chain.")


if __name__ == "__main__":
    main()
