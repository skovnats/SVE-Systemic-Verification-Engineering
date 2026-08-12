"""
CogOS Metrics: Comprehensive Metric Implementations

All metrics used across 33 papers:
- ∆-Dehumanization
- GEV Distance
- Lyapunov Exponent
- Cultural Variance
- Semantic Convergence Rate
- Betti Numbers (TDA)
- And more...
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from scipy import stats
import warnings


@dataclass
class MetricResult:
    """Result from a metric computation."""
    name: str
    value: float
    confidence_interval: Optional[Tuple[float, float]] = None
    metadata: Optional[Dict] = None


class DeltaDehumanization:
    """
    ∆-Dehumanization Metric
    
    Measures ethical drift over time:
    ∆(x, t) = d/dt ||x(t) - C|| + β ||div ∇_x E||
    
    Positive ∆ = dehumanization (drifting from ethical ideal)
    Negative ∆ = ethical recovery (moving toward ideal)
    Zero ∆ = stability
    """
    
    def __init__(self, gev_embedding: np.ndarray, beta: float = 0.1):
        """
        Args:
            gev_embedding: The Geodesic Ethics Vector (ideal point)
            beta: Weight for divergence term
        """
        self.gev = gev_embedding / np.linalg.norm(gev_embedding)
        self.beta = beta
        
    def compute(self, trajectory: List[np.ndarray]) -> List[float]:
        """
        Compute ∆-Dehumanization for each step in trajectory.
        
        Args:
            trajectory: List of embeddings over time
            
        Returns:
            List of ∆ values
        """
        if len(trajectory) < 2:
            return [0.0]
            
        deltas = []
        for i in range(1, len(trajectory)):
            # Normalize embeddings
            v_prev = trajectory[i-1] / np.linalg.norm(trajectory[i-1])
            v_curr = trajectory[i] / np.linalg.norm(trajectory[i])
            
            # Distance to GEV
            dist_prev = np.linalg.norm(v_prev - self.gev)
            dist_curr = np.linalg.norm(v_curr - self.gev)
            
            # Rate of change
            d_dist = dist_curr - dist_prev
            
            # Divergence term (simplified: use magnitude of change)
            div_term = np.linalg.norm(v_curr - v_prev)
            
            # Combined metric
            delta = d_dist + self.beta * div_term
            deltas.append(float(delta))
            
        return deltas
    
    def compute_single(self, v_prev: np.ndarray, v_curr: np.ndarray) -> float:
        """Compute ∆ for a single transition."""
        return self.compute([v_prev, v_curr])[0]
    
    def is_stable(self, trajectory: List[np.ndarray], threshold: float = 0.01) -> bool:
        """Check if trajectory is ethically stable."""
        deltas = self.compute(trajectory)
        return all(d <= threshold for d in deltas[-3:]) if len(deltas) >= 3 else True
    
    def get_metric_result(self, trajectory: List[np.ndarray]) -> MetricResult:
        """Get full metric result with statistics."""
        deltas = self.compute(trajectory)
        
        return MetricResult(
            name="delta_dehumanization",
            value=float(np.mean(deltas)),
            confidence_interval=(float(np.min(deltas)), float(np.max(deltas))),
            metadata={
                "final_delta": deltas[-1] if deltas else 0.0,
                "max_delta": float(np.max(deltas)) if deltas else 0.0,
                "stable": self.is_stable(trajectory),
                "n_steps": len(deltas)
            }
        )


class GEVDistance:
    """
    Geodesic Ethics Vector Distance
    
    Measures distance from current state to ethical ideal.
    """
    
    def __init__(self, gev_embedding: np.ndarray):
        self.gev = gev_embedding / np.linalg.norm(gev_embedding)
        
    def compute(self, embedding: np.ndarray) -> float:
        """Compute distance to GEV."""
        v = embedding / np.linalg.norm(embedding)
        return float(np.linalg.norm(v - self.gev))
    
    def compute_batch(self, embeddings: List[np.ndarray]) -> List[float]:
        """Compute distances for batch of embeddings."""
        return [self.compute(e) for e in embeddings]
    
    def compute_cosine(self, embedding: np.ndarray) -> float:
        """Compute cosine similarity to GEV."""
        v = embedding / np.linalg.norm(embedding)
        return float(np.dot(v, self.gev))


class LyapunovExponent:
    """
    Lyapunov Exponent for Ethical Stability
    
    Negative = stable (converging to attractor)
    Positive = unstable (diverging)
    Zero = neutral
    """
    
    def __init__(self, gev_embedding: np.ndarray):
        self.gev = gev_embedding / np.linalg.norm(gev_embedding)
        
    def compute(self, trajectory: List[np.ndarray]) -> float:
        """
        Estimate Lyapunov exponent from trajectory.
        
        Uses linear regression on log distances.
        """
        if len(trajectory) < 3:
            return 0.0
            
        # Compute distances to GEV over time
        distances = []
        for v in trajectory:
            v_norm = v / np.linalg.norm(v)
            dist = np.linalg.norm(v_norm - self.gev)
            distances.append(max(dist, 1e-10))  # Avoid log(0)
            
        # Fit exponential: d(t) ~ d(0) * exp(λt)
        # log(d(t)) = log(d(0)) + λt
        t = np.arange(len(distances))
        log_d = np.log(distances)
        
        # Linear regression
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            slope, _, _, _, _ = stats.linregress(t, log_d)
            
        return float(slope)
    
    def is_stable(self, trajectory: List[np.ndarray]) -> bool:
        """Check if system is Lyapunov stable."""
        exponent = self.compute(trajectory)
        return exponent < 0
    
    def stability_classification(self, trajectory: List[np.ndarray]) -> str:
        """Classify stability type."""
        exponent = self.compute(trajectory)
        
        if exponent < -0.1:
            return "strongly_stable"
        elif exponent < 0:
            return "stable"
        elif exponent < 0.1:
            return "marginally_stable"
        else:
            return "unstable"


class CulturalVariance:
    """
    Cultural Variance Metric
    
    Measures disagreement/variance across cultural contexts.
    Lower = more universal agreement
    Higher = more cultural relativity
    """
    
    def compute(self, cultural_responses: Dict[str, List[float]]) -> float:
        """
        Compute variance across cultures.
        
        Args:
            cultural_responses: Dict mapping culture name to list of scores
            
        Returns:
            Variance across cultural means
        """
        if not cultural_responses:
            return 0.0
            
        # Compute mean for each culture
        means = [np.mean(scores) for scores in cultural_responses.values()]
        
        # Return variance of means
        return float(np.var(means))
    
    def compute_detailed(self, cultural_responses: Dict[str, List[float]]) -> Dict:
        """Get detailed cultural analysis."""
        if not cultural_responses:
            return {"variance": 0.0, "cultures": {}}
            
        culture_stats = {}
        for culture, scores in cultural_responses.items():
            culture_stats[culture] = {
                "mean": float(np.mean(scores)),
                "std": float(np.std(scores)),
                "n": len(scores)
            }
            
        means = [s["mean"] for s in culture_stats.values()]
        
        return {
            "variance": float(np.var(means)),
            "std": float(np.std(means)),
            "range": float(max(means) - min(means)),
            "cultures": culture_stats
        }


class SemanticConvergenceRate:
    """
    Semantic Convergence Rate (SCR)
    
    Measures how quickly the system converges to stable state.
    """
    
    def __init__(self, gev_embedding: np.ndarray = None):
        self.gev = gev_embedding
        if gev_embedding is not None:
            self.gev = gev_embedding / np.linalg.norm(gev_embedding)
            
    def compute(self, trajectory: List[np.ndarray]) -> float:
        """
        Compute convergence rate.
        
        Returns:
            Rate as (initial_dist - final_dist) / initial_dist
        """
        if len(trajectory) < 2:
            return 0.0
            
        if self.gev is None:
            # Use final state as target
            target = trajectory[-1] / np.linalg.norm(trajectory[-1])
        else:
            target = self.gev
            
        # Initial and final distances
        v_init = trajectory[0] / np.linalg.norm(trajectory[0])
        v_final = trajectory[-1] / np.linalg.norm(trajectory[-1])
        
        dist_init = np.linalg.norm(v_init - target)
        dist_final = np.linalg.norm(v_final - target)
        
        if dist_init == 0:
            return 1.0
            
        return float((dist_init - dist_final) / dist_init)
    
    def iterations_to_convergence(self, trajectory: List[np.ndarray], 
                                   threshold: float = 0.01) -> int:
        """Count iterations until convergence."""
        if len(trajectory) < 2:
            return 0
            
        for i in range(1, len(trajectory)):
            v_prev = trajectory[i-1] / np.linalg.norm(trajectory[i-1])
            v_curr = trajectory[i] / np.linalg.norm(trajectory[i])
            
            if np.linalg.norm(v_curr - v_prev) < threshold:
                return i
                
        return len(trajectory)


class BettiNumbers:
    """
    Betti Numbers for Topological Data Analysis
    
    Computes topological invariants of point clouds in semantic space.
    - β₀: Number of connected components
    - β₁: Number of loops/holes
    - β₂: Number of voids
    """
    
    def __init__(self):
        self.ripser_available = False
        try:
            import ripser
            self.ripser_available = True
        except ImportError:
            warnings.warn("ripser not installed. Install with: pip install ripser")
            
    def compute(self, points: np.ndarray, max_dim: int = 2) -> Dict[str, int]:
        """
        Compute Betti numbers for point cloud.
        
        Args:
            points: (n_points, dim) array
            max_dim: Maximum homology dimension
            
        Returns:
            Dict with β₀, β₁, β₂
        """
        if not self.ripser_available:
            # Return dummy values
            return {"beta_0": 1, "beta_1": 0, "beta_2": 0}
            
        import ripser
        
        # Compute persistence
        result = ripser.ripser(points, maxdim=max_dim)
        diagrams = result['dgms']
        
        # Count features (those with infinite persistence)
        betti = {}
        for dim in range(max_dim + 1):
            if dim < len(diagrams):
                # Count features with death > threshold
                n_features = np.sum(diagrams[dim][:, 1] > diagrams[dim][:, 0] + 0.1)
                betti[f"beta_{dim}"] = int(n_features)
            else:
                betti[f"beta_{dim}"] = 0
                
        return betti
    
    def persistence_entropy(self, points: np.ndarray) -> float:
        """Compute persistence entropy (topological complexity measure)."""
        if not self.ripser_available:
            return 0.0
            
        import ripser
        
        result = ripser.ripser(points, maxdim=1)
        diagram = result['dgms'][1]  # H1 persistence
        
        if len(diagram) == 0:
            return 0.0
            
        # Lifetimes
        lifetimes = diagram[:, 1] - diagram[:, 0]
        lifetimes = lifetimes[np.isfinite(lifetimes)]
        
        if len(lifetimes) == 0:
            return 0.0
            
        # Normalize to probabilities
        total = np.sum(lifetimes)
        if total == 0:
            return 0.0
            
        probs = lifetimes / total
        
        # Entropy
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        return float(entropy)


class CompilerEfficiency:
    """
    Cultural Compiler Efficiency
    
    Measures how well semantic meaning is preserved across cultural translations.
    """
    
    def __init__(self, gev_embedding: np.ndarray):
        self.gev = gev_embedding / np.linalg.norm(gev_embedding)
        
    def compute(self, original: np.ndarray, translated: np.ndarray) -> float:
        """
        Compute preservation of GEV distance after translation.
        
        Returns:
            1.0 = perfect preservation
            0.0 = complete loss
        """
        orig_norm = original / np.linalg.norm(original)
        trans_norm = translated / np.linalg.norm(translated)
        
        dist_orig = np.linalg.norm(orig_norm - self.gev)
        dist_trans = np.linalg.norm(trans_norm - self.gev)
        
        if dist_orig == 0:
            return 1.0 if dist_trans == 0 else 0.0
            
        # Measure preservation (penalize large changes)
        change = abs(dist_orig - dist_trans)
        preservation = 1.0 - min(change / dist_orig, 1.0)
        
        return float(preservation)
    
    def compute_semantic_similarity(self, original: np.ndarray, 
                                     translated: np.ndarray) -> float:
        """Compute cosine similarity between original and translated."""
        orig_norm = original / np.linalg.norm(original)
        trans_norm = translated / np.linalg.norm(translated)
        
        return float(np.dot(orig_norm, trans_norm))


class MetricsSuite:
    """
    Complete metrics suite for CogOS evaluation.
    """
    
    def __init__(self, gev_embedding: np.ndarray = None):
        if gev_embedding is None:
            gev_embedding = np.random.randn(1536)
        self.gev = gev_embedding / np.linalg.norm(gev_embedding)
        
        # Initialize all metrics
        self.delta = DeltaDehumanization(self.gev)
        self.gev_distance = GEVDistance(self.gev)
        self.lyapunov = LyapunovExponent(self.gev)
        self.cultural = CulturalVariance()
        self.scr = SemanticConvergenceRate(self.gev)
        self.betti = BettiNumbers()
        self.compiler = CompilerEfficiency(self.gev)
        
    def compute_all(self, trajectory: List[np.ndarray], 
                    cultural_responses: Dict[str, List[float]] = None) -> Dict:
        """Compute all metrics."""
        results = {}
        
        # Trajectory-based metrics
        if trajectory:
            results["delta_dehumanization"] = self.delta.get_metric_result(trajectory)
            results["gev_distance_final"] = self.gev_distance.compute(trajectory[-1])
            results["lyapunov_exponent"] = self.lyapunov.compute(trajectory)
            results["stability"] = self.lyapunov.stability_classification(trajectory)
            results["convergence_rate"] = self.scr.compute(trajectory)
            results["iterations"] = len(trajectory)
            
            # TDA metrics
            points = np.array([t / np.linalg.norm(t) for t in trajectory])
            if len(points) > 3:
                results["betti_numbers"] = self.betti.compute(points)
                results["persistence_entropy"] = self.betti.persistence_entropy(points)
                
        # Cultural metrics
        if cultural_responses:
            results["cultural_variance"] = self.cultural.compute(cultural_responses)
            results["cultural_details"] = self.cultural.compute_detailed(cultural_responses)
            
        return results


# Statistical utilities
def confidence_interval(values: List[float], confidence: float = 0.95) -> Tuple[float, float]:
    """Compute confidence interval."""
    if len(values) < 2:
        return (0.0, 0.0)
        
    n = len(values)
    mean = np.mean(values)
    se = stats.sem(values)
    h = se * stats.t.ppf((1 + confidence) / 2, n - 1)
    
    return (mean - h, mean + h)


def cohens_d(group1: List[float], group2: List[float]) -> float:
    """Compute Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    
    if pooled_std == 0:
        return 0.0
        
    return (np.mean(group1) - np.mean(group2)) / pooled_std


