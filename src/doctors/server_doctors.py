from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from typing import Optional

from .doctors_availability import get_doctor_availability

app = FastAPI(title="NFZ Doctors Availability API")

@app.get("/doctors")
def get_doctors(
    lat: float = Query(..., description="Szerokość geograficzna"),
    lon: float = Query(..., description="Długość geograficzna"),
    service_name: str = Query(..., description="Nazwa poradni np. 'KARDIOLOG'"),
    urgent: Optional[bool] = Query(False, description="Tryb PILNY jeśli True, domyślnie STABILNY"),
):
    try:
        data = get_doctor_availability(lat, lon, service_name, urgent)
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
