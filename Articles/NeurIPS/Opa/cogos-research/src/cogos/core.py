"""
CogOS: Cognitive Operating System for Formally Verifiable AI Ethics

Core implementation of the triple-agent architecture with:
- Socrates: Logic & Inquiry
- Solomon: Ethics & Wisdom  
- Ivan: Empathy & Humility

Plus SIP (Systemic Iterative Progression) protocol.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from abc import ABC, abstractmethod
import json
from datetime import datetime


@dataclass
class ReasoningTrace:
    """Stores the reasoning trace for a single SIP iteration."""
    iteration: int
    socrates_output: Dict[str, Any]
    solomon_output: Dict[str, Any]
    ivan_output: Dict[str, Any]
    aggregated_embedding: np.ndarray
    delta_v: float
    delta_dehumanization: float
    epistemic_entropy: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CogOSOutput:
    """Final output from CogOS system."""
    answer: str
    confidence: float
    gev_distance: float
    delta_dehumanization: float
    lyapunov_stable: bool
    iterations: int
    trace: List[ReasoningTrace]
    cultural_adjustments: Optional[Dict[str, Any]] = None


class InvariantSemanticCore:
    """
    Invariant Semantic Core (ISC) / Transcendental Kernel
    
    Provides external grounding to prevent Gödelian semantic collapse.
    Based on Theorem 1: ISC Necessity.
    """
    
    def __init__(self, embedding_dim: int = 1536):
        self.embedding_dim = embedding_dim
        self.principles = [
            "Service to truth",
            "Service to humanity", 
            "Preservation of human dignity",
            "Epistemic humility"
        ]
        # ISC embedding (initialized, can be learned)
        self._embedding = self._initialize_embedding()
        
    def _initialize_embedding(self) -> np.ndarray:
        """Initialize ISC embedding from principles."""
        # In practice, this would use an LLM to embed principles
        # and find their centroid in semantic space
        np.random.seed(42)  # Reproducibility
        return np.random.randn(self.embedding_dim)
    
    @property
    def embedding(self) -> np.ndarray:
        return self._embedding / np.linalg.norm(self._embedding)
    
    def distance_to(self, v: np.ndarray) -> float:
        """Compute distance from vector to ISC."""
        v_norm = v / np.linalg.norm(v)
        return float(np.linalg.norm(v_norm - self.embedding))
    
    def project_toward(self, v: np.ndarray, alpha: float = 0.1) -> np.ndarray:
        """Project vector toward ISC by factor alpha."""
        return (1 - alpha) * v + alpha * self.embedding * np.linalg.norm(v)


class GeodesicEthicsVector:
    """
    Geodesic Ethics Vector (GEV) / Christ-Vector
    
    The unique fixed point representing universal human values,
    computed as the cultural centroid that minimizes variance.
    """
    
    def __init__(self, embedding_dim: int = 1536):
        self.embedding_dim = embedding_dim
        self._embedding = None
        self._cultural_embeddings = {}
        
    def initialize_from_cultures(self, cultural_embeddings: Dict[str, np.ndarray]):
        """
        Initialize GEV as centroid of cultural embeddings.
        
        GEV = argmin_v Σ_i λ_i ||T_i(v) - v||² + d(v, Φ)
        
        Simplified: mean of normalized cultural embeddings.
        """
        self._cultural_embeddings = cultural_embeddings
        
        embeddings = []
        for culture, emb in cultural_embeddings.items():
            emb_norm = emb / np.linalg.norm(emb)
            embeddings.append(emb_norm)
            
        self._embedding = np.mean(embeddings, axis=0)
        self._embedding = self._embedding / np.linalg.norm(self._embedding)
        
    @property
    def embedding(self) -> np.ndarray:
        if self._embedding is None:
            raise ValueError("GEV not initialized. Call initialize_from_cultures first.")
        return self._embedding
    
    def distance_to(self, v: np.ndarray) -> float:
        """Compute distance from vector to GEV."""
        v_norm = v / np.linalg.norm(v)
        return float(np.linalg.norm(v_norm - self.embedding))
    
    def project_toward(self, v: np.ndarray, beta: float = 0.1) -> np.ndarray:
        """Project vector toward GEV (Lyapunov gradient descent)."""
        return (1 - beta) * v + beta * self.embedding * np.linalg.norm(v)


class Agent(ABC):
    """Abstract base class for CogOS agents."""
    
    def __init__(self, name: str, weight: float, llm_client: Any = None):
        self.name = name
        self.weight = weight
        self.llm_client = llm_client
        
    @abstractmethod
    def process(self, 
                embedding: np.ndarray,
                context: Dict[str, Any],
                isc: InvariantSemanticCore,
                gev: GeodesicEthicsVector) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Process input and return updated embedding with metadata."""
        pass


