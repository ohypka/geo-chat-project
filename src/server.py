import os
import json
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

import google.generativeai as genai
from geo_chat import create_provider, Location

from .weather_environment import (
    normalize_environment_data,
    get_environment_for_points,
    get_hourly_environment_timeseries,
)

try:
    from src.bikes.nextbike import normalize_nextbike_data
except ImportError:
    def normalize_nextbike_data(): return []

try:
    from src.traffic.traffic import get_traffic_data
except ImportError:
    def get_traffic_data(): return []

load_dotenv()

app = FastAPI(title="Geo Chat – Environment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class Point(BaseModel):
    lat: float
    lon: float
    name: Optional[str] = None


@app.get("/environment")
def get_environment(lat: float, lon: float, name: Optional[str] = None):
    return JSONResponse(content=normalize_environment_data(lat, lon, name=name))


# --- KONFIGURACJA AI ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

weather_provider = create_provider("weather", api_key=os.getenv("OPENWEATHER_API_KEY"))
doctors_provider = create_provider("doctors")


# --- ZAAWANSOWANE DEFINICJE NARZĘDZI ---
# Tutaj definiujemy parametry, o które AI ma prawo pytać użytkownika.

def get_weather(city: str):
    """Pobiera aktualną pogodę."""
    pass


def get_doctors(specialization: str, scope: str = "city", city: str = None, radius_km: int = 10, urgent: bool = False):
    """
    Szuka lekarzy lub placówek medycznych.

    :param specialization: Specjalizacja (np. kardiolog, okulista, pediatra).
    :param scope: Zakres wyszukiwania. Wartości:
                  - "city" (konkretne miasto),
                  - "near_me" (blisko użytkownika, wymaga promienia),
                  - "poland" (cała Polska, rzadcy specjaliści).
    :param city: Nazwa miasta (wymagane jeśli scope="city").
    :param radius_km: Promień wyszukiwania w kilometrach (używane gdy scope="near_me"). Domyślnie 10.
    :param urgent: Czy szukać pilnych terminów (termin "na już").
    """
    pass


def get_bikes(city: str = "Wroclaw", location_query: str = None, radius_m: int = 500):
    """
    Szuka stacji rowerowych.

    :param city: Miasto (domyślnie Wroclaw).
    :param location_query: Nazwa ulicy, punktu orientacyjnego lub dzielnicy (np. "Grunwaldzka", "Rynek").
    :param radius_m: Promień szukania w metrach (gdy szukamy blisko punktu).
    """
    pass


def get_traffic(city: str, street: str = None):
    """
    Sprawdza natężenie ruchu (korki).

    :param city: Miasto.
    :param street: Konkretna ulica do sprawdzenia (opcjonalne - jeśli brak, sprawdza ogólny stan miasta).
    """
    pass

    # --- PROMPT INŻYNIERIA (Instrukcja Inteligencji) ---
SYSTEM_INSTRUCTION = (
    "Jesteś inteligentnym asystentem Geo Chat. Twoim celem jest precyzyjne dostarczenie danych na mapie. "
    "ZASADY:"
    "1. Jeśli zapytanie jest niejasne (np. 'znajdź lekarza' bez podania miasta lub lokalizacji), "
    "NIE ZGADUJ. Dopytaj użytkownika o szczegóły (np. 'W jakim mieście?', 'W jakim promieniu?'). "
    "2. Jeśli użytkownik poda ulicę przy rowerach/korkach, użyj tego parametru. "
    "3. Gdy otrzymasz wyniki z narzędzi, opisz je użytkownikowi w kontekście jego zapytania. "
    "4. Bądź pomocny i konkretny."
    "5. Pamiętaj kontekst rozmowy"
    )

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

tools = [get_weather, get_doctors, get_bikes, get_traffic]
model = genai.GenerativeModel('gemini-flash-latest', tools=tools) if GOOGLE_API_KEY else None

weather_provider = create_provider("weather", api_key=os.getenv("OPENWEATHER_API_KEY"))
doctors_provider = create_provider("doctors")

# Model z pamięcią systemową
model = genai.GenerativeModel(
    'gemini-flash-latest',
    tools=tools,
    system_instruction=SYSTEM_INSTRUCTION
) if GOOGLE_API_KEY else None

class ChatHistoryItem(BaseModel):
    role: str
    parts: List[Dict[str, str]]
class ChatRequest(BaseModel):
    message: str
    history: List[ChatHistoryItem] = []  # <--- Tutaj wpada historia z Reacta
    lat: float = 52.2297
    lon: float = 21.0122


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Brak klucza API Google.")

    print(f"Pytanie: {request.message} | Historia: {len(request.history)} wiadomości")

    # 1. Konwersja historii z formatu Reacta na format Gemini
    # Gemini wymaga formatu: [{'role': 'user', 'parts': ['text']}, {'role': 'model', 'parts': ['text']}]
    gemini_history = []
    for item in request.history:
        # Ignorujemy puste wiadomości lub błędy, bierzemy tylko tekst
        text_content = item.parts[0].get('text', '') if item.parts else ''
        if text_content:
            gemini_history.append({
                "role": item.role,
                "parts": [text_content]
            })

    # 2. Uruchamiamy czat Z HISTORIĄ
    chat = model.start_chat(history=gemini_history, enable_automatic_function_calling=False)

    try:
        # 3. Wysyłamy nową wiadomość
        response = chat.send_message(request.message)

        response_text = ""
        map_data = None
        layer_type = None

        # 4. Obsługa narzędzi (Function Calling)
        if response.parts and response.parts[0].function_call:
            fc = response.parts[0].function_call
            fn_name = fc.name
            args = fc.args

            print(f" AI uruchamia: {fn_name} {args}")
            ai_summary_data = {}

            # --- LOGIKA FUNKCJI ---
            if fn_name == "get_weather":
                city = args.get("city", "Warsaw")
                try:
                    loc = Location(lat=request.lat, lon=request.lon, name=city)
                    data = weather_provider.get_data(loc)
                    map_data = data.dict()
                    layer_type = "weather"
                    ai_summary_data = data.metrics
                except Exception as e:
                    ai_summary_data = {"error": str(e)}

            elif fn_name == "get_doctors":
                spec = args.get("specialization")
                target_city = args.get("city")
                scope = args.get("scope", "city")
                try:
                    search_loc = Location(lat=request.lat, lon=request.lon)
                    if target_city: search_loc.name = target_city

                    data = doctors_provider.get_data(search_loc, service_name=spec)
                    count = data.metrics.get('facilities_count', 0)
                    map_data = data.dict()
                    layer_type = "doctors"
                    ai_summary_data = {"found": count, "city": target_city or "current location"}
                except Exception as e:
                    ai_summary_data = {"error": str(e)}

            elif fn_name == "get_bikes":
                target_city = args.get("city", "Wroclaw")
                street = args.get("location_query")
                try:
                    raw_data = normalize_nextbike_data()
                    final_features = raw_data
                    if street:
                        final_features = [s for s in raw_data if
                                          street.lower() in (s.get("properties", {}).get("name", "") or "").lower()]

                    map_data = {"type": "FeatureCollection", "features": final_features}
                    layer_type = "bikes"
                    ai_summary_data = {"total": len(raw_data), "filtered": len(final_features), "street": street}
                except Exception as e:
                    ai_summary_data = {"error": str(e)}

            elif fn_name == "get_traffic":
                try:
                    raw_data = get_traffic_data()
                    map_data = {"type": "FeatureCollection", "features": raw_data}
                    layer_type = "traffic"
                    ai_summary_data = {"status": "ok"}
                except Exception as e:
                    ai_summary_data = {"error": "No traffic data"}

            # 5. Odsyłamy dane do AI, żeby je opisało
            final_response = chat.send_message(
                {
                    "function_response": {
                        "name": fn_name,
                        "response": {"result": ai_summary_data}
                    }
                }
            )
            response_text = final_response.text

        else:
            response_text = response.text

        return {
            "response": response_text,
            "mapData": map_data,
            "layerType": layer_type
        }

    except Exception as e:
        print(f" Error: {e}")
        return {"response": f"Błąd: {str(e)}", "mapData": None, "layerType": None}


@app.get("/environment")
def get_environment(lat: float, lon: float):
    return JSONResponse(content=normalize_environment_data(lat, lon))