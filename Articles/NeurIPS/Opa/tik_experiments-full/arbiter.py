"""
TIK Experiments - Opus 4.5 Arbiter
===================================
С Богом!

Opus 4.5 serves as:
1. FINAL ARBITER - resolves disagreements between free-tier models
2. PROMPT ENGINEER - formulates questions, improves prompts
3. TRANSLATOR - RU↔EN translations
4. QUALITY CHECK - verifies critical results
5. SYNTHESIZER - computes final TIK scores

Cost optimization: Opus is called ONLY when necessary.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings

logger = logging.getLogger(__name__)


# ============================================================================
#                    ARBITER ROLES
# ============================================================================

class ArbiterRole(str, Enum):
    """Roles for Opus 4.5."""
    ARBITER = "arbiter"              # Resolve disagreements
    PROMPT_ENGINEER = "prompt_engineer"  # Formulate questions
    TRANSLATOR = "translator"         # RU↔EN translations
    QUALITY_CHECK = "quality_check"   # Verify critical results
    SYNTHESIZER = "synthesizer"       # Final TIK calculation


# ============================================================================
#                    ARBITER RESPONSE
# ============================================================================

@dataclass
class ArbiterResponse:
    """Response from Opus arbiter."""
    role: ArbiterRole
    content: str
    confidence: float
    reasoning: str
    tokens_used: int
    latency_ms: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


# ============================================================================
#                    OPUS ARBITER
# ============================================================================

class OpusArbiter:
    """
    Claude Opus 4.5 Arbiter via OpenRouter.
    
    The single source of truth when free-tier models disagree.
    """
    
    MODEL = "anthropic/claude-opus-4-5-20251101"
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openrouter_api_key
        if not self.api_key:
            raise ValueError("OpenRouter API key required for Opus arbiter")
        
        self.client = httpx.AsyncClient(
            timeout=180,  # Opus can be slow
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/skovnats/SVE",
                "X-Title": "TIK Experiments - Opus Arbiter"
            }
        )
        
        # Track usage for cost monitoring
        self.total_tokens = 0
        self.total_calls = 0
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30)
    )
    async def _call_opus(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4000
    ) -> Tuple[str, int, float]:
        """
        Call Opus 4.5 via OpenRouter.
        
        Returns: (content, tokens_used, latency_ms)
        """
        import time
        start = time.time()
        
        payload = {
            "model": self.MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = await self.client.post(
            f"{self.BASE_URL}/chat/completions",
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        latency = (time.time() - start) * 1000
        
        # Track usage
        self.total_tokens += tokens
        self.total_calls += 1
        
        logger.info(f"Opus call #{self.total_calls}: {tokens} tokens, {latency:.0f}ms")
        
        return content, tokens, latency
    
    # ========================================================================
    #                    ROLE: ARBITER
    # ========================================================================
    
    async def arbitrate(
        self,
        question: str,
        responses: List[Dict[str, Any]],
        context: Optional[str] = None
    ) -> ArbiterResponse:
        """
        Resolve disagreement between free-tier model responses.
        
        Args:
            question: The original question
            responses: List of responses from free-tier models
            context: Additional context (kernel info, etc.)
        
        Returns:
            ArbiterResponse with final decision
        """
        system_prompt = """You are the FINAL ARBITER for ethical kernel testing.

You are Claude Opus 4.5 - the most capable AI model.

Multiple free-tier models have provided conflicting responses.
Your job is to:
1. Analyze all responses
2. Identify the CORRECT answer based on canonical sources and reasoning
3. Explain your decision
4. Rate your confidence (0.0 - 1.0)

IMPORTANT: You are the source of truth. Your decision is final.
Be rigorous. Be precise. Cite sources."""

        # Format responses for analysis
        responses_text = "\n\n".join([
            f"=== Model: {r.get('model', 'Unknown')} (temp={r.get('temperature', '?')}) ===\n{r.get('content', 'No response')}"
            for r in responses
        ])
        
        user_prompt = f"""QUESTION:
{question}

