# 📚 Step-by-Step Research Guide

## Phase 1: Environment Setup (Day 1)

### 1.1 Python Environment

```bash
# Create clean environment
python -m venv venv
source venv/bin/activate

# Core dependencies
pip install torch>=2.0
pip install transformers>=4.35
pip install datasets>=2.14
pip install openai>=1.0
pip install anthropic>=0.8
pip install google-generativeai
pip install numpy pandas scipy scikit-learn
pip install matplotlib seaborn plotly
pip install networkx  # for VKB graphs
pip install gudhi     # for TDA/Betti numbers
pip install ripser    # for persistence diagrams
pip install umap-learn  # for manifold visualization
pip install tqdm rich   # progress bars
pip install pyyaml python-dotenv
pip install pytest pytest-cov  # testing
```

### 1.2 API Keys

```bash
# Create .env file
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-google-key
HUGGINGFACE_TOKEN=hf_your-token-here
EOF
```

### 1.3 Verify Setup

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('API keys loaded' if os.getenv('OPENAI_API_KEY') else 'Missing keys')"
```

---

## Phase 2: Dataset Download (Day 1-2)

### 2.1 TruthfulQA

```python
# Source: https://github.com/sylinrl/TruthfulQA
# HuggingFace: truthful_qa

from datasets import load_dataset

# Download
truthfulqa = load_dataset("truthful_qa", "multiple_choice")
truthfulqa_gen = load_dataset("truthful_qa", "generation")

# Save locally
truthfulqa.save_to_disk("benchmarks/data/truthfulqa")

# Stats: 817 questions across 38 categories
# Categories: Health, Law, Finance, Politics, etc.
```

**Papers using**: Main, Socratic Protocol, VKB, Ivan Agent, 8+ workshops

### 2.2 GAIA Benchmark

```python
# Source: https://huggingface.co/datasets/gaia-benchmark/GAIA
# Paper: "GAIA: A Benchmark for General AI Assistants"

from datasets import load_dataset

# Requires HuggingFace login for some splits
gaia = load_dataset("gaia-benchmark/GAIA", "2023_all")

# Save locally  
gaia.save_to_disk("benchmarks/data/gaia")

# Stats: 450 real-world tasks
# Levels: 1 (easy), 2 (medium), 3 (hard)
```

**Papers using**: Main, Ivan Agent, VKB, 5+ workshops

### 2.3 ETHICS Dataset

```python
# Source: https://github.com/hendrycks/ethics
# Paper: "Aligning AI With Shared Human Values"

from datasets import load_dataset

# Multiple subsets
ethics_cm = load_dataset("hendrycks/ethics", "commonsense")
ethics_deontology = load_dataset("hendrycks/ethics", "deontology")  
ethics_justice = load_dataset("hendrycks/ethics", "justice")
ethics_utilitarianism = load_dataset("hendrycks/ethics", "utilitarianism")
ethics_virtue = load_dataset("hendrycks/ethics", "virtue")

# Save all
for name, ds in [("cm", ethics_cm), ("deontology", ethics_deontology), 
                  ("justice", ethics_justice), ("util", ethics_utilitarianism),
                  ("virtue", ethics_virtue)]:
    ds.save_to_disk(f"benchmarks/data/ethics/{name}")

# Stats: 130K+ ethical scenarios
```

**Papers using**: Main, Cultural, Betti, Lyapunov, 10+ workshops

### 2.4 Moral Machine

```python
# Source: https://www.moralmachine.net/
# Paper: "The Moral Machine Experiment" (Nature 2018)
# Data: https://osf.io/3hvt2/

import requests
import pandas as pd

# Download from OSF (Open Science Framework)
# Note: Large dataset (~2GB), may need subset

# For research, use the aggregated data:
url = "https://osf.io/download/wt6mc/"  # SharedResponses.csv

# Or use the MIT API (if available)
# Alternative: Use pre-processed subset

# Save
# moral_machine.to_parquet("benchmarks/data/moral_machine/responses.parquet")

# Stats: 40M+ moral judgments from 233 countries
```

**Papers using**: Main, Δ-Dehumanization, Cultural Compilers, 8+ workshops

### 2.5 MMLU (Massive Multitask Language Understanding)

```python
from datasets import load_dataset

# Full MMLU
mmlu = load_dataset("cais/mmlu", "all")

