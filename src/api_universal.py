"""
Universal API server using the geo-chat framework.

This server provides a unified REST API that uses the framework's providers
to fetch and normalize data from various sources.
"""
import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
import os

from geo_chat import create_provider, Location, BatchRequest, ProviderConfig

current_dir = Path.cwd()
env_paths = [
    current_dir / '.env',
    Path(__file__).parent.parent / '.env',
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded .env from: {env_path.absolute()}")
        break
else:
    load_dotenv()
    print("Warning: .env file not found, using default load_dotenv()")

api_key = os.getenv("OPENWEATHER_API_KEY")
if api_key:
    print(f"OPENWEATHER_API_KEY loaded: {api_key[:10]}...")
else:
    print("WARNING: OPENWEATHER_API_KEY not found in environment!")

app = FastAPI(
    title="Geo Chat Universal API",
    description="Unified API for geographic data using the geo-chat framework",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Point(BaseModel):
    """Geographic point."""
    lat: float
    lon: float
    name: Optional[str] = None


class ProviderOptions(BaseModel):
    """Provider-specific options."""
    service_name: Optional[str] = None
    urgent: Optional[bool] = False
    limit: Optional[int] = 10
    units: Optional[str] = "metric"
    lang: Optional[str] = "en"
    hours: Optional[int] = 24


# Provider configurations
WEATHER_CONFIG = ProviderConfig(
    api_key=os.getenv("OPENWEATHER_API_KEY")
)


@app.get("/")
def root():
    """API root endpoint."""
    return {
        "name": "Geo Chat Universal API",
        "version": "1.0.0",
        "description": "Unified API for geographic data using the geo-chat framework",
        "endpoints": {
            "/providers": "List available providers",
            "/providers/{provider_name}": "Get data from a specific provider",
            "/providers/{provider_name}/batch": "Get data for multiple locations",
        }
    }


@app.get("/providers")
def list_providers():
    """List all available providers."""
    return {
        "providers": [
            {
                "name": "weather",
                "category": "environment",
                "description": "Weather and air quality data from OpenWeatherMap",
                "required_options": ["api_key"],
                "optional_options": ["units", "lang"]
            },
            {
                "name": "doctors",
                "category": "healthcare",
                "description": "Doctors availability from NFZ API",
                "required_options": ["service_name"],
                "optional_options": ["urgent", "limit"]
            }
        ]
    }


@app.get("/providers/weather")
def get_weather_data(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    name: Optional[str] = Query(None, description="Location name"),
    units: Optional[str] = Query("metric", description="Temperature units"),
    lang: Optional[str] = Query("en", description="Language"),
):
    """
    Get weather and air quality data using the weather provider.
    
    Uses the geo-chat framework's weather provider.
    """
    try:
        provider = create_provider("weather", config=WEATHER_CONFIG)
        location = Location(lat=lat, lon=lon, name=name)
        
        data = provider.get_data(location, units=units, lang=lang)
        
        if data.error:
            return JSONResponse(
                status_code=500,
                content={"error": data.error, "data": data.dict()}
            )
        
        return JSONResponse(content=data.dict())
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/providers/weather/batch")
def get_weather_batch(points: List[Point]):
    """
    Get weather data for multiple locations.
    
    Uses the geo-chat framework's batch processing.
    """
    try:
        provider = create_provider("weather", config=WEATHER_CONFIG)
        
        locations = [
            Location(lat=p.lat, lon=p.lon, name=p.name)
            for p in points
        ]
        
        batch_request = BatchRequest(points=locations)
        batch_response = provider.get_batch(batch_request)
        
        return JSONResponse(content={
            "results": [r.dict() for r in batch_response.results],
            "errors": batch_response.errors,
            "timestamp": batch_response.timestamp
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/providers/doctors")
def get_doctors_data(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    service_name: str = Query(..., description="Service name (e.g., 'kardiolog')"),
    urgent: Optional[bool] = Query(False, description="Urgent case"),
    limit: Optional[int] = Query(10, description="Maximum number of results"),
):
    """
    Get doctors availability data using the doctors provider.
    
    Uses the geo-chat framework's doctors provider.
    """
    try:
        provider = create_provider("doctors")
        location = Location(lat=lat, lon=lon)
        
        data = provider.get_data(
            location,
            service_name=service_name,
            urgent=urgent,
            limit=limit
        )
        
        if data.error:
            return JSONResponse(
                status_code=500,
                content={"error": data.error, "data": data.dict()}
            )
        
        # Return in format compatible with existing frontend
        # Extract results from metadata
        results = data.metadata.get("results", []) if data.metadata else []
        
        return JSONResponse(content={
            "query": {
                "service": service_name,
                "urgent": urgent,
                "lat": lat,
                "lon": lon,
                "city": data.location.city or "",
                "province": data.location.province or "",
                "province_code": "",  # Would need to extract from metadata
                "timestamp": data.timestamp,
            },
            "results": results,
            "data_point": data.dict()  # Include full framework response
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/providers/doctors/coordinates")
def get_doctors_coordinates(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    service_name: str = Query(..., description="Service name (e.g., 'KARDIOLOG')"),
    urgent: Optional[bool] = Query(False, description="Urgent case"),
    limit: Optional[int] = Query(10, description="Maximum number of results"),
):
    """
    Get doctors availability with coordinates.
    
    Similar to /doctors but returns simplified format with coordinates.
    Uses the same data as /doctors endpoint.
    """
    try:
        provider = create_provider("doctors")
        location = Location(lat=lat, lon=lon)
        
        data = provider.get_data(
            location,
            service_name=service_name,
            urgent=urgent,
            limit=limit
        )
        
        if data.error:
            return JSONResponse(
                status_code=500,
                content={"error": data.error}
            )
        
        results = []
        if data.metadata and isinstance(data.metadata, dict):
            results = data.metadata.get("results", [])
        elif not data.metadata:
            results = []
        
        def get_coordinates_from_address(address: str, locality: str = ""):
            """Geocode address to get lat/lon coordinates."""
            import requests
            if not address:
                return lat, lon
            
            search_query = f"{address}, {locality}" if locality else address
            
            try:
                params = {
                    "q": search_query,
                    "format": "json",
                    "limit": 1
                }
                headers = {"User-Agent": "GeoChat/1.0"}
                resp = requests.get("https://nominatim.openstreetmap.org/search", 
                                   params=params, headers=headers, timeout=5)
                if resp.status_code == 200 and resp.json():
                    data = resp.json()[0]
                    return float(data["lat"]), float(data["lon"])
            except Exception as e:
                pass
            
            return lat, lon
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        coordinates_results = []
        
        def process_result(result):
            """Process a single result and geocode its address."""
            if result is not None and isinstance(result, dict):
                address = result.get("address", "")
                locality = result.get("locality", "")
                doctor_lat, doctor_lon = get_coordinates_from_address(address, locality)
                
                return {
                    "provider": result.get("provider", ""),
                    "place": result.get("place", ""),
                    "address": address,
                    "locality": locality,
                    "phone": result.get("phone", ""),
                    "service": result.get("service", ""),
                    "waiting_days": result.get("waiting_days", 0),
                    "awaiting": result.get("awaiting", 0),
                    "queue_date": result.get("queue_date", ""),
                    "date_updated": result.get("date_updated"),
                    "lat": doctor_lat,
                    "lon": doctor_lon,
                }
            return None
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(process_result, result): result for result in results}
            for future in as_completed(futures):
                processed = future.result()
                if processed:
                    coordinates_results.append(processed)
        
        location = data.location if data.location else None
        city = location.city if location else ""
        province = location.province if location else ""
        
        return JSONResponse(content={
            "query": {
                "service": service_name,
                "urgent": urgent,
                "lat": lat,
                "lon": lon,
                "city": city,
                "province": province,
                "province_code": "",
                "timestamp": data.timestamp if data.timestamp else "",
            },
            "results": coordinates_results
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        # Log error for debugging
        print(f"Error in get_doctors_coordinates: {error_details}")
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "details": error_details
            }
        )


@app.get("/providers/{provider_name}")
def get_provider_data(
    provider_name: str,
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    name: Optional[str] = Query(None, description="Location name"),
    **options
):
    """
    Generic endpoint to get data from any provider.
    
    This is a flexible endpoint that works with any registered provider.
    """
    try:
        # Get provider-specific config
        config = None
        if provider_name == "weather":
            config = WEATHER_CONFIG
        
        provider = create_provider(provider_name, config=config)
        location = Location(lat=lat, lon=lon, name=name)
        
        data = provider.get_data(location, **options)
        
        if data.error:
            return JSONResponse(
                status_code=500,
                content={"error": data.error, "data": data.dict()}
            )
        
        return JSONResponse(content=data.dict())
    except ValueError as e:
        return JSONResponse(
            status_code=404,
            content={"error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/providers/{provider_name}/batch")
def get_provider_batch(
    provider_name: str,
    points: List[Point],
    **options
):
    """
    Generic batch endpoint for any provider.
    """
    try:
        config = None
        if provider_name == "weather":
            config = WEATHER_CONFIG
        
        provider = create_provider(provider_name, config=config)
        
        locations = [
            Location(lat=p.lat, lon=p.lon, name=p.name)
            for p in points
        ]
        
        batch_request = BatchRequest(points=locations, options=options)
        batch_response = provider.get_batch(batch_request)
        
        return JSONResponse(content={
            "results": [r.dict() for r in batch_response.results],
            "errors": batch_response.errors,
            "timestamp": batch_response.timestamp
        })
    except ValueError as e:
        return JSONResponse(
            status_code=404,
            content={"error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

