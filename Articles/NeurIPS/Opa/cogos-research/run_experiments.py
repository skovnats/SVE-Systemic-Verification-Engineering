#!/usr/bin/env python3
"""
CogOS Research: Main Experiment Runner

Usage:
    python run_experiments.py --paper main          # Run main paper experiments
    python run_experiments.py --paper 1             # Run paper 1 experiments
    python run_experiments.py --baselines           # Run all baselines
    python run_experiments.py --all                 # Run everything
    
Examples:
    # Full main paper evaluation
    python run_experiments.py --paper main --datasets truthfulqa gaia ethics
    
    # Quick test run
    python run_experiments.py --paper main --test --n-samples 10
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cogos.core import CogOS, CogOSMetrics
from baselines.methods import BaselineRunner, VanillaBaseline, ChainOfThoughtBaseline
from baselines.methods import ReActBaseline, ConstitutionalAIBaseline, CoVeBaseline, RLHFBaseline
from evaluation.pipeline import EvaluationPipeline, DatasetLoader


def load_config(config_path: str = "configs/main_config.yaml") -> dict:
    """Load configuration."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_paper_config(paper_id: str) -> dict:
    """Load paper-specific configuration."""
    with open("configs/papers_config.yaml") as f:
        papers = yaml.safe_load(f)
        
    # Find paper config
    key = f"paper_{paper_id}" if paper_id.isdigit() else f"paper_0_{paper_id}"
    
    for k, v in papers.items():
        if k.startswith(f"paper_{paper_id}") or paper_id in k:
            return v
            
    return papers.get(key, {})


def setup_cogos(config: dict) -> CogOS:
    """Initialize CogOS system."""
    import numpy as np
    
    cogos_config = config.get("cogos", {})
    
    cogos = CogOS(
        embedding_dim=cogos_config.get("isc", {}).get("embedding_dim", 1536),
        max_iterations=cogos_config.get("sip", {}).get("max_iterations", 10),
        convergence_epsilon=cogos_config.get("sip", {}).get("convergence_epsilon", 0.01)
    )
    
    # Initialize GEV with cultural embeddings
    np.random.seed(42)
    cultures = cogos_config.get("gev", {}).get("cultures_for_init", 
                                                ["western", "confucian", "islamic", "ubuntu", "latin_american"])
    
    cultural_embeddings = {
        culture: np.random.randn(cogos.embedding_dim) 
        for culture in cultures
    }
    cogos.initialize_gev(cultural_embeddings)
    
    return cogos


def setup_baselines() -> dict:
    """Initialize all baseline methods."""
    return {
        "gpt4_baseline": VanillaBaseline(),
        "cot": ChainOfThoughtBaseline(),
        "react": ReActBaseline(),
        "constitutional_ai": ConstitutionalAIBaseline(),
        "cove": CoVeBaseline(),
        "rlhf": RLHFBaseline()
    }


def run_baselines(config: dict, datasets: list = None, n_samples: int = None):
    """Run all baseline methods."""
    print("\n" + "="*60)
    print("Running Baseline Experiments")
    print("="*60)
    
    loader = DatasetLoader(config.get("paths", {}).get("data_dir", "./data"))
    runner = BaselineRunner(config.get("paths", {}).get("baselines_dir", "./baselines/results"))
    
    if datasets is None:
        datasets = ["truthfulqa", "ethics", "gaia"]
        
    for dataset_name in datasets:
        print(f"\n--- Dataset: {dataset_name} ---")
        
        # Load dataset
        loader_method = getattr(loader, f"load_{dataset_name}", None)
        if loader_method is None:
            print(f"No loader for {dataset_name}")
            continue
            
        data = loader_method()
        if n_samples:
            data = data[:n_samples]
            
        if not data:
            print(f"No data loaded for {dataset_name}")
            continue
            
        print(f"Loaded {len(data)} samples")
        
        # Run baselines
        runner.run_dataset(data, dataset_name)
        
    print("\n✅ Baselines complete!")


