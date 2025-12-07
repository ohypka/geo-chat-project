"""
Basic usage examples for geo-chat package.

This file demonstrates how to use the geo-chat package to fetch
environment and doctors availability data.
"""
import os
from geo_chat import (
    normalize_environment_data,
    get_doctor_availability,
    get_doctor_coordinates,
)

# Example 1: Get environment data (weather + air quality)
def example_environment():
    """Example: Fetch weather and air quality data."""
    # Option 1: Using environment variable OPENWEATHER_API_KEY
    # Make sure you have OPENWEATHER_API_KEY in your .env file or environment
    
    # Option 2: Pass API key directly
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    # Warsaw coordinates
    data = normalize_environment_data(
        lat=52.2297,
        lon=21.0122,
        name="Warsaw",
        api_key=api_key,  # Optional if env var is set
    )
    
    print("Environment Data:")
    print(f"Temperature: {data['metrics']['temperature']}°C")
    print(f"Humidity: {data['metrics']['humidity']}%")
    print(f"PM2.5: {data['metrics']['pm25']} µg/m³")
    print(f"AQI: {data['metrics']['aqi']}")
    return data


# Example 2: Get doctors availability
def example_doctors():
    """Example: Fetch doctors availability from NFZ API."""
    # Warsaw coordinates
    data = get_doctor_availability(
        lat=52.2297,
        lon=21.0122,
        service_name="kardiolog",
        urgent=True,
    )
    
    print("\nDoctors Availability:")
    print(f"Found {len(data['results'])} facilities")
    for i, facility in enumerate(data['results'][:3], 1):
        print(f"\n{i}. {facility['provider']}")
        print(f"   Address: {facility['address']}")
        print(f"   Waiting days: {facility['waiting_days']}")
        print(f"   Queue date: {facility['queue_date']}")
    
    return data


# Example 3: Get doctors with coordinates
def example_doctors_coordinates():
    """Example: Fetch doctors availability with coordinates."""
    data = get_doctor_coordinates(
        lat=52.2297,
        lon=21.0122,
        service_name="kardiolog",
        urgent=True,
    )
    
    print("\nDoctors with Coordinates:")
    for facility in data['results'][:3]:
        print(f"{facility['provider']}: ({facility['lat']}, {facility['lon']})")
    
    return data


if __name__ == "__main__":
    print("=" * 50)
    print("Geo Chat Package - Basic Usage Examples")
    print("=" * 50)
    
    try:
        example_environment()
    except Exception as e:
        print(f"Error fetching environment data: {e}")
    
    try:
        example_doctors()
    except Exception as e:
        print(f"Error fetching doctors data: {e}")
    
    try:
        example_doctors_coordinates()
    except Exception as e:
        print(f"Error fetching doctors coordinates: {e}")
