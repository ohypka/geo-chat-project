import requests
from typing import Dict, Any
from datetime import datetime
from urllib.parse import quote

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
NFZ_BASE_URL = "https://api.nfz.gov.pl/app-itl-api/queues"

HEADERS = {"User-Agent": "NFZDoctorFinder/1.1"}

PROVINCE_CODES = {
    "DOLNOŚLĄSKIE": "01",
    "KUJAWSKO-POMORSKIE": "02",
    "LUBELSKIE": "03",
    "LUBUSKIE": "04",
    "ŁÓDZKIE": "05",
    "MAŁOPOLSKIE": "06",
    "MAZOWIECKIE": "07",
    "OPOLSKIE": "08",
    "PODKARPACKIE": "09",
    "PODLASKIE": "10",
    "POMORSKIE": "11",
    "ŚLĄSKIE": "12",
    "ŚWIĘTOKRZYSKIE": "13",
    "WARMIŃSKO-MAZURSKIE": "14",
    "WIELKOPOLSKIE": "15",
    "ZACHODNIOPOMORSKIE": "16",
}


def get_location_from_coords(lat: float, lon: float) -> Dict[str, str]:
    """Reverse geocoding – zamiana współrzędnych na miasto i województwo"""
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1,
        "accept-language": "pl",
    }
    resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
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

    return {"city": city.upper(), "province": province, "province_code": province_code}


def get_doctor_availability(lat: float, lon: float, service_name: str, urgent: bool = False) -> Dict[str, Any]:
    """Pobiera 10 najbliższych terminów leczenia z NFZ."""
    location = get_location_from_coords(lat, lon)
    case = 1 if urgent else 2

    url = (
        f"{NFZ_BASE_URL}?case={case}"
        f"&province={location['province_code']}"
        f"&locality={quote(location['city'].capitalize())}"
        f"&benefit={quote(service_name)}"
        f"&format=json"
    )

    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for item in data.get("data", [])[:10]:
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
            "lat": lat,
            "lon": lon,
            "city": location["city"],
            "province": location["province"],
            "province_code": location["province_code"],
            "timestamp": datetime.utcnow().isoformat(),
        },
        "results": results,
    }
