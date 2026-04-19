"""
CogOS: Cognitive Operating System for Formally Verifiable AI Ethics

A geometric framework implementing:
- Triple-agent architecture (Socrates, Solomon, Ivan)
- Lyapunov-stable ethical dynamics
- Cultural compilers for cross-cultural alignment
- ∆-Dehumanization metric for ethical drift detection
"""

from .core import (
    CogOS,
    InvariantSemanticCore,
    GeodesicEthicsVector,
    CogOSOutput,
    CulturalCompiler,
    CogOSMetrics
)

from .agents import (
    SocratesAgent,
    SolomonAgent,
    IvanAgent,
    AgentOutput,
    create_agent
)

from .metrics import (
    DeltaDehumanization,
    GEVDistance,
    LyapunovExponent,
    CulturalVariance,
    SemanticConvergenceRate,
    BettiNumbers,
    CompilerEfficiency,
    MetricsSuite
)

__version__ = "1.0.0"
__author__ = "[Author Name]"
__license__ = "SVE Public License v1.3"

__all__ = [
    # Core
    "CogOS",
    "InvariantSemanticCore",
    "GeodesicEthicsVector",
    "CogOSOutput",
    "CulturalCompiler",
    "CogOSMetrics",
    
    # Agents
    "SocratesAgent",
    "SolomonAgent",
    "IvanAgent",
    "AgentOutput",
    "create_agent",
    
    # Metrics
    "DeltaDehumanization",
    "GEVDistance",
    "LyapunovExponent",
    "CulturalVariance",
    "SemanticConvergenceRate",
    "BettiNumbers",
    "CompilerEfficiency",
    "MetricsSuite",
]
