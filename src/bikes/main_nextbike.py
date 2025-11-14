from pprint import pprint

# Import względny – działa, gdy main.py i nextbike.py są w tym samym pakiecie (folderze)
from .nextbike import normalize_nextbike_data


def main():
    """
    Pobiera i wyświetla znormalizowane dane Nextbike dla Polski,
    weryfikując poprawność działania normalizacji.
    """
    print("Pobieranie i normalizacja danych Nextbike dla Polski...")

    try:
        data = normalize_nextbike_data()

        print(f"\nSukces! Pobrano {len(data)} stacji Nextbike.")

        if not data:
            print("Uwaga: Lista stacji jest pusta. Możliwe problemy z API lub internetem.")
            return

        print("\nPrzykładowy element (weryfikacja formatu danych):")
        pprint(data[10])

        # Dodatkowy czytelny podgląd typów rowerów (bez pprint)
        print("\nCzytelne typy rowerów dla przykładowej stacji:")
        sample = data[10]

        for bike_type_info in sample.get("bike_types", []):
            print(f"  • {bike_type_info['type_name']} — {bike_type_info['count']} szt.")

    except Exception as e:
        print(f"\nBłąd podczas pobierania danych: {e}")
        print("Sprawdź połączenie internetowe oraz zależności (pip install -r requirements.txt).")


if __name__ == "__main__":
    main()
