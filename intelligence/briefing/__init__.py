"""Weekly intelligence briefing system."""

__version__ = "1.0.0"

from intelligence.briefing.runner import BriefingRunner
from intelligence.briefing.types import BriefingData, BriefingSection

__all__ = ["BriefingRunner", "BriefingData", "BriefingSection"]
