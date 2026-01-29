#!/usr/bin/env python3
"""
Recursively verify all .ots files under a folder.

Two naming types (per your workflow):
TYPE 1: <target_filename>.ots         -> target is <target_filename>
TYPE 2: <target_stem>_<n>.ots         -> target is <target_stem>.md

Robustness:
- Uses absolute paths for ots CLI calls
- Optional upgrade step
- Never crashes if receipts disappear mid-run; records ERROR and continues
- Writes VERIFIED_OTS_REPORT.md in root

Usage:
  python3 verify_all_ots.py
  python3 verify_all_ots.py /path/to/root
  python3 verify_all_ots.py /path/to/root --no-upgrade
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


TYPE2_RE = re.compile(r"^(?P<stem>.+)_(?P<n>\d+)\.ots$", re.IGNORECASE)

EXCLUDE_SUBSTRINGS = [
    "_SVE-Systemic-Verification-Engineering_License_SIGNED",
]

def is_excluded(path: Path) -> bool:
    name = path.name
    return any(excl in name for excl in EXCLUDE_SUBSTRINGS)



@dataclass
class Result:
    proof: Path
    target: Optional[Path]
    ots_type: str
    status: str
    detail: str


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


def classify_verify_output(s: str) -> str:
    t = s.lower()
    if "success!" in t:
        return "SUCCESS"
    if "pending confirmation" in t:
        return "PENDING"
    if "error" in t or "failed" in t:
        return "ERROR"
    return "UNKNOWN"


def try_upgrade(ots: str, proof: Path) -> Path:
    """
    Best-effort upgrade. Some versions may rewrite/replace the file.
    Return a path that exists if possible; otherwise return original (caller handles missing).
    """
    proof = proof.resolve()
    run_cmd([ots, "upgrade", str(proof)], cwd=proof.parent)

    if proof.exists():
        return proof

    # conservative: exact-name glob (in case FS casing etc.)
    exact = list(proof.parent.glob(proof.name))
    if exact:
        return exact[0].resolve()

    return proof


def verify_with_target(ots: str, proof: Path, target: Path) -> Tuple[str, str]:
    """
    Try:
      1) ots verify <proof> -f <target>
      2) fallback: copy proof to <target>.ots and run ots verify <target>.ots
    Never raises; returns (status, detail).
    """
    proof = proof.resolve()
    target = target.resolve()

    if not proof.exists():
        return "ERROR", "Proof file missing (may have been rewritten/removed by upgrade/verify). Try --no-upgrade."

    # Attempt 1: explicit target
    code, out, err = run_cmd([ots, "verify", str(proof), "-f", str(target)], cwd=proof.parent)
    if code == 0:
        detail = out or "Verified (no output)"
        return classify_verify_output(detail), detail

    # Attempt 2: fallback
    tmp = target.with_name(target.name + ".ots")
    try:
        if tmp.exists():
            tmp.unlink()

        # proof can disappear between checks; handle it
        try:
            shutil.copy2(proof, tmp)
        except FileNotFoundError:
            return "ERROR", "Proof file disappeared before fallback copy (race). Rerun; preferably with --no-upgrade."

        code2, out2, err2 = run_cmd([ots, "verify", str(tmp.resolve())], cwd=proof.parent)
        if code2 == 0:
            detail2 = out2 or "Verified (no output)"
            return classify_verify_output(detail2), detail2

        detail_err = err2 or out2 or err or out or "unknown"
        return "ERROR", f"VERIFY_ERROR: {detail_err}"
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass


def infer_target_and_type(proof: Path) -> Tuple[Optional[Path], str]:
    """
    TYPE 1: <target>.ots -> target is proof name without ".ots" IF file exists
    TYPE 2: <stem>_<n>.ots -> target is <stem>.md IF exists
    """
    proof = proof.resolve()

    # TYPE 1
    target1 = proof.with_name(proof.name[:-4])  # strip ".ots"
    if target1.exists() and target1.is_file():
        return target1, "TYPE_1:<target>.ots"

    # TYPE 2
    m = TYPE2_RE.match(proof.name)
    if m:
        stem = m.group("stem")
        target2 = proof.parent / f"{stem}.md"
        if target2.exists() and target2.is_file():
            return target2, "TYPE_2:<stem>_<n>.ots -> <stem>.md"
        return None, "TYPE_2:TARGET_<stem>.md_NOT_FOUND"

    return None, "UNKNOWN_TYPE"


def md_escape(s: str) -> str:
    return s.replace("|", r"\|")


def write_report(root: Path, results: List[Result], out_name: str = "VERIFIED_OTS_REPORT.md") -> Path:
    root = root.resolve()
    out = root / out_name
    lines = [
        "# OTS Verification Report",
        "",
        "| Proof (.ots) | Target | Type | Status | Detail |",
        "|---|---|---|---|---|",
    ]

    for r in results:
        detail_clean = r.detail.replace("\n", " ")
        # best-effort relative paths (proof may be missing)
        try:
            proof_rel = str(r.proof.resolve().relative_to(root))
        except Exception:
            proof_rel = str(r.proof)

        if r.target:
            try:
                target_rel = str(r.target.resolve().relative_to(root))
            except Exception:
                target_rel = str(r.target)
        else:
            target_rel = ""

        lines.append(
            f"| {md_escape(proof_rel)} | {md_escape(target_rel)} | "
            f"{md_escape(r.ots_type)} | {md_escape(r.status)} | {md_escape(detail_clean)} |"
        )

    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("path", nargs="?", default=".", help="Root folder to scan (default: pwd)")
    p.add_argument("--no-upgrade", action="store_true", help="Skip 'ots upgrade' step")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"ERROR: not a directory: {root}")

    ots = ensure_ots_cli()

    proofs = sorted(p for p in root.rglob("*.ots") if p.is_file() and not is_excluded(p))

    total = len(proofs)

    print(f"Root: {root}")
    print(f"Found {total} .ots file(s).")
    

    results: List[Result] = []
    counts = {"SUCCESS": 0, "PENDING": 0, "ERROR": 0, "UNKNOWN": 0}

    for i, proof in enumerate(proofs, 1):
        rel = proof.relative_to(root)
        print(f"[{i}/{total}] {rel}")

        target, ots_type = infer_target_and_type(proof)

        if not args.no_upgrade:
            proof = try_upgrade(ots, proof)

        if target is None:
            results.append(
                Result(
                    proof=proof,
                    target=None,
                    ots_type=ots_type,
                    status="ERROR",
                    detail="Target not found for this .ots naming scheme",
                )
            )
            counts["ERROR"] += 1
            continue

        status, detail = verify_with_target(ots, proof, target)
        if status not in counts:
            status = "UNKNOWN"
        counts[status] += 1
        results.append(Result(proof=proof, target=target, ots_type=ots_type, status=status, detail=detail))

    out = write_report(root, results)

    print("\nSummary:")
    print(f"  SUCCESS: {counts['SUCCESS']}")
    print(f"  PENDING: {counts['PENDING']}")
    print(f"  ERROR:   {counts['ERROR']}")
    print(f"  UNKNOWN: {counts['UNKNOWN']}")
    print(f"\nWrote report: {out}")
    print("Tip: For evidence runs, prefer: --no-upgrade (so receipts don’t mutate mid-audit).")


if __name__ == "__main__":
    main()
