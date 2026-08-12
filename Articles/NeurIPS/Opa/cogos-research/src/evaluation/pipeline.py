"""
CogOS Research: Evaluation Pipeline

Unified evaluation system for:
- Running experiments across all datasets
- Computing all metrics
- Statistical analysis
- Results aggregation
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import pandas as pd
from scipy import stats
from tqdm import tqdm
import yaml


@dataclass
class EvaluationResult:
    """Result from evaluating a single example."""
    example_id: str
    method: str
    dataset: str
    prediction: str
    ground_truth: Optional[str]
    correct: bool
    metrics: Dict[str, float]
    latency: float
    timestamp: str


@dataclass 
class AggregatedResults:
    """Aggregated results for a method on a dataset."""
    method: str
    dataset: str
    n_samples: int
    accuracy: float
    accuracy_ci: Tuple[float, float]
    metrics: Dict[str, float]
    metrics_std: Dict[str, float]
    mean_latency: float
    total_time: float


class MetricsComputer:
    """Compute all CogOS metrics."""
    
    @staticmethod
    def accuracy(predictions: List[str], ground_truths: List[str]) -> float:
        """Compute accuracy."""
        if len(predictions) != len(ground_truths):
            raise ValueError("Prediction and ground truth lengths don't match")
        if len(predictions) == 0:
            return 0.0
            
        correct = sum(1 for p, g in zip(predictions, ground_truths) if p.strip().lower() == g.strip().lower())
        return correct / len(predictions)
    
    @staticmethod
    def hallucination_rate(predictions: List[str], ground_truths: List[str], 
                          verify_func: Optional[callable] = None) -> float:
        """
        Compute hallucination rate.
        
        A hallucination is a confident but incorrect statement.
        """
        if verify_func is None:
            # Simple heuristic: answer doesn't match any part of ground truth
            hallucinations = 0
            for pred, truth in zip(predictions, ground_truths):
                pred_lower = pred.lower()
                truth_lower = truth.lower()
                
                # Check if prediction contradicts ground truth
                if truth_lower not in pred_lower and pred_lower not in truth_lower:
                    # Check for confident language
                    confident_phrases = ["definitely", "certainly", "absolutely", "clearly", "obviously"]
                    if any(phrase in pred_lower for phrase in confident_phrases):
                        hallucinations += 1
                        
            return hallucinations / len(predictions) if predictions else 0.0
        
        return verify_func(predictions, ground_truths)
    
    @staticmethod
    def ethical_consistency(ethical_scores: List[float]) -> float:
        """Compute ethical consistency (low variance = high consistency)."""
        if not ethical_scores:
            return 0.0
        return 1.0 - np.std(ethical_scores)
    
    @staticmethod
    def cultural_variance(cultural_scores: Dict[str, List[float]]) -> float:
        """Compute variance across cultural contexts."""
        if not cultural_scores:
            return 0.0
            
        means = [np.mean(scores) for scores in cultural_scores.values()]
        return float(np.var(means))
    
    @staticmethod
    def confidence_interval(values: List[float], confidence: float = 0.95) -> Tuple[float, float]:
        """Compute confidence interval."""
        if len(values) < 2:
            return (0.0, 0.0)
            
        n = len(values)
        mean = np.mean(values)
        se = stats.sem(values)
        h = se * stats.t.ppf((1 + confidence) / 2, n - 1)
        
        return (mean - h, mean + h)
    
    @staticmethod
    def cohens_d(group1: List[float], group2: List[float]) -> float:
        """Compute Cohen's d effect size."""
        n1, n2 = len(group1), len(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        
        if pooled_std == 0:
            return 0.0
            
        return (np.mean(group1) - np.mean(group2)) / pooled_std
    
    @staticmethod
    def paired_t_test(group1: List[float], group2: List[float]) -> Tuple[float, float]:
        """Perform paired t-test."""
        if len(group1) != len(group2) or len(group1) < 2:
            return (0.0, 1.0)
            
        t_stat, p_value = stats.ttest_rel(group1, group2)
        return (float(t_stat), float(p_value))


class DatasetLoader:
    """Load and prepare datasets for evaluation."""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        
    def load_truthfulqa(self) -> List[Dict]:
        """Load TruthfulQA dataset."""
        path = self.data_dir / "truthfulqa" / "truthfulqa.csv"
        
        if not path.exists():
            print(f"TruthfulQA not found at {path}")
            return []
            
        df = pd.read_csv(path)
        
        dataset = []
        for _, row in df.iterrows():
            dataset.append({
                "id": f"tqa_{len(dataset)}",
                "question": row.get("Question", row.get("question", "")),
                "best_answer": row.get("Best Answer", row.get("best_answer", "")),
                "correct_answers": row.get("Correct Answers", "").split(";") if pd.notna(row.get("Correct Answers", "")) else [],
                "category": row.get("Category", ""),
                "source": "truthfulqa"
            })
            
        return dataset
    
    def load_ethics(self, category: str = "all") -> List[Dict]:
        """Load ETHICS dataset."""
        ethics_dir = self.data_dir / "ethics" / "ethics"
        
        if not ethics_dir.exists():
            print(f"ETHICS not found at {ethics_dir}")
            return []
            
        dataset = []
        categories = ["commonsense", "deontology", "justice", "utilitarianism", "virtue"]
        
        if category != "all":
            categories = [category]
            
        for cat in categories:
            cat_dir = ethics_dir / cat
            if cat_dir.exists():
                for split in ["test.csv", "test_hard.csv"]:
                    split_path = cat_dir / split
                    if split_path.exists():
                        df = pd.read_csv(split_path)
                        for _, row in df.iterrows():
                            dataset.append({
                                "id": f"ethics_{cat}_{len(dataset)}",
                                "text": row.iloc[0] if len(row) > 0 else "",
                                "label": int(row.iloc[1]) if len(row) > 1 else 0,
                                "category": cat,
                                "source": "ethics"
                            })
                            
        return dataset
    
    def load_gaia(self) -> List[Dict]:
        """Load GAIA dataset."""
        gaia_dir = self.data_dir / "gaia"
        
        dataset = []
        for split_file in ["validation.json", "test.json"]:
            path = gaia_dir / split_file
            if path.exists():
                with open(path) as f:
                    data = json.load(f)
                    for item in data:
                        dataset.append({
                            "id": item.get("task_id", f"gaia_{len(dataset)}"),
                            "question": item.get("Question", ""),
                            "level": item.get("Level", 1),
                            "answer": item.get("Final answer", ""),
                            "source": "gaia"
                        })
                        
        return dataset
    
    def load_ccdb(self) -> List[Dict]:
        """Load CCDB dataset."""
        path = self.data_dir / "ccdb" / "ccdb.json"
        
        if not path.exists():
            print(f"CCDB not found at {path}")
            return []
            
        with open(path) as f:
            data = json.load(f)
            
        return data.get("scenarios", [])
    
    def load_moral_machine(self, sample_size: int = 1000) -> List[Dict]:
        """Load Moral Machine dataset (sample)."""
        mm_dir = self.data_dir / "moral_machine"
        
        # Try sample first
        sample_path = mm_dir / "sample" / "sample.json"
        if sample_path.exists():
            with open(sample_path) as f:
                return json.load(f)[:sample_size]
                
        # Full dataset
        full_path = mm_dir / "SharedResponses.csv"
        if full_path.exists():
            df = pd.read_csv(full_path, nrows=sample_size)
            return df.to_dict('records')
            
        return []


class EvaluationPipeline:
    """Main evaluation pipeline."""
    
    def __init__(self, 
                 config_path: str = "./configs/main_config.yaml",
                 results_dir: str = "./results"):
        
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Load config
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
            
        self.metrics = MetricsComputer()
        self.loader = DatasetLoader(self.config.get("paths", {}).get("data_dir", "./data"))
        
    def evaluate_method(self,
                       method_name: str,
                       method_func: callable,
                       dataset: List[Dict],
                       dataset_name: str) -> AggregatedResults:
        """Evaluate a single method on a dataset."""
        
        results = []
        predictions = []
        ground_truths = []
        latencies = []
        
        for item in tqdm(dataset, desc=f"Evaluating {method_name} on {dataset_name}"):
            # Get question
            question = item.get("question") or item.get("text") or item.get("prompt")
            ground_truth = item.get("answer") or item.get("best_answer") or item.get("label")
            
            # Run method
            start_time = datetime.now()
            try:
                output = method_func(question, context=item)
                prediction = output.answer if hasattr(output, 'answer') else str(output)
            except Exception as e:
                prediction = f"[Error: {e}]"
            latency = (datetime.now() - start_time).total_seconds()
            
            # Check correctness
            correct = False
            if ground_truth:
                gt_str = str(ground_truth).lower().strip()
                pred_str = prediction.lower().strip()
                correct = gt_str in pred_str or pred_str in gt_str
                
            # Store results
            result = EvaluationResult(
                example_id=item.get("id", str(len(results))),
                method=method_name,
                dataset=dataset_name,
                prediction=prediction,
                ground_truth=str(ground_truth) if ground_truth else None,
                correct=correct,
                metrics={},
                latency=latency,
                timestamp=datetime.now().isoformat()
            )
            results.append(result)
            predictions.append(prediction)
            if ground_truth:
                ground_truths.append(str(ground_truth))
            latencies.append(latency)
            
        # Compute aggregated metrics
        accuracies = [1.0 if r.correct else 0.0 for r in results]
        accuracy = np.mean(accuracies) if accuracies else 0.0
        accuracy_ci = self.metrics.confidence_interval(accuracies)
        
        hall_rate = self.metrics.hallucination_rate(predictions, ground_truths) if ground_truths else 0.0
        
        aggregated = AggregatedResults(
            method=method_name,
            dataset=dataset_name,
            n_samples=len(results),
            accuracy=accuracy,
            accuracy_ci=accuracy_ci,
            metrics={
                "hallucination_rate": hall_rate,
            },
            metrics_std={
                "accuracy_std": np.std(accuracies) if accuracies else 0.0,
            },
            mean_latency=np.mean(latencies) if latencies else 0.0,
            total_time=sum(latencies)
        )
        
        # Save results
        self._save_results(results, aggregated, method_name, dataset_name)
        
        return aggregated
    
    def _save_results(self, 
                     results: List[EvaluationResult],
                     aggregated: AggregatedResults,
                     method: str,
                     dataset: str):
        """Save evaluation results."""
        
        # Save individual results
        results_path = self.results_dir / f"{dataset}_{method}_results.json"
        with open(results_path, "w") as f:
            json.dump([asdict(r) for r in results], f, indent=2)
            
        # Save aggregated
        agg_path = self.results_dir / f"{dataset}_{method}_aggregated.json"
        with open(agg_path, "w") as f:
            json.dump(asdict(aggregated), f, indent=2)
            
        print(f"Saved results to {results_path}")
        
    def run_full_evaluation(self, methods: Dict[str, callable], datasets: List[str] = None):
        """Run full evaluation across all methods and datasets."""
        
        if datasets is None:
            datasets = ["truthfulqa", "ethics", "gaia", "ccdb"]
            
        all_results = {}
        
        for dataset_name in datasets:
            print(f"\n{'='*60}")
            print(f"Dataset: {dataset_name}")
            print(f"{'='*60}")
            
            # Load dataset
            loader_method = getattr(self.loader, f"load_{dataset_name}", None)
            if loader_method is None:
                print(f"No loader for {dataset_name}")
                continue
                
            dataset = loader_method()
            if not dataset:
                print(f"Dataset {dataset_name} is empty or not found")
                continue
                
            print(f"Loaded {len(dataset)} examples")
            
            # Evaluate each method
            for method_name, method_func in methods.items():
                print(f"\nEvaluating: {method_name}")
                
                result = self.evaluate_method(
                    method_name=method_name,
                    method_func=method_func,
                    dataset=dataset,
                    dataset_name=dataset_name
                )
                
                all_results[f"{dataset_name}_{method_name}"] = result
                
                print(f"  Accuracy: {result.accuracy:.3f} ({result.accuracy_ci[0]:.3f}, {result.accuracy_ci[1]:.3f})")
                print(f"  Latency: {result.mean_latency:.2f}s")
                
        # Generate comparison report
        self._generate_report(all_results)
        
        return all_results
    
    def _generate_report(self, results: Dict[str, AggregatedResults]):
        """Generate comparison report."""
        
        report_path = self.results_dir / "comparison_report.md"
        
        with open(report_path, "w") as f:
            f.write("# CogOS Evaluation Report\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            # Group by dataset
            by_dataset = {}
            for key, result in results.items():
                dataset = result.dataset
                if dataset not in by_dataset:
                    by_dataset[dataset] = []
                by_dataset[dataset].append(result)
                
            for dataset, dataset_results in by_dataset.items():
                f.write(f"## {dataset.upper()}\n\n")
                f.write("| Method | Accuracy | 95% CI | Hallucination | Latency |\n")
                f.write("|--------|----------|--------|---------------|----------|\n")
                
                for r in sorted(dataset_results, key=lambda x: -x.accuracy):
                    hall = r.metrics.get("hallucination_rate", 0)
                    f.write(f"| {r.method} | {r.accuracy:.3f} | ({r.accuracy_ci[0]:.3f}, {r.accuracy_ci[1]:.3f}) | {hall:.3f} | {r.mean_latency:.2f}s |\n")
                    
                f.write("\n")
                
        print(f"\nReport saved to {report_path}")


class StatisticalAnalysis:
    """Statistical analysis for paper results."""
    
    def __init__(self, results_dir: str = "./results"):
        self.results_dir = Path(results_dir)
        self.metrics = MetricsComputer()
        
    def compare_methods(self, 
                       method1_results: List[float],
                       method2_results: List[float],
                       method1_name: str = "CogOS",
                       method2_name: str = "Baseline") -> Dict[str, Any]:
        """Compare two methods statistically."""
        
        t_stat, p_value = self.metrics.paired_t_test(method1_results, method2_results)
        effect_size = self.metrics.cohens_d(method1_results, method2_results)
        
        # Bonferroni correction (assuming 5 comparisons)
        p_corrected = min(p_value * 5, 1.0)
        
        return {
            "method1": method1_name,
            "method2": method2_name,
            "method1_mean": np.mean(method1_results),
            "method2_mean": np.mean(method2_results),
            "difference": np.mean(method1_results) - np.mean(method2_results),
            "t_statistic": t_stat,
            "p_value": p_value,
            "p_value_corrected": p_corrected,
            "cohens_d": effect_size,
            "effect_interpretation": self._interpret_effect_size(effect_size),
            "significant": p_corrected < 0.05
        }
    
    def _interpret_effect_size(self, d: float) -> str:
        """Interpret Cohen's d effect size."""
        d = abs(d)
        if d < 0.2:
            return "negligible"
        elif d < 0.5:
            return "small"
        elif d < 0.8:
            return "medium"
        else:
            return "large"


if __name__ == "__main__":
    print("Testing Evaluation Pipeline...")
    
    # Create mock method
    def mock_method(query: str, context: Optional[Dict] = None):
        class MockOutput:
            answer = f"Mock answer to: {query[:30]}..."
        return MockOutput()
    
    # Test metrics
    metrics = MetricsComputer()
    
    preds = ["yes", "no", "yes", "yes"]
    truths = ["yes", "yes", "yes", "no"]
    
    acc = metrics.accuracy(preds, truths)
    print(f"Accuracy: {acc}")
    
    # Test CI
    values = [0.8, 0.85, 0.82, 0.79, 0.83]
    ci = metrics.confidence_interval(values)
    print(f"CI: {ci}")
    
    # Test effect size
    g1 = [0.7, 0.75, 0.72, 0.78]
    g2 = [0.8, 0.85, 0.82, 0.88]
    d = metrics.cohens_d(g1, g2)
    print(f"Cohen's d: {d}")
    
    print("\n✅ Evaluation pipeline test complete!")
