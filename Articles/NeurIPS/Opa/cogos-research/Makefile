# CogOS Research Makefile
# NeurIPS 2025 Submission Package

.PHONY: all setup data baselines experiments figures tables clean help

# Default target
all: setup data baselines experiments figures tables

# =============================================================================
# SETUP
# =============================================================================

setup: ## Install dependencies and setup environment
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Setup complete!"

setup-dev: setup ## Install development dependencies
	pip install pytest black isort mypy
	@echo "✅ Dev setup complete!"

# =============================================================================
# DATA
# =============================================================================

data: ## Download all datasets
	@echo "📥 Downloading datasets..."
	python scripts/download_datasets.py --all
	python scripts/create_ccdb.py
	@echo "✅ Data ready!"

data-truthfulqa: ## Download TruthfulQA only
	python scripts/download_datasets.py --dataset truthfulqa

data-gaia: ## Download GAIA only
	python scripts/download_datasets.py --dataset gaia

data-ethics: ## Download ETHICS only
	python scripts/download_datasets.py --dataset ethics

data-ccdb: ## Create CCDB benchmark
	python scripts/create_ccdb.py --n-scenarios 500

# =============================================================================
# EXPERIMENTS
# =============================================================================

baselines: ## Run all baseline experiments
	@echo "🔬 Running baselines..."
	python run_experiments.py --baselines
	@echo "✅ Baselines complete!"

experiments: ## Run main paper experiments
	@echo "🔬 Running experiments..."
	python run_experiments.py --paper main
	@echo "✅ Experiments complete!"

experiments-test: ## Run quick test experiments
	@echo "🧪 Running test experiments..."
	python run_experiments.py --paper main --test --n-samples 10
	@echo "✅ Test complete!"

experiments-paper-%: ## Run experiments for specific paper (e.g., make experiments-paper-4)
	python run_experiments.py --paper $*

# =============================================================================
# OUTPUTS
# =============================================================================

figures: ## Generate all figures
	@echo "📊 Generating figures..."
	python scripts/generate_figures.py --paper main
	@echo "✅ Figures complete!"

tables: ## Generate LaTeX tables
	@echo "📋 Generating tables..."
	python scripts/generate_latex.py --paper main
	@echo "✅ Tables complete!"

# =============================================================================
# HUMAN EVALUATION
# =============================================================================

human-eval-create: ## Create human evaluation study
	@echo "📝 Creating human evaluation study..."
	python scripts/human_eval.py --create-study --platform prolific
	@echo "✅ Study created!"

human-eval-analyze: ## Analyze human evaluation results
	python scripts/human_eval.py --analyze --study-id $(STUDY_ID)

# =============================================================================
# PAPERS
# =============================================================================

paper-main: experiments figures tables ## Generate main paper content
	@echo "📄 Main paper ready!"

paper-all: ## Generate content for all papers
	@echo "📚 Generating all paper content..."
	for i in $$(seq 1 32); do \
		python run_experiments.py --paper $$i --test; \
	done
	@echo "✅ All papers processed!"

# =============================================================================
# CODE QUALITY
# =============================================================================

test: ## Run tests
	pytest tests/ -v

lint: ## Run linters
	black --check src/ scripts/
	isort --check-only src/ scripts/
	flake8 src/ scripts/

format: ## Format code
	black src/ scripts/
	isort src/ scripts/

typecheck: ## Run type checking
	mypy src/

quality: lint typecheck test ## Run all quality checks

# =============================================================================
# UTILITIES
# =============================================================================

clean: ## Clean generated files
	@echo "🧹 Cleaning..."
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache .mypy_cache
	rm -rf *.egg-info
	find . -name "*.pyc" -delete
	@echo "✅ Clean!"

clean-results: ## Clean results (careful!)
	@echo "⚠️  Cleaning results..."
	rm -rf results/*
	rm -rf baselines/results/*
	@echo "✅ Results cleaned!"

clean-all: clean clean-results ## Clean everything

# =============================================================================
# DOCKER
# =============================================================================

docker-build: ## Build Docker image
	docker build -t cogos-research .

docker-run: ## Run in Docker
	docker run -it --gpus all -v $(PWD):/workspace cogos-research

# =============================================================================
# INFO
# =============================================================================

info: ## Show project info
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║           CogOS Research - NeurIPS 2025                      ║"
	@echo "╠══════════════════════════════════════════════════════════════╣"
	@echo "║ Papers: 1 Main + 32 Workshops = 33 total                     ║"
	@echo "║ Main Deadline: May 15, 2025                                  ║"
	@echo "║ Workshops: June-August 2025                                  ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "📁 Project Structure:"
	@echo "   configs/     - Configuration files"
	@echo "   src/         - Source code"
	@echo "   scripts/     - Utility scripts"
	@echo "   data/        - Datasets"
	@echo "   results/     - Experiment results"
	@echo "   figures/     - Generated figures"
	@echo "   papers/      - Paper drafts"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "   make setup   - Install dependencies"
	@echo "   make data    - Download datasets"
	@echo "   make experiments-test - Quick test run"

help: ## Show this help
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
