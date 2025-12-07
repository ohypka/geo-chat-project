"""
Weather and air quality provider using OpenWeatherMap API.

Example usage:
    from geo_chat.core import create_provider, Location, ProviderConfig
    
    config = ProviderConfig(api_key="your_key")
    provider = create_provider("weather", config=config)
    
    location = Location(lat=52.2297, lon=21.0122, name="Warsaw")
    data = provider.get_data(location)
"""
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

from ..core.base import BaseProvider, ProviderConfig
from ..core.models import DataPoint, Location
from ..core.registry import register_provider

load_dotenv()

BASE_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
AIR_POLLUTION_URL = "https://api.openweathermap.org/data/2.5/air_pollution"


@register_provider(name="weather", category="environment")
class WeatherProvider(BaseProvider):
    """
    Provider for weather and air quality data from OpenWeatherMap.
    
    Configuration:
        api_key: OpenWeatherMap API key (required)
        units: Temperature units (default: "metric")
        lang: Language for descriptions (default: "en")
    """
    
    def __init__(self, config: Optional[ProviderConfig] = None):
        super().__init__(config)
        self.category = "environment"
        self.name = "openweather"
        
        self.api_key = self.config.api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key is required. Set OPENWEATHER_API_KEY env var or pass via config.")
    
    def fetch(self, location: Location, **options) -> Dict[str, Any]:
        """Fetch weather and air quality data from OpenWeather API."""
        units = options.get("units", self.config.get("units", "metric"))
        lang = options.get("lang", self.config.get("lang", "en"))
        
        weather_params = {
            "lat": location.lat,
            "lon": location.lon,
            "appid": self.api_key,
            "units": units,
            "lang": lang,
        }
        weather_resp = requests.get(BASE_WEATHER_URL, params=weather_params, timeout=self.config.timeout)
        weather_resp.raise_for_status()
        weather_data = weather_resp.json()
        
        air_params = {
            "lat": location.lat,
            "lon": location.lon,
            "appid": self.api_key,
        }
        air_resp = requests.get(AIR_POLLUTION_URL, params=air_params, timeout=self.config.timeout)
        air_resp.raise_for_status()
        air_data = air_resp.json()
        
        return {
            "weather": weather_data,
            "air": air_data,
        }
    
    def normalize(self, raw_data: Dict[str, Any], location: Location) -> DataPoint:
        """Normalize OpenWeather data to standard format."""
        weather = raw_data.get("weather", {})
        air = raw_data.get("air", {})
        
        main = weather.get("main", {})
        rain = weather.get("rain", {})
        snow = weather.get("snow", {})
        
        air_list = air.get("list", [{}])
        air_item = air_list[0] if air_list else {}
        components = air_item.get("components", {})
        aqi = air_item.get("main", {}).get("aqi")
        
        location_name = location.name or weather.get("name")
        
        return DataPoint(
            category=self.category,
            source=self.name,
            location=Location(
                lat=location.lat,
                lon=location.lon,
                name=location_name,
                city=location.city,
                country=location.country,
            ),
            timestamp=datetime.now(timezone.utc).isoformat(),
            metrics={
                "temperature": main.get("temp"),
                "humidity": main.get("humidity"),
                "pressure": main.get("pressure"),
                "rain_1h": rain.get("1h", 0.0),
                "snow_1h": snow.get("1h", 0.0),
                "pm25": components.get("pm2_5"),
                "pm10": components.get("pm10"),
                "aqi": aqi,
            },
            raw=raw_data,
        )
