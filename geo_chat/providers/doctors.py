"""
Doctors availability provider using NFZ (Polish National Health Fund) API.

Example usage:
    from geo_chat.core import create_provider, Location
    
    provider = create_provider("doctors")
    location = Location(lat=52.2297, lon=21.0122)
    data = provider.get_data(location, service_name="kardiolog", urgent=True)
"""
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import quote

from ..core.base import BaseProvider, ProviderConfig
from ..core.models import DataPoint, Location
from ..core.registry import register_provider

from src.utils.geocoding import calculate_distance

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
NFZ_BASE_URL = "https://api.nfz.gov.pl/app-itl-api/queues"
HEADERS = {"User-Agent": "NFZDoctorFinder/1.1"}

PROVINCE_CODES = {
    "DOLNOŚLĄSKIE": "01", "KUJAWSKO-POMORSKIE": "02", "LUBELSKIE": "03",
    "LUBUSKIE": "04", "ŁÓDZKIE": "05", "MAŁOPOLSKIE": "06",
    "MAZOWIECKIE": "07", "OPOLSKIE": "08", "PODKARPACKIE": "09",
    "PODLASKIE": "10", "POMORSKIE": "11", "ŚLĄSKIE": "12",
    "ŚWIĘTOKRZYSKIE": "13", "WARMIŃSKO-MAZURSKIE": "14",
    "WIELKOPOLSKIE": "15", "ZACHODNIOPOMORSKIE": "16",
}


@register_provider(name="doctors", category="healthcare")
class DoctorsProvider(BaseProvider):
    """
    Provider for doctors availability data from NFZ API.
    
    Options:
        service_name: Medical service name (e.g., "kardiolog") - REQUIRED
        urgent: Whether to search for urgent cases (default: False)
        limit: Maximum number of results (default: 10)
    """
    
    def __init__(self, config: Optional[ProviderConfig] = None):
        super().__init__(config)
        self.category = "healthcare"
        self.name = "nfz"
    
    def _get_location_info(self, location: Location) -> Dict[str, str]:
        """Get city and province from coordinates using reverse geocoding."""
        params = {
            "lat": location.lat,
            "lon": location.lon,
            "format": "json",
            "addressdetails": 1,
            "accept-language": "pl",
        }
        resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=self.config.timeout)
        resp.raise_for_status()
        data = resp.json()
        
        addr = data.get("address", {})
        city = addr.get("city") or addr.get("town") or addr.get("village")
        province = addr.get("state")
        
        if not city or not province:
            raise ValueError("Nie udało się ustalić miasta lub województwa z podanych współrzędnych")
        
        province = province.replace("województwo", "").strip().upper()
        province_code = PROVINCE_CODES.get(province)
        if not province_code:
            raise ValueError(f"Nieznany kod województwa dla: {province}")
        
        return {
            "city": city.upper(),
            "province": province,
            "province_code": province_code,
        }
    
    def fetch(self, location: Location, **options) -> Dict[str, Any]:
        """Fetch doctors availability from NFZ API."""
        service_name = options.get("service_name")
        if not service_name:
            raise ValueError("service_name option is required for doctors provider")
        
        urgent = options.get("urgent", False)
        limit = options.get("limit", 10)
        
        location_info = self._get_location_info(location)
        
        case = 1 if urgent else 2
        url = (
            f"{NFZ_BASE_URL}?case={case}"
            f"&province={location_info['province_code']}"
            f"&locality={quote(location_info['city'].capitalize())}"
            f"&benefit={quote(service_name)}"
            f"&format=json"
        )
        
        resp = requests.get(url, headers=HEADERS, timeout=self.config.timeout)
        resp.raise_for_status()
        data = resp.json()
        
        results = []
        raw_items = data.get("data", [])

        # Sprawdzamy czy mamy punkt odniesienia (np. współrzędne ulicy Reja)
        target_lat = options.get("target_lat")
        target_lon = options.get("target_lon")

        for item in raw_items:
            attr = item.get("attributes", {})
        for item in data.get("data", [])[:limit]:
            attr = item.get("attributes", {})
            stats = attr.get("statistics", {}).get("provider-data", {})
            dates = attr.get("dates", {})

            results.append({
                "provider": attr.get("provider"),
                "place": attr.get("place"),
                "address": attr.get("address"),
                "locality": attr.get("locality"),
                "phone": attr.get("phone"),
                "service": attr.get("benefit"),
                "waiting_days": stats.get("average-period"),
                "awaiting": stats.get("awaiting"),
                "queue_date": dates.get("date"),
                "date_updated": stats.get("update"),
            })
        
        return {
            "query": {
                "service": service_name,
                "urgent": urgent,
                "lat": location.lat,
                "lon": location.lon,
                "city": location_info["city"],
                "province": location_info["province"],
                "province_code": location_info["province_code"],
                "timestamp": datetime.utcnow().isoformat(),
            },
            "results": results,
        }
    
    def normalize(self, raw_data: Dict[str, Any], location: Location) -> DataPoint:
        """Normalize NFZ data to standard format."""
        query = raw_data.get("query", {})
        results = raw_data.get("results", [])
        
        if results:
            first_result = results[0]
            metrics = {
                "facilities_count": len(results),
                "waiting_days": first_result.get("waiting_days"),
                "awaiting": first_result.get("awaiting"),
                "queue_date": first_result.get("queue_date"),
            }
        else:
            metrics = {
                "facilities_count": 0,
            }
        
        return DataPoint(
            category=self.category,
            source=self.name,
            location=Location(
                lat=location.lat,
                lon=location.lon,
                name=location.name,
                city=query.get("city"),
                province=query.get("province"),
            ),
            timestamp=query.get("timestamp", datetime.utcnow().isoformat()),
            metrics=metrics,
            metadata={
                "service": query.get("service"),
                "urgent": query.get("urgent"),
                "results": results,
            },
            raw=raw_data,
        )
