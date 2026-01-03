from pprint import pprint
from typing import List, Dict, Any

from .traffic import normalize_traffic_data, get_traffic_for_points


def main():
    lat = 52.2297
    lon = 21.0122

    print("Single point: current traffic-Warsaw")
    single = normalize_traffic_data(lat, lon, name="Warsaw")
    pprint(single)

    print("\nMultiple points: batch traffic data")
    points: List[Dict[str, Any]] = [
        {"lat": 52.2297, "lon": 21.0122, "name": "Warsaw"},
        {"lat": 50.0647, "lon": 19.9450, "name": "Krakow"},
        {"lat": 51.1079, "lon": 17.0385, "name": "Wroclaw"},
        {"lat": 53.1325, "lon": 23.1688, "name": "Bialystok"},
    ]
    batch = get_traffic_for_points(points)
    pprint(batch)


if __name__ == "__main__":
    main()
