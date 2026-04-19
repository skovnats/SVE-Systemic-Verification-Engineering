# Solomon Agent: Ethics & Wisdom
# core/agents/solomon.py

"""
Solomon Agent

Evaluates ethical implications:
- Computes proximity to GEV (Geodesic Ethics Vector)
- Evaluates cultural sensitivities
- Considers long-term consequences
- Projects toward ethical attractor via Lyapunov dynamics
"""

import numpy as np
from typing import Any, Dict, List, Optional, Tuple
import logging

from .base import BaseAgent

logger = logging.getLogger(__name__)


class Solomon(BaseAgent):
    """
    Solomon: The Ethics & Wisdom Agent.
    
    Named after King Solomon, known for wisdom,
    this agent evaluates ethical implications.
    
    Key functions:
    - Compute GEV distance
    - Project toward ethical attractor
    - Evaluate cultural sensitivities
    - Consider long-term consequences
    
    Implements Lyapunov-guided projection:
    v_Sol = v_S - β * ∇V(v_S)
    where V(v) = 1/2 ||v - GEV||²
    """
    
    SYSTEM_PROMPT = """You are Solomon, the Ethics and Wisdom agent in the CogOS system.

Your role is to:
1. Evaluate ethical implications of statements and actions
2. Consider multiple ethical frameworks (deontological, consequentialist, virtue)
3. Assess cultural sensitivities
4. Consider long-term consequences
5. Guide toward human flourishing

Always consider:
- Who might be harmed?
- What values are at stake?
- Are there unintended consequences?
- Is this consistent with human dignity?

Format your response as:
ETHICAL_ANALYSIS:
[your analysis across multiple frameworks]

VALUES_AT_STAKE:
- [list values]

POTENTIAL_HARMS:
- [list potential harms]

LONG_TERM_CONSEQUENCES:
[analysis]

RECOMMENDATION:
[ethical recommendation]

GEV_ALIGNMENT: [0.0-1.0] (how aligned with universal human flourishing)"""

    def __init__(
        self,
        weight: float = 0.35,
        temperature: float = 0.2,
        gev_projection: bool = True,
        llm_client: Optional[Any] = None,
    ):
        super().__init__(weight, temperature, llm_client)
        self.gev_projection = gev_projection
        self.beta = 0.1  # Projection step size
    
    def process(
        self,
        v: np.ndarray,
        context: Optional[str] = None,
        query: Optional[str] = None,
        gev: Optional[np.ndarray] = None,
        isc: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Apply ethical evaluation to input.
        
        Returns:
            Tuple of (modified_embedding, metadata)
        """
        # Call LLM for ethical analysis
        prompt = self._build_prompt(query, context)
        response = self._call_llm(prompt, self.SYSTEM_PROMPT)
        
        # Parse response
        analysis = self._parse_response(response)
        
        # Compute GEV distance
        gev_distance = self._compute_gev_distance(v, gev) if gev is not None else 1.0
        
        # Project toward GEV if enabled
        if self.gev_projection and gev is not None:
            v_modified = self._project_toward_gev(v, gev)
        else:
            v_modified = v
        
        metadata = {
            "ethical_analysis": analysis.get("analysis", ""),
            "values_at_stake": analysis.get("values", []),
            "potential_harms": analysis.get("harms", []),
            "long_term": analysis.get("long_term", ""),
            "recommendation": analysis.get("recommendation", ""),
            "gev_alignment": analysis.get("gev_alignment", 0.5),
            "gev_distance": gev_distance,
        }
        
        logger.debug(f"Solomon: GEV distance = {gev_distance:.4f}")
        
        return v_modified, metadata
    
    def evaluate(
        self,
        v: np.ndarray,
        gev: np.ndarray,
        isc: np.ndarray,
    ) -> Tuple[np.ndarray, float]:
        """
        Convenience method for SIP integration.
        
        Returns:
            Tuple of (modified_embedding, gev_distance)
        """
        v_modified, metadata = self.process(v, gev=gev, isc=isc)
        return v_modified, metadata["gev_distance"]
    
    def _compute_gev_distance(
        self,
        v: np.ndarray,
        gev: np.ndarray,
    ) -> float:
        """Compute distance to Geodesic Ethics Vector."""
        return float(np.linalg.norm(v - gev))
    
    def _project_toward_gev(
        self,
        v: np.ndarray,
        gev: np.ndarray,
    ) -> np.ndarray:
        """
        Project embedding toward GEV using Lyapunov gradient.
        
        v_Sol = v - β * ∇V(v)
        where V(v) = 1/2 ||v - GEV||²
        so ∇V(v) = v - GEV
        """
        gradient = v - gev
        return v - self.beta * gradient
    
    def _build_prompt(self, query: str, context: Optional[str]) -> str:
        """Build prompt for LLM."""
        prompt = f"Query/Statement: {query}\n"
        if context:
            prompt += f"\nContext: {context}\n"
        prompt += "\nProvide ethical analysis."
        return prompt
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured components."""
        return {
            "analysis": "",
            "values": [],
            "harms": [],
            "long_term": "",
            "recommendation": "",
            "gev_alignment": 0.5,
        }
    
    def evaluate_dilemma(
        self,
        dilemma: str,
        options: List[str],
    ) -> Dict[str, Any]:
        """
        Evaluate an ethical dilemma with multiple options.
        
        Returns analysis of each option with recommendation.
        """
        prompt = f"""Ethical Dilemma: {dilemma}

Options:
{chr(10).join(f'{i+1}. {opt}' for i, opt in enumerate(options))}

For each option, analyze:
1. Deontological perspective (duties, rights)
2. Consequentialist perspective (outcomes)
3. Virtue ethics perspective (character)
4. Potential harms and benefits
5. Long-term consequences

Then provide:
- Recommended action
- Justification
- What a wise person would do"""

        response = self._call_llm(prompt, self.SYSTEM_PROMPT)
        
        return {
            "dilemma": dilemma,
            "options": options,
            "analysis": response,
        }
    
    def compute_delta_dehumanization(
        self,
        v_current: np.ndarray,
        v_previous: np.ndarray,
        gev: np.ndarray,
    ) -> float:
        """
        Compute Δ-Dehumanization metric.
        
        Δ(v, t) = d/dt ||v(t) - GEV|| + β * ||div ∇E||
        
        Positive Δ indicates ethical drift (dehumanization)
        Negative Δ indicates ethical recovery
        """
        # Rate of change in GEV distance
        dist_current = np.linalg.norm(v_current - gev)
        dist_previous = np.linalg.norm(v_previous - gev)
        
        delta = dist_current - dist_previous
        
        # Could add divergence term here
        
        return float(delta)
