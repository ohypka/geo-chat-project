"""
Built-in data providers for geo-chat package.

This module automatically registers all available providers.
"""

from .weather import WeatherProvider
from .doctors import DoctorsProvider

__all__ = [
    "WeatherProvider",
    "DoctorsProvider",
]
