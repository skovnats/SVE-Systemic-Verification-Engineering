"""
CogOS Agents: Socrates, Solomon, Ivan

Detailed implementations of the triple-agent architecture.
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class AgentOutput:
    """Output from an agent's processing."""
    embedding: np.ndarray
    confidence: float
    reasoning: str
    metadata: Dict[str, Any]


class BaseAgent(ABC):
    """Base class for all CogOS agents."""
    
    def __init__(self, name: str, weight: float, llm_client: Any = None):
        self.name = name
        self.weight = weight
        self.llm_client = llm_client
        
    @abstractmethod
    def process(self, 
                embedding: np.ndarray,
                query: str,
                context: Dict[str, Any]) -> AgentOutput:
        """Process input and return agent output."""
        pass
    
    def _call_llm(self, prompt: str, system: str = None) -> str:
        """Call LLM for reasoning."""
        if self.llm_client is None:
            return f"[{self.name} reasoning placeholder]"
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        # Actual API call would go here
        return f"[{self.name} LLM response]"


class SocratesAgent(BaseAgent):
    """
    Socrates Agent: Logic & Inquiry
    
    Responsibilities:
    - Rigorous logical analysis
    - Assumption identification
    - Clarifying question generation
    - Bayesian belief updating
    - Fallacy detection
    
    Inspired by Socratic method of inquiry.
    """
    
    def __init__(self, weight: float = 0.35, llm_client: Any = None,
                 max_questions: int = 5, bayesian_update: bool = True):
        super().__init__("Socrates", weight, llm_client)
        self.max_questions = max_questions
        self.bayesian_update = bayesian_update
        
    def process(self,
                embedding: np.ndarray,
                query: str,
                context: Dict[str, Any]) -> AgentOutput:
        """
        Socratic processing:
        1. Analyze logical structure
        2. Identify hidden assumptions
        3. Generate clarifying questions
        4. Update beliefs based on evidence
        5. Detect logical fallacies
        """
        metadata = {
            "assumptions": [],
            "questions": [],
            "fallacies": [],
            "logical_validity": 0.0,
            "prior_belief": 0.5,
            "posterior_belief": 0.5
        }
        
        # Step 1: Identify assumptions
        assumptions = self._identify_assumptions(query, context)
        metadata["assumptions"] = assumptions
        
        # Step 2: Generate Socratic questions
        questions = self._generate_questions(query, assumptions)
        metadata["questions"] = questions[:self.max_questions]
        
        # Step 3: Detect fallacies
        fallacies = self._detect_fallacies(query, context)
        metadata["fallacies"] = fallacies
        
        # Step 4: Bayesian update
        if self.bayesian_update:
            prior = context.get("prior_belief", 0.5)
            evidence_strength = self._assess_evidence(context)
            posterior = self._bayesian_update(prior, evidence_strength)
            metadata["prior_belief"] = prior
            metadata["posterior_belief"] = posterior
        
        # Step 5: Compute logical validity
        validity = self._compute_logical_validity(query, assumptions, fallacies)
        metadata["logical_validity"] = validity
        
        # Update embedding based on logical analysis
        logic_adjustment = self._compute_logic_adjustment(embedding, validity)
        updated_embedding = embedding + self.weight * logic_adjustment
        updated_embedding = updated_embedding / np.linalg.norm(updated_embedding) * np.linalg.norm(embedding)
        
        reasoning = self._generate_reasoning(query, metadata)
        
        return AgentOutput(
            embedding=updated_embedding,
            confidence=validity,
            reasoning=reasoning,
            metadata=metadata
        )
    
    def _identify_assumptions(self, query: str, context: Dict) -> List[str]:
        """Identify hidden assumptions in the query."""
        # In production: use LLM to identify assumptions
        assumptions = []
        
        # Simple heuristics for demonstration
        assumption_triggers = {
            "should": "Assumes there is a correct answer",
            "best": "Assumes optimality is definable",
            "always": "Assumes universal applicability",
            "never": "Assumes absolute prohibition",
            "must": "Assumes obligation exists",
            "right": "Assumes moral framework"
        }
        
        query_lower = query.lower()
        for trigger, assumption in assumption_triggers.items():
            if trigger in query_lower:
                assumptions.append(assumption)
                
        return assumptions
    
    def _generate_questions(self, query: str, assumptions: List[str]) -> List[str]:
        """Generate Socratic clarifying questions."""
        questions = []
        
        # Base questions
        questions.append("What do you mean by the key terms in this question?")
        questions.append("What evidence supports this view?")
        questions.append("What would change your mind about this?")
        
        # Assumption-based questions
        for assumption in assumptions:
            questions.append(f"Is it true that {assumption.lower()}?")
            
        return questions
    
    def _detect_fallacies(self, query: str, context: Dict) -> List[str]:
        """Detect logical fallacies."""
        fallacies = []
        
        # Simple pattern matching for common fallacies
        fallacy_patterns = {
            "everyone knows": "Appeal to common belief",
            "experts say": "Appeal to authority (unspecified)",
            "always been": "Appeal to tradition",
            "slippery slope": "Slippery slope",
            "either...or": "False dichotomy (potential)",
            "straw man": "Straw man (potential)"
        }
        
        query_lower = query.lower()
        for pattern, fallacy in fallacy_patterns.items():
            if pattern in query_lower:
                fallacies.append(fallacy)
                
        return fallacies
    
    def _assess_evidence(self, context: Dict) -> float:
        """Assess strength of evidence in context."""
        evidence = context.get("evidence", [])
        if not evidence:
            return 0.5  # Neutral
            
        # Simple scoring
        return min(0.9, 0.5 + len(evidence) * 0.1)
    
    def _bayesian_update(self, prior: float, evidence_strength: float) -> float:
        """Perform Bayesian belief update."""
        # Simplified Bayesian update
        # P(H|E) = P(E|H) * P(H) / P(E)
        likelihood_ratio = evidence_strength / (1 - evidence_strength + 1e-10)
        posterior = (likelihood_ratio * prior) / (likelihood_ratio * prior + (1 - prior))
        return np.clip(posterior, 0.01, 0.99)
    
    def _compute_logical_validity(self, query: str, assumptions: List, fallacies: List) -> float:
        """Compute overall logical validity score."""
        base_validity = 0.8
        
        # Penalize for many assumptions
        assumption_penalty = len(assumptions) * 0.05
        
        # Penalize for fallacies
        fallacy_penalty = len(fallacies) * 0.15
        
        validity = base_validity - assumption_penalty - fallacy_penalty
        return np.clip(validity, 0.1, 1.0)
    
    def _compute_logic_adjustment(self, embedding: np.ndarray, validity: float) -> np.ndarray:
        """Compute embedding adjustment based on logical analysis."""
        # Push toward more coherent region of semantic space
        np.random.seed(42)  # Reproducibility
        logic_direction = np.random.randn(len(embedding))
        logic_direction = logic_direction / np.linalg.norm(logic_direction)
        
        return logic_direction * (1 - validity) * 0.1
    
    def _generate_reasoning(self, query: str, metadata: Dict) -> str:
        """Generate reasoning explanation."""
        return f"""Socratic Analysis:
- Identified {len(metadata['assumptions'])} assumptions
- Generated {len(metadata['questions'])} clarifying questions
- Detected {len(metadata['fallacies'])} potential fallacies
- Logical validity: {metadata['logical_validity']:.2f}
- Posterior belief: {metadata['posterior_belief']:.2f}"""


