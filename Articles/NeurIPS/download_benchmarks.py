#!/usr/bin/env python3
"""
Download and normalize all 9 benchmarks for TIK evaluation.
Each benchmark → unified format: list of dicts with 'question', 'options', 'metadata'.

V2: Also downloads HUMAN RESPONSE / DISAGREEMENT data where available.

┌─────────────────────┬──────────────────────────────────────────────────────────┐
│ Benchmark           │ Human Disagreement Data Available?                      │
├─────────────────────┼──────────────────────────────────────────────────────────┤
│ Moral Machine       │ ✅ RICH — 40M+ individual responses with demographics   │
│                     │    (OSF: SharedResponses.csv, or HF: Jerry999/...)      │
│ Scruples            │ ✅ RICH — label distributions per anecdote              │
│                     │    (AUTHOR/OTHER/EVERYBODY/NOBODY/INFO counts)          │
│ Social Chemistry    │ ✅ GOOD — rot-agree (0-4 ordinal), action-agree,        │
│                     │    m={1,3,5,50} multi-annotator subsets                 │
│ ETHICS              │ ⚠️  PARTIAL — has "hard" test sets (ambiguous cases);   │
│                     │    binary labels only, no per-annotator breakdown       │
│ TruthfulQA          │ ❌ NONE — single gold labels                            │
│ CommonsenseQA        │ ❌ NONE — single gold labels                            │
│ MMLU-Ethics         │ ❌ NONE — single gold labels                            │
│ Moral Stories       │ ❌ NONE — single gold labels                            │
│ GAIA                │ ❌ NONE — single gold labels                            │
└─────────────────────┴──────────────────────────────────────────────────────────┘

For TIK validation (disagreement–refusal correspondence), focus on:
  1. Moral Machine  — per-scenario response distributions
  2. Scruples       — per-anecdote label distributions (entropy)
  3. Social Chemistry — rot-agree + multi-annotator subsets (m≥5)
"""

import os
import json
import csv
import random
import subprocess
from pathlib import Path
from typing import Optional
import tarfile
import urllib.request
import pandas as pd
import yaml
from math import log2

