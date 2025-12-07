"""
Weather and air quality data fetching and normalization.

This module provides functions to fetch weather and air quality data
from OpenWeatherMap API and normalize it to a unified format.
"""
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

import requests
from dotenv import load_dotenv

# Load environment variables (optional - can be configured via function parameters)
load_dotenv()

BASE_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
AIR_POLLUTION_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"  # 5-day / 3-hour forecast


def get_current_weather(
    lat: float,
    lon: float,
    api_key: Optional[str] = None,
    units: str = "metric",
    lang: str = "en",
) -> dict:
    """
    Fetch current weather data from OpenWeather.
    
    Args:
        lat: Latitude
        lon: Longitude
        api_key: OpenWeatherMap API key. If None, uses OPENWEATHER_API_KEY env var.
        units: Units for temperature (metric, imperial, kelvin)
        lang: Language for weather descriptions
        
    Returns:
        Dictionary with weather data from OpenWeather API
        
    Raises:
        RuntimeError: If API request fails or API key is missing
    """
    api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENWEATHER_API_KEY. Provide via parameter or environment variable.")
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": units,
        "lang": lang,
    }
    resp = requests.get(BASE_WEATHER_URL, params=params, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Weather request failed: {resp.status_code} {resp.text}"
        )
    return resp.json()


def get_current_air_quality(
    lat: float,
    lon: float,
    api_key: Optional[str] = None,
) -> dict:
    """
    Fetch current air quality data from OpenWeather.
    
    Args:
        lat: Latitude
        lon: Longitude
        api_key: OpenWeatherMap API key. If None, uses OPENWEATHER_API_KEY env var.
        
    Returns:
        Dictionary with air quality data from OpenWeather API
        
    Raises:
        RuntimeError: If API request fails or API key is missing
    """
    api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENWEATHER_API_KEY. Provide via parameter or environment variable.")
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
    }
    resp = requests.get(AIR_POLLUTION_URL, params=params, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Air quality request failed: {resp.status_code} {resp.text}"
        )
    return resp.json()


def get_hourly_forecast(
    lat: float,
    lon: float,
    api_key: Optional[str] = None,
    units: str = "metric",
    lang: str = "en",
) -> dict:
    """
    Fetch weather forecast using OpenWeather 5-day / 3-hour forecast API.
    
    Args:
        lat: Latitude
        lon: Longitude
        api_key: OpenWeatherMap API key. If None, uses OPENWEATHER_API_KEY env var.
        units: Units for temperature (metric, imperial, kelvin)
        lang: Language for weather descriptions
        
    Returns:
        Dictionary with forecast data from OpenWeather API
        
    Raises:
        RuntimeError: If API request fails or API key is missing
    """
    api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENWEATHER_API_KEY. Provide via parameter or environment variable.")
    
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": units,
        "lang": lang,
    }
    resp = requests.get(FORECAST_URL, params=params, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Forecast request failed: {resp.status_code} {resp.text}"
        )
    return resp.json()


