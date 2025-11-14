from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import List, Dict, Any

from .nextbike import normalize_nextbike_data

app = FastAPI(title="Nextbike API")


@app.get("/nextbike", response_model=List[Dict[str, Any]])
def get_nextbike():
    """
    Pobiera aktualne dane o wszystkich stacjach Nextbike w Polsce.
    Zwraca ujednoliconą listę stacji, dostępnych rowerów/miejsc oraz ich typów.
    """
    try:
        data = normalize_nextbike_data()
        return JSONResponse(content=data)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "message": "Nie udało się pobrać danych z Nextbike API."},
        )