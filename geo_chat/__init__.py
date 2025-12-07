"""
Geo Chat - Universal Python package for collecting and standardizing geographic data.

This package provides a framework for creating data providers that can fetch
and normalize geographic data from various APIs into a unified format.

Quick Start:
    from geo_chat import create_provider, Location
    
    # Create a provider
    provider = create_provider("weather", api_key="your_key")
    
    # Fetch data
    location = Location(lat=52.2297, lon=21.0122, name="Warsaw")
    data = provider.get_data(location)
    
Creating Custom Providers:
    See examples/custom_provider.py for a complete example.
"""

__version__ = "0.1.0"

# Core framework
from .core import (
    BaseProvider,
    ProviderConfig,
    Location,
    DataPoint,
    BatchRequest,
    BatchResponse,
    create_provider,
    get_provider,
    ProviderRegistry,
)

# Import providers to register them
from . import providers

__all__ = [
    # Core framework
    "BaseProvider",
    "ProviderConfig",
    "Location",
    "DataPoint",
    "BatchRequest",
    "BatchResponse",
    "create_provider",
    "get_provider",
    "ProviderRegistry",
    # Convenience exports
    "providers",
]