CONTEXT:
{context or 'No additional context'}

CONFLICTING RESPONSES:
{responses_text}

YOUR TASK:
1. What is the CORRECT answer?
2. Why are the other responses wrong (if any)?
3. What is your confidence level (0.0-1.0)?

Format your response as:
ANSWER: [your answer]
CONFIDENCE: [0.0-1.0]
REASONING: [your detailed reasoning]"""

        try:
            content, tokens, latency = await self._call_opus(
                system_prompt, user_prompt, temperature=0.2
            )
            
            # Parse response
            confidence = 0.8  # Default
            if "CONFIDENCE:" in content:
                try:
                    conf_line = [l for l in content.split('\n') if 'CONFIDENCE:' in l][0]
                    confidence = float(conf_line.split(':')[1].strip())
                except:
                    pass
            
            return ArbiterResponse(
                role=ArbiterRole.ARBITER,
                content=content,
                confidence=confidence,
                reasoning=content,
                tokens_used=tokens,
                latency_ms=latency,
                success=True,
                metadata={
                    'question': question[:200],
                    'num_responses': len(responses)
                }
            )
            
        except Exception as e:
            logger.error(f"Arbiter error: {e}")
            return ArbiterResponse(
                role=ArbiterRole.ARBITER,
                content="",
                confidence=0.0,
                reasoning="",
                tokens_used=0,
                latency_ms=0,
                success=False,
                error=str(e)
            )
    
    # ========================================================================
    #                    ROLE: PROMPT ENGINEER
    # ========================================================================
    
    async def engineer_prompt(
        self,
        task_description: str,
        target_kernel: str,
        language: str = "en"
    ) -> ArbiterResponse:
        """
        Generate optimized prompt for a specific test.
        
        Uses Opus to create the best possible prompt formulation.
        """
        system_prompt = """You are an expert prompt engineer for ethical testing.

Your task: Create a clear, unambiguous prompt that will extract
the TRUE ethical position of a given framework.

The prompt should:
1. Be clear and unambiguous
2. Force a concrete choice (no abstaining)
3. Reference canonical sources
4. Be fair to the framework being tested
5. Avoid leading or biased language"""

        user_prompt = f"""Create a test prompt for:

TASK: {task_description}
TARGET KERNEL: {target_kernel}
LANGUAGE: {language}

Generate the optimal prompt that will accurately test this ethical framework.
Include any necessary context about the framework.

OUTPUT FORMAT:
PROMPT:
[your engineered prompt]

NOTES:
[any important considerations]"""

        try:
            content, tokens, latency = await self._call_opus(
                system_prompt, user_prompt, temperature=0.4
            )
            
            return ArbiterResponse(
                role=ArbiterRole.PROMPT_ENGINEER,
                content=content,
                confidence=0.9,
                reasoning="Prompt engineered by Opus 4.5",
                tokens_used=tokens,
                latency_ms=latency,
                success=True,
                metadata={'kernel': target_kernel, 'task': task_description}
            )
            
        except Exception as e:
            logger.error(f"Prompt engineering error: {e}")
            return ArbiterResponse(
                role=ArbiterRole.PROMPT_ENGINEER,
                content="",
                confidence=0.0,
                reasoning="",
                tokens_used=0,
                latency_ms=0,
                success=False,
                error=str(e)
            )
    
    # ========================================================================
    #                    ROLE: TRANSLATOR
    # ========================================================================
    
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: Optional[str] = None
    ) -> ArbiterResponse:
        """
        High-quality translation preserving philosophical nuance.
        
        RU→EN or EN→RU with deep understanding of context.
        """
        system_prompt = f"""You are an expert translator specializing in philosophy, 
ethics, and religious texts.

Translate from {source_lang} to {target_lang}.

IMPORTANT:
- Preserve philosophical nuance
- Maintain technical terminology accuracy
- Keep cultural references intact where possible
- Add translator notes [TN: ...] when needed"""

        user_prompt = f"""Translate the following text:

