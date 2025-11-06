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
