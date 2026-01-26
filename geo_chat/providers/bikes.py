"""
Bikes provider using Nextbike API.
"""
from typing import Dict, Any, Optional
import requests
from datetime import datetime, timezone
from ..core.base import BaseProvider, ProviderConfig
from ..core.models import DataPoint, Location
from ..core.registry import register_provider
from src.utils.geocoding import calculate_distance

NEXTBIKE_API_URL = "https://maps.nextbike.net/maps/nextbike-live.json"

@register_provider(name="bikes", category="mobility")
class BikesProvider(BaseProvider):
    def __init__(self, config: Optional[ProviderConfig] = None):
        super().__init__(config)
        self.category = "mobility"
        self.name = "nextbike"
        self.city_id = self.config.get("city_id", 148)

    def fetch(self, location: Location, **options) -> Dict[str, Any]:
        city_id = options.get("city_id", self.city_id)
        resp = requests.get(NEXTBIKE_API_URL, params={"city": city_id}, timeout=self.config.timeout)
        resp.raise_for_status()
        return resp.json()

    def normalize(self, raw_data: Dict[str, Any], location: Location) -> DataPoint:
        MAX_DISTANCE_KM = 2
        # Pobieramy współrzędne z obiektu location (już po geocodingu)
        user_lat = float(location.lat)
        user_lon = float(location.lon)

        print(f"DEBUG BIKES: Szukam stacji wokół: {user_lat}, {user_lon}")

        stations = []
        try:
            countries = raw_data.get("countries", [])
            if countries:
                for country in countries:
                    for city in country.get("cities", []):
                        stations.extend(city.get("places", []))
        except Exception:
            stations = []

        nearest_station = None
        min_distance = float('inf')
        total_bikes = 0

        features = []
        for station in stations:
            try:
                s_lat = float(station.get("lat"))
                s_lon = float(station.get("lng"))
                bikes_count = int(station.get("bikes", 0))
                total_bikes += bikes_count

                # OBLICZAMY DYSTANS
                # calculate_distance zwraca metry, więc dzielimy przez 1000, żeby mieć km
                dist_km = calculate_distance(user_lat, user_lon, s_lat, s_lon) / 1000.0

                if dist_km > MAX_DISTANCE_KM:
                    continue

                if dist_km < min_distance:
                    min_distance = dist_km
                    nearest_station = {
                        "name": station.get("name"),
                        "distance": dist_km,
                        "bikes": bikes_count,
                        "coords": (s_lat, s_lon)
                    }

                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [s_lon, s_lat]},
                    "properties": {"name": station.get("name"), "bikes": bikes_count}
                })
            except (ValueError, TypeError):
                continue

        metrics = {
            "total_stations": len(stations),
            "total_bikes": total_bikes,
            "data_freshness": "live"
        }

        if nearest_station:
            # Logujemy co znaleźliśmy, żebyś widziała w konsoli
            print(f"DEBUG BIKES: Najbliższa stacja to '{nearest_station['name']}' "
                  f"w odległości {nearest_station['distance']:.2f} km "
                  f"(współrzędne stacji: {nearest_station['coords']})")

            metrics.update({
                "nearest_station_name": nearest_station["name"],
                "nearest_station_dist_km": round(nearest_station["distance"], 2),
                "nearest_station_bikes": nearest_station["bikes"]
            })

        return DataPoint(
            category=self.category,
            source=self.name,
            location=location,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metrics=metrics,
            raw={"type": "FeatureCollection", "features": features},
        )