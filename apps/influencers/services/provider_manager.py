import logging
from django.conf import settings
from apps.influencers.providers import MockProvider

logger = logging.getLogger(__name__)

class ProviderManager:
    _registry = {
        'mock': MockProvider,
        # Future providers will be added here:
        # 'instagram': InstagramProvider,
        # 'youtube': YouTubeProvider,
    }

    @classmethod
    def get_active_provider(cls):
        provider_name = getattr(settings, 'DEFAULT_PROVIDER', 'mock').lower()
        
        if not getattr(settings, 'DISCOVERY_ENABLED', True):
            raise ValueError("Real-time discovery is currently disabled in settings.")
            
        if provider_name not in cls._registry:
            logger.error(f"Requested provider '{provider_name}' not found in registry.")
            raise ValueError(f"Unsupported provider: {provider_name}")
            
        logger.info(f"Initializing provider: {provider_name}")
        return cls._registry[provider_name]()