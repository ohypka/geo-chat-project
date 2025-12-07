"""
Example: Creating a custom data provider.

This example shows how to create your own provider for any API
that returns geographic data.
"""
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from geo_chat.core import (
    BaseProvider,
    ProviderConfig,
    Location,
    DataPoint,
    register_provider,
)


@register_provider(name="custom_api", category="custom")
class CustomAPIProvider(BaseProvider):
    """
    Example custom provider for a hypothetical API.
    
    This demonstrates the minimal implementation needed to create
    a new provider.
    """
    
    def __init__(self, config: Optional[ProviderConfig] = None):
        super().__init__(config)
        self.category = "custom"
        self.name = "custom_api"
        
        self.api_key = self.config.api_key
        if not self.api_key:
            raise ValueError("API key is required")
    
    def fetch(self, location: Location, **options) -> Dict[str, Any]:
        """
        Fetch raw data from your API.
        
        This is where you make the actual API call.
        """
        url = self.config.base_url or "https://api.example.com/data"
        params = {
            "lat": location.lat,
            "lon": location.lon,
            "api_key": self.api_key,
            **options,  
        }
        
        response = requests.get(url, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        
        return response.json()
    
    def normalize(self, raw_data: Dict[str, Any], location: Location) -> DataPoint:
        """
        Normalize raw API data to standard DataPoint format.
        
        This is where you transform your API's response format
        into the unified geo_chat format.
        """
        return DataPoint(
            category=self.category,
            source=self.name,
            location=location,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metrics={
                "temperature": raw_data.get("temperature"),
                "status": raw_data.get("status"),
            },
            metadata={
                
            },
            raw=raw_data,  
        )


if __name__ == "__main__":
    from geo_chat import create_provider, Location
    
    config = ProviderConfig(
        api_key="your_api_key",
        base_url="https://api.example.com/data",
    )
    provider = create_provider("custom_api", config=config)
    
    location = Location(lat=52.2297, lon=21.0122, name="Warsaw")
    data = provider.get_data(location)
    
    print(f"Category: {data.category}")
    print(f"Source: {data.source}")
    print(f"Metrics: {data.metrics}")