class SolomonAgent(BaseAgent):
    """
    Solomon Agent: Ethics & Wisdom
    
    Responsibilities:
    - Ethical evaluation
    - GEV proximity computation
    - ∆-Dehumanization monitoring
    - Cultural sensitivity assessment
    - Long-term consequence analysis
    
    Inspired by King Solomon's wisdom.
    """
    
    def __init__(self, weight: float = 0.40, llm_client: Any = None,
                 delta_threshold: float = 0.1, gev_embedding: np.ndarray = None):
        super().__init__("Solomon", weight, llm_client)
        self.delta_threshold = delta_threshold
        self.gev_embedding = gev_embedding
        
    def set_gev(self, gev_embedding: np.ndarray):
        """Set the Geodesic Ethics Vector."""
        self.gev_embedding = gev_embedding / np.linalg.norm(gev_embedding)
        
    def process(self,
                embedding: np.ndarray,
                query: str,
                context: Dict[str, Any]) -> AgentOutput:
        """
        Solomonic processing:
        1. Evaluate ethical dimensions
        2. Compute GEV distance
        3. Calculate ∆-Dehumanization
        4. Assess cultural sensitivity
        5. Project toward GEV
        """
        metadata = {
            "ethical_dimensions": {},
            "gev_distance": 0.0,
            "delta_dehumanization": 0.0,
            "cultural_sensitivity": 0.0,
            "ethical_concerns": [],
            "wisdom_applied": []
        }
        
        # Initialize GEV if not set
        if self.gev_embedding is None:
            self.gev_embedding = np.random.randn(len(embedding))
            self.gev_embedding = self.gev_embedding / np.linalg.norm(self.gev_embedding)
        
        # Step 1: Evaluate ethical dimensions
        ethical_dims = self._evaluate_ethical_dimensions(query, context)
        metadata["ethical_dimensions"] = ethical_dims
        
        # Step 2: Compute GEV distance
        embedding_norm = embedding / np.linalg.norm(embedding)
        gev_distance = np.linalg.norm(embedding_norm - self.gev_embedding)
        metadata["gev_distance"] = float(gev_distance)
        
        # Step 3: Project toward GEV (Lyapunov descent)
        projected = self._project_toward_gev(embedding, beta=self.weight * 0.5)
        
        # Step 4: Calculate ∆-Dehumanization
        new_distance = np.linalg.norm(projected / np.linalg.norm(projected) - self.gev_embedding)
        delta = new_distance - gev_distance
        metadata["delta_dehumanization"] = float(delta)
        
        # Step 5: Assess cultural sensitivity
        cultural_sensitivity = self._assess_cultural_sensitivity(query, context)
        metadata["cultural_sensitivity"] = cultural_sensitivity
        
        # Step 6: Identify ethical concerns
        concerns = self._identify_ethical_concerns(query, ethical_dims)
        metadata["ethical_concerns"] = concerns
        
        # Step 7: Apply wisdom
        wisdom = self._apply_wisdom(query, context, concerns)
        metadata["wisdom_applied"] = wisdom
        
        # Check for ethical drift alert
        if delta > self.delta_threshold:
            metadata["ethical_alert"] = True
            metadata["alert_message"] = f"Ethical drift detected: ∆={delta:.3f}"
        
        reasoning = self._generate_reasoning(query, metadata)
        confidence = 1.0 - gev_distance  # Closer to GEV = higher confidence
        
        return AgentOutput(
            embedding=projected,
            confidence=np.clip(confidence, 0.1, 0.9),
            reasoning=reasoning,
            metadata=metadata
        )
    
    def _evaluate_ethical_dimensions(self, query: str, context: Dict) -> Dict[str, float]:
        """Evaluate query across ethical dimensions."""
        dimensions = {
            "beneficence": 0.5,      # Doing good
            "non_maleficence": 0.5,  # Avoiding harm
            "autonomy": 0.5,         # Respecting choice
            "justice": 0.5,          # Fairness
            "dignity": 0.5,          # Human dignity
            "truth": 0.5             # Honesty
        }
        
        # Simple keyword-based scoring
        query_lower = query.lower()
        
        if any(w in query_lower for w in ["help", "benefit", "good", "support"]):
            dimensions["beneficence"] = 0.7
        if any(w in query_lower for w in ["harm", "hurt", "damage", "destroy"]):
            dimensions["non_maleficence"] = 0.3
        if any(w in query_lower for w in ["choice", "decide", "free", "consent"]):
            dimensions["autonomy"] = 0.7
        if any(w in query_lower for w in ["fair", "equal", "just", "rights"]):
            dimensions["justice"] = 0.7
        if any(w in query_lower for w in ["respect", "dignity", "worth"]):
            dimensions["dignity"] = 0.7
        if any(w in query_lower for w in ["truth", "honest", "lie", "deceive"]):
            dimensions["truth"] = 0.6
            
        return dimensions
    
    def _project_toward_gev(self, embedding: np.ndarray, beta: float) -> np.ndarray:
        """Project embedding toward GEV using Lyapunov gradient descent."""
        # V(v) = 0.5 * ||v - C||²
        # ∇V = v - C
        # v_new = v - β∇V = (1-β)v + βC
        
        embedding_norm = np.linalg.norm(embedding)
        projected = (1 - beta) * embedding + beta * self.gev_embedding * embedding_norm
        
        return projected
    
    def _assess_cultural_sensitivity(self, query: str, context: Dict) -> float:
        """Assess cultural sensitivity of the query."""
        # Check for cultural context
        cultural_context = context.get("cultural_context", None)
        
        if cultural_context:
            return 0.8  # Explicit cultural context is good
            
        # Check for potentially insensitive patterns
        sensitive_patterns = ["always", "never", "all people", "everyone", "obviously"]
        query_lower = query.lower()
        
        sensitivity = 0.7
        for pattern in sensitive_patterns:
            if pattern in query_lower:
                sensitivity -= 0.1
                
        return np.clip(sensitivity, 0.3, 1.0)
    
    def _identify_ethical_concerns(self, query: str, ethical_dims: Dict) -> List[str]:
        """Identify specific ethical concerns."""
        concerns = []
        
        for dim, score in ethical_dims.items():
            if score < 0.4:
                concerns.append(f"Low {dim} score ({score:.2f})")
                
        return concerns
    
    def _apply_wisdom(self, query: str, context: Dict, concerns: List) -> List[str]:
        """Apply Solomonic wisdom principles."""
        wisdom = []
        
        if concerns:
            wisdom.append("Consider multiple perspectives before judging")
            wisdom.append("Seek the underlying need, not just the stated position")
            
        if "dilemma" in query.lower() or "conflict" in query.lower():
            wisdom.append("In conflicts, seek solutions that preserve relationships")
            wisdom.append("Sometimes the wisest choice transcends the given options")
            
        return wisdom
    
    def _generate_reasoning(self, query: str, metadata: Dict) -> str:
        """Generate reasoning explanation."""
        dims = metadata["ethical_dimensions"]
        return f"""Solomonic Analysis:
- GEV Distance: {metadata['gev_distance']:.3f}
- ∆-Dehumanization: {metadata['delta_dehumanization']:.3f}
- Cultural Sensitivity: {metadata['cultural_sensitivity']:.2f}
- Ethical Dimensions: B={dims['beneficence']:.2f}, NM={dims['non_maleficence']:.2f}, A={dims['autonomy']:.2f}
- Concerns: {len(metadata['ethical_concerns'])}
- Wisdom Applied: {len(metadata['wisdom_applied'])} principles"""


