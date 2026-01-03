"""
Environment module for weather and air quality data.

Uses OpenWeatherMap API to fetch and normalize environmental data.
"""

from .weather import (
    get_current_weather,
    get_current_air_quality,
    get_hourly_forecast,
    normalize_environment_data,
    get_environment_for_points,
    get_hourly_environment_timeseries,
)

__all__ = [
    "get_current_weather",
    "get_current_air_quality",
    "get_hourly_forecast",
    "normalize_environment_data",
    "get_environment_for_points",
    "get_hourly_environment_timeseries",
]
