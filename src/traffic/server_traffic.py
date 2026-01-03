from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .traffic import normalize_traffic_data, get_traffic_for_points

app = FastAPI(title="Traffic API")


class Point(BaseModel):
    lat: float
    lon: float
    name: Optional[str] = None


@app.get("/traffic")
def get_traffic(lat: float = Query(..., description="Latitude"),
                lon: float = Query(..., description="Longitude"),
                name: Optional[str] = Query(None, description="Optional location name")):
    try:
        data = normalize_traffic_data(lat, lon, name=name)
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )


@app.post("/traffic/batch")
def get_traffic_batch(points: List[Point]):
    pts: List[Dict[str, Any]] = [p.dict() for p in points]
    data = get_traffic_for_points(pts)
    return JSONResponse(content=data)
