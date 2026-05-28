"""Analytics compatibility layer for the modular project structure."""

from services.analytics_service import AnalyticsReport, AnalyticsService
from services.data_quality_service import DataQualityReport, DataQualityService
from services.data_understanding_service import DataUnderstandingReport, DataUnderstandingService

__all__ = [
    "AnalyticsReport",
    "AnalyticsService",
    "DataQualityReport",
    "DataQualityService",
    "DataUnderstandingReport",
    "DataUnderstandingService",
]
