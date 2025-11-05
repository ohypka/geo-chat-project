from pprint import pprint

from weather_environment import normalize_environment_data


def main():
    # Example: Warsaw
    lat = 52.2297 # szerokosc geograficzna
    lon = 21.0122 # dlugosc geograficzna

    data = normalize_environment_data(lat, lon, name="Warsaw")
    pprint(data)


if __name__ == "__main__":
    main()
