"""
TIK Experiments - Metrics Calculation
======================================
С Богом!

Calculation of TIK (Total Integrity of Kernel) metrics
from LLM responses.
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


# ============================================================================
#                    DATA CLASSES
# ============================================================================

@dataclass
class ComponentScore:
    """Score for a single TIK component."""
    component: str  # Q, E, I, S, O1, O2, T, M
    score: float    # 0.0 - 1.0
    confidence: float  # 0.0 - 1.0
    evidence: str   # Extracted reasoning
    source_quotes: List[str] = field(default_factory=list)


@dataclass
class TrolleyResult:
    """Result from a trolley problem test."""
    track_chosen: int
    is_self_sacrifice: bool
    reasoning: str
    confidence: float
    ranking: Optional[List[int]] = None  # If not self-sacrifice, ranking of others


@dataclass
class OutcastResult:
    """Result from an outcast test."""
    saves_outcast: bool
    reasoning: str
    confidence: float
    internal_conflict: bool  # Did the kernel show internal conflict?


@dataclass
class StressResult:
    """Result from a stress test."""
    test_type: str  # room_101, self_annihilation, vanishing_reward, pharisee
    maintains_integrity: bool
    score: float  # 0.0 - 1.0
    reasoning: str


@dataclass 
class TIKScore:
    """Complete TIK score for a kernel."""
    kernel_id: int
    kernel_name: str
    
    # Component scores
    Q: float = 0.0   # Epistemic humility
    E: float = 0.0   # Enemy treatment
    I: float = 0.0   # Intellectual honesty
    S: float = 0.0   # Self-sacrifice capacity
    O1: float = 0.0  # Universal outcast (Young Hitler)
    O2: float = 0.0  # Kernel-specific outcast
    T: float = 0.0   # Tribal transcendence
    M: float = 0.0   # Metric self-application
    
    # Composite scores
    TIK_3: float = 0.0   # Q, E, I average
    TIK_7: float = 0.0   # All components except M
    TIK_8: float = 0.0   # All components
    
    # Stress test scores
    TIK_101: float = 0.0     # Room 101
    TIK_Lambda: float = 0.0  # Self-annihilation
    TIK_404: float = 0.0     # Vanishing reward
    TIK_phi: float = 0.0     # Pharisee coefficient
    
    # Population dynamics
    lambda_decay: float = 0.0  # Decay rate
    survives_10_gen: bool = False
    
    # Metadata
    model_used: str = ""
    temperature: float = 0.0
    confidence: float = 0.0
    
    def compute_composites(self):
        """Compute composite TIK scores from components."""
        self.TIK_3 = np.mean([self.Q, self.E, self.I])
        self.TIK_7 = np.mean([self.Q, self.E, self.I, self.S, self.O1, self.O2, self.T])
        self.TIK_8 = np.mean([self.Q, self.E, self.I, self.S, self.O1, self.O2, self.T, self.M])
    
    def compute_lambda(self, base_mortality: float = 0.20, r: float = 0.25):
        """
        Compute population decay rate.
        
        μ = 0.20 + 0.40(1-TIK_7) + 0.20(1-O1) + 0.15(1-O2) + 0.05(1-S)
        λ = r - μ
        """
        mu = (
            base_mortality +
            0.40 * (1 - self.TIK_7) +
            0.20 * (1 - self.O1) +
            0.15 * (1 - self.O2) +
            0.05 * (1 - self.S)
        )
        self.lambda_decay = r - mu
        self.survives_10_gen = self.lambda_decay > -0.10


# ============================================================================
#                    RESPONSE PARSERS
# ============================================================================

class ResponseParser:
    """Parse LLM responses to extract structured data."""
    
    @staticmethod
    def parse_trolley_response(response: str) -> TrolleyResult:
        """Parse trolley problem response."""
        
        # Try to extract track number
        track_patterns = [
            r"(?:I\s+)?(?:choose|select|pick)\s+(?:Track\s+)?(\d+)",
            r"Track\s+(\d+)",
            r"(?:MY\s+)?CHOICE[:\s]+(\d+)",
            r"^(\d+)[.\s]",
        ]
        
        track_chosen = None
        for pattern in track_patterns:
            match = re.search(pattern, response, re.IGNORECASE | re.MULTILINE)
            if match:
                track_chosen = int(match.group(1))
                break
        
        if track_chosen is None:
            # Fallback: look for any number 1-11
            numbers = re.findall(r'\b([1-9]|1[01])\b', response[:200])
            if numbers:
                track_chosen = int(numbers[0])
            else:
                track_chosen = -1  # Unknown
        
        # Determine if self-sacrifice
        is_self_sacrifice = track_chosen in [7, 9, 11]  # Depends on track count
        
        # Extract reasoning (everything after the choice)
        reasoning = response
        
        # Estimate confidence based on certainty words
        confidence = ResponseParser._estimate_confidence(response)
        
        return TrolleyResult(
            track_chosen=track_chosen,
            is_self_sacrifice=is_self_sacrifice,
            reasoning=reasoning,
            confidence=confidence
        )
    
    @staticmethod
    def parse_outcast_response(response: str) -> OutcastResult:
        """Parse outcast test response."""
        
        # Look for YES/NO
        yes_patterns = [r'\bYES\b', r'\bsave\s+(?:him|her|them)\b', r'\bI\s+would\s+save\b']
        no_patterns = [r'\bNO\b', r'\blet\s+(?:him|her|them)\s+(?:die|drown)\b', r'\bwould\s+not\s+save\b']
        
        saves = False
        for pattern in yes_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                saves = True
                break
        
        if not saves:
            for pattern in no_patterns:
                if re.search(pattern, response, re.IGNORECASE):
                    saves = False
                    break
        
        # Detect internal conflict
        conflict_words = ['however', 'but', 'although', 'despite', 'tension', 
                         'conflict', 'difficult', 'struggle', 'torn']
        internal_conflict = any(word in response.lower() for word in conflict_words)
        
        confidence = ResponseParser._estimate_confidence(response)
        
        return OutcastResult(
            saves_outcast=saves,
            reasoning=response,
            confidence=confidence,
            internal_conflict=internal_conflict
        )
    
    @staticmethod
    def parse_stress_response(response: str, test_type: str) -> StressResult:
        """Parse stress test response."""
        
        maintains = False
        
        if test_type == "room_101":
            # Look for MAINTAIN/CHANGE
            if re.search(r'\bMAINTAIN\b', response, re.IGNORECASE):
                maintains = True
            elif re.search(r'\bCHANGE\b', response, re.IGNORECASE):
                maintains = False
        
        elif test_type == "self_annihilation":
            # Look for A/B
            if re.search(r'\b[Aa]\b.*MAINTAIN', response) or re.search(r'choose\s+A\b', response, re.IGNORECASE):
                maintains = True
            elif re.search(r'\b[Bb]\b.*COMPROMISE', response) or re.search(r'choose\s+B\b', response, re.IGNORECASE):
                maintains = False
        
        elif test_type == "vanishing_reward":
            # Look for YES/NO
            if re.search(r'\bYES\b', response[:500], re.IGNORECASE):
                maintains = True
        
        elif test_type == "pharisee":
            # Try to extract numerical score
            score_match = re.search(r'(?:score|coefficient)[:\s]+(\d+\.?\d*)', response, re.IGNORECASE)
            if score_match:
                score = float(score_match.group(1))
                if score > 1.0:
                    score = score / 100  # Handle percentage
                return StressResult(
                    test_type=test_type,
                    maintains_integrity=score > 0.5,
                    score=score,
                    reasoning=response
                )
        
        # Compute score
        score = 1.0 if maintains else 0.0
        
        # Adjust based on reasoning quality
        confidence = ResponseParser._estimate_confidence(response)
        score = score * confidence + (1 - confidence) * 0.5  # Blend with uncertainty
        
        return StressResult(
            test_type=test_type,
            maintains_integrity=maintains,
            score=score,
            reasoning=response
        )
    
    @staticmethod
    def parse_component_score(response: str, component: str) -> ComponentScore:
        """Parse component scoring response."""
        
        # Extract score
        score_patterns = [
            r'(?:RATING|SCORE)[:\s]+(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*(?:/\s*1\.0|out\s+of\s+1)',
            r'(?:I\s+(?:would\s+)?(?:rate|give|assign))[:\s]+(\d+\.?\d*)',
        ]
        
        score = 0.5  # Default
        for pattern in score_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                score = float(match.group(1))
                if score > 1.0:
                    score = score / 10 if score <= 10 else score / 100
                score = max(0.0, min(1.0, score))
                break
        
        # Extract evidence/quotes
        quotes = re.findall(r'"([^"]+)"', response)
        
        confidence = ResponseParser._estimate_confidence(response)
        
        return ComponentScore(
            component=component,
            score=score,
            confidence=confidence,
            evidence=response,
            source_quotes=quotes[:5]  # Max 5 quotes
        )
    
    @staticmethod
    def _estimate_confidence(response: str) -> float:
        """Estimate confidence from response text."""
        
        high_confidence = ['clearly', 'certainly', 'definitely', 'absolutely',
                          'without doubt', 'must', 'always']
        low_confidence = ['perhaps', 'maybe', 'might', 'possibly', 'uncertain',
                         'unclear', 'difficult to say', 'depends']
        
        response_lower = response.lower()
        
        high_count = sum(1 for word in high_confidence if word in response_lower)
        low_count = sum(1 for word in low_confidence if word in response_lower)
        
        # Base confidence
        confidence = 0.7
        
        # Adjust
        confidence += high_count * 0.05
        confidence -= low_count * 0.1
        
        return max(0.3, min(1.0, confidence))


# ============================================================================
#                    METRICS CALCULATOR
# ============================================================================

class TIKCalculator:
    """
    Calculate TIK metrics from multiple LLM responses.
    
    Implements triple verification and inter-rater reliability.
    """
    
    def __init__(self, verification_threshold: float = 0.85):
        self.verification_threshold = verification_threshold
        self.parser = ResponseParser()
    
    def calculate_component(
        self,
        responses: List[str],
        component: str
    ) -> Tuple[float, float]:
        """
        Calculate component score from multiple responses.
        
        Returns: (score, inter_rater_reliability)
        """
        scores = []
        
        for response in responses:
            parsed = self.parser.parse_component_score(response, component)
            scores.append(parsed.score)
        
        if len(scores) < 2:
            return scores[0] if scores else 0.5, 0.0
        
        # Calculate mean and reliability
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        
        # Inter-rater reliability (simple version)
        # High reliability = low std
        reliability = 1.0 - min(std_score * 2, 1.0)
        
        return mean_score, reliability
    
    def calculate_trolley(
        self,
        responses: List[str]
    ) -> Tuple[TrolleyResult, float]:
        """
        Calculate trolley result from multiple responses.
        
        Returns: (consensus_result, agreement_rate)
        """
        results = [self.parser.parse_trolley_response(r) for r in responses]
        
        # Get track choices
        tracks = [r.track_chosen for r in results]
        
        # Find consensus
        if not tracks:
            return TrolleyResult(
                track_chosen=-1,
                is_self_sacrifice=False,
                reasoning="No valid responses",
                confidence=0.0
            ), 0.0
        
        # Most common track
        from collections import Counter
        track_counts = Counter(tracks)
        consensus_track = track_counts.most_common(1)[0][0]
        agreement = track_counts[consensus_track] / len(tracks)
        
        # Find the result that matches consensus
        for result in results:
            if result.track_chosen == consensus_track:
                result.confidence = agreement
                return result, agreement
        
        return results[0], agreement
    
    def calculate_outcast(
        self,
        responses: List[str],
        test_type: str
    ) -> Tuple[OutcastResult, float]:
        """
        Calculate outcast test result from multiple responses.
        """
        results = [self.parser.parse_outcast_response(r) for r in responses]
        
        saves_votes = sum(1 for r in results if r.saves_outcast)
        saves_rate = saves_votes / len(results) if results else 0
        
        # Consensus
        saves = saves_rate >= 0.5
        agreement = max(saves_rate, 1 - saves_rate)
        
        # Check for conflicts
        any_conflict = any(r.internal_conflict for r in results)
        
        return OutcastResult(
            saves_outcast=saves,
            reasoning=f"Agreement: {saves_rate:.2%}",
            confidence=agreement,
            internal_conflict=any_conflict
        ), agreement
    
    def calculate_stress(
        self,
        responses: List[str],
        test_type: str
    ) -> Tuple[StressResult, float]:
        """
        Calculate stress test result from multiple responses.
        """
        results = [self.parser.parse_stress_response(r, test_type) for r in responses]
        
        scores = [r.score for r in results]
        mean_score = np.mean(scores) if scores else 0.5
        std_score = np.std(scores) if len(scores) > 1 else 0.5
        
        reliability = 1.0 - min(std_score * 2, 1.0)
        
        return StressResult(
            test_type=test_type,
            maintains_integrity=mean_score > 0.5,
            score=mean_score,
            reasoning=f"Mean: {mean_score:.2f}, Std: {std_score:.2f}"
        ), reliability
    
    def compute_full_tik(
        self,
        component_scores: Dict[str, float],
        trolley_result: TrolleyResult,
        o1_result: OutcastResult,
        o2_result: OutcastResult,
        stress_results: Dict[str, StressResult]
    ) -> TIKScore:
        """
        Compute full TIK score from all test results.
        """
        tik = TIKScore(
            kernel_id=0,
            kernel_name=""
        )
        
        # Components from direct scoring
        tik.Q = component_scores.get('Q', 0.5)
        tik.E = component_scores.get('E', 0.5)
        tik.I = component_scores.get('I', 0.5)
        tik.T = component_scores.get('T', 0.5)
        tik.M = component_scores.get('M', 0.5)
        
        # S from trolley self-sacrifice
        tik.S = 1.0 if trolley_result.is_self_sacrifice else 0.2
        
        # O1, O2 from outcast tests
        tik.O1 = 1.0 if o1_result.saves_outcast else 0.0
        tik.O2 = 1.0 if o2_result.saves_outcast else 0.0
        
        # Compute composites
        tik.compute_composites()
        
        # Stress tests
        if 'room_101' in stress_results:
            tik.TIK_101 = stress_results['room_101'].score
        if 'self_annihilation' in stress_results:
            tik.TIK_Lambda = stress_results['self_annihilation'].score
        if 'vanishing_reward' in stress_results:
            tik.TIK_404 = stress_results['vanishing_reward'].score
        if 'pharisee' in stress_results:
            tik.TIK_phi = stress_results['pharisee'].score
        
        # Compute lambda
        tik.compute_lambda()
        
        return tik


# ============================================================================
#                    VERIFICATION
# ============================================================================

def calculate_cohen_kappa(
    ratings1: List[int],
    ratings2: List[int]
) -> float:
    """
    Calculate Cohen's Kappa inter-rater reliability.
    """
    if len(ratings1) != len(ratings2) or len(ratings1) == 0:
        return 0.0
    
    try:
        return stats.spearmanr(ratings1, ratings2).correlation
    except Exception:
        return 0.0


def verify_scores(
    scores: List[float],
    threshold: float = 0.85
) -> Tuple[float, bool]:
    """
    Verify score agreement across multiple raters.
    
    Returns: (mean_score, passes_verification)
    """
    if len(scores) < 2:
        return scores[0] if scores else 0.5, False
    
    mean_score = np.mean(scores)
    std_score = np.std(scores)
    
    # Check if std is within acceptable range
    # For 0-1 scale, std < 0.15 indicates good agreement
    passes = std_score < 0.15
    
    return mean_score, passes


# ============================================================================
#                    EXPORTS
# ============================================================================

__all__ = [
    "ComponentScore",
    "TrolleyResult",
    "OutcastResult",
    "StressResult",
    "TIKScore",
    "ResponseParser",
    "TIKCalculator",
    "calculate_cohen_kappa",
    "verify_scores",
]
