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
def get_environment(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    name: Optional[str] = Query(None, description="Optional location name"),
):
    """
    Get current environment data (weather + air quality) for a single point.
    """
    try:
        data = normalize_environment_data(lat, lon, name=name)
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


@app.post("/environment/batch")
def get_environment_batch(points: List[Point]):
    """
    Get environment data for multiple points at once.

    Request body: JSON array of {lat, lon, name?}
    """
    pts: List[Dict[str, Any]] = [p.dict() for p in points]
    data = get_environment_for_points(pts)
    return JSONResponse(content=data)


@app.get("/environment/hourly")
def get_environment_hourly(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    hours: int = Query(24, ge=1, le=120, description="Number of hours forward (approx.)"),
    name: Optional[str] = Query(None, description="Optional location name"),
):
    """
    Get environment timeseries for the next `hours` hours (approximate).

    Uses 3-hour forecast steps from OpenWeather.
    """
    try:
        data = get_hourly_environment_timeseries(lat, lon, hours=hours, name=name)
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


# Konfiguracja API Google (Darmowe w Free Tier)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("UWAGA: Brak klucza GOOGLE_API_KEY. Czat nie będzie działał.")

# Providerzy do danych
weather_provider = create_provider("weather", api_key=os.getenv("OPENWEATHER_API_KEY"))
doctors_provider = create_provider("doctors")


# Definicje narzędzi dla AI
def get_weather(city: str): pass

def get_doctors(specialization: str, urgent: bool = False): pass

def get_bikes(city: str = "Wroclaw"): pass

def get_traffic(location: str = "Wroclaw"): pass


# Inicjalizacja modelu
tools = [get_weather, get_doctors, get_bikes, get_traffic]
model = genai.GenerativeModel('gemini-flash-latest', tools=tools) if GOOGLE_API_KEY else None


class ChatRequest(BaseModel):
    message: str
    lat: float = 52.2297
    lon: float = 21.0122


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint obsługujący czat z AI sterujący mapą.
    """
    if not model:
        raise HTTPException(status_code=500, detail="Brak konfiguracji AI (klucza Google).")

    print(f"Pytanie: {request.message}")

    # Rozpocznij sesję czatu
    chat = model.start_chat(enable_automatic_function_calling=False)

    system_instruction = (
        "Jesteś asystentem mapy Geo Chat. "
        "Masz narzędzia: pogoda, lekarze, rowery, ruch drogowy. "
        "UŻYJ ich, gdy użytkownik pyta o dane. "
        "Odpowiadaj krótko i po polsku."
    )

    try:
        # Wysyłamy zapytanie do AI
        response = chat.send_message(f"{system_instruction}\nUżytkownik: {request.message}")

        response_text = ""
        map_data = None
        layer_type = None

        # Sprawdzamy, czy AI chce użyć narzędzia (Function Calling)
        if response.parts and response.parts[0].function_call:
            fc = response.parts[0].function_call
            fn_name = fc.name
            args = fc.args

            print(f"AI wybrało narzędzie: {fn_name}")

            if fn_name == "get_weather":
                city = args.get("city", "Warsaw")
                loc = Location(lat=request.lat, lon=request.lon, name=city)
                data = weather_provider.get_data(loc)
                response_text = f"Pogoda w {city}: {data.metrics.get('temperature')}°C."
                map_data = data.dict()
                layer_type = "weather"

            elif fn_name == "get_doctors":
                spec = args.get("specialization")
                urgent = args.get("urgent", False)
                loc = Location(lat=request.lat, lon=request.lon)
                data = doctors_provider.get_data(loc, service_name=spec, urgent=urgent)
                count = data.metrics.get('facilities_count', 0)
                response_text = f"Znaleziono {count} placówek ({spec})."
                map_data = data.dict()
                layer_type = "doctors"

            elif fn_name == "get_bikes":
                raw_data = normalize_nextbike_data()
                count = len(raw_data) if raw_data else 0
                response_text = f"Pobrałem dane rowerowe. Liczba stacji: {count}."
                map_data = {"type": "FeatureCollection", "features": raw_data}
                layer_type = "bikes"

            elif fn_name == "get_traffic":
                raw_data = get_traffic_data()
                response_text = "Pobrałem dane o natężeniu ruchu."
                map_data = {"type": "FeatureCollection", "features": raw_data}
                layer_type = "traffic"

        else:
            # Dopiero jeśli NIE MA funkcji, czytamy zwykły tekst
            response_text = response.text

        return {
            "response": response_text,
            "mapData": map_data,
            "layerType": layer_type
        }

    except Exception as e:
        print(f"Błąd: {e}")
        raise HTTPException(status_code=500, detail=str(e))