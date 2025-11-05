import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not OPENWEATHER_API_KEY:
    raise RuntimeError("Missing OPENWEATHER_API_KEY")

BASE_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
AIR_POLLUTION_URL = "https://api.openweathermap.org/data/2.5/air_pollution"


def get_current_weather(lat: float, lon: float) -> dict:
    """Fetch current weather data from OpenWeather."""
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "en",
    }
    resp = requests.get(BASE_WEATHER_URL, params=params, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Weather request failed: {resp.status_code} {resp.text}"
        )
    return resp.json()


def get_current_air_quality(lat: float, lon: float) -> dict:
    """Fetch current air quality data from OpenWeather."""
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
    }
    resp = requests.get(AIR_POLLUTION_URL, params=params, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Air quality request failed: {resp.status_code} {resp.text}"
        )
    return resp.json()


def normalize_environment_data(lat: float, lon: float, name: str | None = None) -> dict:
    """
    Combine weather and air quality data into a unified format
    ready for visualization on the map.
    """
    weather = get_current_weather(lat, lon)
    air = get_current_air_quality(lat, lon)

    ts = datetime.now(timezone.utc).isoformat()

    main = weather.get("main", {})
    rain = weather.get("rain", {})
    snow = weather.get("snow", {})

    air_list = air.get("list", [{}])
    air_item = air_list[0] if air_list else {}
    components = air_item.get("components", {})
    aqi = air_item.get("main", {}).get("aqi")

    return {
        "category": "environment", # moduł pogoda + smog
        "source": "openweather",
        "location": {
            "lat": lat, # szerokosc geograficzna
            "lon": lon, # dlugosc geograficzna
            "name": name or weather.get("name"),
        },
        "timestamp": ts,
        "metrics": {
            "temperature": main.get("temp"), # temperatura w stopniach Celsjusza
            "humidity": main.get("humidity"), # wilgotnosc w %
            "pressure": main.get("pressure"), # cisnienie w hPa
            "rain_1h": rain.get("1h", 0.0), # opad deszczu z ostatniej godziny (mm, jesli w ogole jest w danych; inaczej 0)
            "snow_1h": snow.get("1h", 0.0), # opad sniegu z ostatniej godziny (mm; domyslnie 0),
            "pm25": components.get("pm2_5"), # stezenie pylu PM2.5 (µg/m³)
            "pm10": components.get("pm10"), # stezenie pylu PM10 (µg/m³),
            "aqi": aqi, # indeks jakosci powietrza 1–5 (1 = very good, 5 = very bad).
        },
        "raw": {
            "weather": weather,
            "air": air,
        },
    }