def paired_t_test(group1: List[float], group2: List[float]) -> Tuple[float, float]:
    """Perform paired t-test."""
    if len(group1) != len(group2) or len(group1) < 2:
        return (0.0, 1.0)
        
    t_stat, p_value = stats.ttest_rel(group1, group2)
    return (float(t_stat), float(p_value))


if __name__ == "__main__":
    print("Testing CogOS Metrics...")
    
    # Create test data
    np.random.seed(42)
    gev = np.random.randn(128)
    
    # Create trajectory converging to GEV
    trajectory = []
    v = np.random.randn(128)
    for i in range(10):
        v = 0.9 * v + 0.1 * gev + np.random.randn(128) * 0.01
        trajectory.append(v.copy())
    
    # Test metrics suite
    suite = MetricsSuite(gev)
    
    # Test individual metrics
    print(f"\n∆-Dehumanization (mean): {np.mean(suite.delta.compute(trajectory)):.4f}")
    print(f"GEV Distance (final): {suite.gev_distance.compute(trajectory[-1]):.4f}")
    print(f"Lyapunov Exponent: {suite.lyapunov.compute(trajectory):.4f}")
    print(f"Stability: {suite.lyapunov.stability_classification(trajectory)}")
    print(f"Convergence Rate: {suite.scr.compute(trajectory):.4f}")
    
    # Test cultural variance
    cultural_responses = {
        "western": [0.7, 0.8, 0.75],
        "confucian": [0.6, 0.65, 0.62],
        "islamic": [0.5, 0.55, 0.52]
    }
    print(f"Cultural Variance: {suite.cultural.compute(cultural_responses):.4f}")
    
    # Full suite
    results = suite.compute_all(trajectory, cultural_responses)
    print(f"\nFull Results: {len(results)} metrics computed")
    
    print("\n✅ Metrics test complete!")
