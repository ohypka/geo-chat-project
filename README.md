# Environment Module (Weather and Air Quality)
Module for collecting and standardizing environmental data such as temperature, humidity, pressure, air quality (PM2.5, PM10, AQI) and hourly forecasts.  
Uses OpenWeatherMap API and provides unified JSON output for map visualization.

## Features
- Fetch current weather and air quality data from OpenWeather API
- Normalize data for one or multiple geographic points
- Batch requests support (multiple points)
- Hourly forecast for the next hours
- FastAPI backend with endpoints for integration
- Standardized JSON format

## Structure
src/
- weather_environment.py - data fetching and normalization
- main.py - example usage and local tests
- server.py - FastAPI backend with API endpoints
- __init__.py - package marker

## Endpoints
/environment - GET - current weather and air quality  
/environment/batch - POST - data for multiple points  
/environment/hourly - GET - hourly forecast

## Example JSON
```json
{
  "category": "environment",
  "source": "openweather",
  "location": {
    "lat": 52.2297,
    "lon": 21.0122,
    "name": "Warsaw"
  },
  "timestamp": "2025-11-06T09:22:55.155884+00:00",
  "metrics": {
    "temperature": 10.18,
    "humidity": 77,
    "pressure": 1021,
    "rain_1h": 0.0,
    "snow_1h": 0.0,
    "pm25": 12.56,
    "pm10": 16.61,
    "aqi": 2
  }
}
```

## How to run

### 1. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add .env file with
```bash
OPENWEATHER_API_KEY=your_api_key
```

### 4. Run server
```bash
uvicorn src.server:app --reload
```

### 5. Open documentation
```bash
http://127.0.0.1:8000/docs
```


## Dependencies
- Python 3.10+
- requests
- python-dotenv
- fastapi
- uvicorn



# Doctors Availability Module  
Module for fetching and standardizing medical queue data from the **Narodowy Fundusz Zdrowia (NFZ) API**.  
Allows you to check the **nearest available appointment dates** for a given specialization (e.g. *kardiolog*) and location (based on GPS coordinates).

---

## Features
- Reverse geocoding using **OpenStreetMap Nominatim API**
- Fetch real data from **NFZ API (`/queues`)**
- Supports **urgent (pilny)** and **stable (stabilny)** cases  
- Automatic detection of **city** and **province** from coordinates
- Returns standardized **JSON output** for easy integration
- Includes **FastAPI backend** with `/doctors` endpoint
- Supports direct use as a Python module or REST API

---

## Structure
src/doctors/
- doctors_availability.py
- main_doctors.py
- server_doctors.py

## Endpoints
/doctors - GET - list of up to 10 nearest facilities for given specialization and location

