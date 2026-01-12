import requests
from typing import Optional, Tuple


def get_coordinates(city: str, street: str = None) -> Optional[Tuple[float, float]]:
    """
    Zamienia adres (Miasto + opcjonalna Ulica) na współrzędne (lat, lon).
    """
    base_url = "https://nominatim.openstreetmap.org/search"

    # Budujemy zapytanie "Ulica, Miasto" lub samo "Miasto"
    q = f"{street}, {city}" if street else city

    params = {
        "q": q,
        "format": "json",
        "limit": 1,
        "countrycodes": "pl"  # Ograniczamy do Polski
    }

    headers = {
        "User-Agent": "GeoChatProject/1.0"
    }

    try:
        resp = requests.get(base_url, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        if data and len(data) > 0:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon

    except Exception as e:
        print(f"Błąd geocodingu dla '{q}': {e}")

    return None


# Funkcja do liczenia odległości (Haversine) - przyda się do sortowania wyników
from math import radians, cos, sin, asin, sqrt


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Zwraca odległość w metrach między dwoma punktami.
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Promień ziemi w km
    return c * r * 1000  # Wynik w metrach