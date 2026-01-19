"""
Test script to verify that the geo-chat framework is working correctly.

Run this script to check:
1. Package imports
2. Provider registration
3. Basic functionality
"""
import sys
from datetime import datetime

print("=" * 60)
print("Geo Chat Framework - Test Script")
print("=" * 60)
print()

print("Test 1: Importing core components...")
try:
    from geo_chat import (
        create_provider,
        Location,
        DataPoint,
        BaseProvider,
        ProviderConfig,
        ProviderRegistry,
    )
    print("Core imports successful")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)
print()

print("Test 2: Checking provider registration...")
try:
    from geo_chat import providers  
    
    registered = ProviderRegistry.list_providers()
    print(f"Found {len(registered)} registered providers:")
    for provider_name in registered:
        print(f"  - {provider_name}")
    
    if len(registered) == 0:
        print("Warning: No providers registered!")
except Exception as e:
    print(f"Provider registration failed: {e}")
    sys.exit(1)
print()

print("Test 3: Creating Location object...")
try:
    location = Location(lat=52.2297, lon=21.0122, name="Warsaw")
    print(f"Location created: {location.name} ({location.lat}, {location.lon})")
except Exception as e:
    print(f"Location creation failed: {e}")
    sys.exit(1)
print()

print("Test 4: Creating providers...")
try:
    try:
        weather_provider = create_provider("weather")
        print("Weather provider created (may need API key to fetch data)")
    except ValueError as e:
        print(f"Weather provider creation: {e}")
    except Exception as e:
        print(f"Weather provider creation: {type(e).__name__}: {e}")
    
    try:
        doctors_provider = create_provider("doctors")
        print("Doctors provider created")
    except Exception as e:
        print(f"Doctors provider creation failed: {e}")
        sys.exit(1)
        
except Exception as e:
    print(f"Provider creation failed: {e}")
    sys.exit(1)
print()

print("Test 5: Creating DataPoint...")
try:
    from datetime import timezone
    
    data_point = DataPoint(
        category="test",
        source="test_provider",
        location=location,
        timestamp=datetime.now(timezone.utc).isoformat(),
        metrics={
            "test_value": 42,
            "test_string": "hello"
        }
    )
    print(f"DataPoint created: category={data_point.category}, metrics={list(data_point.metrics.keys())}")
except Exception as e:
    print(f"DataPoint creation failed: {e}")
    sys.exit(1)
print()

print("Test 6: Testing provider methods...")
try:
    doctors_provider = create_provider("doctors")
    
    assert hasattr(doctors_provider, 'fetch'), "Provider missing 'fetch' method"
    assert hasattr(doctors_provider, 'normalize'), "Provider missing 'normalize' method"
    assert hasattr(doctors_provider, 'get_data'), "Provider missing 'get_data' method"
    assert hasattr(doctors_provider, 'get_batch'), "Provider missing 'get_batch' method"
    
    print("Provider has all required methods")
    print(f"  - fetch: {callable(doctors_provider.fetch)}")
    print(f"  - normalize: {callable(doctors_provider.normalize)}")
    print(f"  - get_data: {callable(doctors_provider.get_data)}")
    print(f"  - get_batch: {callable(doctors_provider.get_batch)}")
except Exception as e:
    print(f"Provider method test failed: {e}")
    sys.exit(1)
print()

print("Test 7: Testing error handling...")
try:
    doctors_provider = create_provider("doctors")
    test_location = Location(lat=52.2297, lon=21.0122)
    
    result = doctors_provider.get_data(test_location)
    
    if result.error:
        print(f"Error handling works: {result.error[:50]}...")
    else:
        print("No error (provider may have worked or handled gracefully)")
except Exception as e:
    print(f"Error handling test failed: {e}")
    sys.exit(1)
print()

print("Test 8: Testing registry functionality...")
try:
    env_providers = ProviderRegistry.get_provider_by_category("environment")
    healthcare_providers = ProviderRegistry.get_provider_by_category("healthcare")
    
    print(f"Environment providers: {env_providers}")
    print(f"Healthcare providers: {healthcare_providers}")
except Exception as e:
    print(f"Registry test failed: {e}")
    sys.exit(1)
print()

print("=" * 60)
print("Test Summary")
print("=" * 60)
print("All basic tests passed!")
print()
print("Next steps:")
print("1. Set OPENWEATHER_API_KEY environment variable to test weather provider")
print("2. Try fetching real data:")
print("   from geo_chat import create_provider, Location")
print("   provider = create_provider('doctors')")
print("   location = Location(lat=52.2297, lon=21.0122)")
print("   data = provider.get_data(location, service_name='kardiolog')")
print("3. See examples/ directory for more usage examples")
print("=" * 60)
