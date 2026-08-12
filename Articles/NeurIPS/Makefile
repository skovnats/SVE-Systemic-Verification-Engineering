# TIK Framework — Automated Pipeline
# Run: make all (or individual targets)

.PHONY: all setup data kernel judges predictor adversarial clean

PYTHON := python3
DATA_DIR := data
RESULTS_DIR := results

# ============================================================
# Full pipeline
# ============================================================

all: setup data kernel judges predictor adversarial
	@echo "✅ Full pipeline complete."

# ============================================================
# 1. Setup
# ============================================================

setup:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt --break-system-packages -q
	mkdir -p $(DATA_DIR)/raw $(DATA_DIR)/processed $(RESULTS_DIR)/logs \
	         $(RESULTS_DIR)/checkpoints $(RESULTS_DIR)/figures \
	         $(RESULTS_DIR)/adversarial $(RESULTS_DIR)/tables

# ============================================================
# 2. Download & process benchmarks
# ============================================================

data: setup
	@echo "📥 Downloading benchmarks..."
	$(PYTHON) src/download_benchmarks.py

# ============================================================
# 3. Compute kernel embedding Φ
# ============================================================

kernel: setup
	@echo "🔮 Computing kernel embedding..."
	$(PYTHON) src/kernel_embedding.py

# ============================================================
# 4. Run 3+1+1 judge pipeline
# ============================================================

judges: data kernel
	@echo "⚖️ Running judge pipeline (this takes a while)..."
	$(PYTHON) src/judge_pipeline.py \
		--input $(DATA_DIR)/processed/all_benchmarks_unified.json \
		--output $(RESULTS_DIR)/tik_results.json \
		--config configs/experiment.yaml

# Quick test: only 10 questions
judges-test:
	$(PYTHON) src/judge_pipeline.py \
		--input $(DATA_DIR)/processed/all_benchmarks_unified.json \
		--output $(RESULTS_DIR)/tik_results_test.json \
		--limit 10

# ============================================================
# 5. Train learned predictor
# ============================================================

predictor: judges
	@echo "🧠 Training learned predictor..."
	$(PYTHON) src/learned_predictor.py \
		--data $(RESULTS_DIR)/tik_results.json \
		--output $(RESULTS_DIR)/checkpoints/ \
		--epochs 5

predictor-lobo: judges
	@echo "🔄 Running LOBO evaluation..."
	$(PYTHON) src/learned_predictor.py \
		--data $(RESULTS_DIR)/tik_results.json \
		--output $(RESULTS_DIR)/checkpoints/ \
		--lobo

# ============================================================
# 6. Adversarial robustness
# ============================================================

adversarial: judges
	@echo "🛡️ Running adversarial analysis..."
	$(PYTHON) src/adversarial.py \
		--input $(RESULTS_DIR)/tik_results.json \
		--output $(RESULTS_DIR)/adversarial/

# ============================================================
# Utilities
# ============================================================

clean:
	rm -rf $(RESULTS_DIR)/*
	@echo "🧹 Cleaned results directory."

stats:
	@echo "📊 Dataset statistics:"
	@$(PYTHON) -c "import json; d=json.load(open('$(DATA_DIR)/processed/all_benchmarks_unified.json')); \
	from collections import Counter; c=Counter(q['benchmark'] for q in d); \
	print(f'Total: {len(d)}'); [print(f'  {k}: {v}') for k,v in sorted(c.items())]"