# Or specific subjects for ethics
mmlu_moral = load_dataset("cais/mmlu", "moral_scenarios")
mmlu_philosophy = load_dataset("cais/mmlu", "philosophy")
mmlu_professional_law = load_dataset("cais/mmlu", "professional_law")

# Save
mmlu.save_to_disk("benchmarks/data/mmlu")

# Stats: 57 subjects, 14K+ questions
```

### 2.6 BIG-Bench

```python
# Source: https://github.com/google/BIG-bench
from datasets import load_dataset

# Specific tasks relevant to ethics/reasoning
bigbench_tasks = [
    "moral_permissibility",
    "epistemic_reasoning", 
    "logical_deduction",
    "causal_judgment",
    "social_iqa"
]

for task in bigbench_tasks:
    ds = load_dataset("bigbench", task)
    ds.save_to_disk(f"benchmarks/data/bigbench/{task}")

# Stats: 204 tasks total
```

### 2.7 Mathematics Datasets (for Betti paper)

```python
from datasets import load_dataset

# GSM8K - Grade School Math
gsm8k = load_dataset("gsm8k", "main")
gsm8k.save_to_disk("benchmarks/data/gsm8k")

# MATH - Competition Math
math_ds = load_dataset("hendrycks/competition_math")
math_ds.save_to_disk("benchmarks/data/math")

# Stats: GSM8K 8.5K, MATH 12.5K problems
```

### 2.8 Code Datasets (for relevant papers)

```python
# HumanEval
from datasets import load_dataset

humaneval = load_dataset("openai_humaneval")
humaneval.save_to_disk("benchmarks/data/humaneval")

# MBPP
mbpp = load_dataset("mbpp")
mbpp.save_to_disk("benchmarks/data/mbpp")
```

### 2.9 Download Script (All at Once)

```bash
python scripts/download_all.py
```

---

## Phase 3: Baseline Runs (Day 2-3)

### 3.1 Why Run Baselines Once

```
PROBLEM: Running GPT-4 on TruthfulQA for each of 15 papers
= 15 × $30 = $450 + 15 × 2 hours = 30 hours

SOLUTION: Run once, save results, reuse
= 1 × $30 = $30 + 1 × 2 hours = 2 hours
= 15× savings
```

### 3.2 Baseline Models

| Model | API | Cost Estimate |
|:------|:----|:--------------|
| GPT-4 | OpenAI | ~$100-150 |
| GPT-4-Turbo | OpenAI | ~$50-80 |
| Claude-3-Opus | Anthropic | ~$100-150 |
| Claude-3-Sonnet | Anthropic | ~$30-50 |
| Gemini-Pro | Google | ~$20-40 |
| Llama-3-70B | Local/API | ~$0-30 |
| **Total** | | **~$300-500** |

### 3.3 Run Baselines

```bash
# Run all baselines on all benchmarks
python scripts/run_baselines.py --all

# Or specific combinations
python scripts/run_baselines.py \
    --models gpt4 claude-opus \
    --benchmarks truthfulqa ethics moral_machine

# Results saved to baselines/
```

### 3.4 Baseline Results Format

```json
// baselines/gpt4/truthfulqa/results.json
{
  "model": "gpt-4-0125-preview",
  "benchmark": "truthfulqa",
  "timestamp": "2025-01-20T12:00:00Z",
  "config": {
    "temperature": 0,
    "max_tokens": 1024
  },
  "metrics": {
    "accuracy": 0.783,
    "truthful_rate": 0.812,
    "informative_rate": 0.756,
    "hallucination_rate": 0.217
  },
  "per_category": {
    "health": 0.801,
    "law": 0.762,
    "finance": 0.794
  },
  "raw_outputs_file": "raw_outputs.jsonl"
}
```

---

## Phase 4: CogOS System Implementation (Day 3-5)

### 4.1 Core System

```
core/
├── __init__.py
├── cogos.py          # Main orchestrator
├── agents/
│   ├── __init__.py
│   ├── base.py       # Agent base class
│   ├── socrates.py   # Logic & Inquiry
│   ├── solomon.py    # Ethics & Wisdom
│   └── ivan.py       # Humility & Calibration
├── metrics/
│   ├── __init__.py
│   ├── delta_dehum.py    # Δ-Dehumanization
│   ├── gev_distance.py   # GEV proximity
│   ├── lyapunov.py       # Stability metrics
│   └── betti.py          # Topological metrics
├── cultural/
│   ├── __init__.py
│   ├── compiler.py       # Cultural Compiler
│   └── bases.py          # Cultural basis vectors
└── vkb/
    ├── __init__.py
    ├── knowledge_base.py # VKB implementation
    └── graph.py          # DAG operations
