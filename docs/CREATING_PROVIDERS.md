# Creating Custom Providers

This guide explains how to create your own data provider for the geo-chat framework.

## Overview

A provider is a class that:
1. Fetches data from an API (or any data source)
2. Normalizes it to the standard `DataPoint` format
3. Can be registered and used like any built-in provider

## Step-by-Step Guide

### 1. Create Your Provider Class

Inherit from `BaseProvider` and implement two required methods:

```python
from geo_chat.core import BaseProvider, Location, DataPoint, register_provider

@register_provider(name="my_api", category="my_category")
class MyAPIProvider(BaseProvider):
    def fetch(self, location: Location, **options) -> dict:
        pass
    
    def normalize(self, raw_data: dict, location: Location) -> DataPoint:
        pass
```

### 2. Implement `fetch()` Method

This method makes the actual API call:

```python
def fetch(self, location: Location, **options) -> dict:
    """
    Fetch raw data from your API.
    
    Args:
        location: Location to fetch data for
        **options: Provider-specific options (e.g., filters, parameters)
    
    Returns:
        Raw API response as dictionary
    """
    import requests
    
    url = "https://api.example.com/data"
    params = {
        "lat": location.lat,
        "lon": location.lon,
        "api_key": self.config.api_key,
        **options,  # Pass through custom options
    }
    
    response = requests.get(url, params=params, timeout=self.config.timeout)
    response.raise_for_status()
    
    return response.json()
```

### 3. Implement `normalize()` Method

Transform your API's response to the standard format:

```python
def normalize(self, raw_data: dict, location: Location) -> DataPoint:
    """
    Normalize raw API data to DataPoint format.
    
    Args:
        raw_data: Raw data from fetch() method
        location: Original location object
    
    Returns:
        Normalized DataPoint
    """
    from datetime import datetime, timezone
    
    return DataPoint(
        category=self.category,  # Set in __init__ or use default
        source=self.name,        # Set in __init__ or use default
        location=location,
        timestamp=datetime.now(timezone.utc).isoformat(),
        metrics={
            # Extract metrics from raw_data
            "temperature": raw_data.get("temp"),
            "status": raw_data.get("status"),
            # Add any other metrics
        },
        metadata={
            # Optional: additional metadata
            "api_version": raw_data.get("version"),
        },
        raw=raw_data,  # Optional: keep raw data for reference
    )
```

### 4. Initialize Provider

Set up configuration in `__init__`:

```python
def __init__(self, config: Optional[ProviderConfig] = None):
    super().__init__(config)
    self.category = "my_category"
    self.name = "my_api"
    
    # Validate required configuration
    self.api_key = self.config.api_key
    if not self.api_key:
        raise ValueError("API key is required")
```

### 5. Register Your Provider

Use the `@register_provider` decorator:

```python
@register_provider(name="my_api", category="my_category")
class MyAPIProvider(BaseProvider):
    # ... implementation
```

## Complete Example

```python
"""
Complete example of a custom provider.
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


@register_provider(name="traffic", category="transport")
class TrafficProvider(BaseProvider):
    """Provider for traffic data from a hypothetical API."""
    
    def __init__(self, config: Optional[ProviderConfig] = None):
        super().__init__(config)
        self.category = "transport"
        self.name = "traffic_api"
        self.api_key = self.config.api_key or "default_key"
    
    def fetch(self, location: Location, **options) -> Dict[str, Any]:
        """Fetch traffic data."""
        url = self.config.base_url or "https://api.traffic.com/data"
        params = {
            "lat": location.lat,
            "lon": location.lon,
            "key": self.api_key,
        }
        response = requests.get(url, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()
    
    def normalize(self, raw_data: Dict[str, Any], location: Location) -> DataPoint:
        """Normalize traffic data."""
        return DataPoint(
            category=self.category,
            source=self.name,
            location=location,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metrics={
                "speed": raw_data.get("current_speed"),
                "free_flow_speed": raw_data.get("free_flow_speed"),
                "congestion_level": raw_data.get("congestion"),
            },
            raw=raw_data,
        )
```

## Using Your Provider

Once registered, use it like any other provider:

```python
from geo_chat import create_provider, Location

# Create provider
provider = create_provider(
    "traffic",
    api_key="your_key",
    base_url="https://api.traffic.com"
)

# Use it
location = Location(lat=52.2297, lon=21.0122)
data = provider.get_data(location)

print(f"Speed: {data.metrics['speed']} km/h")
```

## Advanced Features

### Custom Options

Providers can accept custom options:

```python
data = provider.get_data(
    location,
    custom_param="value",
    another_param=123
)
```

These are passed to `fetch()` via `**options`.

### Batch Processing

Batch processing works automatically:

```python
from geo_chat import BatchRequest

request = BatchRequest(
    points=[
        Location(lat=52.2297, lon=21.0122),
        Location(lat=50.0647, lon=19.9450),
    ]
)

response = provider.get_batch(request)
for result in response.results:
    print(result.metrics)
```

### Error Handling

Providers should handle errors gracefully. The base class returns error DataPoints:

```python
data = provider.get_data(location)
if data.error:
    print(f"Error: {data.error}")
else:
    print(f"Success: {data.metrics}")
```

## Best Practices

1. **Validate Input**: Check required options in `fetch()`
2. **Handle Errors**: Let exceptions bubble up - base class handles them
3. **Document Options**: Add docstrings explaining available options
4. **Keep Raw Data**: Include `raw` field for debugging
5. **Use Metadata**: Store provider-specific info in `metadata`
6. **Set Categories**: Use meaningful category names
7. **Test Thoroughly**: Test with various locations and edge cases

## DataPoint Structure

Always return data in this format:

```python
DataPoint(
    category="your_category",      # Required
    source="your_provider_name",   # Required
    location=Location(...),        # Required
    timestamp="ISO format",         # Required
    metrics={...},                 # Required: dict of metric values
    metadata={...},               # Optional: additional info
    raw={...},                     # Optional: raw API response
    error="error message"          # Optional: if error occurred
)
```

## Questions?

See `examples/custom_provider.py` for a complete working example.
