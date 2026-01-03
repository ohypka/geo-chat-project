"""
Factory for creating provider instances.
"""
from typing import Optional
from .base import BaseProvider, ProviderConfig
from .registry import registry


def create_provider(
    provider_name: str,
    config: Optional[ProviderConfig] = None,
    **config_kwargs
) -> BaseProvider:
    """
    Create a provider instance by name.
    
    Args:
        provider_name: Name of the provider (must be registered)
        config: ProviderConfig instance (optional)
        **config_kwargs: Configuration parameters (alternative to config object)
        
    Returns:
        Provider instance
        
    Raises:
        ValueError: If provider is not found
        
    Example:
        config = ProviderConfig(api_key="your_key")
        provider = create_provider("weather", config=config)
        
        provider = create_provider("weather", api_key="your_key")
    """
    provider_class = registry.get_provider_class(provider_name)
    
    if provider_class is None:
        available = ", ".join(registry.list_providers())
        raise ValueError(
            f"Provider '{provider_name}' not found. "
            f"Available providers: {available}"
        )
    
    if config is None and config_kwargs:
        config = ProviderConfig(**config_kwargs)
    
    return provider_class(config=config)


def get_provider(provider_name: str) -> Optional[BaseProvider]:
    """
    Get a cached provider instance or create a new one.
    
    Args:
        provider_name: Name of the provider
        
    Returns:
        Provider instance or None if not found
    """
    if provider_name in registry._instances:
        return registry._instances[provider_name]
    
    try:
        provider = create_provider(provider_name)
        registry._instances[provider_name] = provider
        return provider
    except ValueError:
        return None
