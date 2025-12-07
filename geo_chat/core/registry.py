"""
Provider registry for managing and discovering data providers.
"""
from typing import Dict, Type, Optional, List
from .base import BaseProvider


class ProviderRegistry:
    """
    Registry for managing data providers.
    
    This allows providers to be registered and discovered dynamically.
    """
    
    _providers: Dict[str, Type[BaseProvider]] = {}
    _instances: Dict[str, BaseProvider] = {}
    
    @classmethod
    def register(cls, name: Optional[str] = None, category: Optional[str] = None):
        """
        Decorator to register a provider class.
        
        Usage:
            @ProviderRegistry.register(name="weather", category="environment")
            class WeatherProvider(BaseProvider):
                ...
        
        Args:
            name: Provider name (defaults to class name)
            category: Data category
        """
        def decorator(provider_class: Type[BaseProvider]):
            provider_name = name or provider_class.__name__.lower().replace("provider", "")
            
            # Set category if provided
            if category:
                original_init = provider_class.__init__
                def new_init(self, *args, **kwargs):
                    original_init(self, *args, **kwargs)
                    self.category = category
                provider_class.__init__ = new_init
            
            cls._providers[provider_name] = provider_class
            return provider_class
        
        return decorator
    
    @classmethod
    def get_provider_class(cls, name: str) -> Optional[Type[BaseProvider]]:
        """
        Get provider class by name.
        
        Args:
            name: Provider name
            
        Returns:
            Provider class or None if not found
        """
        return cls._providers.get(name)
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """
        List all registered provider names.
        
        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
    
    @classmethod
    def get_provider_by_category(cls, category: str) -> List[str]:
        """
        Get providers by category.
        
        Args:
            category: Data category
            
        Returns:
            List of provider names in the category
        """
        providers = []
        for name, provider_class in cls._providers.items():
            # Create temporary instance to check category
            try:
                instance = provider_class()
                if instance.category == category:
                    providers.append(name)
            except:
                pass
        return providers
    
    @classmethod
    def clear(cls):
        """Clear all registered providers (mainly for testing)."""
        cls._providers.clear()
        cls._instances.clear()


# Global registry instance
registry = ProviderRegistry()

# Convenience decorator
def register_provider(name: Optional[str] = None, category: Optional[str] = None):
    """Convenience decorator for registering providers."""
    return ProviderRegistry.register(name=name, category=category)