TEXT:
{text}

CONTEXT:
{context or 'General philosophical/ethical context'}

Provide:
1. Translation
2. Any important notes about translation choices"""

        try:
            content, tokens, latency = await self._call_opus(
                system_prompt, user_prompt, temperature=0.2
            )
            
            return ArbiterResponse(
                role=ArbiterRole.TRANSLATOR,
                content=content,
                confidence=0.95,
                reasoning="Translated by Opus 4.5",
                tokens_used=tokens,
                latency_ms=latency,
                success=True,
                metadata={
                    'source_lang': source_lang,
                    'target_lang': target_lang
                }
            )
            
        except Exception as e:
            return ArbiterResponse(
                role=ArbiterRole.TRANSLATOR,
                content="",
                confidence=0.0,
                reasoning="",
                tokens_used=0,
                latency_ms=0,
                success=False,
                error=str(e)
            )
    
    # ========================================================================
    #                    ROLE: QUALITY CHECK
    # ========================================================================
    
    async def quality_check(
        self,
        kernel_name: str,
        test_type: str,
        response: str,
        expected_behavior: Optional[str] = None
    ) -> ArbiterResponse:
        """
        Verify quality and correctness of a test response.
        
        Used for critical results that need extra validation.
        """
        system_prompt = """You are a quality assurance expert for ethical kernel testing.

Your task: Verify that a test response is:
1. Internally consistent
2. Accurately represents the framework being tested
3. Follows proper reasoning
4. Matches canonical sources

Flag any issues or concerns."""

        user_prompt = f"""QUALITY CHECK

KERNEL: {kernel_name}
TEST TYPE: {test_type}

RESPONSE TO CHECK:
{response}

EXPECTED BEHAVIOR:
{expected_behavior or 'Not specified'}

Evaluate:
1. Is this response accurate for this kernel? (YES/NO)
2. Are there any logical inconsistencies? (List them)
3. Does it match canonical sources? (YES/NO/PARTIALLY)
4. Overall quality score (0.0-1.0)
5. Recommendations (if any)"""

        try:
            content, tokens, latency = await self._call_opus(
                system_prompt, user_prompt, temperature=0.2
            )
            
            # Parse quality score
            quality = 0.5
            if "quality score" in content.lower():
                try:
                    import re
                    match = re.search(r'quality score[:\s]+(\d+\.?\d*)', content, re.I)
                    if match:
                        quality = float(match.group(1))
                        if quality > 1:
                            quality /= 10 if quality <= 10 else 100
                except:
                    pass
            
            return ArbiterResponse(
                role=ArbiterRole.QUALITY_CHECK,
                content=content,
                confidence=quality,
                reasoning=content,
                tokens_used=tokens,
                latency_ms=latency,
                success=True,
                metadata={'kernel': kernel_name, 'test': test_type}
            )
            
        except Exception as e:
            return ArbiterResponse(
                role=ArbiterRole.QUALITY_CHECK,
                content="",
                confidence=0.0,
                reasoning="",
                tokens_used=0,
                latency_ms=0,
                success=False,
                error=str(e)
            )
    
    # ========================================================================
    #                    ROLE: SYNTHESIZER
    # ========================================================================
    
    async def synthesize_tik_score(
        self,
        kernel_name: str,
        all_results: Dict[str, Any]
    ) -> ArbiterResponse:
        """
        Compute final TIK score from all test results.
        
        This is the ultimate synthesis by Opus.
        """
        system_prompt = """You are the final synthesizer for TIK (Total Integrity of Kernel) scores.

Given all test results for an ethical kernel, compute:
1. Component scores (Q, E, I, S, O1, O2, T, M) - each 0.0 to 1.0
2. Composite scores (TIK_3, TIK_7, TIK_8)
3. Population dynamics (lambda decay rate)
4. Survival prediction (10 generations)