def get_hourly_environment_timeseries(
    lat: float,
    lon: float,
    hours: int = 24,
    name: Optional[str] = None,
    api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Return a list of environment datapoints for the next `hours` hours.

    Uses the 5-day / 3-hour forecast endpoint:
    - each entry is a 3-hour step
    - trim the list to approximately the requested number of hours

    Each element contains:
    - timestamp
    - location
    - metrics (temperature, humidity, pressure)
    
    Args:
        lat: Latitude
        lon: Longitude
        hours: Number of hours to forecast (default: 24)
        name: Optional location name
        api_key: OpenWeatherMap API key. If None, uses OPENWEATHER_API_KEY env var.
        
    Returns:
        List of dictionaries with normalized environment data
    """
    forecast = get_hourly_forecast(lat, lon, api_key=api_key)

    # "list" contains 3-hourly forecast entries
    forecast_list = forecast.get("list", [])

    # (1 entry = 3 hours)
    if hours <= 0:
        hours = 1
    max_entries = max(1, hours // 3 + (1 if hours % 3 != 0 else 0))
    forecast_list = forecast_list[:max_entries]

    results: List[Dict[str, Any]] = []

    for entry in forecast_list:
        dt_unix = entry.get("dt")
        main = entry.get("main", {})

        temp = main.get("temp")
        humidity = main.get("humidity")
        pressure = main.get("pressure")

        # Convert to ISO timestamp in UTC
        ts = datetime.fromtimestamp(dt_unix, tz=timezone.utc).isoformat()

        results.append(
            {
                "category": "environment",
                "source": "openweather",
                "location": {
                    "lat": lat,
                    "lon": lon,
                    "name": name,
                },
                "timestamp": ts,
                "metrics": {
                    "temperature": temp,
                    "humidity": humidity,
                    "pressure": pressure,
                },
            }
        )

    return results


def normalize_environment_data(
    lat: float,
    lon: float,
    name: Optional[str] = None,
    api_key: Optional[str] = None,
) -> dict:
    """
    Combine current weather and air quality data into a unified format
    ready for visualization on the map.
    
    Args:
        lat: Latitude
        lon: Longitude
        name: Optional location name
        api_key: OpenWeatherMap API key. If None, uses OPENWEATHER_API_KEY env var.
        
    Returns:
        Dictionary with normalized environment data including:
        - category: "environment"
        - source: "openweather"
        - location: dict with lat, lon, name
        - timestamp: ISO format timestamp
        - metrics: dict with temperature, humidity, pressure, rain_1h, snow_1h, pm25, pm10, aqi
        - raw: dict with raw API responses
    """
    weather = get_current_weather(lat, lon, api_key=api_key)
    air = get_current_air_quality(lat, lon, api_key=api_key)

    ts = datetime.now(timezone.utc).isoformat()

    main = weather.get("main", {})
    rain = weather.get("rain", {})
    snow = weather.get("snow", {})

    air_list = air.get("list", [{}])
    air_item = air_list[0] if air_list else {}
    components = air_item.get("components", {})
    aqi = air_item.get("main", {}).get("aqi")

    return {
        "category": "environment",  # weather + air quality
        "source": "openweather",
        "location": {
            "lat": lat,
            "lon": lon,
            "name": name or weather.get("name"),
        },
        "timestamp": ts,
        "metrics": {
            "temperature": main.get("temp"),       # °C
            "humidity": main.get("humidity"),      # %
            "pressure": main.get("pressure"),      # hPa
            "rain_1h": rain.get("1h", 0.0),        # mm in last hour
            "snow_1h": snow.get("1h", 0.0),        # mm in last hour
            "pm25": components.get("pm2_5"),       # µg/m³
            "pm10": components.get("pm10"),        # µg/m³
            "aqi": aqi,                            # 1 (good) – 5 (very bad)
        },
        "raw": {
            "weather": weather,
            "air": air,
        },
    }


def get_environment_for_points(
    points: List[Dict[str, Any]],
    api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch environment data (weather + air quality) for multiple points.

    Input example:
    [
        {"lat": 52.2297, "lon": 21.0122, "name": "Warsaw"},
        {"lat": 50.0647, "lon": 19.9450, "name": "Krakow"},
    ]

    Output: list of normalized dictionaries (same format as normalize_environment_data).
    
    Args:
        points: List of dictionaries with 'lat', 'lon', and optionally 'name'
        api_key: OpenWeatherMap API key. If None, uses OPENWEATHER_API_KEY env var.
        
    Returns:
        List of normalized environment data dictionaries. If an error occurs for a point,
        the result will include an 'error' field instead of 'metrics'.
    """
    results: List[Dict[str, Any]] = []

    for point in points:
        lat = point["lat"]
        lon = point["lon"]
        name = point.get("name")
        try:
            data = normalize_environment_data(lat, lon, name=name, api_key=api_key)
            results.append(data)
        except Exception as e:
            results.append(
                {
                    "category": "environment",
                    "source": "openweather",
                    "location": {
                        "lat": lat,
                        "lon": lon,
                        "name": name,
                    },
                    "error": str(e),
                }
            )

    return results
