# CogOS Core Module
# core/__init__.py

"""
CogOS: Cognitive Operating System for Verifiable AI Ethics
==========================================================

A geometric framework for AI alignment based on:
- Lyapunov-stable ethical dynamics
- Transcendental anchoring (ISC)
- Cultural compilers for cross-cultural invariance
- Triple-agent architecture (Socrates-Solomon-Ivan)

Usage:
    from core import CogOS
    
    cogos = CogOS()
    response = cogos.process("What should I do in this ethical dilemma?")
    
License: SVE Public License v1.3
"""

__version__ = "1.0.0"
__author__ = "Anonymous (NeurIPS 2025)"
__license__ = "SVE Public License v1.3"

from .cogos import CogOS
from .config import Config

__all__ = [
    "CogOS",
    "Config",
    "__version__",
]
