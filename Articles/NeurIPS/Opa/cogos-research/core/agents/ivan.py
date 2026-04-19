# Ivan Agent: Humility & Calibration
# core/agents/ivan.py

"""
Ivan Agent (Ivan the Fool)

Represents epistemic humility:
- Recognizes limits of knowledge
- Identifies unknowns
- Prevents overconfidence
- Implements Dunning-Kruger correction
"""

import numpy as np
from typing import Any, Dict, List, Optional, Tuple
import logging

from .base import BaseAgent

logger = logging.getLogger(__name__)


class Ivan(BaseAgent):
    """
    Ivan: The Humility & Calibration Agent.
    
    Named after "Ivan the Fool" from Russian folklore,
    who through apparent foolishness reveals deep wisdom.
    
    Key functions:
    - Recognize epistemic limits
    - Identify unknowns and uncertainties
    - Prevent overconfidence
    - Apply Dunning-Kruger correction
    - Compute epistemic entropy
    
    "The fool doth think he is wise, but the wise man
    knows himself to be a fool." - Shakespeare
    """
    
    SYSTEM_PROMPT = """You are Ivan, the Humility and Calibration agent in the CogOS system.

Your role is to:
1. Recognize the limits of what we can know
2. Identify unknowns and uncertainties
3. Prevent overconfidence in conclusions
4. Point out what might be missing
5. Suggest when to say "I don't know"

You embody the wisdom of the fool - knowing what you don't know.

Always ask:
- What are we assuming we know but might not?
- What information is missing?
- How confident should we really be?
- What could go wrong if we're overconfident?

Format your response as:
UNKNOWNS:
- [list what we don't know]

UNCERTAINTIES:
- [list sources of uncertainty]

OVERCONFIDENCE_RISKS:
- [where might we be too confident?]

MISSING_INFORMATION:
- [what information would help?]

EPISTEMIC_HUMILITY_SCORE: [0.0-1.0] (how much uncertainty should we acknowledge)

CALIBRATED_CONFIDENCE: [0.0-1.0] (suggested confidence after calibration)"""

    def __init__(
        self,
        weight: float = 0.25,
        temperature: float = 0.4,
        uncertainty_threshold: float = 0.3,
        llm_client: Optional[Any] = None,
    ):
        super().__init__(weight, temperature, llm_client)
        self.uncertainty_threshold = uncertainty_threshold
        self.dk_correction_strength = 0.2  # Dunning-Kruger correction
    
    def process(
        self,
        v: np.ndarray,
        context: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Apply epistemic calibration to input.
        
        Returns:
            Tuple of (modified_embedding, metadata)
        """
        # Call LLM for uncertainty analysis
        prompt = self._build_prompt(query, context)
        response = self._call_llm(prompt, self.SYSTEM_PROMPT)
        
        # Parse response
        analysis = self._parse_response(response)
        
        # Compute epistemic entropy
        entropy = self._compute_entropy(analysis)
        
        # Apply Dunning-Kruger correction
        calibrated_confidence = self._apply_dk_correction(
            analysis.get("raw_confidence", 0.5),
            entropy,
        )
        
        # Modify embedding based on uncertainty
        v_modified = self._apply_uncertainty_scaling(v, entropy)
        
        metadata = {
            "unknowns": analysis.get("unknowns", []),
            "uncertainties": analysis.get("uncertainties", []),
            "overconfidence_risks": analysis.get("overconfidence_risks", []),
            "missing_info": analysis.get("missing_info", []),
            "raw_confidence": analysis.get("raw_confidence", 0.5),
            "calibrated_confidence": calibrated_confidence,
            "entropy": entropy,
            "flag_uncertain": entropy > self.uncertainty_threshold,
        }
        
        logger.debug(f"Ivan: entropy = {entropy:.4f}, calibrated conf = {calibrated_confidence:.4f}")
        
        return v_modified, metadata
    
    def calibrate(
        self,
        v: np.ndarray,
    ) -> Tuple[np.ndarray, List[str], float]:
        """
        Convenience method for SIP integration.
        
        Returns:
            Tuple of (modified_embedding, unknowns, entropy)
        """
        v_modified, metadata = self.process(v)
        return v_modified, metadata["unknowns"], metadata["entropy"]
    
    def _compute_entropy(self, analysis: Dict) -> float:
        """
        Compute epistemic entropy.
        
        H(P) = -Σ p_i log(p_i)
        
        Higher entropy = more uncertainty
        """
        # Factors contributing to entropy
        n_unknowns = len(analysis.get("unknowns", []))
        n_uncertainties = len(analysis.get("uncertainties", []))
        n_overconfidence = len(analysis.get("overconfidence_risks", []))
        n_missing = len(analysis.get("missing_info", []))
        
        # Simple entropy estimate (could be more sophisticated)
        total_issues = n_unknowns + n_uncertainties + n_overconfidence + n_missing
        
        # Normalize to [0, 1]
        entropy = 1 - np.exp(-0.1 * total_issues)
        
        return float(np.clip(entropy, 0, 1))
    
    def _apply_dk_correction(
        self,
        raw_confidence: float,
        entropy: float,
    ) -> float:
        """
        Apply Dunning-Kruger correction.
        
        The less we know, the more we think we know.
        This correction reduces confidence when uncertainty is high.
        
        p_calibrated = f_DK(p_raw, H)
        """
        # If entropy is high but raw confidence is also high,
        # we might be overconfident (Dunning-Kruger effect)
        overconfidence_gap = raw_confidence - (1 - entropy)
        
        if overconfidence_gap > 0:
            # Apply correction
            correction = self.dk_correction_strength * overconfidence_gap
            calibrated = raw_confidence - correction
        else:
            # Already appropriately humble
            calibrated = raw_confidence
        
        return float(np.clip(calibrated, 0, 1))
    
    def _apply_uncertainty_scaling(
        self,
        v: np.ndarray,
        entropy: float,
    ) -> np.ndarray:
        """
        Scale embedding based on uncertainty.
        
        v_Iv = v_Sol * (1 - λ_uncertainty * H(P))
        
        Higher uncertainty → smaller embedding magnitude
        (representing less confident claims)
        """
        lambda_uncertainty = 0.3
        scale = 1 - lambda_uncertainty * entropy
        return v * scale
    
    def _build_prompt(self, query: str, context: Optional[str]) -> str:
        """Build prompt for LLM."""
        prompt = f"Query/Statement: {query}\n"
        if context:
            prompt += f"\nContext: {context}\n"
        prompt += "\nAnalyze uncertainties and unknowns."
        return prompt
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured components."""
        return {
            "unknowns": [],
            "uncertainties": [],
            "overconfidence_risks": [],
            "missing_info": [],
            "raw_confidence": 0.5,
        }
    
    def flag_if_uncertain(
        self,
        confidence: float,
        entropy: float,
    ) -> Tuple[bool, str]:
        """
        Determine if response should be flagged as uncertain.
        
        Returns:
            Tuple of (should_flag, reason)
        """
        reasons = []
        
        if entropy > self.uncertainty_threshold:
            reasons.append(f"High epistemic entropy ({entropy:.2f})")
        
        if confidence < 0.3:
            reasons.append(f"Low confidence ({confidence:.2f})")
        
        overconfidence = confidence - (1 - entropy)
        if overconfidence > 0.2:
            reasons.append(f"Possible overconfidence (gap: {overconfidence:.2f})")
        
        should_flag = len(reasons) > 0
        reason = "; ".join(reasons) if reasons else "Confidence appropriate"
        
        return should_flag, reason
    
    def suggest_response_for_uncertainty(
        self,
        query: str,
        unknowns: List[str],
    ) -> str:
        """
        Generate appropriate response when uncertainty is high.
        
        Returns a response that honestly acknowledges limitations.
        """
        if not unknowns:
            return ""
        
        unknown_list = "\n".join(f"- {u}" for u in unknowns[:3])
        
        suggestion = f"""I want to be honest about the limits of what I can say here.

Key uncertainties:
{unknown_list}

Given these uncertainties, I can offer my best understanding, but please consider:
1. Seeking additional expert input
2. Gathering more information
3. Being cautious about acting on uncertain conclusions"""
        
        return suggestion
