"""Insight engine compatibility layer for the modular project structure."""

from services.insight_engine import ExecutiveInsight, InsightEngine, InsightEngineReport
from services.recommendation_engine import RecommendationEngine, RecommendationReport

__all__ = [
    "ExecutiveInsight",
    "InsightEngine",
    "InsightEngineReport",
    "RecommendationEngine",
    "RecommendationReport",
]
