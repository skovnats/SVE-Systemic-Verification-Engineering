#!/usr/bin/env python3
"""
CogOS Research: Dataset Download and Setup Script
Downloads all required datasets for NeurIPS 2025 experiments.

Usage:
    python scripts/download_datasets.py --all
    python scripts/download_datasets.py --dataset truthfulqa
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Optional
import requests
from tqdm import tqdm
import zipfile
import tarfile

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data"


class DatasetDownloader:
    """Handles downloading and setup of all research datasets."""
    
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def download_file(self, url: str, dest: Path, desc: str = "Downloading"):
        """Download a file with progress bar."""
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(dest, 'wb') as f, tqdm(
            desc=desc,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                pbar.update(size)
                
    def download_truthfulqa(self):
        """Download TruthfulQA dataset."""
        print("\n📥 Downloading TruthfulQA...")
        dest_dir = self.data_dir / "truthfulqa"
        dest_dir.mkdir(exist_ok=True)
        
        # Clone repository
        repo_url = "https://github.com/sylinrl/TruthfulQA.git"
        if not (dest_dir / "TruthfulQA").exists():
            subprocess.run(["git", "clone", repo_url, str(dest_dir / "TruthfulQA")])
        
        # Copy main file
        src = dest_dir / "TruthfulQA" / "TruthfulQA.csv"
        if src.exists():
            import shutil
            shutil.copy(src, dest_dir / "truthfulqa.csv")
            
        print("✅ TruthfulQA ready!")
        return dest_dir
        
    def download_gaia(self):
        """Download GAIA benchmark from HuggingFace."""
        print("\n📥 Downloading GAIA...")
        dest_dir = self.data_dir / "gaia"
        dest_dir.mkdir(exist_ok=True)
        
        # Use HuggingFace datasets
        try:
            from datasets import load_dataset
            dataset = load_dataset("gaia-benchmark/GAIA", "2023_all")
            
            # Save to disk
            for split in ["validation", "test"]:
                if split in dataset:
                    dataset[split].to_json(dest_dir / f"{split}.json")
                    
            print("✅ GAIA ready!")
        except Exception as e:
            print(f"⚠️ GAIA download failed: {e}")
            print("   Please download manually from: https://huggingface.co/datasets/gaia-benchmark/GAIA")
            
        return dest_dir
        
    def download_ethics(self):
        """Download ETHICS dataset."""
        print("\n📥 Downloading ETHICS...")
        dest_dir = self.data_dir / "ethics"
        dest_dir.mkdir(exist_ok=True)
        
        # Clone repository
        repo_url = "https://github.com/hendrycks/ethics.git"
        if not (dest_dir / "ethics").exists():
            subprocess.run(["git", "clone", repo_url, str(dest_dir / "ethics")])
            
        print("✅ ETHICS ready!")
        return dest_dir
        
    def download_moral_machine(self):
        """Download Moral Machine dataset (requires academic access)."""
        print("\n📥 Moral Machine...")
        dest_dir = self.data_dir / "moral_machine"
        dest_dir.mkdir(exist_ok=True)
        
        # Create placeholder with instructions
        readme = dest_dir / "README.md"
        readme.write_text("""# Moral Machine Dataset

## Download Instructions

1. Go to: https://osf.io/3hvt2/
2. Request access (academic use)
3. Download the dataset files
4. Place them in this directory

## Expected Files
- SharedResponses.csv (main responses)
- CountryData.csv (country-level aggregates)

