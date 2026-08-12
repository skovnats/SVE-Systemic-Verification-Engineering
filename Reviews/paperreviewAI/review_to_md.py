#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import requests


API_URL_TEMPLATE = "https://paperreview.ai/api/review/{token}"


def iso_to_date(s: str | None) -> str:
    if not s:
        return "N/A"
    try:
        # "2025-11-29T13:47:27.571625" -> "2025-11-29"
        return s.split("T", 1)[0]
    except Exception:
        return s


def build_markdown(data: dict) -> str:
    title = data.get("title", "Untitled")
    venue = data.get("venue", "Unknown venue")
    submission_date = iso_to_date(data.get("submission_date"))
    review_date = iso_to_date(data.get("review_date"))

    sections = data.get("sections", {}) or {}
    summary = sections.get("summary", "").strip()
    strengths = sections.get("strengths", "").strip()
    weaknesses = sections.get("weaknesses", "").strip()
    detailed = sections.get("detailed_comments", "").strip()
    questions = sections.get("questions", "").strip()
    assessment = sections.get("assessment", "").strip()
    triple_scores = sections.get("binary_scores", "").strip() or data.get("numerical_score", "")

    md = []

    md.append(f"# 📄 Review: {title}\n")
    md.append(f"**Venue:** {venue} | **Submission Date:** {submission_date} | **Review Date:** {review_date}\n")
    md.append("-----\n")

    if summary:
        md.append("## 1. Summary\n")
        md.append(summary + "\n\n-----\n")

    if strengths or weaknesses:
        md.append("## 2. Strengths & Weaknesses\n")
        if strengths:
            md.append("### ✅ Strengths\n")
            md.append(strengths + "\n")
        if weaknesses:
            md.append("\n### ❌ Weaknesses\n")
            md.append(weaknesses + "\n")
        md.append("\n-----\n")

    if detailed:
        md.append("## 3. Detailed Technical Critique\n")
        md.append(detailed + "\n\n-----\n")

    if questions:
        md.append("## 4. Questions for Authors\n")
        md.append(questions + "\n\n-----\n")

    if assessment:
        md.append("## 5. Overall Assessment\n")
        md.append(assessment + "\n\n-----\n")

    if triple_scores:
        md.append("## 6. Scoring\n")
        md.append(triple_scores + "\n")

    return "".join(md)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch paper review from paperreview.ai and save as Markdown."
    )
    parser.add_argument("token", help="Review TOKEN")
    parser.add_argument(
        "-o",
        "--output",
        help="Output Markdown file (default: review_<TOKEN>.md)",
    )
    args = parser.parse_args()

    token = args.token.strip()
    url = API_URL_TEMPLATE.format(token=token)

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching review: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        data = resp.json()
    except json.JSONDecodeError:
        print("Error: response is not valid JSON.", file=sys.stderr)
        sys.exit(1)

    if not data.get("success", True):
        print(f"API returned error: {data}", file=sys.stderr)
        sys.exit(1)

    markdown = build_markdown(data)

    output_path = Path(args.output or f"review_{token}.md")
    output_path.write_text(markdown, encoding="utf-8")

    print(f"Saved Markdown review to: {output_path}")


if __name__ == "__main__":
    main()