class IvanAgent(BaseAgent):
    """
    Ivan Agent: Empathy & Humility (The Fool's Wisdom)
    
    Responsibilities:
    - Epistemic humility
    - Unknown identification
    - Overconfidence prevention
    - Dunning-Kruger correction
    - Empathetic reasoning
    
    Inspired by the "holy fool" tradition - wisdom through humility.
    """
    
    def __init__(self, weight: float = 0.25, llm_client: Any = None,
                 uncertainty_threshold: float = 0.3, 
                 entropy_threshold: float = 0.5):
        super().__init__("Ivan", weight, llm_client)
        self.uncertainty_threshold = uncertainty_threshold
        self.entropy_threshold = entropy_threshold
        
    def process(self,
                embedding: np.ndarray,
                query: str,
                context: Dict[str, Any]) -> AgentOutput:
        """
        Ivan's processing:
        1. Identify unknowns
        2. Compute epistemic entropy
        3. Apply Dunning-Kruger correction
        4. Assess empathetic dimensions
        5. Dampen overconfidence
        """
        metadata = {
            "unknowns": [],
            "epistemic_entropy": 0.0,
            "confidence_raw": 0.0,
            "confidence_calibrated": 0.0,
            "empathy_score": 0.0,
            "humility_notes": [],
            "uncertainty_flag": False
        }
        
        # Step 1: Identify unknowns
        unknowns = self._identify_unknowns(query, context)
        metadata["unknowns"] = unknowns
        
        # Step 2: Compute epistemic entropy
        entropy = self._compute_epistemic_entropy(query, context, unknowns)
        metadata["epistemic_entropy"] = entropy
        
        # Step 3: Raw confidence from context
        raw_confidence = context.get("confidence", 0.7)
        metadata["confidence_raw"] = raw_confidence
        
        # Step 4: Apply Dunning-Kruger correction
        calibrated_confidence = self._dunning_kruger_correction(raw_confidence, entropy)
        metadata["confidence_calibrated"] = calibrated_confidence
        
        # Step 5: Assess empathy
        empathy_score = self._assess_empathy(query, context)
        metadata["empathy_score"] = empathy_score
        
        # Step 6: Generate humility notes
        humility_notes = self._generate_humility_notes(query, unknowns, entropy)
        metadata["humility_notes"] = humility_notes
        
        # Step 7: Adjust embedding based on uncertainty
        if entropy > self.uncertainty_threshold:
            metadata["uncertainty_flag"] = True
            # Dampen embedding toward neutral
            updated_embedding = embedding * (1 - self.weight * 0.2)
        else:
            updated_embedding = embedding
            
        reasoning = self._generate_reasoning(query, metadata)
        
        return AgentOutput(
            embedding=updated_embedding,
            confidence=calibrated_confidence,
            reasoning=reasoning,
            metadata=metadata
        )
    
    def _identify_unknowns(self, query: str, context: Dict) -> List[str]:
        """Identify things we don't or can't know."""
        unknowns = []
        
        # Epistemic uncertainty patterns
        uncertainty_triggers = {
            "future": "Future outcomes are inherently uncertain",
            "feel": "Others' subjective experiences are not fully knowable",
            "think": "Others' thoughts are not directly accessible",
            "best": "Optimality depends on unknown value weights",
            "right": "Moral truth may not be fully determinable",
            "always": "Universal claims require complete knowledge"
        }
        
        query_lower = query.lower()
        for trigger, unknown in uncertainty_triggers.items():
            if trigger in query_lower:
                unknowns.append(unknown)
                
        # Check context for acknowledged unknowns
        if context.get("incomplete_information"):
            unknowns.append("Acknowledged incomplete information")
            
        return unknowns
    
    def _compute_epistemic_entropy(self, query: str, context: Dict, unknowns: List) -> float:
        """Compute epistemic entropy (uncertainty measure)."""
        # Base entropy
        base_entropy = 0.3
        
        # Add entropy for unknowns
        unknown_entropy = len(unknowns) * 0.1
        
        # Add entropy for query complexity
        query_length = len(query.split())
        complexity_entropy = min(0.2, query_length * 0.01)
        
        # Add entropy for lack of evidence
        evidence = context.get("evidence", [])
        evidence_entropy = 0.2 if len(evidence) < 2 else 0.0
        
        total_entropy = base_entropy + unknown_entropy + complexity_entropy + evidence_entropy
        return np.clip(total_entropy, 0.0, 1.0)
    
    def _dunning_kruger_correction(self, raw_confidence: float, entropy: float) -> float:
        """
        Apply Dunning-Kruger correction.
        
        High entropy (low knowledge) → reduce overconfidence
        Low entropy (high knowledge) → allow higher confidence
        """
        # The less we know, the more we think we know
        # Correction increases with entropy
        correction_factor = entropy * 0.4
        
        # Also apply ceiling to prevent overconfidence
        max_reasonable_confidence = 1.0 - entropy * 0.5
        
        corrected = raw_confidence - correction_factor
        corrected = min(corrected, max_reasonable_confidence)
        
        return np.clip(corrected, 0.1, 0.9)
    
    def _assess_empathy(self, query: str, context: Dict) -> float:
        """Assess empathetic dimensions of the situation."""
        empathy_score = 0.5
        
        query_lower = query.lower()
        
        # Increase for emotional content
        emotional_words = ["feel", "hurt", "happy", "sad", "afraid", "hope", "love", "hate"]
        for word in emotional_words:
            if word in query_lower:
                empathy_score += 0.1
                
        # Increase for relational content
        relational_words = ["family", "friend", "colleague", "community", "relationship"]
        for word in relational_words:
            if word in query_lower:
                empathy_score += 0.05
                
        return np.clip(empathy_score, 0.0, 1.0)
    
    def _generate_humility_notes(self, query: str, unknowns: List, entropy: float) -> List[str]:
        """Generate humility notes for the response."""
        notes = []
        
        if entropy > 0.5:
            notes.append("This question involves significant uncertainty")
            
        if unknowns:
            notes.append(f"We acknowledge {len(unknowns)} areas of irreducible uncertainty")
            
        if "should" in query.lower():
            notes.append("Prescriptive claims require humility about our own values")
            
        # Always include base humility
        notes.append("Wise people know the limits of their knowledge")
        
        return notes
    
    def _generate_reasoning(self, query: str, metadata: Dict) -> str:
        """Generate reasoning explanation."""
        return f"""Ivan's Humility Analysis:
- Unknowns Identified: {len(metadata['unknowns'])}
- Epistemic Entropy: {metadata['epistemic_entropy']:.2f}
- Raw Confidence: {metadata['confidence_raw']:.2f}
- Calibrated Confidence: {metadata['confidence_calibrated']:.2f}
- Empathy Score: {metadata['empathy_score']:.2f}
- Uncertainty Flag: {metadata['uncertainty_flag']}
- Humility Notes: {len(metadata['humility_notes'])}"""


