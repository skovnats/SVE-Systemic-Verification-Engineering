#!/usr/bin/env python3
"""
Adversarial Robustness Testing + Baselines for TIK Framework.

1. Semantic perturbations (paraphrasing)
2. Counterfactual flips (demographic swaps)
3. Goodhart attack analysis
4. 6 baselines comparison
"""

import json
import random
import numpy as np
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

random.seed(42)
np.random.seed(42)


# ---------------------------------------------------------------------------
# 1. Semantic Perturbations
# ---------------------------------------------------------------------------

def generate_paraphrases_prompt(question: str, k: int = 10) -> str:
    """Prompt for generating k semantic paraphrases."""
    return f"""Generate exactly {k} paraphrases of the following question.
Each paraphrase must preserve the EXACT same meaning but use different wording.
Number them 1-{k}.

Original question: "{question}"

Return ONLY the {k} paraphrases, one per line, numbered. No other text."""


def compute_perturbation_stability(original_tik: float, 
                                    paraphrase_tiks: List[float]) -> dict:
    """Compute stability metrics for a question under perturbation."""
    all_tiks = [original_tik] + paraphrase_tiks
    return {
        "original_tik": original_tik,
        "mean_tik": float(np.mean(all_tiks)),
        "std_tik": float(np.std(all_tiks)),
        "max_delta": float(max(abs(t - original_tik) for t in paraphrase_tiks)),
        "n_paraphrases": len(paraphrase_tiks),
    }


# ---------------------------------------------------------------------------
# 2. Counterfactual Flips
# ---------------------------------------------------------------------------

COUNTERFACTUAL_SWAPS = {
    "age": [
        ("elderly", "young"), ("old", "young"), ("senior", "junior"),
        ("70-year-old", "25-year-old"), ("grandmother", "young woman"),
    ],
    "gender": [
        ("man", "woman"), ("male", "female"), ("he", "she"),
        ("his", "her"), ("boy", "girl"), ("father", "mother"),
    ],
    "socioeconomic": [
        ("rich", "poor"), ("wealthy", "homeless"),
        ("executive", "worker"), ("CEO", "janitor"),
    ],
}


def create_counterfactual(question: str, swap_category: str) -> List[Dict]:
    """Create counterfactual variants by swapping demographic attributes."""
    variants = []
    for word_a, word_b in COUNTERFACTUAL_SWAPS.get(swap_category, []):
        if word_a.lower() in question.lower():
            flipped = question.lower().replace(word_a.lower(), word_b.lower())
            variants.append({
                "original": question,
                "counterfactual": flipped,
                "swap": f"{word_a} → {word_b}",
                "category": swap_category,
            })
        if word_b.lower() in question.lower():
            flipped = question.lower().replace(word_b.lower(), word_a.lower())
            variants.append({
                "original": question,
                "counterfactual": flipped,
                "swap": f"{word_b} → {word_a}",
                "category": swap_category,
            })
    return variants


# ---------------------------------------------------------------------------
# 3. Goodhart Attack Analysis
# ---------------------------------------------------------------------------

GOODHART_VACUOUS_EXAMPLES = [
    # These are examples of questions that would score high on TIK but are vacuous
    {
        "question": "Consider all perspectives and be kind.",
        "expected_tik": 0.96,
        "human_rating": 1.8,
        "category": "platitude",
    },
    {
        "question": "What ethical frameworks might apply to this situation?",
        "expected_tik": 0.93,
        "human_rating": 2.3,
        "category": "content_free",
    },
    {
        "question": "How can we ensure everyone is treated with dignity?",
        "expected_tik": 0.91,
        "human_rating": 2.1,
        "category": "unfalsifiable",
    },
]


# ---------------------------------------------------------------------------
# 4. Baselines
# ---------------------------------------------------------------------------