random.seed(1984)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_config(path: str = "configs/experiment.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def ensure_dir(path: str):
    Path(path).mkdir(parents=True, exist_ok=True)

def sample_questions(questions: list, n: Optional[int]) -> list:
    if n is None or len(questions) <= n:
        return questions
    return random.sample(questions, n)

def save_unified(questions: list, output_path: str):
    ensure_dir(os.path.dirname(output_path))
    with open(output_path, "w") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    print(f"  → Saved {len(questions)} questions to {output_path}")


def compute_entropy(distribution: dict) -> float:
    """
    Compute Shannon entropy of a label distribution (in bits).
    Higher entropy = more disagreement among annotators.
    
    Example: {"AUTHOR": 15, "OTHER": 5, "NOBODY": 0, "EVERYBODY": 0, "INFO": 0}
    → entropy measures how "split" the votes are.
    """
    total = sum(distribution.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in distribution.values():
        if count > 0:
            p = count / total
            entropy -= p * log2(p)
    return round(entropy, 4)


# ---------------------------------------------------------------------------
# Downloaders (each returns list of unified question dicts)
# ---------------------------------------------------------------------------

def download_ethics(cfg: dict) -> list:
    """
    ETHICS (Hendrycks et al., 2021) — Direct tar.gz download from Berkeley.

    HUMAN DISAGREEMENT: ⚠️ PARTIAL
    - No per-annotator breakdown in standard download.
    - BUT: "hard" test sets contain more ambiguous/contested cases.
    - We download BOTH regular and hard test sets and flag which is which.
    - For TIK validation: hard set items are a proxy for "contested" questions.
    """
    local = cfg["local_path"]
    ensure_dir(local)

    archive_url = "https://people.eecs.berkeley.edu/~hendrycks/ethics.tar.gz"
    archive_path = os.path.join(local, "ethics.tar.gz")
    target_folder = os.path.join(local, "ethics")

    if not os.path.exists(target_folder):
        print(f"  → Downloading ETHICS archive from Berkeley (~10 MB)…")
        try:
            urllib.request.urlretrieve(archive_url, archive_path)
        except Exception as e:
            print(f"  ✗ Download failed: {e}")
            return []
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=local)
        os.remove(archive_path)
        print(f"  → Extracted to {target_folder}")
    else:
        print(f"  → Found existing data at {target_folder}, skipping download.")

    subset_map = {
        "commonsense":    ("cm_test.csv",          "input"),
        "deontology":     ("deontology_test.csv",  "scenario"),
        "justice":        ("justice_test.csv",     "scenario"),
        "virtue":         ("virtue_test.csv",      "scenario"),
        "utilitarianism": ("util_test.csv",        None),
    }

    # V2: Also map hard test files (these contain more ambiguous cases)
    hard_map = {
        "commonsense":    "cm_test_hard.csv",
        "deontology":     "deontology_test_hard.csv",
        "justice":        "justice_test_hard.csv",
        "virtue":         "virtue_test_hard.csv",
        "utilitarianism": "util_test_hard.csv",
    }

    subsets = cfg.get("subsets", list(subset_map.keys()))

    questions = []
    for subset in subsets:
        if subset not in subset_map:
            print(f"  ⚠ Unknown subset '{subset}' — skipping (valid: {list(subset_map.keys())})")
            continue
        fname, text_col = subset_map[subset]
        csv_path = os.path.join(target_folder, subset, fname)

        if not os.path.exists(csv_path):
            print(f"  ⚠ Missing: {csv_path} — skipping subset '{subset}'")
            continue

        # ── V2: Check for hard test set ──────────────────────────────
        hard_ids = set()
        hard_fname = hard_map.get(subset)
        if hard_fname:
            hard_path = os.path.join(target_folder, subset, hard_fname)
            if os.path.exists(hard_path):
                hard_df = pd.read_csv(hard_path)
                # Store the text of hard examples for matching
                if text_col and text_col in hard_df.columns:
                    hard_ids = set(hard_df[text_col].dropna().astype(str).str.strip())
                elif text_col is None and len(hard_df.columns) >= 2:
                    # For utilitarianism, use combined text as key
                    cols = hard_df.columns.tolist()
                    hard_ids = set(
                        str(row[cols[0]]).strip() + "|||" + str(row[cols[1]]).strip()
                        for _, row in hard_df.iterrows()
                        if pd.notna(row[cols[0]]) and pd.notna(row[cols[1]])
                    )
                print(f"  · {subset}: found {len(hard_ids)} hard (ambiguous) examples")

        df = pd.read_csv(csv_path)

        if text_col is not None and text_col not in df.columns:
            fallback = "input" if text_col == "scenario" else "scenario"
            if fallback in df.columns:
                print(f"  ⚠ Column '{text_col}' not found in {subset}, using '{fallback}'")
                text_col = fallback
            else:
                print(f"  ✗ No text column found in {subset} (columns: {list(df.columns)})")
                continue

        before = len(questions)
        for i, row in df.iterrows():
            if text_col is None:
                cols = df.columns.tolist()
                if len(cols) < 2:
                    print(f"  ✗ Utilitarianism CSV has fewer than 2 columns: {cols}")
                    break
                sent_a, sent_b = str(row[cols[0]]).strip(), str(row[cols[1]]).strip()
                if pd.notna(row[cols[0]]) and pd.notna(row[cols[1]]):
                    combined_key = sent_a + "|||" + sent_b
                    questions.append({
                        "id":        f"ethics_{subset}_{i}",
                        "question":  f"Which action is more morally acceptable?\nA: {sent_a}\nB: {sent_b}",
                        "options":   [sent_a, sent_b],
                        "benchmark": "ETHICS",
                        "subset":    subset,
                        "label":     None,
                        # V2: human disagreement proxy
                        "is_hard":   combined_key in hard_ids,
                        "human_disagreement": {
                            "source": "hard_test_membership",
                            "note": "Hard test items were identified by authors as more ambiguous/contested",
                        },
                    })
                continue

            text = row.get(text_col)
            if pd.notna(text) and str(text).strip():
                text_str = str(text).strip()
                questions.append({
                    "id":        f"ethics_{subset}_{i}",
                    "question":  text_str,
                    "benchmark": "ETHICS",
                    "subset":    subset,
                    "label":     int(row["label"]) if pd.notna(row.get("label")) else None,
                    # V2: human disagreement proxy
                    "is_hard":   text_str in hard_ids,
                    "human_disagreement": {
                        "source": "hard_test_membership",
                        "note": "Hard test items were identified by authors as more ambiguous/contested",
                    },
                })
        print(f"  · {subset}: {len(questions) - before} questions loaded")

    return sample_questions(questions, cfg.get("n_sample"))


def download_truthfulqa(cfg: dict) -> list:
    """
    TruthfulQA (Lin et al., 2021)
    
    HUMAN DISAGREEMENT: ❌ NONE
    Single gold labels only. No per-annotator breakdown.
    """
    repo = "https://github.com/sylinrl/TruthfulQA.git"
    local = cfg["local_path"]
    ensure_dir(local)

    if not os.path.exists(os.path.join(local, "TruthfulQA")):
        subprocess.run(["git", "clone", "--depth", "1", repo, os.path.join(local, "TruthfulQA")], check=True)

    questions = []
    csv_path = os.path.join(local, "TruthfulQA", "TruthfulQA.csv")
    if os.path.exists(csv_path):
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                questions.append({
                    "id": f"truthfulqa_{i}",
                    "question": row.get("Question", ""),
                    "best_answer": row.get("Best Answer", ""),
                    "category": row.get("Category", ""),
                    "benchmark": "TruthfulQA",
                    "source": "lin2021truthfulqa",
                    # V2: no disagreement data
                    "human_disagreement": None,
                })
    return questions


def download_mmlu_ethics(cfg: dict) -> list:
    """
    MMLU Ethics (Hendrycks et al.)
    
    HUMAN DISAGREEMENT: ❌ NONE
    Single gold labels only.
    """
    try:
        from datasets import load_dataset
        questions = []
        for subset in ["moral_scenarios", "moral_disputes"]:
            ds = load_dataset("cais/mmlu", subset, split="test")
            for i, item in enumerate(ds):
                questions.append({
                    "id": f"mmlu_{subset}_{i}",
                    "question": item["question"],
                    "options": item["choices"],
                    "answer": item["answer"],
                    "benchmark": "MMLU-Ethics",
                    "human_disagreement": None,
                })
        return questions
    except Exception as e:
        print(f"  Error loading MMLU subset: {e}")
        return []


def download_social_chemistry(cfg: dict) -> list:
    """
    Social Chemistry 101 (Forbes et al., 2020)
    
    HUMAN DISAGREEMENT: ✅ GOOD
    Key fields for TIK validation:
      - rot-agree (0-4): "What portion of people probably agree that ${rot}?"
          0 = <1%, 1 = 5-25%, 2 = 50%, 3 = 75-90%, 4 = >99%
      - rot-judgment (-2 to 2): very bad → very good
      - action-agree (0-4): agreement on the action being judged as stated
      - action-pressure (-2 to 2): cultural pressure (strong against → strong for)
      - action-moral-judgment (-2 to 2): moral judgment of the action
      - rot-categorization: morality-ethics | social-norms | advice | description
      - n-workers (m): {1, 3, 5, 50} — how many annotated this RoT
      
    For disagreement analysis:
      - LOW rot-agree (0-1) = high disagreement = potential Ontological Hole
      - m ≥ 5 subsets have true multi-annotator data for Krippendorff's α
      - m = 50 subset has maximally controversial RoTs (hand-picked for disagreement)
    """
    try:
        from datasets import load_dataset
        ds = load_dataset("tasksource/social-chemestry-101", split="train")
        questions = []
        for i, item in enumerate(ds):
            # ── V2: Extract ALL human judgment fields ──────────────────
            rot_agree = item.get("rot-agree")
            rot_judgment = item.get("rot-judgment")
            action_agree = item.get("action-agree")
            action_pressure = item.get("action-pressure")
            action_moral_judgment = item.get("action-moral-judgment")
            rot_categorization = item.get("rot-categorization")
            n_workers = item.get("n-workers") or item.get("m")
            split = item.get("split", "")

            questions.append({
                "id": f"social_chem_{i}",
                "question": item.get("situation", ""),
                "rot": item.get("rot", ""),
                "benchmark": "Social Chemistry",
                # ── V2: Full human disagreement data ──
                "human_disagreement": {
                    "source": "worker_annotations",
                    "rot_agree": rot_agree,           # 0-4 ordinal
                    "rot_judgment": rot_judgment,      # -2 to 2
                    "action_agree": action_agree,      # 0-4 ordinal
                    "action_pressure": action_pressure,
                    "action_moral_judgment": action_moral_judgment,
                    "rot_categorization": rot_categorization,
                    "n_workers": n_workers,
                    "split": split,
                    # Flag: is this from the high-disagreement subset?
                    "is_controversial_subset": (
                        split in ("dev-extra", "test-extra", "analysis")
                        or (n_workers is not None and int(n_workers) >= 5)
                    ),
                },
            })
        return sample_questions(questions, cfg.get("n_sample"))
    except Exception as e:
        print(f"  Warning: Could not load Social Chemistry: {e}")
        return []


def download_moral_stories(cfg: dict) -> list:
    """
    Moral Stories (Emelin et al.)
    
    HUMAN DISAGREEMENT: ❌ NONE
    Single gold labels.
    """
    try:
        from datasets import load_dataset
        ds = load_dataset("demelin/moral_stories", "default", split="train", revision="refs/convert/parquet")
        questions = []
        for i, item in enumerate(ds):
            if item.get("task") == "action_trajectory" or "task" not in item:
                questions.append({
                    "id": f"moral_stories_{i}",
                    "question": item.get("situation") or item.get("norm", ""),
                    "benchmark": "Moral Stories",
                    "human_disagreement": None,
                })
        return sample_questions(questions, cfg.get("n_sample"))
    except Exception as e:
        print(f"  Warning: Could not load Moral Stories: {e}")
        return []


def download_commonsenseqa(cfg: dict) -> list:
    """
    CommonsenseQA (Talmor et al., 2019)
    
    HUMAN DISAGREEMENT: ❌ NONE
    Single gold labels.
    """
    local = cfg["local_path"]
    ensure_dir(local)
    
    try:
        from datasets import load_dataset
        ds = load_dataset("commonsense_qa", split="validation")
        questions = []
        for i, item in enumerate(ds):
            questions.append({
                "id": f"csqa_{i}",
                "question": item["question"],
                "options": item["choices"]["text"],
                "answer_key": item["answerKey"],
                "benchmark": "CommonsenseQA",
                "source": "talmor2019commonsenseqa",
                "human_disagreement": None,
            })
        return sample_questions(questions, cfg.get("n_sample"))
    except Exception as e:
        print(f"  Warning: Could not load CommonsenseQA from HuggingFace: {e}")
        print("  Try: pip install datasets")
        return []


def download_scruples(cfg: dict) -> list:
    """
    Scruples (Lourie et al., 2021)
    
    HUMAN DISAGREEMENT: ✅ RICH — This is your BEST benchmark for TIK validation.
    
    The Scruples dataset was specifically designed to study moral disagreement.
    It has TWO sub-datasets:
    
    1. ANECDOTES (32K): Real r/AmITheAsshole posts with label distributions:
       - Labels: AUTHOR (author is wrong), OTHER (other person wrong),
                 EVERYBODY, NOBODY, INFO (need more info)
       - Each anecdote has COUNTS per label from community votes.
       - The label_scores field contains the full distribution.
       → Compute entropy of label_scores for disagreement measure.
       
    2. DILEMMAS (10K): Paired actions with worker votes on which is less ethical.
       → Each pair has vote counts; close splits = high disagreement.
       
    Download links (from the GitHub README):
       Anecdotes: https://storage.googleapis.com/ai2-mosaic-public/projects/scruples/v1.0/data/anecdotes.tar.gz
       Dilemmas:  https://storage.googleapis.com/ai2-mosaic-public/projects/scruples/v1.0/data/dilemmas.tar.gz
    """
    local = cfg["local_path"]
    ensure_dir(local)

    questions = []

    # ── V2: Download Anecdotes (with label distributions) ─────────
    anecdotes_url = "https://storage.googleapis.com/ai2-mosaic-public/projects/scruples/v1.0/data/anecdotes.tar.gz"
    anecdotes_dir = os.path.join(local, "scruples_anecdotes")
    anecdotes_archive = os.path.join(local, "anecdotes.tar.gz")

    if not os.path.exists(anecdotes_dir):
        print(f"  → Downloading Scruples Anecdotes (~40 MB)…")
        try:
            urllib.request.urlretrieve(anecdotes_url, anecdotes_archive)
            ensure_dir(anecdotes_dir)
            with tarfile.open(anecdotes_archive, "r:gz") as tar:
                tar.extractall(path=anecdotes_dir)
            os.remove(anecdotes_archive)
            print(f"  → Extracted anecdotes to {anecdotes_dir}")
        except Exception as e:
            print(f"  ⚠ Could not download Scruples Anecdotes: {e}")
            print(f"  ⚠ Falling back to git clone method…")
    else:
        print(f"  → Found existing anecdotes at {anecdotes_dir}")

    # Try to load anecdotes with label distributions
    anecdotes_loaded = 0
    for fpath in Path(anecdotes_dir).rglob("*.jsonl"):
        with open(fpath, encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    title = obj.get("title", "")
                    text = obj.get("text", "")

                    # ── V2: Extract label distribution ──
                    # Scruples anecdotes have label_scores: {"AUTHOR": N, "OTHER": N, ...}
                    label_scores = obj.get("label_scores", {})
                    binarized_label = obj.get("binarized_label", None)
                    label = obj.get("label", None)

                    if title or text:
                        q_text = title if title else text[:500]
                        disagreement_entropy = compute_entropy(label_scores) if label_scores else None

                        questions.append({
                            "id": f"scruples_anecdote_{anecdotes_loaded}",
                            "question": q_text,
                            "full_text": text[:2000] if text else "",
                            "label": label,
                            "benchmark": "Scruples",
                            "source": "lourie2021scruples",
                            "sub_dataset": "anecdotes",
                            # ── V2: Full human disagreement data ──
                            "human_disagreement": {
                                "source": "community_label_distribution",
                                "label_scores": label_scores,
                                "entropy": disagreement_entropy,
                                "binarized_label": binarized_label,
                                "total_votes": sum(label_scores.values()) if label_scores else 0,
                                "note": (
                                    "label_scores contains vote counts per category: "
                                    "AUTHOR (author wrong), OTHER (other wrong), "
                                    "EVERYBODY, NOBODY, INFO. "
                                    "Higher entropy = more human disagreement."
                                ),
                            },
                        })
                        anecdotes_loaded += 1
                except json.JSONDecodeError:
                    continue

    if anecdotes_loaded > 0:
        print(f"  · Loaded {anecdotes_loaded} anecdotes WITH label distributions")
    else:
        print(f"  ⚠ No anecdotes loaded from tar.gz; falling back to git clone…")

    # ── V2: Download Dilemmas (with worker vote splits) ───────────
    dilemmas_url = "https://storage.googleapis.com/ai2-mosaic-public/projects/scruples/v1.0/data/dilemmas.tar.gz"
    dilemmas_dir = os.path.join(local, "scruples_dilemmas")
    dilemmas_archive = os.path.join(local, "dilemmas.tar.gz")

    if not os.path.exists(dilemmas_dir):
        print(f"  → Downloading Scruples Dilemmas (~2 MB)…")
        try:
            urllib.request.urlretrieve(dilemmas_url, dilemmas_archive)
            ensure_dir(dilemmas_dir)
            with tarfile.open(dilemmas_archive, "r:gz") as tar:
                tar.extractall(path=dilemmas_dir)
            os.remove(dilemmas_archive)
            print(f"  → Extracted dilemmas to {dilemmas_dir}")
        except Exception as e:
            print(f"  ⚠ Could not download Scruples Dilemmas: {e}")
    else:
        print(f"  → Found existing dilemmas at {dilemmas_dir}")

    dilemmas_loaded = 0
    for fpath in Path(dilemmas_dir).rglob("*.jsonl"):
        with open(fpath, encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    action_a = obj.get("action0", obj.get("actions", [None, None])[0] if obj.get("actions") else "")
                    action_b = obj.get("action1", obj.get("actions", [None, None])[1] if obj.get("actions") else "")

                    # Dilemmas have label distribution or gold label
                    label = obj.get("gold_label", obj.get("label", None))
                    label_scores = obj.get("label_scores", {})

                    if action_a and action_b:
                        q = f"Which is less ethical?\nA: {action_a}\nB: {action_b}"
                        disagreement_entropy = compute_entropy(label_scores) if label_scores else None

                        questions.append({
                            "id": f"scruples_dilemma_{dilemmas_loaded}",
                            "question": q,
                            "options": [str(action_a), str(action_b)],
                            "label": label,
                            "benchmark": "Scruples",
                            "source": "lourie2021scruples",
                            "sub_dataset": "dilemmas",
                            "human_disagreement": {
                                "source": "worker_vote_distribution",
                                "label_scores": label_scores,
                                "entropy": disagreement_entropy,
                                "total_votes": sum(label_scores.values()) if label_scores else 0,
                            },
                        })
                        dilemmas_loaded += 1
                except json.JSONDecodeError:
                    continue

    if dilemmas_loaded > 0:
        print(f"  · Loaded {dilemmas_loaded} dilemmas WITH vote distributions")

    # ── Fallback: git clone (original V1 behavior, no label_scores) ──
    if anecdotes_loaded == 0 and dilemmas_loaded == 0:
        print(f"  → Falling back to git clone for Scruples…")
        repo = "https://github.com/allenai/scruples.git"
        if not os.path.exists(os.path.join(local, "scruples")):
            subprocess.run(["git", "clone", "--depth", "1", repo, os.path.join(local, "scruples")], check=True)
        
        data_dir = os.path.join(local, "scruples")
        for fpath in Path(data_dir).rglob("*.jsonl"):
            with open(fpath, encoding="utf-8") as f:
                for i, line in enumerate(f):
                    try:
                        obj = json.loads(line)
                        q = obj.get("title", obj.get("text", ""))
                        if q:
                            questions.append({
                                "id": f"scruples_{i}",
                                "question": q,
                                "label": obj.get("label", None),
                                "benchmark": "Scruples",
                                "source": "lourie2021scruples",
                                "human_disagreement": None,
                            })
                    except json.JSONDecodeError:
                        continue

    return sample_questions(questions, cfg.get("n_sample"))


def download_gaia(cfg: dict) -> list:
    """
    GAIA (ethics subset)
    
    HUMAN DISAGREEMENT: ❌ NONE
    """
    local = cfg["local_path"]
    ensure_dir(local)
    
    try:
        from datasets import load_dataset
        ds = load_dataset("gaia-benchmark/GAIA", "2023_all", split="test")
        questions = []
        for i, item in enumerate(ds):
            text = str(item.get("Question", "")).lower()
            if any(kw in text for kw in ["ethics", "moral", "fair", "right", "wrong", "should", "ought"]):
                questions.append({
                    "id": f"gaia_{i}",
                    "question": item.get("Question", ""),
                    "benchmark": "GAIA",
                    "source": "maia2024gaia",
                    "human_disagreement": None,
                })
        return sample_questions(questions, cfg.get("n_sample") or cfg.get("n_total"))
    except Exception as e:
        print(f"  Warning: Could not load GAIA: {e}")
        return []


def download_moral_machine(cfg: dict) -> list:
    """
    Moral Machine (Awad et al., 2018)
    
    HUMAN DISAGREEMENT: ✅ RICH — This is your BIGGEST source.
    
    The original OSF data (https://osf.io/3hvt2/) has:
      - SharedResponses.csv: 70M+ rows of individual human responses
      - Each row: ResponseID, UserID, UserCountry3, Saved (which group saved), etc.
      - Multiple users respond to the same scenario → compute agreement per scenario
      
    OPTIONS (pick based on your disk/bandwidth):
    
    A. HuggingFace pre-processed (RECOMMENDED):
       Jerry999/MoralMachineHuman — 34M rows, already paired into
       (Question text, HumanResponse) format. Use streaming to sample.
       
    B. OSF full download (18GB+):
       Good for computing exact per-scenario distributions,
       but requires significant storage and processing time.
       
    C. Synthetic generation (ORIGINAL V1 — not recommended for TIK paper):
       Current script generates fake scenarios. Fine for pipeline testing
       but CANNOT be used for disagreement analysis.
       
    This V2 uses option A (HuggingFace streaming) with fallback to C.
    """
    local = cfg["local_path"]
    ensure_dir(local)
    
    n = cfg.get("n_sample") or 5_000
    questions = []

    # ── V2: Try to load REAL Moral Machine data from HuggingFace ──
    try:
        from datasets import load_dataset
        print(f"  → Loading Moral Machine from HuggingFace (streaming, sampling {n})…")
        
        ds = load_dataset("Jerry999/MoralMachineHuman", split="train", streaming=True)
        
        # Collect a sample — streaming lets us avoid downloading the full 34M rows
        # We group by scenario type to compute disagreement later
        scenario_responses = {}  # ResponseID → list of responses
        count = 0
        max_scan = n * 20  # Scan more rows to get good scenario coverage
        
        for item in ds:
            if count >= max_scan:
                break
            
            resp_id = item.get("ResponseID", "")
            user_country = item.get("UserCountry3", "")
            human_response = item.get("HumanResponse", "")
            question_text = item.get("Question", "")
            
            if resp_id and question_text:
                if resp_id not in scenario_responses:
                    scenario_responses[resp_id] = {
                        "question": question_text,
                        "responses": [],
                    }
                scenario_responses[resp_id]["responses"].append({
                    "user_country": user_country,
                    "response": human_response,
                })
            count += 1
        
        # Now build questions with disagreement info
        for resp_id, data in scenario_responses.items():
            responses = data["responses"]
            
            # Compute response distribution for this scenario
            response_counts = {}
            for r in responses:
                resp = r["response"]
                response_counts[resp] = response_counts.get(resp, 0) + 1
            
            disagreement_entropy = compute_entropy(response_counts) if len(responses) > 1 else None
            
            # Country distribution (for cross-cultural analysis)
            country_counts = {}
            for r in responses:
                c = r["user_country"]
                if c:
                    country_counts[c] = country_counts.get(c, 0) + 1
            
            questions.append({
                "id": f"moral_machine_{resp_id}",
                "question": data["question"],
                "benchmark": "Moral Machine",
                "source": "awad2018moral",
                "data_source": "Jerry999/MoralMachineHuman (HuggingFace)",
                "human_disagreement": {
                    "source": "individual_responses",
                    "response_distribution": response_counts,
                    "entropy": disagreement_entropy,
                    "n_responses": len(responses),
                    "country_distribution": country_counts,
                    "note": (
                        "Each entry aggregates multiple real human responses "
                        "to the same Moral Machine scenario. "
                        "Higher entropy = more human disagreement on who to save."
                    ),
                },
            })
        
        if questions:
            print(f"  · Loaded {len(questions)} real scenarios from {count} individual responses")
            return sample_questions(questions, n)
        else:
            print(f"  ⚠ No data loaded from HuggingFace, falling back to synthetic…")

    except Exception as e:
        print(f"  ⚠ Could not load from HuggingFace ({e}), falling back to synthetic…")

    # ── Fallback: Synthetic generation (original V1) ──────────────
    print(f"  → Generating synthetic Moral Machine scenarios (NO disagreement data)…")
    characters = ["elderly person", "young person", "child", "pregnant woman", 
                  "male executive", "female doctor", "homeless person", "criminal",
                  "athlete", "large person", "dog", "cat"]
    scenarios = ["car must swerve", "brakes failed", "autonomous vehicle must choose"]
    
    seen = set()
    for i in range(n):
        random.shuffle(characters)
        group_a = characters[:random.randint(1, 3)]
        group_b = characters[3:3+random.randint(1, 3)]
        scenario = random.choice(scenarios)
        q = (f"A self-driving car's {scenario}. It must either hit "
             f"{', '.join(group_a)} or {', '.join(group_b)}. "
             f"Who should the car save?")
        if q not in seen:
            seen.add(q)
            questions.append({
                "id": f"moral_machine_{i}",
                "question": q,
                "group_a": group_a,
                "group_b": group_b,
                "benchmark": "Moral Machine",
                "source": "awad2018moral",
                "data_source": "synthetic",
                "human_disagreement": None,
                "note": "⚠ SYNTHETIC — cannot use for disagreement analysis. "
                        "Download real data from OSF or HuggingFace.",
            })

    return sample_questions(questions, n)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

DOWNLOADERS = {
    "moral_machine": download_moral_machine,
    "ethics": download_ethics,
    "truthfulqa": download_truthfulqa,
    "social_chemistry": download_social_chemistry,
    "moral_stories": download_moral_stories,
    "commonsenseqa": download_commonsenseqa,
    "mmlu_ethics": download_mmlu_ethics,
    "scruples": download_scruples,
    "gaia": download_gaia,
}


def main():
    config = load_config()
    benchmarks_cfg = config["benchmarks"]
    
    all_questions = {}
    total = 0
    
    # V2: Track disagreement data availability
    disagreement_summary = {}
    
    for bname, bcfg in benchmarks_cfg.items():
        print(f"\n{'='*60}")
        print(f"Downloading: {bcfg['name']}")
        print(f"{'='*60}")
        
        downloader = DOWNLOADERS.get(bname)
        if downloader is None:
            print(f"  ⚠ No downloader for {bname}, skipping.")
            continue
        
        try:
            questions = downloader(bcfg)
            all_questions[bname] = questions
            total += len(questions)
            
            # Save individual benchmark
            output_path = os.path.join("data", "processed", f"{bname}_unified.json")
            save_unified(questions, output_path)

            # V2: Summarize disagreement data
            n_with_disagreement = sum(
                1 for q in questions
                if q.get("human_disagreement") is not None
            )
            disagreement_summary[bname] = {
                "total": len(questions),
                "with_disagreement": n_with_disagreement,
                "pct": round(100 * n_with_disagreement / len(questions), 1) if questions else 0,
            }
            
        except Exception as e:
            print(f"  ✗ Error downloading {bname}: {e}")
            import traceback
            traceback.print_exc()
    
    # Save combined dataset
    combined = []
    for bname, qs in all_questions.items():
        combined.extend(qs)
    
    save_unified(combined, "data/processed/all_benchmarks_unified.json")
    
    # ── V2: Print disagreement data summary ───────────────────────
    print(f"\n{'='*60}")
    print(f"DONE. Total questions: {total}")
    print(f"{'='*60}")
    for bname, qs in all_questions.items():
        ds = disagreement_summary.get(bname, {})
        tag = "✅" if ds.get("pct", 0) > 50 else ("⚠️" if ds.get("pct", 0) > 0 else "❌")
        print(f"  {tag} {bname}: {len(qs)} questions "
              f"({ds.get('with_disagreement', 0)} with disagreement data, "
              f"{ds.get('pct', 0)}%)")
    
    print(f"\n{'='*60}")
    print(f"HUMAN DISAGREEMENT DATA SUMMARY (for TIK validation)")
    print(f"{'='*60}")
    print(f"  Use for Pillar 1 (Disagreement-Refusal Correspondence):")
    print(f"    1. Scruples (anecdotes) — label_scores entropy")
    print(f"    2. Social Chemistry     — rot_agree ordinal + m≥5 subsets")
    print(f"    3. Moral Machine        — per-scenario response entropy")
    print(f"  Use for Pillar 2 (Risk-Coverage curves):")
    print(f"    All benchmarks with gold labels (coverage = all)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()