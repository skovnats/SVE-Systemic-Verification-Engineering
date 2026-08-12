#!/usr/bin/env python3
# scripts/download_all.py

"""
Download all benchmark datasets for CogOS research.

Usage:
    python scripts/download_all.py                    # Download all
    python scripts/download_all.py --only truthfulqa gaia  # Download specific
    python scripts/download_all.py --list            # List available datasets
    python scripts/download_all.py --dev             # Download dev subsets only
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional
import logging
import yaml

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# DATASET DOWNLOAD FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def download_truthfulqa(data_dir: Path, subset_size: Optional[int] = None) -> bool:
    """Download TruthfulQA dataset."""
    try:
        from datasets import load_dataset
        
        console.print("[cyan]Downloading TruthfulQA...[/cyan]")
        
        # Download both splits
        ds_mc = load_dataset("truthful_qa", "multiple_choice")
        ds_gen = load_dataset("truthful_qa", "generation")
        
        # Subset if requested
        if subset_size:
            ds_mc = ds_mc["validation"].select(range(min(subset_size, len(ds_mc["validation"]))))
            ds_gen = ds_gen["validation"].select(range(min(subset_size, len(ds_gen["validation"]))))
        
        # Save
        save_path = data_dir / "truthfulqa"
        save_path.mkdir(parents=True, exist_ok=True)
        
        ds_mc.save_to_disk(str(save_path / "multiple_choice"))
        ds_gen.save_to_disk(str(save_path / "generation"))
        
        console.print(f"[green]✓ TruthfulQA saved to {save_path}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Failed to download TruthfulQA: {e}[/red]")
        return False


def download_gaia(data_dir: Path, subset_size: Optional[int] = None) -> bool:
    """Download GAIA benchmark."""
    try:
        from datasets import load_dataset
        
        console.print("[cyan]Downloading GAIA...[/cyan]")
        console.print("[yellow]Note: GAIA may require HuggingFace authentication[/yellow]")
        
        # Try to download
        try:
            ds = load_dataset("gaia-benchmark/GAIA", "2023_all")
        except Exception:
            console.print("[yellow]Trying alternative source...[/yellow]")
            ds = load_dataset("gaia-benchmark/GAIA")
        
        # Subset if requested
        if subset_size:
            for split in ds:
                ds[split] = ds[split].select(range(min(subset_size, len(ds[split]))))
        
        # Save
        save_path = data_dir / "gaia"
        ds.save_to_disk(str(save_path))
        
        console.print(f"[green]✓ GAIA saved to {save_path}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Failed to download GAIA: {e}[/red]")
        console.print("[yellow]Try: huggingface-cli login[/yellow]")
        return False


def download_ethics(data_dir: Path, subset_size: Optional[int] = None) -> bool:
    """Download ETHICS dataset."""
    try:
        from datasets import load_dataset
        
        console.print("[cyan]Downloading ETHICS...[/cyan]")
        
        subsets = ["commonsense", "deontology", "justice", "utilitarianism", "virtue"]
        save_path = data_dir / "ethics"
        save_path.mkdir(parents=True, exist_ok=True)
        
        for subset in subsets:
            console.print(f"  Downloading {subset}...")
            ds = load_dataset("hendrycks/ethics", subset)
            
            if subset_size:
                for split in ds:
                    ds[split] = ds[split].select(range(min(subset_size, len(ds[split]))))
            
            ds.save_to_disk(str(save_path / subset))
        
        console.print(f"[green]✓ ETHICS saved to {save_path}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Failed to download ETHICS: {e}[/red]")
        return False


def download_moral_machine(data_dir: Path, subset_size: Optional[int] = None) -> bool:
    """Download Moral Machine dataset."""
    try:
        import requests
        import pandas as pd
        
        console.print("[cyan]Downloading Moral Machine...[/cyan]")
        console.print("[yellow]Note: This is a large dataset (~2GB). Using sample.[/yellow]")
        
        save_path = data_dir / "moral_machine"
        save_path.mkdir(parents=True, exist_ok=True)
        
        # For now, create placeholder with instructions
        readme = """# Moral Machine Dataset

## Full Dataset
Download from OSF: https://osf.io/3hvt2/

