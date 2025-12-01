"""Dashboard interface for Pipeline."""

from pipeline.dashboard.app import Dashboard
from pipeline.dashboard.views import (
    LibraryView,
    SyncView,
    DistributionView,
    MetadataView,
)

__all__ = [
    "Dashboard",
    "LibraryView",
    "SyncView",
    "DistributionView",
    "MetadataView",
]
