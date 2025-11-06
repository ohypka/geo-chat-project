from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .weather_environment import (
    normalize_environment_data,
    get_environment_for_points,
    get_hourly_environment_timeseries,
)


app = FastAPI(title="Geo Chat – Environment API")


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