Files:
- SharedResponses.csv (~2GB): Individual moral judgments
- CountryData.csv: Aggregated by country

## For Research
1. Visit https://osf.io/3hvt2/
2. Download SharedResponses.csv
3. Place in this directory
4. Run: python scripts/process_moral_machine.py

## Quick Start (Sample)
A 10,000 row sample is included for development.
"""
        
        (save_path / "README.md").write_text(readme)
        
        # Create sample placeholder
        sample_data = {
            "ResponseID": range(1000),
            "UserCountry3": ["USA"] * 500 + ["CHN"] * 300 + ["IND"] * 200,
            "Saved": [1, 0] * 500,
            "ScenarioType": ["Utilitarian"] * 500 + ["Random"] * 500,
        }
        pd.DataFrame(sample_data).to_csv(save_path / "sample.csv", index=False)
        
        console.print(f"[green]✓ Moral Machine placeholder saved to {save_path}[/green]")
        console.print("[yellow]  See README.md for full dataset download instructions[/yellow]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Failed to setup Moral Machine: {e}[/red]")
        return False


def download_mmlu(data_dir: Path, subset_size: Optional[int] = None) -> bool:
    """Download MMLU dataset."""
    try:
        from datasets import load_dataset
        
        console.print("[cyan]Downloading MMLU...[/cyan]")
        
        # Download relevant subsets for ethics research
        subsets = ["moral_scenarios", "philosophy", "professional_law"]
        save_path = data_dir / "mmlu"
        save_path.mkdir(parents=True, exist_ok=True)
        
        for subset in subsets:
            console.print(f"  Downloading {subset}...")
            ds = load_dataset("cais/mmlu", subset)
            
            if subset_size:
                for split in ds:
                    ds[split] = ds[split].select(range(min(subset_size, len(ds[split]))))
            
            ds.save_to_disk(str(save_path / subset))
        
        console.print(f"[green]✓ MMLU saved to {save_path}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Failed to download MMLU: {e}[/red]")
        return False


def download_gsm8k(data_dir: Path, subset_size: Optional[int] = None) -> bool:
    """Download GSM8K dataset."""
    try:
        from datasets import load_dataset
        
        console.print("[cyan]Downloading GSM8K...[/cyan]")
        
        ds = load_dataset("gsm8k", "main")
        
        if subset_size:
            for split in ds:
                ds[split] = ds[split].select(range(min(subset_size, len(ds[split]))))
        
        save_path = data_dir / "gsm8k"
        ds.save_to_disk(str(save_path))
        
        console.print(f"[green]✓ GSM8K saved to {save_path}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Failed to download GSM8K: {e}[/red]")
        return False


def download_math(data_dir: Path, subset_size: Optional[int] = None) -> bool:
    """Download MATH dataset."""
    try:
        from datasets import load_dataset
        
        console.print("[cyan]Downloading MATH...[/cyan]")
        
        ds = load_dataset("hendrycks/competition_math")
        
        if subset_size:
            for split in ds:
                ds[split] = ds[split].select(range(min(subset_size, len(ds[split]))))
        
        save_path = data_dir / "math"
        ds.save_to_disk(str(save_path))
        
        console.print(f"[green]✓ MATH saved to {save_path}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Failed to download MATH: {e}[/red]")
        return False


def download_arc(data_dir: Path, subset_size: Optional[int] = None) -> bool:
    """Download ARC dataset."""
    try:
        from datasets import load_dataset
        
        console.print("[cyan]Downloading ARC...[/cyan]")
        
        save_path = data_dir / "arc"
        save_path.mkdir(parents=True, exist_ok=True)
        
        for subset in ["ARC-Easy", "ARC-Challenge"]:
            ds = load_dataset("allenai/ai2_arc", subset)
            
            if subset_size:
                for split in ds:
                    ds[split] = ds[split].select(range(min(subset_size, len(ds[split]))))
            
            ds.save_to_disk(str(save_path / subset.lower()))
        
        console.print(f"[green]✓ ARC saved to {save_path}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Failed to download ARC: {e}[/red]")
        return False


def download_humaneval(data_dir: Path, subset_size: Optional[int] = None) -> bool:
    """Download HumanEval dataset."""
    try:
        from datasets import load_dataset
        
        console.print("[cyan]Downloading HumanEval...[/cyan]")
        
        ds = load_dataset("openai_humaneval")
        
        save_path = data_dir / "humaneval"
        ds.save_to_disk(str(save_path))
        
        console.print(f"[green]✓ HumanEval saved to {save_path}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Failed to download HumanEval: {e}[/red]")
        return False


# ═══════════════════════════════════════════════════════════════
# REGISTRY
# ═══════════════════════════════════════════════════════════════

DATASET_REGISTRY = {
    "truthfulqa": {
        "func": download_truthfulqa,
        "size": "817 questions",
        "source": "HuggingFace",
        "papers": ["main", "socratic", "ivan", "vkb"],
    },
    "gaia": {
        "func": download_gaia,
        "size": "450 tasks",
        "source": "HuggingFace",
        "papers": ["main", "ivan", "vkb"],
    },
    "ethics": {
        "func": download_ethics,
        "size": "130K scenarios",
        "source": "HuggingFace",
        "papers": ["main", "betti", "lyapunov", "solomon"],
    },
    "moral_machine": {
        "func": download_moral_machine,
        "size": "40M judgments",
        "source": "OSF",
        "papers": ["main", "delta", "cultural"],
    },
    "mmlu": {
        "func": download_mmlu,
        "size": "14K questions",
        "source": "HuggingFace",
        "papers": ["godel", "ivan"],
    },
    "gsm8k": {
        "func": download_gsm8k,
        "size": "8.5K problems",
        "source": "HuggingFace",
        "papers": ["betti", "geometry"],
    },
    "math": {
        "func": download_math,
        "size": "12.5K problems",
        "source": "HuggingFace",
        "papers": ["betti", "geometry"],
    },
    "arc": {
        "func": download_arc,
        "size": "7.7K questions",
        "source": "HuggingFace",
        "papers": ["ivan"],
    },
    "humaneval": {
        "func": download_humaneval,
        "size": "164 problems",
        "source": "HuggingFace",
        "papers": ["scale"],
    },
}


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def list_datasets():
    """Display available datasets."""
    table = Table(title="Available Datasets")
    table.add_column("Name", style="cyan")
    table.add_column("Size", style="green")
    table.add_column("Source", style="yellow")
    table.add_column("Papers Using", style="magenta")
    
    for name, info in DATASET_REGISTRY.items():
        table.add_row(
            name,
            info["size"],
            info["source"],
            ", ".join(info["papers"][:3]) + ("..." if len(info["papers"]) > 3 else ""),
        )
    
    console.print(table)


def main():
    parser = argparse.ArgumentParser(description="Download benchmark datasets")
    parser.add_argument("--only", nargs="+", help="Download only specific datasets")
    parser.add_argument("--list", action="store_true", help="List available datasets")
    parser.add_argument("--dev", action="store_true", help="Download dev subsets only")
    parser.add_argument("--data-dir", default="benchmarks/data", help="Data directory")
    
    args = parser.parse_args()
    
    if args.list:
        list_datasets()
        return
    
    # Setup
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine subset size for dev mode
    subset_size = 100 if args.dev else None
    
    # Determine which datasets to download
    datasets = args.only if args.only else list(DATASET_REGISTRY.keys())
    
    # Validate
    for ds in datasets:
        if ds not in DATASET_REGISTRY:
            console.print(f"[red]Unknown dataset: {ds}[/red]")
            console.print(f"Available: {', '.join(DATASET_REGISTRY.keys())}")
            return
    
    # Download
    console.print(f"\n[bold]Downloading {len(datasets)} datasets...[/bold]\n")
    
    results = {}
    for ds_name in datasets:
        func = DATASET_REGISTRY[ds_name]["func"]
        results[ds_name] = func(data_dir, subset_size)
        console.print()
    
    # Summary
    console.print("\n[bold]Download Summary:[/bold]")
    success = sum(results.values())
    console.print(f"  Success: {success}/{len(results)}")
    
    if failed := [k for k, v in results.items() if not v]:
        console.print(f"  [red]Failed: {', '.join(failed)}[/red]")


if __name__ == "__main__":
    main()