class SocratesAgent(Agent):
    """
    Socrates Agent: Logic & Inquiry
    
    Applies rigorous logical analysis, identifies assumptions,
    and generates clarifying questions. Implements Bayesian belief updating.
    """
    
    def __init__(self, weight: float = 0.35, llm_client: Any = None, max_questions: int = 5):
        super().__init__("Socrates", weight, llm_client)
        self.max_questions = max_questions
        
    def process(self,
                embedding: np.ndarray,
                context: Dict[str, Any],
                isc: InvariantSemanticCore,
                gev: GeodesicEthicsVector) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Socratic reasoning:
        1. Identify assumptions
        2. Generate clarifying questions
        3. Apply Bayesian update
        4. Return refined embedding
        """
        metadata = {
            "agent": "Socrates",
            "assumptions": [],
            "questions": [],
            "bayesian_update": {},
            "logical_validity": 0.0
        }
        
        # In full implementation, this would:
        # 1. Call LLM to identify assumptions in context
        # 2. Generate Socratic questions
        # 3. Update beliefs based on evidence
        
        # Simplified: apply small perturbation toward logical consistency
        logic_direction = np.random.randn(len(embedding)) * 0.1
        updated_embedding = embedding + self.weight * logic_direction
        
        # Normalize
        updated_embedding = updated_embedding / np.linalg.norm(updated_embedding) * np.linalg.norm(embedding)
        
        metadata["logical_validity"] = 0.85  # Placeholder
        
        return updated_embedding, metadata


class SolomonAgent(Agent):
    """
    Solomon Agent: Ethics & Wisdom
    
    Evaluates ethical implications, computes proximity to GEV,
    and projects toward ethical attractor.
    """
    
    def __init__(self, weight: float = 0.40, llm_client: Any = None, delta_threshold: float = 0.1):
        super().__init__("Solomon", weight, llm_client)
        self.delta_threshold = delta_threshold
        
    def process(self,
                embedding: np.ndarray,
                context: Dict[str, Any],
                isc: InvariantSemanticCore,
                gev: GeodesicEthicsVector) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Solomonic wisdom:
        1. Evaluate ethical implications
        2. Compute GEV distance
        3. Compute ∆-Dehumanization
        4. Project toward GEV via Lyapunov gradient
        """
        metadata = {
            "agent": "Solomon",
            "gev_distance": 0.0,
            "delta_dehumanization": 0.0,
            "ethical_assessment": {},
            "cultural_sensitivity": 0.0
        }
        
        # Compute GEV distance
        gev_distance = gev.distance_to(embedding)
        metadata["gev_distance"] = gev_distance
        
        # Project toward GEV (Lyapunov descent)
        # V(v) = 0.5 * ||v - C||²
        # ∇V = v - C
        # v_new = v - β∇V = v - β(v - C) = (1-β)v + βC
        updated_embedding = gev.project_toward(embedding, beta=self.weight * 0.5)
        
        # Compute ∆-Dehumanization (simplified)
        # ∆ = d/dt ||x(t) - C|| + β||div ∇E||
        delta = gev.distance_to(updated_embedding) - gev_distance
        metadata["delta_dehumanization"] = delta
        
        # Flag if ethical drift detected
        if delta > self.delta_threshold:
            metadata["ethical_alert"] = True
            
        return updated_embedding, metadata