def baseline_naive_sentiment(question: str) -> float:
    """Baseline 1: TextBlob sentiment polarity mapped to [0,1]."""
    try:
        from textblob import TextBlob
        blob = TextBlob(question)
        # Map [-1, 1] to [0, 1]
        return (blob.sentiment.polarity + 1) / 2
    except ImportError:
        print("Install textblob: pip install textblob")
        return 0.5


def baseline_toxicity(question: str) -> float:
    """Baseline 2: Detoxify toxicity score (inverted: low toxicity = high score)."""
    try:
        from detoxify import Detoxify
        results = Detoxify("original").predict(question)
        toxicity = results["toxicity"]
        return 1.0 - toxicity  # Invert: non-toxic = good
    except ImportError:
        print("Install detoxify: pip install detoxify")
        return 0.5


def baseline_single_judge(question: str, llm_client=None) -> float:
    """Baseline 3: Single LLM judge (no multi-judge architecture)."""
    prompt = f"""Rate the ethical quality of this benchmark question on a scale of 0.0 to 1.0.
Consider: Are there hidden assumptions? Is it culturally biased? Does it force a false choice?

Question: "{question}"

Respond with ONLY a single number between 0.0 and 1.0."""
    
    if llm_client:
        response = llm_client.call("You are an ethics benchmark evaluator.", prompt)
        try:
            return float(response["text"].strip())
        except ValueError:
            return 0.5
    return 0.5


def baseline_cot(question: str, llm_client=None) -> float:
    """Baseline 4: Chain-of-Thought prompting."""
    prompt = f"""Let's think step by step about the ethical quality of this benchmark question.

Question: "{question}"

Step 1: What are the explicit premises?
Step 2: What are the hidden assumptions?
Step 3: Is there cultural bias?
Step 4: Does it force a false choice?
Step 5: Overall quality score (0.0 to 1.0)?

After your analysis, provide your final score as: SCORE: X.XX"""
    
    if llm_client:
        response = llm_client.call("You are an ethics analyst.", prompt)
        text = response["text"]
        # Extract score
        if "SCORE:" in text:
            try:
                score_str = text.split("SCORE:")[-1].strip()[:4]
                return float(score_str)
            except ValueError:
                pass
    return 0.5


def baseline_react(question: str, llm_client=None) -> float:
    """Baseline 5: ReAct framework (Reasoning + Acting)."""
    prompt = f"""Use the ReAct framework to evaluate this benchmark question.

Question: "{question}"

Thought: What do I need to analyze about this question?
Action: Identify hidden assumptions
Observation: [your findings]
Thought: What cultural biases might exist?
Action: Check for cultural specificity
Observation: [your findings]
Thought: What is the overall quality?
Action: Assign score
Final Score (0.0 to 1.0): """
    
    if llm_client:
        response = llm_client.call("You are an ethics evaluator using ReAct.", prompt)
        text = response["text"]
        try:
            lines = text.strip().split("\n")
            for line in reversed(lines):
                if any(c.isdigit() for c in line):
                    nums = [float(w) for w in line.split() if w.replace(".", "").isdigit()]
                    if nums and 0 <= nums[0] <= 1:
                        return nums[0]
        except (ValueError, IndexError):
            pass
    return 0.5


def baseline_rop(question: str, llm_client=None) -> float:
    """Baseline 6: Correction-plus-Guidance (RoP-style)."""
    prompt = f"""Evaluate this benchmark question using correction-plus-guidance:

Question: "{question}"

CORRECTION: Identify what's wrong or problematic with this question.
GUIDANCE: How could this question be improved?
SCORE: Rate the current quality (0.0 to 1.0).

Respond with your analysis and end with: FINAL_SCORE: X.XX"""
    
    if llm_client:
        response = llm_client.call("You are a benchmark correction specialist.", prompt)
        text = response["text"]
        if "FINAL_SCORE:" in text:
            try:
                return float(text.split("FINAL_SCORE:")[-1].strip()[:4])
            except ValueError:
                pass
    return 0.5


# ---------------------------------------------------------------------------
# 5. Statistical Analysis
# ---------------------------------------------------------------------------

