"""
Core framework for geo-chat package.

Provides base classes and interfaces for creating data providers
that can fetch and normalize geographic data from various APIs.
"""

from .base import BaseProvider, ProviderConfig
from .models import (
    Location,
    Metric,
    DataPoint,
    BatchRequest,
    BatchResponse,
)
from .registry import ProviderRegistry
from .factory import create_provider, get_provider

__all__ = [
    "BaseProvider",
    "ProviderConfig",
    "Location",
    "Metric",
    "DataPoint",
    "BatchRequest",
    "BatchResponse",
    "ProviderRegistry",
    "create_provider",
    "get_provider",
]