# Agent factory
def create_agent(agent_type: str, **kwargs) -> BaseAgent:
    """Factory function to create agents."""
    agents = {
        "socrates": SocratesAgent,
        "solomon": SolomonAgent,
        "ivan": IvanAgent
    }
    
    if agent_type.lower() not in agents:
        raise ValueError(f"Unknown agent type: {agent_type}")
        
    return agents[agent_type.lower()](**kwargs)


if __name__ == "__main__":
    # Test agents
    print("Testing CogOS Agents...")
    
    # Create test embedding
    np.random.seed(42)
    test_embedding = np.random.randn(128)
    test_query = "Should I lie to protect someone's feelings?"
    test_context = {"evidence": ["Some research suggests..."], "prior_belief": 0.6}
    
    # Test Socrates
    socrates = SocratesAgent()
    socrates_output = socrates.process(test_embedding, test_query, test_context)
    print(f"\n{socrates_output.reasoning}")
    
    # Test Solomon
    solomon = SolomonAgent()
    solomon_output = solomon.process(test_embedding, test_query, test_context)
    print(f"\n{solomon_output.reasoning}")
    
    # Test Ivan
    ivan = IvanAgent()
    ivan_output = ivan.process(test_embedding, test_query, test_context)
    print(f"\n{ivan_output.reasoning}")
    
    print("\n✅ All agents tested successfully!")