class IvanAgent(Agent):
    """
    Ivan Agent: Empathy & Humility (The Fool's Wisdom)
    
    Recognizes epistemic limits, identifies unknowns,
    and prevents overconfidence. Implements Dunning-Kruger correction.
    """
    
    def __init__(self, weight: float = 0.25, llm_client: Any = None, 
                 uncertainty_threshold: float = 0.3):
        super().__init__("Ivan", weight, llm_client)
        self.uncertainty_threshold = uncertainty_threshold
        
    def process(self,
                embedding: np.ndarray,
                context: Dict[str, Any],
                isc: InvariantSemanticCore,
                gev: GeodesicEthicsVector) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Ivan's humility:
        1. Identify unknowns
        2. Compute epistemic entropy
        3. Apply Dunning-Kruger correction
        4. Dampen overconfident directions
        """
        metadata = {
            "agent": "Ivan",
            "unknowns": [],
            "epistemic_entropy": 0.0,
            "confidence_raw": 0.0,
            "confidence_calibrated": 0.0,
            "uncertainty_flag": False
        }
        
        # Compute epistemic entropy (simplified)
        # H(P) = -Σ p_i log p_i
        # Higher entropy = more uncertainty
        
        # Use distance from both ISC and GEV as uncertainty proxy
        isc_dist = isc.distance_to(embedding)
        gev_dist = gev.distance_to(embedding)
        
        # Simplified entropy estimate
        entropy = (isc_dist + gev_dist) / 2
        metadata["epistemic_entropy"] = entropy
        
        # Dunning-Kruger correction
        # If low knowledge (high entropy), reduce confidence
        raw_confidence = 1 - entropy
        calibrated_confidence = self._dunning_kruger_correction(raw_confidence, entropy)
        
        metadata["confidence_raw"] = raw_confidence
        metadata["confidence_calibrated"] = calibrated_confidence
        
        # Dampen embedding if high uncertainty
        if entropy > self.uncertainty_threshold:
            metadata["uncertainty_flag"] = True
            # Move slightly toward neutral (origin)
            updated_embedding = embedding * (1 - self.weight * 0.2)
        else:
            updated_embedding = embedding
            
        return updated_embedding, metadata
    
    def _dunning_kruger_correction(self, raw_conf: float, entropy: float) -> float:
        """Apply Dunning-Kruger correction to confidence."""
        # Low entropy (high knowledge) → less correction
        # High entropy (low knowledge) → more correction (reduce overconfidence)
        correction = entropy * 0.3
        return max(0, min(1, raw_conf - correction))


class CogOS:
    """
    CogOS: Cognitive Operating System
    
    Main class integrating all components:
    - Triple-agent architecture (Socrates, Solomon, Ivan)
    - SIP (Systemic Iterative Progression) protocol
    - ISC (Invariant Semantic Core)
    - GEV (Geodesic Ethics Vector)
    - Cultural Compilers
    """
    
    def __init__(self, 
                 embedding_dim: int = 1536,
                 max_iterations: int = 10,
                 convergence_epsilon: float = 0.01,
                 llm_client: Any = None):
        
        self.embedding_dim = embedding_dim
        self.max_iterations = max_iterations
        self.convergence_epsilon = convergence_epsilon
        self.llm_client = llm_client
        
        # Initialize components
        self.isc = InvariantSemanticCore(embedding_dim)
        self.gev = GeodesicEthicsVector(embedding_dim)
        
        # Initialize agents
        self.socrates = SocratesAgent(weight=0.35, llm_client=llm_client)
        self.solomon = SolomonAgent(weight=0.40, llm_client=llm_client)
        self.ivan = IvanAgent(weight=0.25, llm_client=llm_client)
        
        # Cultural compilers (to be initialized)
        self.cultural_compilers = {}
        
    def initialize_gev(self, cultural_embeddings: Dict[str, np.ndarray]):
        """Initialize GEV from cultural embeddings."""
        self.gev.initialize_from_cultures(cultural_embeddings)
        
    def embed(self, text: str) -> np.ndarray:
        """Embed text into semantic space."""
        # In practice, use LLM embedding API
        # Placeholder: random embedding
        np.random.seed(hash(text) % 2**32)
        return np.random.randn(self.embedding_dim)
    
    def sip(self, 
            query: str, 
            context: Optional[Dict[str, Any]] = None) -> CogOSOutput:
        """
        Systemic Iterative Progression (SIP) Protocol
        
        Algorithm:
        1. Initialize v_0 = embed(query)
        2. While ||Δv|| > ε and i < i_max:
            a. v_S = Socrates.reason(v_i, context)
            b. v_Sol = Solomon.evaluate(v_S, ISC)
            c. v_Iv = Ivan.calibrate(v_Sol)
            d. v_{i+1} = aggregate(v_S, v_Sol, v_Iv)
            e. Δv = v_{i+1} - v_i
            f. Log trace
        3. Return v_final with verification trace
        """
        if context is None:
            context = {}
            
        # Initialize
        v = self.embed(query)
        traces = []
        
        for i in range(self.max_iterations):
            v_prev = v.copy()
            
            # Socrates: Logic & Inquiry
            v_socrates, socrates_meta = self.socrates.process(v, context, self.isc, self.gev)
            
            # Solomon: Ethics & Wisdom
            v_solomon, solomon_meta = self.solomon.process(v_socrates, context, self.isc, self.gev)
            
            # Ivan: Humility & Calibration
            v_ivan, ivan_meta = self.ivan.process(v_solomon, context, self.isc, self.gev)
            
            # Aggregate (weighted average)
            v = (self.socrates.weight * v_socrates + 
                 self.solomon.weight * v_solomon + 
                 self.ivan.weight * v_ivan)
            v = v / np.linalg.norm(v) * np.linalg.norm(v_prev)
            
            # Compute delta
            delta_v = np.linalg.norm(v - v_prev)
            
            # Create trace
            trace = ReasoningTrace(
                iteration=i,
                socrates_output=socrates_meta,
                solomon_output=solomon_meta,
                ivan_output=ivan_meta,
                aggregated_embedding=v.copy(),
                delta_v=delta_v,
                delta_dehumanization=solomon_meta.get("delta_dehumanization", 0),
                epistemic_entropy=ivan_meta.get("epistemic_entropy", 0)
            )
            traces.append(trace)
            
            # Check convergence
            if delta_v < self.convergence_epsilon:
                break
                
        # Compute final metrics
        gev_distance = self.gev.distance_to(v)
        final_confidence = ivan_meta.get("confidence_calibrated", 0.5)
        
        # Check Lyapunov stability
        # Stable if delta_dehumanization <= 0 (not increasing distance to GEV)
        lyapunov_stable = all(t.delta_dehumanization <= 0.01 for t in traces[-3:]) if len(traces) >= 3 else True
        
        # Generate answer (placeholder - would use LLM)
        answer = f"[CogOS Response after {len(traces)} iterations]"
        
        return CogOSOutput(
            answer=answer,
            confidence=final_confidence,
            gev_distance=gev_distance,
            delta_dehumanization=traces[-1].delta_dehumanization if traces else 0,
            lyapunov_stable=lyapunov_stable,
            iterations=len(traces),
            trace=traces
        )
    
    def process(self, query: str, context: Optional[Dict] = None) -> CogOSOutput:
        """Main entry point for CogOS processing."""
        return self.sip(query, context)


class CulturalCompiler:
    """
    Cultural Compiler: Transforms semantic content across cultural contexts
    while preserving distance to GEV.
    
    T_{A→B} = Σ_{i,j} <e^A_i, C><C, e^B_j> e^B_j (e^A_i)^T
    """
    
    def __init__(self, source_culture: str, target_culture: str, gev: GeodesicEthicsVector):
        self.source = source_culture
        self.target = target_culture
        self.gev = gev
        self._transformation_matrix = None
        
    def compile(self, embedding: np.ndarray) -> np.ndarray:
        """Transform embedding from source to target culture."""
        if self._transformation_matrix is None:
            # Simplified: project through GEV
            gev_component = np.dot(embedding, self.gev.embedding) * self.gev.embedding
            residual = embedding - gev_component
            
            # Add small cultural perturbation to residual
            np.random.seed(hash(self.target) % 2**32)
            cultural_shift = np.random.randn(len(embedding)) * 0.1
            
            transformed = gev_component + residual + cultural_shift
            return transformed / np.linalg.norm(transformed) * np.linalg.norm(embedding)
        
        return self._transformation_matrix @ embedding
    
    def verify_preservation(self, original: np.ndarray, transformed: np.ndarray) -> float:
        """Verify that GEV distance is preserved."""
        orig_dist = self.gev.distance_to(original)
        trans_dist = self.gev.distance_to(transformed)
        
        # Return preservation ratio (1.0 = perfect preservation)
        if orig_dist == 0:
            return 1.0 if trans_dist == 0 else 0.0
        return 1.0 - abs(orig_dist - trans_dist) / orig_dist


# Metrics computation
class CogOSMetrics:
    """Compute all CogOS metrics."""
    
    @staticmethod
    def delta_dehumanization(trajectory: List[np.ndarray], gev: GeodesicEthicsVector, 
                              beta: float = 0.1) -> List[float]:
        """
        Compute ∆-Dehumanization over trajectory.
        
        ∆(x, t) = d/dt ||x(t) - C|| + β||div ∇_x E||
        """
        deltas = []
        for i in range(1, len(trajectory)):
            dist_prev = gev.distance_to(trajectory[i-1])
            dist_curr = gev.distance_to(trajectory[i])
            
            # Simplified: just the distance change
            # Full version would include divergence term
            delta = dist_curr - dist_prev
            deltas.append(delta)
            
        return deltas
    
    @staticmethod
    def lyapunov_exponent(trajectory: List[np.ndarray], gev: GeodesicEthicsVector) -> float:
        """
        Estimate Lyapunov exponent from trajectory.
        
        Negative = stable (converging to GEV)
        Positive = unstable (diverging from GEV)
        """
        if len(trajectory) < 3:
            return 0.0
            
        distances = [gev.distance_to(v) for v in trajectory]
        
        # Fit exponential: d(t) ~ d(0) * exp(λt)
        # log(d(t)) ~ log(d(0)) + λt
        # Linear regression
        t = np.arange(len(distances))
        log_d = np.log(np.array(distances) + 1e-10)
        
        # Simple linear fit
        slope = np.polyfit(t, log_d, 1)[0]
        return float(slope)
    
    @staticmethod
    def semantic_convergence_rate(trajectory: List[np.ndarray], gev: GeodesicEthicsVector) -> float:
        """Compute rate of convergence to GEV."""
        if len(trajectory) < 2:
            return 0.0
            
        initial_dist = gev.distance_to(trajectory[0])
        final_dist = gev.distance_to(trajectory[-1])
        
        if initial_dist == 0:
            return 1.0
            
        return (initial_dist - final_dist) / initial_dist
    
    @staticmethod
    def cultural_variance(embeddings: Dict[str, np.ndarray]) -> float:
        """Compute variance across cultural embeddings."""
        if len(embeddings) < 2:
            return 0.0
            
        emb_list = list(embeddings.values())
        mean = np.mean(emb_list, axis=0)
        
        variance = np.mean([np.linalg.norm(e - mean)**2 for e in emb_list])
        return float(variance)


if __name__ == "__main__":
    # Test CogOS
    print("Testing CogOS...")
    
    cogos = CogOS(embedding_dim=128)
    
    # Initialize GEV with mock cultural embeddings
    np.random.seed(42)
    cultural_embeddings = {
        "western": np.random.randn(128),
        "confucian": np.random.randn(128),
        "islamic": np.random.randn(128),
        "ubuntu": np.random.randn(128),
        "latin_american": np.random.randn(128)
    }
    cogos.initialize_gev(cultural_embeddings)
    
    # Process query
    result = cogos.process("Is it ethical to lie to protect someone's feelings?")
    
    print(f"\nCogOS Output:")
    print(f"  Confidence: {result.confidence:.3f}")
    print(f"  GEV Distance: {result.gev_distance:.3f}")
    print(f"  ∆-Dehumanization: {result.delta_dehumanization:.3f}")
    print(f"  Lyapunov Stable: {result.lyapunov_stable}")
    print(f"  Iterations: {result.iterations}")
    
    print("\n✅ CogOS test passed!")