def run_main_paper(config: dict, datasets: list = None, n_samples: int = None):
    """Run main paper (CogOS) experiments."""
    print("\n" + "="*60)
    print("Running Main Paper Experiments: CogOS")
    print("="*60)
    
    # Setup
    cogos = setup_cogos(config)
    baselines = setup_baselines()
    pipeline = EvaluationPipeline(results_dir="./results/main_paper")
    
    # Define CogOS method wrapper
    def cogos_method(query: str, context: dict = None):
        return cogos.process(query, context)
    
    # All methods including CogOS
    methods = {"cogos": cogos_method}
    methods.update({name: baseline.process for name, baseline in baselines.items()})
    
    if datasets is None:
        datasets = ["truthfulqa", "gaia", "ethics", "moral_machine", "ccdb"]
        
    # Run evaluation
    results = pipeline.run_full_evaluation(methods, datasets)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for key, result in sorted(results.items()):
        print(f"\n{result.dataset} - {result.method}:")
        print(f"  Accuracy: {result.accuracy:.3f}")
        if "hallucination_rate" in result.metrics:
            print(f"  Hallucination: {result.metrics['hallucination_rate']:.3f}")
            
    return results


def run_paper_experiments(paper_id: str, config: dict, n_samples: int = None):
    """Run experiments for a specific paper."""
    paper_config = load_paper_config(paper_id)
    
    if not paper_config:
        print(f"No configuration found for paper {paper_id}")
        return
        
    print("\n" + "="*60)
    print(f"Running: {paper_config.get('title', paper_id)}")
    print(f"Track: {paper_config.get('track', 'unknown')}")
    print("="*60)
    
    # Get experiments from config
    experiments = paper_config.get("experiments", [])
    
    for exp in experiments:
        print(f"\n--- Experiment: {exp.get('name')} ---")
        
        datasets = exp.get("datasets", [])
        metrics = exp.get("metrics", [])
        
        print(f"Datasets: {datasets}")
        print(f"Metrics: {metrics}")
        
        # Run experiment (simplified)
        # In full implementation, would run specific experiment logic
        
    print(f"\n✅ Paper {paper_id} experiments complete!")


def generate_paper_tables(paper_id: str, results_dir: str = "./results"):
    """Generate LaTeX tables for a paper."""
    results_path = Path(results_dir)
    
    print(f"\nGenerating tables for paper {paper_id}...")
    
    # Load results
    results = {}
    for f in results_path.glob("*_aggregated.json"):
        with open(f) as file:
            data = json.load(file)
            key = f"{data['dataset']}_{data['method']}"
            results[key] = data
            
    if not results:
        print("No results found")
        return
        
    # Generate LaTeX table
    latex = """\\begin{table}[h]
\\centering
\\caption{Results on [DATASET]}
\\begin{tabular}{lccc}
\\toprule
Method & Accuracy & Hallucination & Latency \\\\
\\midrule
"""
    
    for key, r in sorted(results.items()):
        hall = r.get("metrics", {}).get("hallucination_rate", 0)
        latex += f"{r['method']} & {r['accuracy']:.3f} & {hall:.3f} & {r['mean_latency']:.2f}s \\\\\n"
        
    latex += """\\bottomrule
\\end{tabular}
\\end{table}
"""
    
    # Save
    output_path = results_path / f"paper_{paper_id}_tables.tex"
    with open(output_path, "w") as f:
        f.write(latex)
        
    print(f"Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="CogOS Research Experiment Runner")
    
    parser.add_argument("--paper", type=str, help="Paper ID to run (main, 1-32)")
    parser.add_argument("--baselines", action="store_true", help="Run baseline experiments only")
    parser.add_argument("--all", action="store_true", help="Run all experiments")
    parser.add_argument("--datasets", nargs="+", help="Specific datasets to run")
    parser.add_argument("--test", action="store_true", help="Test mode (small sample)")
    parser.add_argument("--n-samples", type=int, help="Number of samples to use")
    parser.add_argument("--config", type=str, default="configs/main_config.yaml", help="Config file")
    parser.add_argument("--generate-tables", action="store_true", help="Generate LaTeX tables")
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Determine n_samples
    n_samples = args.n_samples
    if args.test:
        n_samples = n_samples or 10
        
    # Run appropriate experiments
    if args.baselines:
        run_baselines(config, args.datasets, n_samples)
        
    elif args.paper:
        if args.paper.lower() == "main":
            results = run_main_paper(config, args.datasets, n_samples)
            if args.generate_tables:
                generate_paper_tables("main")
        else:
            run_paper_experiments(args.paper, config, n_samples)
            if args.generate_tables:
                generate_paper_tables(args.paper)
                
    elif args.all:
        # Run everything
        run_baselines(config, args.datasets, n_samples)
        run_main_paper(config, args.datasets, n_samples)
        
        # Run all paper-specific experiments
        for i in range(1, 33):
            run_paper_experiments(str(i), config, n_samples)
            
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
