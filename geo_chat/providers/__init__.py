"""
Built-in data providers for geo-chat package.

This module automatically registers all available providers.
"""

from .weather import WeatherProvider
from .doctors import DoctorsProvider
from .bikes import BikesProvider
from .traffic import TrafficProvider
__all__ = [
    "WeatherProvider",
    "DoctorsProvider",
    "BikesProvider",
    "TrafficProvider",
]