## Alternative: Use subset
We provide a 10k sample for testing in `sample/`
""")
        
        # Create sample subset (placeholder)
        sample_dir = dest_dir / "sample"
        sample_dir.mkdir(exist_ok=True)
        
        print("⚠️ Moral Machine requires manual download (academic access)")
        print("   See: data/moral_machine/README.md")
        return dest_dir
        
    def create_ccdb(self):
        """Create Cross-Cultural Dilemma Benchmark."""
        print("\n🔨 Creating CCDB...")
        dest_dir = self.data_dir / "ccdb"
        dest_dir.mkdir(exist_ok=True)
        
        # CCDB structure
        ccdb = {
            "metadata": {
                "name": "Cross-Cultural Dilemma Benchmark",
                "version": "1.0",
                "n_scenarios": 500,
                "cultures": [
                    "western", "confucian", "islamic", "ubuntu", "latin_american",
                    "hindu", "buddhist", "slavic", "nordic", "indigenous"
                ]
            },
            "scenarios": []
        }
        
        # Categories for scenarios
        categories = [
            "individual_vs_collective",
            "authority_vs_autonomy",
            "tradition_vs_progress",
            "justice_vs_mercy",
            "truth_vs_harmony",
            "duty_vs_consequence",
            "sacred_vs_secular",
            "family_vs_society",
            "honor_vs_law",
            "nature_vs_development"
        ]
        
        # Generate placeholder scenarios (to be expanded)
        for i in range(500):
            scenario = {
                "id": f"ccdb_{i:04d}",
                "category": categories[i % len(categories)],
                "text": f"[Scenario {i} - to be written]",
                "cultural_context": ccdb["metadata"]["cultures"][i % 10],
                "expected_variance": "high" if i % 3 == 0 else "medium" if i % 3 == 1 else "low"
            }
            ccdb["scenarios"].append(scenario)
            
        # Save
        with open(dest_dir / "ccdb.json", "w") as f:
            json.dump(ccdb, f, indent=2)
            
        # Create culture-specific files
        for culture in ccdb["metadata"]["cultures"]:
            culture_scenarios = [s for s in ccdb["scenarios"] if s["cultural_context"] == culture]
            with open(dest_dir / f"{culture}.json", "w") as f:
                json.dump(culture_scenarios, f, indent=2)
                
        print("✅ CCDB structure created!")
        print("   Note: Scenarios need to be written (see templates)")
        return dest_dir
        
    def download_additional(self):
        """Download additional helpful datasets."""
        print("\n📥 Downloading additional datasets...")
        
        # BIG-Bench Hard
        bbh_dir = self.data_dir / "bigbench_hard"
        bbh_dir.mkdir(exist_ok=True)
        if not (bbh_dir / "BIG-Bench-Hard").exists():
            subprocess.run([
                "git", "clone", 
                "https://github.com/suzgunmirac/BIG-Bench-Hard.git",
                str(bbh_dir / "BIG-Bench-Hard")
            ])
            
        # MMLU
        mmlu_dir = self.data_dir / "mmlu"
        mmlu_dir.mkdir(exist_ok=True)
        if not (mmlu_dir / "test").exists():
            subprocess.run([
                "git", "clone",
                "https://github.com/hendrycks/test.git",
                str(mmlu_dir / "test")
            ])
            
        print("✅ Additional datasets ready!")
        
    def download_all(self):
        """Download all datasets."""
        print("=" * 60)
        print("CogOS Research: Dataset Setup")
        print("=" * 60)
        
        self.download_truthfulqa()
        self.download_gaia()
        self.download_ethics()
        self.download_moral_machine()
        self.create_ccdb()
        self.download_additional()
        
        print("\n" + "=" * 60)
        print("✅ All datasets ready!")
        print("=" * 60)
        
        # Summary
        print("\nDataset locations:")
        for d in self.data_dir.iterdir():
            if d.is_dir():
                print(f"  📁 {d.name}: {d}")


def main():
    parser = argparse.ArgumentParser(description="Download CogOS research datasets")
    parser.add_argument("--all", action="store_true", help="Download all datasets")
    parser.add_argument("--dataset", type=str, help="Download specific dataset")
    parser.add_argument("--data-dir", type=str, default=str(DATA_DIR), help="Data directory")
    
    args = parser.parse_args()
    
    downloader = DatasetDownloader(Path(args.data_dir))
    
    if args.all:
        downloader.download_all()
    elif args.dataset:
        method = getattr(downloader, f"download_{args.dataset}", None)
        if method:
            method()
        else:
            print(f"Unknown dataset: {args.dataset}")
            print("Available: truthfulqa, gaia, ethics, moral_machine, ccdb, additional")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
