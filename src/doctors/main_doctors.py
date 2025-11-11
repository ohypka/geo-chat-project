from pprint import pprint
from .doctors_availability import get_doctor_availability

def main():
    lat = 52.2297
    lon = 21.0122
    service = "kardiolog"
    urgent = True

    data = get_doctor_availability(lat, lon, service, urgent)
    pprint(data)

if __name__ == "__main__":
    main()
