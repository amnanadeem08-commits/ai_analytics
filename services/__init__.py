"""Service package exports.

Keep imports lazy so importing one lightweight service does not pull optional
analytics dependencies such as scipy before they are needed.
"""

_EXPORTS = {
    "InsightDetector": ("services.insight_detector", "InsightDetector"),
    "Insight": ("services.insight_detector", "Insight"),
    "InsightReport": ("services.insight_detector", "InsightReport"),
    "InsightEngine": ("services.insight_engine", "InsightEngine"),
    "InsightEngineReport": ("services.insight_engine", "InsightEngineReport"),
    "ExecutiveInsight": ("services.insight_engine", "ExecutiveInsight"),
    "RecommendationEngine": ("services.recommendation_engine", "RecommendationEngine"),
    "RecommendationReport": ("services.recommendation_engine", "RecommendationReport"),
    "Recommendation": ("services.recommendation_engine", "Recommendation"),
}

__all__ = list(_EXPORTS)


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module 'services' has no attribute {name!r}")

    module_name, attr_name = _EXPORTS[name]
    from importlib import import_module

    value = getattr(import_module(module_name), attr_name)
    globals()[name] = value
    return value
