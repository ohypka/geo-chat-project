# nextbike.py
import requests
from typing import List, Dict, Any
from datetime import datetime, timezone

NEXTBIKE_API_URL = "https://api.nextbike.net/maps/nextbike-live.json"
POLAND_COUNTRY_CODE = "pl"
HEADERS = {"User-Agent": "GeoChatNextbikeModule/1.0"}


# --- Słownik ID -> czytelna nazwa (do uzupełnienia/edytowania) ---
# Źródła: publiczne dane historyczne, reverse-engineering integracji, obserwacje.
# Jeśli uzyskasz oficjalny apikey do /api/getBikeTypes.xml, zastąp/zweryfikuj te nazwy.
BIKE_TYPE_MAP: Dict[str, str] = {
    # commonly observed / inferred mappings (examples)
    "71": "Rower standardowy",
    "72": "Rower z fotelikiem dziecięcym",
    "73": "Rower dziecięcy",
    "74": "Tandem",
    "75": "Rower cargo",
    "76": "Rower cargo (typ 2)",
    "77": "Rower trójkołowy",
    "131": "E-bike (elektryczny)",
    "229": "Rower smartlock",
    "230": "E-bike (smartlock)",
    # <- dodaj tutaj kolejne ID, które wylistujesz/zweryfikujesz
}


def get_nextbike_data() -> dict:
    """Pobiera surowe dane o stacjach Nextbike tylko dla Polski (countries=pl)."""
    params = {"countries": POLAND_COUNTRY_CODE}
    try:
        resp = requests.get(NEXTBIKE_API_URL, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        # rzuć jako RuntimeError, żeby wyżej (FastAPI) łatwo to złapać
        raise RuntimeError(f"Nextbike API error: {e}")


def extract_available_bike_types(place: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Ekstrahuje dostępne typy rowerów i ich liczbę na stacji,
    ale zawsze mapuje ID do nazwy przy pomocy BIKE_TYPE_MAP.
    Jeśli ID nie jest znane, zwracamy czytelną domyślną nazwę.
    """
    result: List[Dict[str, Any]] = []
    bike_types = place.get("bike_types")

    if isinstance(bike_types, dict) and bike_types:
        for type_id_str, count in bike_types.items():
            # mapujemy ID na czytelną nazwę
            type_name = BIKE_TYPE_MAP.get(type_id_str, f"Nieznany typ (ID {type_id_str})")
            try:
                available_count = int(count)
            except Exception:
                # defensywnie — jeśli count nie jest liczbą, pomiń lub rzutuj na 0
                available_count = 0

            result.append({
                "type_name": type_name,
                "available_count": available_count
            })

    # Jeśli brak bike_types — zwracamy pustą listę (zgodnie ze spec)
    return result


def normalize_nextbike_data() -> List[Dict[str, Any]]:
    """Normalizuje dane stacji Nextbike do wymaganego formatu JSON."""
    raw = get_nextbike_data()
    results: List[Dict[str, Any]] = []

    ts = datetime.now(timezone.utc).isoformat()
    TRUE_COUNTRY = "Poland"

    for country in raw.get("countries", []):
        system_brand = country.get("name") or "Nextbike Polska"

        for city in country.get("cities", []):
            city_name = city.get("name")

            for place in city.get("places", []):
                # Nie filtrujemy po bike_racks (często null w danych)
                bikes_available = place.get("bikes", 0)
                docks_available = place.get("free_racks", 0)

                results.append({
                    "category": "bikeshare",
                    "source": "nextbike",
                    "location": {
                        "lat": place.get("lat"),
                        "lon": place.get("lng"),
                        "name": place.get("name"),
                        "city": city_name,
                        "country": TRUE_COUNTRY
                    },
                    "timestamp": ts,
                    "metrics": {
                        "bikes_available": bikes_available,
                        "docks_available": docks_available,
                        "rental_key": place.get("number"),
                        "spot_id": place.get("uid"),
                        "available_bike_types": extract_available_bike_types(place),
                        "system_brand": system_brand
                    },
                })

    return results


# --- Pomocniczne: funkcja do zebrania wszystkich unikalnych ID typów rowerów ---
def gather_unique_bike_type_ids() -> List[str]:
    """
    Pobiera live dane i zwraca listę unikalnych ID typów rowerów (jako str).
    Użyteczne do wypełnienia BIKE_TYPE_MAP.
    """
    raw = get_nextbike_data()
    ids = set()
    for country in raw.get("countries", []):
        for city in country.get("cities", []):
            for place in city.get("places", []):
                bt = place.get("bike_types")
                if isinstance(bt, dict):
                    for k in bt.keys():
                        ids.add(str(k))
    return sorted(ids)
