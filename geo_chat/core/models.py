"""
Common data models for geo-chat package.

These models define the standardized format for all geographic data providers.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class Location(BaseModel):
    """Geographic location information."""
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")
    name: Optional[str] = Field(None, description="Location name")
    city: Optional[str] = Field(None, description="City name")
    province: Optional[str] = Field(None, description="Province/state name")
    country: Optional[str] = Field(None, description="Country name")
    address: Optional[str] = Field(None, description="Full address")


class Metric(BaseModel):
    """A single metric value with optional metadata."""
    name: str = Field(..., description="Metric name (e.g., 'temperature', 'waiting_days')")
    value: Any = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., '°C', 'days')")
    description: Optional[str] = Field(None, description="Human-readable description")


class DataPoint(BaseModel):
    """
    Standardized data point format for all providers.
    
    This is the unified format that all providers must return.
    """
    category: str = Field(..., description="Data category (e.g., 'environment', 'healthcare', 'transport')")
    source: str = Field(..., description="Data source/provider name (e.g., 'openweather', 'nfz')")
    location: Location = Field(..., description="Geographic location")
    timestamp: str = Field(..., description="ISO format timestamp in UTC")
    metrics: Dict[str, Any] = Field(..., description="Dictionary of metric values")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    raw: Optional[Dict[str, Any]] = Field(None, description="Raw API response (optional)")
    error: Optional[str] = Field(None, description="Error message if data fetch failed")

    class Config:
        json_schema_extra = {
            "example": {
                "category": "environment",
                "source": "openweather",
                "location": {
                    "lat": 52.2297,
                    "lon": 21.0122,
                    "name": "Warsaw"
                },
                "timestamp": "2025-01-15T10:30:00+00:00",
                "metrics": {
                    "temperature": 10.5,
                    "humidity": 77,
                    "pressure": 1021
                }
            }
        }


class BatchRequest(BaseModel):
    """Request for batch data processing."""
    points: List[Location] = Field(..., description="List of locations to fetch data for")
    provider_name: Optional[str] = Field(None, description="Specific provider to use")
    options: Optional[Dict[str, Any]] = Field(None, description="Provider-specific options")


class BatchResponse(BaseModel):
    """Response for batch data processing."""
    results: List[DataPoint] = Field(..., description="List of data points")
    errors: Optional[List[Dict[str, Any]]] = Field(None, description="List of errors if any")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
