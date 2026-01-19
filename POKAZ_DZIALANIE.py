"""
PROSTY PRZYKŁAD DZIAŁANIA PROVIDERA LEKARZY

Uruchom: python POKAZ_DZIALANIE.py
"""
from geo_chat import create_provider, Location

print("\n" + "="*60)
print("TEST PROVIDERA LEKARZY")
print("="*60 + "\n")

print("1. Tworzenie providera...")
provider = create_provider("doctors")
print(f"   Utworzono: {type(provider).__name__}\n")

print("2. Lokalizacja: Warszawa")
location = Location(lat=52.2297, lon=21.0122, name="Warszawa")
print(f"   Współrzędne: ({location.lat}, {location.lon})\n")

print("3. Pobieranie danych z NFZ API...")
print("   Specjalizacja: kardiolog")
print("   (czekaj...)\n")

data = provider.get_data(
    location,
    service_name="kardiolog",
    urgent=False
)

print("="*60)
print("WYNIKI:")
print("="*60 + "\n")

if data.error:
    print(f"BŁĄD: {data.error}")
else:
    print("SUKCES!\n")
    print(f"Kategoria: {data.category}")
    print(f"Źródło: {data.source}")
    print(f"Miasto: {data.location.city or 'N/A'}")
    print(f"Województwo: {data.location.province or 'N/A'}")
    print()
    
    count = data.metrics.get('facilities_count', 0)
    print(f"Znaleziono placówek: {count}")
    
    if count > 0:
        print(f"Czas oczekiwania: {data.metrics.get('waiting_days')} dni")
        print(f"Data kolejki: {data.metrics.get('queue_date')}")
        print()
        
        if data.metadata and "results" in data.metadata:
            print("Pierwsze placówki:")
            for i, f in enumerate(data.metadata["results"][:3], 1):
                name = f.get('provider', 'N/A')
                if len(name) > 60:
                    name = name[:57] + "..."
                print(f"\n{i}. {name}")
                print(f"   Czas oczekiwania: {f.get('waiting_days')} dni")
                print(f"   Data: {f.get('queue_date')}")
                print(f"   Adres: {f.get('address', 'N/A')}")

print("\n" + "="*60)
print("TEST ZAKOŃCZONY")
print("="*60 + "\n")
