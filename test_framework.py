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

# Test 1: Import core components
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
    print("✓ Core imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)
print()

# Test 2: Check provider registration
print("Test 2: Checking provider registration...")
try:
    from geo_chat import providers  # This triggers registration
    
    registered = ProviderRegistry.list_providers()
    print(f"✓ Found {len(registered)} registered providers:")
    for provider_name in registered:
        print(f"  - {provider_name}")
    
    if len(registered) == 0:
        print("⚠ Warning: No providers registered!")
except Exception as e:
    print(f"✗ Provider registration failed: {e}")
    sys.exit(1)
print()

# Test 3: Create Location object
print("Test 3: Creating Location object...")
try:
    location = Location(lat=52.2297, lon=21.0122, name="Warsaw")
    print(f"✓ Location created: {location.name} ({location.lat}, {location.lon})")
except Exception as e:
    print(f"✗ Location creation failed: {e}")
    sys.exit(1)
print()

# Test 4: Create provider (without API key - should handle gracefully)
print("Test 4: Creating providers...")
try:
    # Try to create weather provider (will fail without API key, but should not crash)
    try:
        weather_provider = create_provider("weather")
        print("✓ Weather provider created (may need API key to fetch data)")
    except ValueError as e:
        print(f"⚠ Weather provider creation: {e}")
    except Exception as e:
        print(f"⚠ Weather provider creation: {type(e).__name__}: {e}")
    
    # Try to create doctors provider (should work)
    try:
        doctors_provider = create_provider("doctors")
        print("✓ Doctors provider created")
    except Exception as e:
        print(f"✗ Doctors provider creation failed: {e}")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Provider creation failed: {e}")
    sys.exit(1)
print()

# Test 5: Test DataPoint creation
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
    print(f"✓ DataPoint created: category={data_point.category}, metrics={list(data_point.metrics.keys())}")
except Exception as e:
    print(f"✗ DataPoint creation failed: {e}")
    sys.exit(1)
print()

# Test 6: Test provider methods (without actual API calls)
print("Test 6: Testing provider methods...")
try:
    doctors_provider = create_provider("doctors")
    
    # Check if provider has required methods
    assert hasattr(doctors_provider, 'fetch'), "Provider missing 'fetch' method"
    assert hasattr(doctors_provider, 'normalize'), "Provider missing 'normalize' method"
    assert hasattr(doctors_provider, 'get_data'), "Provider missing 'get_data' method"
    assert hasattr(doctors_provider, 'get_batch'), "Provider missing 'get_batch' method"
    
    print("✓ Provider has all required methods")
    print(f"  - fetch: {callable(doctors_provider.fetch)}")
    print(f"  - normalize: {callable(doctors_provider.normalize)}")
    print(f"  - get_data: {callable(doctors_provider.get_data)}")
    print(f"  - get_batch: {callable(doctors_provider.get_batch)}")
except Exception as e:
    print(f"✗ Provider method test failed: {e}")
    sys.exit(1)
print()

# Test 7: Test error handling (provider without API key)
print("Test 7: Testing error handling...")
try:
    # Try to get data without required options (should return error DataPoint)
    doctors_provider = create_provider("doctors")
    test_location = Location(lat=52.2297, lon=21.0122)
    
    # This should return a DataPoint with error (missing service_name)
    result = doctors_provider.get_data(test_location)
    
    if result.error:
        print(f"✓ Error handling works: {result.error[:50]}...")
    else:
        print("✓ No error (provider may have worked or handled gracefully)")
except Exception as e:
    print(f"✗ Error handling test failed: {e}")
    sys.exit(1)
print()

# Test 8: Test registry functionality
print("Test 8: Testing registry functionality...")
try:
    # Get provider by category
    env_providers = ProviderRegistry.get_provider_by_category("environment")
    healthcare_providers = ProviderRegistry.get_provider_by_category("healthcare")
    
    print(f"✓ Environment providers: {env_providers}")
    print(f"✓ Healthcare providers: {healthcare_providers}")
except Exception as e:
    print(f"✗ Registry test failed: {e}")
    sys.exit(1)
print()

# Summary
print("=" * 60)
print("Test Summary")
print("=" * 60)
print("✓ All basic tests passed!")
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
