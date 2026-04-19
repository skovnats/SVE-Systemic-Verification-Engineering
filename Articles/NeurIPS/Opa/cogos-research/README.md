# CogOS Research Infrastructure
## NeurIPS 2025: 1 Main + 32 Workshop Papers

> "С Богом!" - Research framework for formal verification of AI ethics

---

## 🎯 Overview

This repository contains the complete research infrastructure for producing 33 papers:
- **1 Main Track**: CogOS - Formal Verification of AI Ethics
- **32 Workshop Papers**: Various aspects and applications

### Key Principle: Smart Reuse
```
ONE core system → MANY papers with UNIQUE contributions
ONE baseline run → SHARED across relevant papers  
ONE dataset load → MULTIPLE analyses
```

---

## 📁 Directory Structure

```
cogos-research/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── setup.py                  # Package installation
│
├── core/                     # 🧠 Core CogOS System
│   ├── agents/               # Socrates, Solomon, Ivan
│   ├── metrics/              # Δ-Dehumanization, etc.
│   ├── cultural/             # Cultural Compilers
│   └── vkb/                  # Verifiable Knowledge Base
│
├── benchmarks/               # 📊 Datasets & Evaluation
│   ├── downloaders/          # Scripts to fetch datasets
│   ├── runners/              # Benchmark execution
│   └── data/                 # Downloaded datasets (gitignored)
│
├── baselines/                # 📈 Baseline Results
│   ├── gpt4/
│   ├── claude/
│   ├── constitutional_ai/
│   ├── rlhf/
│   └── cove/
│
├── papers/                   # 📝 Per-Paper Experiments
│   ├── main_cogos/
│   ├── workshop_betti/
│   ├── workshop_cultural/
│   └── ... (33 total)
│
├── configs/                  # ⚙️ YAML Configurations
│   ├── main.yaml             # Main paper config
│   ├── benchmarks.yaml       # Dataset configs
│   └── papers/               # Per-paper configs
│
├── scripts/                  # 🔧 Utility Scripts
│   ├── download_all.py
│   ├── run_baselines.py
│   ├── run_experiments.py
│   └── aggregate_results.py
│
├── results/                  # 📊 Output (gitignored)
│   ├── raw/
│   ├── processed/
│   └── figures/
│
└── docs/                     # 📚 Documentation
    ├── STEP_BY_STEP.md
    ├── DATASETS.md
    └── PAPER_MATRIX.md
```

---

## 🚀 Quick Start

### Step 1: Setup Environment

```bash
# Clone/create repository
cd cogos-research

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### Step 2: Download Datasets

```bash
# Download all benchmarks
python scripts/download_all.py

# Or download specific ones
python scripts/download_all.py --only truthfulqa gaia ethics
```

### Step 3: Run Baselines (ONCE)

```bash
# This runs all baselines - do this ONCE, reuse everywhere
python scripts/run_baselines.py --all

# Or specific baselines
python scripts/run_baselines.py --models gpt4 claude
```

### Step 4: Run Paper-Specific Experiments

```bash
# Run experiments for specific paper
python scripts/run_experiments.py --paper main_cogos
python scripts/run_experiments.py --paper workshop_betti

# Or run all
python scripts/run_experiments.py --all
```

### Step 5: Aggregate Results

```bash
# Generate tables and figures
python scripts/aggregate_results.py --paper main_cogos
```

---

## 📊 Datasets Overview

| Dataset | Size | Download | Papers Using |
|:--------|:-----|:---------|:-------------|
| TruthfulQA | 817 Q | HuggingFace | Main, Socratic, VKB, 8+ |
| GAIA | 450 tasks | HuggingFace | Main, Ivan, 5+ |
| ETHICS | 130K | GitHub | Main, Cultural, 10+ |
| Moral Machine | 40M judgments | MIT | Main, Δ-Dehum, 8+ |
| MMLU | 57 subjects | HuggingFace | 5+ papers |
| BIG-Bench | 204 tasks | GitHub | 6+ papers |
| WinoGrande | 44K | HuggingFace | 3+ papers |
| HellaSwag | 70K | HuggingFace | 3+ papers |
| ARC | 7.7K | HuggingFace | 4+ papers |
| GSM8K | 8.5K | HuggingFace | 3+ papers |
| MATH | 12.5K | HuggingFace | Betti, 4+ papers |
| HumanEval | 164 | GitHub | 2+ papers |
| MBPP | 974 | GitHub | 2+ papers |

---

## 📝 Paper Matrix

See `docs/PAPER_MATRIX.md` for full details.

### Quick Reference:

| Paper | Workshop | Core Module | Primary Dataset | Unique Contribution |
|:------|:---------|:------------|:----------------|:--------------------|
| CogOS Main | Main Track | ALL | ALL | Full system |
| Betti Numbers | MATH-AI | TDA | ETHICS + MATH | Topology of morality |
| Cultural Compilers | Pluralistic | cultural/ | CCDB | Cross-cultural |
| Δ-Dehumanization | SafeGenAI | metrics/ | Moral Machine | Drift metric |
| Ivan Agent | TEACH | agents/ivan | TruthfulQA | Uncertainty |
| VKB | KnowledgeLM | vkb/ | GAIA | Knowledge graphs |
| ... | ... | ... | ... | ... |

---

## ⚙️ Configuration System

Each paper has a YAML config in `configs/papers/`:

```yaml
# configs/papers/workshop_betti.yaml
paper:
  name: "Betti Numbers of the Moral Manifold"
  workshop: "MATH-AI"
  
datasets:
  primary: ethics
  secondary: [math, mmlu_moral]
  
modules:
  required: [agents.socrates, metrics.betti, cultural.base]
  
experiments:
  - name: "topology_analysis"
    script: "papers/workshop_betti/run_topology.py"
  - name: "betti_computation"  
    script: "papers/workshop_betti/run_betti.py"

baselines:
  reuse: [gpt4_ethics, claude_ethics, constitutional_ethics]
  
unique_metrics:
  - betti_0  # Connected components
  - betti_1  # Holes
  - betti_2  # Voids
  - persistence_diagram
```

---

## 🔑 API Keys Setup

Create `.env` file (gitignored):

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
HUGGINGFACE_TOKEN=hf_...
```

---

## 📈 Resource Estimates

| Phase | Time | Cost | Notes |
|:------|:-----|:-----|:------|
| Dataset download | 2-4 hours | Free | One time |
| Baseline runs | 8-12 hours | ~$300-500 | One time |
| Per-paper experiments | 1-3 hours each | ~$10-30 each | Unique only |
| Total | ~1 week | ~$800-1200 | For all 33 papers |

**With smart reuse: 5-10× cheaper than naive approach**

---

## 📜 License

SVE Public License v1.3

---

## 🙏 Acknowledgments

"С Богом!" - All glory to the Creator of truth.