## Example JSON
```json
{
  "query": {
    "service": "kardiolog",
    "urgent": true,
    "lat": 52.2297,
    "lon": 21.0122,
    "city": "WARSZAWA",
    "province": "MAZOWIECKIE",
    "province_code": "07",
    "timestamp": "2025-11-11T11:54:28.583380"
  },
  "results": [
    {
      "provider": "UNIWERSYTECKIE CENTRUM KLINICZNE WARSZAWSKIEGO UNIWERSYTETU MEDYCZNEGO",
      "place": "ODDZIAŁ KLINICZNY KARDIOLOGII DZIECIĘCEJ I PEDIATRII",
      "address": "ŻWIRKI I WIGURY 63A",
      "locality": "WARSZAWA OCHOTA",
      "phone": "+48 22 317 95 88",
      "service": "KARDIOLOGICZNE ZABIEGI INTERWENCYJNE U DZIECI DO LAT 18, W TYM PRZEZSKÓRNE ZAMYKANIE PRZECIEKÓW Z UŻYCIEM ZESTAWÓW ZAMYKAJĄCYCH",
      "waiting_days": 0,
      "awaiting": 0,
      "queue_date": "2025-11-07",
      "date_updated": "2025-10"
    },
    {
      "provider": "SAMODZIELNY PUBLICZNY SZPITAL KLINICZNY IM. PROF. WITOLDA ORŁOWSKIEGO CENTRUM MEDYCZNEGO KSZTAŁCENIA PODYPLOMOWEGO W WARSZAWIE",
      "place": "PODODDZIAŁ KARDIOLOGII",
      "address": "CZERNIAKOWSKA 231",
      "locality": "WARSZAWA ŚRÓDMIEŚCIE",
      "phone": "+48 22 584 11 47",
      "service": "ODDZIAŁ KARDIOLOGICZNY",
      "waiting_days": 0,
      "awaiting": 0,
      "queue_date": "2025-11-14",
      "date_updated": "2025-10"
    },
    {
      "provider": "PAŃSTWOWY INSTYTUT MEDYCZNY MINISTERSTWA SPRAW WEWNĘTRZNYCH I ADMINISTRACJI",
      "place": "PORADNIA STRUKTURALNYCH CHORÓB SERCA",
      "address": "WOŁOSKA 137",
      "locality": "WARSZAWA MOKOTÓW",
      "phone": "+48 477 221 815",
      "service": "ŚWIADCZENIA Z ZAKRESU KARDIOLOGII",
      "waiting_days": 7,
      "awaiting": 3,
      "queue_date": "2025-11-14",
      "date_updated": "2025-10"
    },
    {
      "provider": "PAŃSTWOWY INSTYTUT MEDYCZNY MINISTERSTWA SPRAW WEWNĘTRZNYCH I ADMINISTRACJI",
      "place": "PORADNIA RZADKICH CHORÓB UKŁADU SERCOWO-NACZYNIOWEGO",
      "address": "WOŁOSKA 137",
      "locality": "WARSZAWA MOKOTÓW",
      "phone": "+48 477 221 815",
      "service": "ŚWIADCZENIA Z ZAKRESU KARDIOLOGII",
      "waiting_days": 63,
      "awaiting": 3,
      "queue_date": "2025-11-14",
      "date_updated": "2025-10"
    },
    {
      "provider": "DARIUSZ BOJANOWSKI ORTOPEDA",
      "place": "PORADNIA KARDIOLOGICZNA",
      "address": "PŁOCHOCIŃSKA 111",
      "locality": "WARSZAWA BIAŁOŁĘKA",
      "phone": "+48 22 452 40 55",
      "service": "ŚWIADCZENIA Z ZAKRESU KARDIOLOGII",
      "waiting_days": 23,
      "awaiting": 35,
      "queue_date": "2025-11-17",
      "date_updated": "2025-10"
    },
    {
      "provider": "NIEPUBLICZNY ZAKŁAD OPIEKI  ZDROWOTNEJ \"SANA\" SP. Z O.O. SP.K",
      "place": "GABINET KARDIOLOGICZNY",
      "address": "STEFANA BATOREGO 31 A",
      "locality": "WARSZAWA MOKOTÓW",
      "phone": "+48 22 825 14 70",
      "service": "ŚWIADCZENIA Z ZAKRESU KARDIOLOGII",
      "waiting_days": 14,
      "awaiting": 8,
      "queue_date": "2025-11-18",
      "date_updated": "2025-10"
    },
    {
      "provider": "SAMODZIELNY ZESPÓŁ PUBLICZNYCH ZAKŁADÓW LECZNICTWA OTWARTEGO WARSZAWA-MOKOTÓW",
      "place": "AOS-KARD-JAD",
      "address": "JADŹWINGÓW 9",
      "locality": "WARSZAWA MOKOTÓW",
      "phone": "22-699-60-99",
      "service": "ŚWIADCZENIA Z ZAKRESU KARDIOLOGII",
      "waiting_days": 12,
      "awaiting": 99,
      "queue_date": "2025-11-24",
      "date_updated": "2025-10"
    },
    {
      "provider": "GRUPA MEDYCZNA VERTIMED SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ",
      "place": "PORADNIA KARDIOLOGICZNA",
      "address": "BRONIKOWSKIEGO 55",
      "locality": "WARSZAWA",
      "phone": "+48 22 405 63 75",
      "service": "ŚWIADCZENIA Z ZAKRESU KARDIOLOGII",
      "waiting_days": 30,
      "awaiting": 24,
      "queue_date": "2025-11-24",
      "date_updated": "2025-10"
    },
    {
      "provider": "SAMODZIELNY  ZESPÓŁ PUBLICZNYCH  ZAKŁADÓW  LECZNICTWA OTWARTEGO WARSZAWA WESOŁA",
      "place": "GABINET KARDIOLOGII",
      "address": "JANA KILIŃSKIEGO 48",
      "locality": "WARSZAWA WESOŁA",
      "phone": "459 595 559",
      "service": "ŚWIADCZENIA Z ZAKRESU KARDIOLOGII",
      "waiting_days": 41,
      "awaiting": 25,
      "queue_date": "2025-11-24",
      "date_updated": "2025-10"
    },
    {
      "provider": "SZPITAL BIELAŃSKI IM.KS.JERZEGO POPIEŁUSZKI SAMODZIELNY PUBLICZNY ZAKŁAD OPIEKI ZDROWOTNEJ",
      "place": "SZPITAL BIELAŃSKI SPZOZ PRZYCHODNIA PRZYSZPITALNA PORADNIA KARDIOLOGICZNA",
      "address": "CEGŁOWSKA 80",
      "locality": "WARSZAWA BIELANY",
      "phone": "022-56-90-470, 196,382",
      "service": "ŚWIADCZENIA Z ZAKRESU KARDIOLOGII",
      "waiting_days": 41,
      "awaiting": 49,
      "queue_date": "2025-11-25",
      "date_updated": "2025-10"
    }
  ]
}
```
## How to run

### 1. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run server
```bash
uvicorn src.server:app --reload
```

### 4. Open documentation
```bash
http://127.0.0.1:8000/docs
```


## Dependencies
- Python 3.10+
- requests
- python-dotenv
- fastapi
- uvicorn

