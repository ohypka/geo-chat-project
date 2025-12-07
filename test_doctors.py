"""
Test providera lekarzy - pokazuje jak działa framework na przykładzie NFZ API.
"""
from geo_chat import create_provider, Location

print("=" * 70)
print("Test Providera Lekarzy (NFZ API)")
print("=" * 70)
print()

print("1. Tworzenie providera...")
try:
    provider = create_provider("doctors")
    print("Provider 'doctors' utworzony pomyślnie")
    print(f"  Typ: {type(provider).__name__}")
    print(f"  Kategoria: {provider.category}")
    print(f"  Źródło: {provider.name}")
except Exception as e:
    print(f"Błąd: {e}")
    exit(1)
print()

print("2. Tworzenie lokalizacji...")
location = Location(
    lat=52.2297,
    lon=21.0122,
    name="Warszawa"
)
print(f"Lokalizacja: {location.name}")
print(f"  Współrzędne: ({location.lat}, {location.lon})")
print()

print("3. Pobieranie danych z NFZ API...")
print("   Specjalizacja: kardiolog")
print("   Typ: stabilny (nie pilny)")
print("   To może chwilę potrwać...")
print()

try:
    data = provider.get_data(
        location,
        service_name="kardiolog",
        urgent=False,  
        limit=5  
    )
    
    print("=" * 70)
    print("WYNIKI")
    print("=" * 70)
    print()

    if data.error:
        print(f"Błąd: {data.error}")
        print()
        print("Możliwe przyczyny:")
        print("- Problem z połączeniem internetowym")
        print("- API NFZ jest niedostępne")
        print("- Nieprawidłowe współrzędne")
    else:
        print("Dane pobrane pomyślnie!")
        print()
        print(f"Kategoria: {data.category}")
        print(f"Źródło: {data.source}")
        print(f"Lokalizacja: {data.location.name or f'{data.location.lat}, {data.location.lon}'}")
        print(f"Miasto: {data.location.city or 'N/A'}")
        print(f"Województwo: {data.location.province or 'N/A'}")
        print(f"Timestamp: {data.timestamp}")
        print()
        
        print("Metryki:")
        facilities_count = data.metrics.get('facilities_count', 0)
        print(f"  Liczba znalezionych placówek: {facilities_count}")
        
        if facilities_count > 0:
            waiting_days = data.metrics.get('waiting_days')
            queue_date = data.metrics.get('queue_date')
            awaiting = data.metrics.get('awaiting')
            
            if waiting_days is not None:
                print(f"  Średni czas oczekiwania: {waiting_days} dni")
            if queue_date:
                print(f"  Najbliższa dostępna data: {queue_date}")
            if awaiting is not None:
                print(f"  Liczba osób w kolejce: {awaiting}")
        print()
        
        if data.metadata and "results" in data.metadata:
            results = data.metadata["results"]
            print(f"Szczegóły placówek ({len(results)} pierwszych):")
            print("-" * 70)
            
            for i, facility in enumerate(results[:5], 1):
                print(f"\n{i}. {facility.get('provider', 'N/A')}")
                print(f"   Miejsce: {facility.get('place', 'N/A')}")
                print(f"   Adres: {facility.get('address', 'N/A')}")
                print(f"   Lokalizacja: {facility.get('locality', 'N/A')}")
                print(f"   Telefon: {facility.get('phone', 'N/A')}")
                print(f"   Czas oczekiwania: {facility.get('waiting_days', 'N/A')} dni")
                print(f"   Osoby w kolejce: {facility.get('awaiting', 'N/A')}")
                print(f"   Data kolejki: {facility.get('queue_date', 'N/A')}")
        
        print()
        print("=" * 70)
        print("Struktura danych (DataPoint):")
        print("=" * 70)
        print(f"  category: {data.category}")
        print(f"  source: {data.source}")
        print(f"  location: {data.location.dict()}")
        print(f"  metrics: {list(data.metrics.keys())}")
        print(f"  metadata keys: {list(data.metadata.keys()) if data.metadata else 'None'}")
        print(f"  has raw data: {data.raw is not None}")
        
except Exception as e:
    print(f"Błąd podczas pobierania danych: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()
print("=" * 70)
print("Test zakończony!")
print("=" * 70)
