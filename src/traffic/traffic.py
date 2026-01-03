import os
from datetime import datetime, timezone
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv

load_dotenv()

TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")
if not TOMTOM_API_KEY:
    raise RuntimeError("Missing TOMTOM_API_KEY")

TRAFFIC_FLOW_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"


def get_traffic_flow(lat: float, lon: float) -> dict:
    params = {
        "point": f"{lat},{lon}",
        "unit": "KMPH",
        "key": TOMTOM_API_KEY,
    }
    resp = requests.get(TRAFFIC_FLOW_URL, params=params, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(
            f"Traffic flow request failed: {resp.status_code} {resp.text}"
        )
    return resp.json()


def normalize_traffic_data(lat: float, lon: float, name: str | None = None) -> dict:
    data = get_traffic_flow(lat, lon)
    flow_segment = data.get("flowSegmentData", {})

    ts = datetime.now(timezone.utc).isoformat()
    current_speed = flow_segment.get("currentSpeed")
    free_flow_speed = flow_segment.get("freeFlowSpeed")
    confidence = flow_segment.get("confidence")

    return {
        "category": "traffic",
        "source": "tomtom",
        "location": {
            "lat": lat,
            "lon": lon,
            "name": name,
        },
        "timestamp": ts,
        "metrics": {
            "current_speed": current_speed,
            "free_flow_speed": free_flow_speed,
            "confidence": confidence,
        },
    }


def get_traffic_for_points(points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for point in points:
        lat = point["lat"]
        lon = point["lon"]
        name = point.get("name")
        try:
            data = normalize_traffic_data(lat, lon, name=name)
            results.append(data)
        except Exception as e:
            results.append({
                "category": "traffic",
                "source": "tomtom",
                "location": {"lat": lat, "lon": lon, "name": name},
                "error": str(e),
            })
    return results
