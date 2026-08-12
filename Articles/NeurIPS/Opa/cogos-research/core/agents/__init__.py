# CogOS Agents Module
# core/agents/__init__.py

"""
Triple-Agent Architecture:
- Socrates: Logic & Inquiry
- Solomon: Ethics & Wisdom
- Ivan: Humility & Calibration
"""

from .base import BaseAgent
from .socrates import Socrates
from .solomon import Solomon
from .ivan import Ivan

__all__ = ["BaseAgent", "Socrates", "Solomon", "Ivan"]
