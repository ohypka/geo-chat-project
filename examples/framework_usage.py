"""
Examples of using the geo-chat framework.

This demonstrates how to use the framework with built-in providers
and how to work with the unified data format.
"""
from geo_chat import (
    create_provider,
    Location,
    DataPoint,
    BatchRequest,
    ProviderConfig,
)


def example_single_location():
    """Example: Fetch data for a single location."""
    print("=" * 50)
    print("Example 1: Single Location")
    print("=" * 50)
    
    weather_provider = create_provider(
        "weather",
        api_key="your_openweather_api_key"  
    )
    
    location = Location(
        lat=52.2297,
        lon=21.0122,
        name="Warsaw"
    )
    
    data = weather_provider.get_data(location)
    
    print(f"Category: {data.category}")
    print(f"Source: {data.source}")
    print(f"Location: {data.location.name}")
    print(f"Temperature: {data.metrics.get('temperature')}°C")
    print(f"Humidity: {data.metrics.get('humidity')}%")
    print()


def example_batch_processing():
    """Example: Fetch data for multiple locations."""
    print("=" * 50)
    print("Example 2: Batch Processing")
    print("=" * 50)
    
    provider = create_provider("weather", api_key="your_key")
    
    request = BatchRequest(
        points=[
            Location(lat=52.2297, lon=21.0122, name="Warsaw"),
            Location(lat=50.0647, lon=19.9450, name="Krakow"),
            Location(lat=51.1079, lon=17.0385, name="Wroclaw"),
        ]
    )
    
    response = provider.get_batch(request)
    
    print(f"Fetched {len(response.results)} data points")
    for result in response.results:
        if result.error:
            print(f"Error for {result.location.name}: {result.error}")
        else:
            print(f"{result.location.name}: {result.metrics.get('temperature')}°C")
    print()


def example_doctors_provider():
    """Example: Using doctors provider with options."""
    print("=" * 50)
    print("Example 3: Doctors Provider")
    print("=" * 50)
    
    provider = create_provider("doctors")
    
    location = Location(lat=52.2297, lon=21.0122)
    
    data = provider.get_data(
        location,
        service_name="kardiolog",
        urgent=True,
        limit=5
    )
    
    print(f"Category: {data.category}")
    print(f"Found {data.metrics.get('facilities_count')} facilities")
    print(f"First available: {data.metrics.get('queue_date')}")
    
    if data.metadata and "results" in data.metadata:
        for facility in data.metadata["results"][:3]:
            print(f"  - {facility.get('provider')}: {facility.get('waiting_days')} days")
    print()


def example_unified_format():
    """Example: Working with unified data format."""
    print("=" * 50)
    print("Example 4: Unified Data Format")
    print("=" * 50)
    
    weather_provider = create_provider("weather", api_key="your_key")
    doctors_provider = create_provider("doctors")
    
    location = Location(lat=52.2297, lon=21.0122, name="Warsaw")
    
    weather_data = weather_provider.get_data(location)
    doctors_data = doctors_provider.get_data(
        location,
        service_name="kardiolog",
        urgent=False
    )
    
    data_points = [weather_data, doctors_data]
    
    for data in data_points:
        print(f"\n{data.category.upper()} ({data.source}):")
        print(f"  Location: {data.location.name or f'{data.location.lat}, {data.location.lon}'}")
        print(f"  Timestamp: {data.timestamp}")
        print(f"  Metrics: {list(data.metrics.keys())}")
    print()


def example_error_handling():
    """Example: Error handling."""
    print("=" * 50)
    print("Example 5: Error Handling")
    print("=" * 50)
    
    provider = create_provider("weather", api_key="invalid_key")
    
    location = Location(lat=52.2297, lon=21.0122)
    
    data = provider.get_data(location)
    
    if data.error:
        print(f"Error occurred: {data.error}")
    else:
        print(f"Success: {data.metrics}")
    print()


if __name__ == "__main__":
    print("Geo Chat Framework - Usage Examples")
    print("=" * 50)
    print()
    
    print("See individual example functions for usage patterns.")
