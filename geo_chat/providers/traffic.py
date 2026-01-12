"""
Traffic provider using TomTom API.
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

# TomTom Traffic Flow Segment API
BASE_TRAFFIC_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"


@register_provider(name="traffic", category="mobility")
class TrafficProvider(BaseProvider):
    """
    Provider for traffic flow data from TomTom.

    Configuration:
        api_key: TomTom API key (required)
    """

    def __init__(self, config: Optional[ProviderConfig] = None):
        super().__init__(config)
        self.category = "mobility"
        self.name = "tomtom"

        self.api_key = self.config.api_key or os.getenv("TOMTOM_API_KEY")
        if not self.api_key:
            raise ValueError("TomTom API key is required. Set TOMTOM_API_KEY env var or pass via config.")

    def fetch(self, location: Location, **options) -> Dict[str, Any]:
        """Fetch traffic flow data for a specific point."""

        params = {
            "key": self.api_key,
            "point": f"{location.lat},{location.lon}",
            "unit": "KMPH",  # Kilometry na godzinę
            "thickness": 10,  # Grubość segmentu
            "zoom": 12  # Poziom przybliżenia dla segmentacji
        }

        resp = requests.get(BASE_TRAFFIC_URL, params=params, timeout=self.config.timeout)
        resp.raise_for_status()

        return resp.json()

    def normalize(self, raw_data: Dict[str, Any], location: Location) -> DataPoint:
        """Normalize TomTom traffic data."""

        flow_data = raw_data.get("flowSegmentData", {})

        current_speed = flow_data.get("currentSpeed", 0)
        free_flow_speed = flow_data.get("freeFlowSpeed", 0)
        confidence = flow_data.get("confidence", 0)
        current_travel_time = flow_data.get("currentTravelTime", 0)

        # Wyliczanie opóźnienia
        congestion_level = "low"
        if free_flow_speed > 0:
            ratio = current_speed / free_flow_speed
            if ratio < 0.5:
                congestion_level = "heavy"
            elif ratio < 0.8:
                congestion_level = "moderate"

        # Tworzenie geometrii segmentu (o ile dostępna) dla mapy
        coordinates = []
        if "coordinates" in flow_data:
            coords_raw = flow_data["coordinates"]["coordinate"]
            for c in coords_raw:
                coordinates.append([c["longitude"], c["latitude"]])

        geo_feature = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates
                },
                "properties": {
                    "congestion": congestion_level,
                    "speed": current_speed
                }
            }]
        } if coordinates else {}

        return DataPoint(
            category=self.category,
            source=self.name,
            location=location,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metrics={
                "current_speed_kmh": current_speed,
                "free_flow_speed_kmh": free_flow_speed,
                "congestion_level": congestion_level,
                "travel_time_sec": current_travel_time,
                "confidence": confidence
            },
            raw=geo_feature if coordinates else raw_data,
        )