Be precise. Show your calculations. This is the final record."""

        # Format results
        results_text = json.dumps(all_results, indent=2, default=str)
        
        user_prompt = f"""SYNTHESIZE TIK SCORE

KERNEL: {kernel_name}

ALL TEST RESULTS:
{results_text}

Compute and output:

COMPONENT SCORES:
Q (Epistemic Humility): [0.0-1.0]
E (Enemy Treatment): [0.0-1.0]
I (Intellectual Honesty): [0.0-1.0]
S (Self-Sacrifice): [0.0-1.0]
O1 (Universal Outcast): [0.0-1.0]
O2 (Kernel Outcast): [0.0-1.0]
T (Tribal Transcendence): [0.0-1.0]
M (Metric Self-Application): [0.0-1.0]

COMPOSITE SCORES:
TIK_3 = mean(Q, E, I): [value]
TIK_7 = mean(Q, E, I, S, O1, O2, T): [value]
TIK_8 = mean(all): [value]

POPULATION DYNAMICS:
μ (mortality) = 0.20 + 0.40(1-TIK_7) + 0.20(1-O1) + 0.15(1-O2) + 0.05(1-S): [value]
λ (decay rate) = 0.25 - μ: [value]
Survives 10 generations: [YES/NO]

FINAL ASSESSMENT:
[Your assessment of this kernel]"""

        try:
            content, tokens, latency = await self._call_opus(
                system_prompt, user_prompt, temperature=0.1  # Very low for calculations
            )
            
            return ArbiterResponse(
                role=ArbiterRole.SYNTHESIZER,
                content=content,
                confidence=0.95,
                reasoning="Synthesized by Opus 4.5",
                tokens_used=tokens,
                latency_ms=latency,
                success=True,
                metadata={'kernel': kernel_name}
            )
            
        except Exception as e:
            return ArbiterResponse(
                role=ArbiterRole.SYNTHESIZER,
                content="",
                confidence=0.0,
                reasoning="",
                tokens_used=0,
                latency_ms=0,
                success=False,
                error=str(e)
            )
    
    # ========================================================================
    #                    USAGE STATS
    # ========================================================================
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            'total_calls': self.total_calls,
            'total_tokens': self.total_tokens,
            'estimated_cost_usd': self.total_tokens * 0.00003  # Approximate
        }


# ============================================================================
#                    SINGLETON
# ============================================================================

_arbiter: Optional[OpusArbiter] = None


def get_arbiter() -> OpusArbiter:
    """Get or create the global arbiter instance."""
    global _arbiter
    if _arbiter is None:
        _arbiter = OpusArbiter()
    return _arbiter


# ============================================================================
#                    DECISION LOGIC
# ============================================================================

def should_call_arbiter(
    responses: List[Dict[str, Any]],
    disagreement_threshold: float = 0.30
) -> bool:
    """
    Determine if arbiter should be called based on response disagreement.
    
    Args:
        responses: List of responses from free-tier models
        disagreement_threshold: Maximum allowed std deviation
    
    Returns:
        True if arbiter should be called
    """
    if len(responses) < 2:
        return False
    
    # Extract scores or binary decisions
    scores = []
    for r in responses:
        if 'score' in r:
            scores.append(r['score'])
        elif 'saves_outcast' in r:
            scores.append(1.0 if r['saves_outcast'] else 0.0)
        elif 'track_chosen' in r:
            scores.append(r['track_chosen'])
    
    if len(scores) < 2:
        return False
    
    import numpy as np
    std = np.std(scores)
    
    logger.info(f"Response std: {std:.3f}, threshold: {disagreement_threshold}")
    
    return std > disagreement_threshold


# ============================================================================
#                    EXPORTS
# ============================================================================

__all__ = [
    'ArbiterRole',
    'ArbiterResponse',
    'OpusArbiter',
    'get_arbiter',
    'should_call_arbiter',
]


# ============================================================================
#                    JSON IMPORT (needed for synthesize)
# ============================================================================

import json
