"""
Simple example showing the framework in action.

This demonstrates how easy it is to use any provider with the same code.
"""
from geo_chat import create_provider, Location, ProviderRegistry

# Show available providers
print("Available providers:", ProviderRegistry.list_providers())
print()

# Example 1: Weather provider
print("Example 1: Weather Provider")
print("-" * 40)
try:
    # Note: Requires OPENWEATHER_API_KEY environment variable
    weather = create_provider("weather")
    location = Location(lat=52.2297, lon=21.0122, name="Warsaw")
    data = weather.get_data(location)
    
    if data.error:
        print(f"Error: {data.error}")
    else:
        print(f"Category: {data.category}")
        print(f"Source: {data.source}")
        print(f"Temperature: {data.metrics.get('temperature')}°C")
        print(f"Humidity: {data.metrics.get('humidity')}%")
except Exception as e:
    print(f"Error: {e}")
print()

# Example 2: Doctors provider
print("Example 2: Doctors Provider")
print("-" * 40)
try:
    doctors = create_provider("doctors")
    location = Location(lat=52.2297, lon=21.0122)
    data = doctors.get_data(
        location,
        service_name="kardiolog",
        urgent=False
    )
    
    if data.error:
        print(f"Error: {data.error}")
    else:
        print(f"Category: {data.category}")
        print(f"Source: {data.source}")
        print(f"Facilities found: {data.metrics.get('facilities_count')}")
except Exception as e:
    print(f"Error: {e}")
print()

# Example 3: Unified format
print("Example 3: All providers return the same format")
print("-" * 40)
print("Every provider returns a DataPoint with:")
print("  - category: Data category")
print("  - source: Provider name")
print("  - location: Location object")
print("  - timestamp: ISO timestamp")
print("  - metrics: Dictionary of values")
print("  - metadata: Additional info (optional)")
print("  - error: Error message if failed (optional)")
