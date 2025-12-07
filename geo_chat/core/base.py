from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .models import DataPoint, Location, BatchRequest, BatchResponse


class ProviderConfig:
    """Configuration for a data provider."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 10,
        **kwargs
    ):
        """
        Initialize provider configuration.
        
        Args:
            api_key: API key for the service (if required)
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.extra = kwargs
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.extra.get(key, default)


class BaseProvider(ABC):
    """
    Base class for all geo-chat data providers.
    
    To create a custom provider:
    1. Inherit from BaseProvider
    2. Implement fetch() method
    3. Implement normalize() method
    4. Register the provider using @register_provider decorator
    """
    
    def __init__(self, config: Optional[ProviderConfig] = None):
        """
        Initialize provider.
        
        Args:
            config: Provider configuration
        """
        self.config = config or ProviderConfig()
        self.name = self.__class__.__name__.lower().replace("provider", "")
        self.category = "general"
    
    @abstractmethod
    def fetch(self, location: Location, **options) -> Dict[str, Any]:
        """
        Fetch raw data from the API for a given location.
        
        This method should make the actual API call and return
        the raw response as a dictionary.
        
        Args:
            location: Location to fetch data for
            **options: Provider-specific options
            
        Returns:
            Raw API response as dictionary
            
        Raises:
            Exception: If API call fails
        """
        pass
    
    @abstractmethod
    def normalize(self, raw_data: Dict[str, Any], location: Location) -> DataPoint:
        """
        Normalize raw API data to standardized DataPoint format.
        
        Args:
            raw_data: Raw data from fetch() method
            location: Original location object
            
        Returns:
            Normalized DataPoint
        """
        pass
    
    def get_data(self, location: Location, **options) -> DataPoint:
        """
        Fetch and normalize data for a location.
        
        This is the main method that combines fetch() and normalize().
        Override this only if you need custom error handling.
        
        Args:
            location: Location to fetch data for
            **options: Provider-specific options
            
        Returns:
            Normalized DataPoint
            
        Raises:
            Exception: If data fetch or normalization fails
        """
        try:
            raw_data = self.fetch(location, **options)
            return self.normalize(raw_data, location)
        except Exception as e:
            return DataPoint(
                category=self.category,
                source=self.name,
                location=location,
                timestamp=self._get_timestamp(),
                metrics={},
                error=str(e)
            )
    
    def get_batch(self, request: BatchRequest) -> BatchResponse:
        """
        Fetch data for multiple locations.
        
        Args:
            request: BatchRequest with list of locations
            
        Returns:
            BatchResponse with list of DataPoints
        """
        results = []
        errors = []
        
        for location in request.points:
            try:
                options = request.options or {}
                data_point = self.get_data(location, **options)
                results.append(data_point)
                
                if data_point.error:
                    errors.append({
                        "location": location.dict(),
                        "error": data_point.error
                    })
            except Exception as e:
                errors.append({
                    "location": location.dict(),
                    "error": str(e)
                })
                results.append(DataPoint(
                    category=self.category,
                    source=self.name,
                    location=location,
                    timestamp=self._get_timestamp(),
                    metrics={},
                    error=str(e)
                ))
        
        return BatchResponse(
            results=results,
            errors=errors if errors else None
        )
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
    
    def validate_location(self, location: Location) -> bool:
        """
        Validate location coordinates.
        
        Override this if you need custom validation.
        
        Args:
            location: Location to validate
            
        Returns:
            True if valid, False otherwise
        """
        return -90 <= location.lat <= 90 and -180 <= location.lon <= 180
