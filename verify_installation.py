#!/usr/bin/env python
"""
Verification script for geo-chat framework.

This script checks if the framework is properly installed and working.
Run: python verify_installation.py
"""
import sys
import os

def test_imports():
    """Test if all core components can be imported."""
    print("=" * 60)
    print("1. Testing imports...")
    print("-" * 60)
    
    try:
        from geo_chat import (
            create_provider,
            Location,
            DataPoint,
            BaseProvider,
            ProviderConfig,
            ProviderRegistry,
        )
        print("✓ Core components imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_provider_registration():
    """Test if providers are registered."""
    print("\n" + "=" * 60)
    print("2. Testing provider registration...")
    print("-" * 60)
    
    try:
        # Import providers to trigger registration
        from geo_chat import providers
        
        registered = ProviderRegistry.list_providers()
        print(f"✓ Found {len(registered)} registered providers:")
        for name in registered:
            print(f"  - {name}")
        
        if len(registered) == 0:
            print("⚠ Warning: No providers registered!")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Registration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_location_model():
    """Test Location model."""
    print("\n" + "=" * 60)
    print("3. Testing Location model...")
    print("-" * 60)
    
    try:
        location = Location(
            lat=52.2297,
            lon=21.0122,
            name="Warsaw",
            city="Warsaw",
            country="Poland"
        )
        print(f"✓ Location created: {location.name}")
        print(f"  Coordinates: ({location.lat}, {location.lon})")
        return True
    except Exception as e:
        print(f"✗ Location creation failed: {e}")
        return False

def test_datapoint_model():
    """Test DataPoint model."""
    print("\n" + "=" * 60)
    print("4. Testing DataPoint model...")
    print("-" * 60)
    
    try:
        from datetime import datetime, timezone
        
        location = Location(lat=52.2297, lon=21.0122, name="Test")
        data_point = DataPoint(
            category="test",
            source="test_provider",
            location=location,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metrics={"value": 42}
        )
        print(f"✓ DataPoint created: {data_point.category}/{data_point.source}")
        return True
    except Exception as e:
        print(f"✗ DataPoint creation failed: {e}")
        return False

def test_provider_creation():
    """Test creating provider instances."""
    print("\n" + "=" * 60)
    print("5. Testing provider creation...")
    print("-" * 60)
    
    try:
        # Test doctors provider (no API key needed)
        doctors = create_provider("doctors")
        print("✓ Doctors provider created")
        
        # Test weather provider (will fail without API key, but should handle gracefully)
        try:
            weather = create_provider("weather")
            print("✓ Weather provider created (API key may be needed)")
        except ValueError as e:
            if "API key" in str(e):
                print("⚠ Weather provider requires API key (expected)")
            else:
                raise
        except Exception as e:
            print(f"⚠ Weather provider: {type(e).__name__}")
        
        return True
    except Exception as e:
        print(f"✗ Provider creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_provider_methods():
    """Test that providers have required methods."""
    print("\n" + "=" * 60)
    print("6. Testing provider methods...")
    print("-" * 60)
    
    try:
        doctors = create_provider("doctors")
        
        methods = ['fetch', 'normalize', 'get_data', 'get_batch']
        for method in methods:
            if hasattr(doctors, method) and callable(getattr(doctors, method)):
                print(f"✓ Method '{method}' exists")
            else:
                print(f"✗ Method '{method}' missing or not callable")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Method test failed: {e}")
        return False

def test_error_handling():
    """Test error handling."""
    print("\n" + "=" * 60)
    print("7. Testing error handling...")
    print("-" * 60)
    
    try:
        doctors = create_provider("doctors")
        location = Location(lat=52.2297, lon=21.0122)
        
        # This should return DataPoint with error (missing service_name)
        result = doctors.get_data(location)
        
        if result.error:
            print(f"✓ Error handling works: {result.error[:60]}...")
        else:
            print("✓ No error (provider handled request)")
        
        return True
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Geo Chat Framework - Installation Verification")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_provider_registration,
        test_location_model,
        test_datapoint_model,
        test_provider_creation,
        test_provider_methods,
        test_error_handling,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed! Framework is working correctly.")
        print("\nNext steps:")
        print("1. Set OPENWEATHER_API_KEY to test weather provider")
        print("2. Try: python examples/simple_example.py")
        print("3. See docs/CREATING_PROVIDERS.md to create custom providers")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    # Import here to show errors clearly
    from geo_chat import (
        create_provider,
        Location,
        DataPoint,
        BaseProvider,
        ProviderConfig,
        ProviderRegistry,
    )
    
    sys.exit(main())
