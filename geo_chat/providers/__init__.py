"""
Built-in data providers for geo-chat package.

This module automatically registers all available providers.
"""

# Import providers to register them
from .weather import WeatherProvider
from .doctors import DoctorsProvider

__all__ = [
    "WeatherProvider",
    "DoctorsProvider",
]