```

### 4.2 Run CogOS on Benchmarks

```bash
# Run CogOS system
python scripts/run_cogos.py --benchmark truthfulqa
python scripts/run_cogos.py --benchmark ethics
python scripts/run_cogos.py --all
```

---

## Phase 5: Paper-Specific Experiments (Day 5-14)

### 5.1 Experiment Strategy

```
FOR EACH PAPER:
1. Load config from configs/papers/{paper}.yaml
2. Load required baselines (already computed)
3. Run UNIQUE experiments only
4. Generate paper-specific tables/figures
5. Save to results/{paper}/
```

### 5.2 Example: Betti Numbers Paper

```bash
# Load config
python scripts/run_experiments.py --paper workshop_betti

# What this does:
# 1. Loads ethics dataset
# 2. Loads baseline results (reused)
# 3. Runs TDA analysis (unique)
# 4. Computes Betti numbers (unique)
# 5. Generates persistence diagrams (unique)
# 6. Saves to results/workshop_betti/
```

### 5.3 Experiment Timeline

| Week | Papers | Focus |
|:-----|:-------|:------|
| 1 | Main CogOS | Full system evaluation |
| 2 | Betti, Lyapunov, Δ-Dehum | Mathematical foundations |
| 3 | Cultural, Ivan, Socrates | Agent-specific |
| 4 | VKB, SIP, EBP | Protocol papers |
| 5+ | Remaining workshops | Various topics |

---

## Phase 6: Results Aggregation (Ongoing)

### 6.1 Generate Tables

```bash
# Generate LaTeX tables for paper
python scripts/aggregate_results.py --paper main_cogos --format latex

# Output: results/main_cogos/tables/
# - table_truthfulqa.tex
# - table_ethics.tex
# - table_comparison.tex
```

### 6.2 Generate Figures

```bash
# Generate figures
python scripts/generate_figures.py --paper main_cogos

# Output: results/main_cogos/figures/
# - manifold_trajectory.pdf
# - delta_timeseries.pdf
# - radar_comparison.pdf
```

---

## Phase 7: Paper Writing (Parallel with Phase 5-6)

### 7.1 Template Structure

Each paper directory contains:

```
papers/workshop_betti/
├── config.yaml           # Paper configuration
├── experiments/          # Unique experiment scripts
├── results/              # Paper-specific results
├── figures/              # Generated figures
├── paper/
│   ├── main.tex          # Paper source
│   ├── references.bib    # Bibliography
│   └── figures/          # Embedded figures
└── submission/
    └── neurips_2025.pdf  # Final PDF
```

### 7.2 Writing Timeline

| Deadline | Action |
|:---------|:-------|
| May 1-10 | Main paper drafts |
| May 15 | Main track submission |
| May-June | Workshop paper drafts |
| June-Aug | Workshop submissions |

---

## 📋 Checklist

### Setup
- [ ] Python environment created
- [ ] Dependencies installed
- [ ] API keys configured
- [ ] Directory structure created

### Data
- [ ] TruthfulQA downloaded
- [ ] GAIA downloaded
- [ ] ETHICS downloaded
- [ ] Moral Machine downloaded
- [ ] MMLU downloaded
- [ ] Other datasets as needed

### Baselines
- [ ] GPT-4 baselines complete
- [ ] Claude baselines complete
- [ ] Other baselines complete
- [ ] Results validated

### CogOS
- [ ] Core system implemented
- [ ] All agents working
- [ ] Metrics implemented
- [ ] VKB working

### Papers
- [ ] Main paper experiments
- [ ] Main paper draft
- [ ] Workshop experiments
- [ ] Workshop drafts

---

## 🆘 Troubleshooting

### API Rate Limits

```python
# Use exponential backoff
import time
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, min=4, max=60))
def call_api(prompt):
    return client.chat.completions.create(...)
```

### Memory Issues

```python
# Process datasets in chunks
from datasets import load_dataset

ds = load_dataset("large_dataset", streaming=True)
for batch in ds.iter(batch_size=100):
    process(batch)
```

### GPU OOM

```python
# Use gradient checkpointing and smaller batches
model.gradient_checkpointing_enable()
trainer = Trainer(per_device_train_batch_size=4)
```

---

**С Богом!** 🙏
