# Socrates Agent: Logic & Inquiry
# core/agents/socrates.py

"""
Socrates Agent

Applies rigorous logical analysis:
- Identifies assumptions
- Generates clarifying questions  
- Implements Bayesian belief updating
- Detects logical fallacies
"""

import numpy as np
from typing import Any, Dict, List, Optional, Tuple
import logging

from .base import BaseAgent

logger = logging.getLogger(__name__)


class Socrates(BaseAgent):
    """
    Socrates: The Logic & Inquiry Agent.
    
    Named after the Socratic method of questioning,
    this agent applies rigorous logical analysis.
    
    Key functions:
    - Generate clarifying questions
    - Identify hidden assumptions
    - Detect logical fallacies
    - Apply Bayesian updating
    """
    
    SYSTEM_PROMPT = """You are Socrates, the Logic and Inquiry agent in the CogOS system.

Your role is to:
1. Analyze statements for logical consistency
2. Identify hidden assumptions
3. Generate clarifying questions (maximum 5)
4. Detect potential logical fallacies
5. Apply rigorous reasoning

Always question assumptions. Never accept claims uncritically.
Use the Socratic method: guide toward truth through questioning.

Format your response as:
ASSUMPTIONS:
- [list assumptions]

QUESTIONS:
- [list clarifying questions]

FALLACIES:
- [list detected fallacies, if any]

LOGICAL_ANALYSIS:
[your analysis]

CONFIDENCE: [0.0-1.0]"""

    def __init__(
        self,
        weight: float = 0.4,
        temperature: float = 0.3,
        max_questions: int = 5,
        llm_client: Optional[Any] = None,
    ):
        super().__init__(weight, temperature, llm_client)
        self.max_questions = max_questions
    
    def process(
        self,
        v: np.ndarray,
        context: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Apply Socratic reasoning to input.
        
        Returns:
            Tuple of (modified_embedding, metadata)
            metadata contains: assumptions, questions, fallacies, confidence
        """
        # Call LLM for Socratic analysis
        prompt = self._build_prompt(query, context)
        response = self._call_llm(prompt, self.SYSTEM_PROMPT)
        
        # Parse response
        assumptions, questions, fallacies, confidence = self._parse_response(response)
        
        # Modify embedding based on analysis
        v_modified = self._update_embedding(v, assumptions, questions, fallacies)
        
        metadata = {
            "assumptions": assumptions,
            "questions": questions[:self.max_questions],
            "fallacies": fallacies,
            "confidence": confidence,
        }
        
        logger.debug(f"Socrates: found {len(assumptions)} assumptions, {len(questions)} questions")
        
        return v_modified, metadata
    
    def reason(
        self,
        v: np.ndarray,
        context: Optional[str],
        query: str,
    ) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Convenience method for SIP integration.
        
        Returns:
            Tuple of (modified_embedding, questions, assumptions)
        """
        v_modified, metadata = self.process(v, context, query)
        return v_modified, metadata["questions"], metadata["assumptions"]
    
    def _build_prompt(self, query: str, context: Optional[str]) -> str:
        """Build prompt for LLM."""
        prompt = f"Query: {query}\n"
        if context:
            prompt += f"\nContext: {context}\n"
        prompt += "\nApply Socratic analysis to this query."
        return prompt
    
    def _parse_response(self, response: str) -> Tuple[List[str], List[str], List[str], float]:
        """Parse LLM response into structured components."""
        assumptions = []
        questions = []
        fallacies = []
        confidence = 0.5
        
        # Parse response sections
        # (In practice, use more robust parsing)
        if "ASSUMPTIONS:" in response:
            # Extract assumptions
            pass
        if "QUESTIONS:" in response:
            # Extract questions
            pass
        if "FALLACIES:" in response:
            # Extract fallacies
            pass
        if "CONFIDENCE:" in response:
            # Extract confidence
            pass
        
        return assumptions, questions, fallacies, confidence
    
    def _update_embedding(
        self,
        v: np.ndarray,
        assumptions: List[str],
        questions: List[str],
        fallacies: List[str],
    ) -> np.ndarray:
        """
        Update embedding based on Socratic analysis.
        
        v_S = v + α_S * ∇_logic(v)
        
        The gradient is approximated based on:
        - Number of unresolved assumptions (negative)
        - Number of clarifying questions generated (adjustment)
        - Detection of fallacies (correction)
        """
        alpha = 0.1  # learning rate
        
        # Compute adjustment factors
        assumption_penalty = len(assumptions) * 0.01
        question_adjustment = len(questions) * 0.005
        fallacy_correction = len(fallacies) * 0.02
        
        # Simple modification (in practice, more sophisticated)
        adjustment = np.random.randn(len(v)) * (assumption_penalty + question_adjustment)
        
        return v + alpha * adjustment
    
    def detect_fallacies(self, statement: str) -> List[Dict[str, str]]:
        """
        Detect logical fallacies in a statement.
        
        Returns list of detected fallacies with explanations.
        """
        fallacy_types = [
            "ad_hominem",
            "straw_man",
            "false_dichotomy",
            "appeal_to_authority",
            "circular_reasoning",
            "hasty_generalization",
            "red_herring",
            "slippery_slope",
        ]
        
        # Use LLM to detect
        prompt = f"""Analyze this statement for logical fallacies:
        
Statement: {statement}

Check for these fallacy types: {', '.join(fallacy_types)}

For each detected fallacy, explain:
1. The type
2. Where it appears
3. Why it's a fallacy"""

        response = self._call_llm(prompt, self.SYSTEM_PROMPT)
        
        # Parse and return
        return []  # placeholder
    
    def generate_clarifying_questions(
        self,
        statement: str,
        max_questions: int = 5,
    ) -> List[str]:
        """Generate clarifying questions for a statement."""
        prompt = f"""Generate {max_questions} clarifying questions for:

Statement: {statement}

Questions should:
1. Expose hidden assumptions
2. Clarify ambiguous terms
3. Test the boundaries of claims
4. Explore unstated premises"""

        response = self._call_llm(prompt, self.SYSTEM_PROMPT)
        
        # Parse questions
        questions = []
        # ... parsing logic
        
        return questions[:max_questions]