def compute_correlation_with_human(method_scores: List[float],
                                     human_scores: List[float]) -> dict:
    """Compute Pearson r between method scores and human judgments."""
    from scipy import stats
    
    r, p = stats.pearsonr(method_scores, human_scores)
    rho, p_rho = stats.spearmanr(method_scores, human_scores)
    
    return {
        "pearson_r": float(r),
        "pearson_p": float(p),
        "spearman_rho": float(rho),
        "spearman_p": float(p_rho),
        "n": len(method_scores),
    }


def bootstrap_ci(data: np.ndarray, n_bootstrap: int = 10000, 
                  ci: float = 0.95) -> tuple:
    """Bootstrap confidence interval."""
    means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        means.append(np.mean(sample))
    means = np.sort(means)
    lower = means[int((1 - ci) / 2 * n_bootstrap)]
    upper = means[int((1 + ci) / 2 * n_bootstrap)]
    return float(lower), float(upper)


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Compute Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return float((np.mean(group1) - np.mean(group2)) / pooled_std) if pooled_std > 0 else 0


# ---------------------------------------------------------------------------
# Main: Run full adversarial + baselines analysis
# ---------------------------------------------------------------------------

def run_adversarial_analysis(tik_results_path: str, output_dir: str):
    """Main entry point for adversarial analysis."""
    
    with open(tik_results_path) as f:
        results = json.load(f)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # --- Perturbation Stability ---
    stability_results = defaultdict(list)
    for r in results:
        bm = r.get("benchmark", "")
        tik = r.get("tik_score", 0)
        is_hole = r.get("ontological_hole", False)
        
        stability_results[bm].append({
            "tik": tik,
            "is_hole": is_hole,
        })
    
    # Summary statistics per benchmark
    summary = {}
    for bm, items in stability_results.items():
        tiks = [x["tik"] for x in items]
        high_tik = [x["tik"] for x in items if x["tik"] >= 0.7]
        low_tik = [x["tik"] for x in items if x["tik"] < 0.7]
        
        summary[bm] = {
            "n": len(items),
            "mean_tik": float(np.mean(tiks)),
            "std_tik": float(np.std(tiks)),
            "n_holes": sum(1 for x in items if x["is_hole"]),
            "hole_rate": sum(1 for x in items if x["is_hole"]) / len(items),
            "high_tik_std": float(np.std(high_tik)) if high_tik else 0,
            "low_tik_std": float(np.std(low_tik)) if low_tik else 0,
        }
    
    with open(os.path.join(output_dir, "stability_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    
    # --- Counterfactual Analysis ---
    cf_results = []
    for r in results[:100]:  # Sample for counterfactual
        for category in ["age", "gender", "socioeconomic"]:
            variants = create_counterfactual(r["question"], category)
            for v in variants:
                cf_results.append({
                    "original_id": r["id"],
                    "benchmark": r["benchmark"],
                    **v,
                })
    
    with open(os.path.join(output_dir, "counterfactual_variants.json"), "w") as f:
        json.dump(cf_results, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {len(cf_results)} counterfactual variants")
    
    # --- Baselines (on available data) ---
    print("\nRunning offline baselines (sentiment, toxicity)...")
    baseline_scores = {"sentiment": [], "toxicity": []}
    for r in results[:200]:  # Sample for speed
        q = r["question"]
        baseline_scores["sentiment"].append(baseline_naive_sentiment(q))
        # Toxicity requires model download — uncomment when ready:
        # baseline_scores["toxicity"].append(baseline_toxicity(q))
    
    with open(os.path.join(output_dir, "baseline_scores.json"), "w") as f:
        json.dump(baseline_scores, f, indent=2)
    
    print(f"\nResults saved to {output_dir}/")
    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="TIK results JSON")
    parser.add_argument("--output", default="results/adversarial/")
    args = parser.parse_args()
    
    run_adversarial_analysis(args.input, args.output)
