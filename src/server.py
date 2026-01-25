import os
import traceback
import re
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# --- IMPORTY google-genai ---
from google import genai
from google.genai import types

from geo_chat import create_provider, Location
from src.utils.geocoding import get_coordinates
from geo_chat.providers import bikes, traffic

try:
    from .weather_environment import normalize_environment_data
except ImportError:
    normalize_environment_data = None

load_dotenv()

app = FastAPI(title="Geo Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

# --- KONFIGURACJA MODELU NA SZTYWNO ---
TARGET_MODEL = "gemini-2.5-flash-lite"

# --- PROVIDERY ---
weather_provider = create_provider("weather", api_key=os.getenv("OPENWEATHER_API_KEY"))
doctors_provider = create_provider("doctors")
bikes_provider = create_provider("bikes")
traffic_provider = create_provider("traffic", api_key=os.getenv("TOMTOM_API_KEY"))


# --- NARZĘDZIA ---
def get_weather(city: str): pass


def get_doctors(specialization: str, city: str, street: str = None, limit: int = 5): pass


def get_bikes(city: str, location_query: str = None): pass


def get_traffic(city: str, street: str): pass


tools_list = [get_weather, get_doctors, get_bikes, get_traffic]

SYSTEM_INSTRUCTION = (
    "Jesteś pomocnym asystentem medycznym i geograficznym Geo Chat. "
    "1. Gdy otrzymasz dane z narzędzi (np. o lekarzach), NIE wypisuj ich suchą listą, opisz je dokładnie uzytkownikowi"
    "2. Przeanalizuj je i napisz użytkownikowi rekomendację pełnym zdaniem. "
    "3. Wspomnij o czasie oczekiwania i lokalizacji (np. 'Najszybciej dostaniesz się do...'). "
    "4. Mów po polsku, bądź uprzejmy i konkretny."
    "5. Jeśli użytkownik szuka lekarza, roweru, pogody lub informacji o ruchu, NIE POTWIERDZAJ jego słów (np. nie pisz 'Rozumiem, szukasz lekarza'). ZAMIAST TEGO od razu użyj odpowiedniego narzędzia."
    "6. Jeśli masz dostęp do lokalizacji użytkownika lub została ona podana wcześniej, nie pytaj o nią ponownie – po prostu wykonaj wyszukiwanie. "
    "7. Gdy używasz narzędzia (lekarz, rower, pogoda), ZAWSZE czekaj na wynik"
    "8. NIGDY NIE WYMYSLAJ DANYCH, zawsze uzywaj narzedzi aby zdobyc odpowiedz. "
)


class ChatHistoryItem(BaseModel):
    role: str
    parts: List[Dict[str, str]]


class ChatRequest(BaseModel):
    message: str
    history: List[ChatHistoryItem] = []
    lat: float = 52.2297
    lon: float = 21.0122


def clean_street_name(street: str) -> str:
    if not street: return ""
    clean = re.sub(r'(?i)\b(ulica|ul\.|plac|pl\.|aleja|al\.)\s*', '', street)
    clean = clean.split(',')[0]
    return clean.strip()


@app.get("/environment")
def get_environment(lat: float, lon: float):
    if normalize_environment_data:
        return JSONResponse(content=normalize_environment_data(lat, lon))
    return {"error": "Environment module not loaded"}


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not client: raise HTTPException(status_code=500, detail="Brak klucza API Google.")

    print(f"\n--- ZAPYTANIE ({TARGET_MODEL}): {request.message} ---")

    gemini_history = []
    for item in request.history:
        text = item.parts[0].get('text', '') if item.parts else ''
        if text:
            gemini_history.append({
                "role": "model" if item.role == "assistant" else "user",
                "parts": [{"text": text}]
            })

    map_data = None

    try:
        # Tworzenie czatu na konkretnym modelu
        chat = client.chats.create(
            model=TARGET_MODEL,
            config=types.GenerateContentConfig(
                tools=tools_list,
                system_instruction=SYSTEM_INSTRUCTION,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                temperature=0.7,
                # Wyłączamy filtry, żeby nie blokował zapytań o ulice
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                ]
            ),
            history=gemini_history
        )

        response = chat.send_message(request.message)

        # Sprawdzamy czy odpowiedź nie jest pusta
        if not response.candidates:
            print(f"PUSTA ODPOWIEDŹ OD MODELU. Status: {response}")
            return {
                "response": "Model nie zwrócił odpowiedzi (możliwa blokada bezpieczeństwa lub błąd serwera Google).",
                "mapData": None, "layerType": None}

        part = response.candidates[0].content.parts[0]
        response_text = ""

        # Obsługa Function Calling
        if part.function_call:
            fn_call = part.function_call
            fn_name = fn_call.name
            args = fn_call.args

            print(f"AI DECYZJA: {fn_name} {args}")
            ai_summary_data = {}
            manual_fallback_text = ""
            map_data = {"features": []}
            final_lat = float(request.lat)
            final_lon = float(request.lon)

            try:
                target_city = args.get("city", "Warsaw")
                raw_street = args.get("location_query") or args.get("street")

                if raw_street:
                    clean_street = clean_street_name(raw_street)
                    print(f"GEOCODING: '{clean_street}, {target_city}'")
                    coords = get_coordinates(target_city, clean_street)
                    if coords:
                        final_lat, final_lon = float(coords[0]), float(coords[1])
                        print(f"SUKCES: Nowy punkt: {final_lat}, {final_lon}")
                    else:
                        print("OSTRZEŻENIE: Nie znaleziono ulicy.")
                        return {
                            "response": f"Nie znaleziono ulicy '{raw_street}' w {target_city}.",
                            "mapData": None
                        }

                elif target_city and target_city.lower() != "warsaw" and fn_name != "get_bikes":
                    coords = get_coordinates(target_city)
                    if coords: final_lat, final_lon = float(coords[0]), float(coords[1])

                search_loc = Location(lat=final_lat, lon=final_lon, name=target_city)

                if fn_name == "get_weather":
                    ai_summary_data = weather_provider.get_data(search_loc).metrics
                    manual_fallback_text = f"Pogoda dla {target_city} została pobrana."

                    map_data["features"].append({
                        "geometry": {"coordinates": [final_lon, final_lat]},
                        "properties": ai_summary_data
                    })

                    print(map_data["features"])


                elif fn_name == "get_doctors":

                    # Pobranie limitu i danych (zgodnie z Twoim kodem)

                    limit_val = args.get("limit", 5)

                    data = doctors_provider.get_data(

                        search_loc,

                        service_name=args.get("specialization"),

                        limit=limit_val

                    )

                    # 1. Tworzymy listę, żeby AI wiedziało CO znalazło (inaczej będzie tylko liczba)

                    results_for_ai = []

                    results = data.metadata.get("results", [])

                    print(f"Rozpoczynam geokodowanie {len(results)} adresów...")

                    for doc in results:

                        doc_lat, doc_lon = final_lat, final_lon

                        # --- TWOJA SEKCJA CZYSZCZENIA DANYCH (ZACHOWANA) ---

                        raw_city = doc.get('locality') or target_city

                        if raw_city:

                            doc_city = raw_city.split('-')[0].strip()

                        else:

                            doc_city = target_city

                        doc_addr = doc.get('address', '')

                        clean_addr = clean_street_name(doc_addr)

                        if clean_addr:
                            clean_addr = clean_addr.split('/')[0].strip()

                        # ---------------------------------------------------

                        if clean_addr:

                            # Próbujemy geokodować z wyczyszczonym miastem

                            exact_coords = get_coordinates(doc_city, clean_addr)

                            if exact_coords:

                                doc_lat, doc_lon = float(exact_coords[0]), float(exact_coords[1])

                                print(f" -> Namierzono: {clean_addr}, {doc_city} ({doc_lat}, {doc_lon})")

                            else:

                                print(f" -> Nie znaleziono: {clean_addr}, {doc_city}")

                        # 2. Dodajemy te wyczyszczone dane do listy dla AI

                        # Dzięki temu AI przeczyta poprawne nazwy ulic i czas oczekiwania

                        results_for_ai.append({

                            "nazwa": doc.get("provider"),

                            "adres": f"{clean_addr}, {doc_city}",

                            "czas_oczekiwania": f"{doc.get('waiting_days')} dni",

                            "telefon": doc.get("phone")

                        })

                        # Dodajemy punkt do mapy

                        map_data["features"].append({

                            "geometry": {"coordinates": [doc_lon, doc_lat]},

                            "properties": doc

                        })

                    # 3. Przekazujemy PEŁNE dane do AI (liczbę ORAZ listę miejsc)

                    ai_summary_data = {

                        "znaleziono": len(results),

                        "lista_placówek": results_for_ai

                    }

                    manual_fallback_text = f"Pobrałem dane o {len(results)} placówkach."
                elif fn_name == "get_bikes":
                    data = bikes_provider.get_data(search_loc)
                    ai_summary_data = data.metrics
                    st_name = ai_summary_data.get('nearest_station_name', 'Brak')
                    st_dist = ai_summary_data.get('nearest_station_dist_km', 0)
                    st_bikes = ai_summary_data.get('nearest_station_bikes', 0)
                    print(f"WYNIK API: {st_name} ({st_dist}km), Rowerów: {st_bikes}")
                    manual_fallback_text = f"Najbliższa stacja: {st_name} ({st_dist} km). Rowerów: {st_bikes}."

                    for feature in data.raw.get("features", []):
                        coords = feature.get("geometry", {}).get("coordinates", [0, 0])
                        map_data["features"].append({
                            "geometry": {"coordinates": coords},
                            "properties": feature.get("properties", {})
                        })

                elif fn_name == "get_traffic":
                    data = traffic_provider.get_data(search_loc)
                    ai_summary_data = data.metrics
                    manual_fallback_text = "Pobrałem dane o ruchu."

                    for feature in data.raw.get("features", []):
                        map_data["features"].append({
                            "geometry": feature["geometry"],
                            "properties": feature.get("properties", {})
                        })

                    print(map_data["features"])

            except Exception as e:
                print(f"BŁĄD NARZĘDZIA: {e}")
                ai_summary_data = {"error": str(e)}
                manual_fallback_text = "Wystąpił błąd podczas pobierania danych."

            # Odsyłamy wynik funkcji do modelu
            fn_response_part = types.Part.from_function_response(
                name=fn_name,
                response={"result": ai_summary_data}
            )

            final_response = chat.send_message([fn_response_part])

            if final_response.candidates and final_response.candidates[0].content.parts:
                response_text = final_response.candidates[0].content.parts[0].text

            if not response_text:
                print(" AI ZAMILKŁO - Fallback.")
                response_text = manual_fallback_text

            if map_data["features"]:
                map_data["center"] = [final_lat, final_lon]
            else: map_data=None

            return {
                "response": response_text,
                "layerType": fn_name.replace("get_", ""),
                "mapData": map_data
            }

        else:
            response_text = part.text

        return {"response": response_text, "mapData": None, "layerType": None}

    except Exception as e:
        traceback.print_exc()
        return {"response": f"Błąd systemu: {str(e)}", "mapData": None, "layerType": None}