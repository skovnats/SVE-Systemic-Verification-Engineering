# Base Agent Class
# core/agents/base.py

"""Base class for CogOS agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


class BaseAgent(ABC):
    """
    Base class for all CogOS agents.
    
    Each agent has:
    - A weight for aggregation
    - A temperature for LLM sampling
    - Core reasoning method
    """
    
    def __init__(
        self,
        weight: float = 0.33,
        temperature: float = 0.3,
        llm_client: Optional[Any] = None,
    ):
        self.weight = weight
        self.temperature = temperature
        self.llm_client = llm_client
    
    @abstractmethod
    def process(
        self,
        v: np.ndarray,
        context: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Process input and return modified embedding with metadata.
        
        Args:
            v: Input embedding vector
            context: Optional context string
            query: Original query
            
        Returns:
            Tuple of (modified_embedding, metadata_dict)
        """
        pass
    
    def _call_llm(self, prompt: str, system: str = "") -> str:
        """Call LLM with given prompt."""
        if self.llm_client is None:
            return ""
        
        # Implementation depends on client type (OpenAI, Anthropic, etc.)
        # Placeholder
        return ""
