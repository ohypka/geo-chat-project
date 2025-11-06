from pprint import pprint

from .weather_environment import (
    normalize_environment_data,
    get_environment_for_points,
    get_hourly_environment_timeseries,
)


def main():
    # Example location: Warsaw
    lat = 52.2297
    lon = 21.0122

    print("Single point: current environment")
    single = normalize_environment_data(lat, lon, name="Warsaw")
    pprint(single)

    print("\nMultiple points: batch environment data")
    points = [
        {"lat": 52.2297, "lon": 21.0122, "name": "Warsaw"},
        {"lat": 50.0647, "lon": 19.9450, "name": "Krakow"},
    ]
    batch = get_environment_for_points(points)
    pprint(batch)

    print("\nHourly timeseries: next 24 hours")
    hourly = get_hourly_environment_timeseries(lat, lon, hours=24, name="Warsaw")
    pprint(hourly)


if __name__ == "__main__":
    main()
