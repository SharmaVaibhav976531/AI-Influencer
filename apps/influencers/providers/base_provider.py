from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseProvider(ABC):
    """Abstract base class for all external influencer data providers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name (e.g., 'mock', 'instagram')."""
        pass

    @abstractmethod
    def search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for influencers based on criteria.
        Returns a list of dictionaries representing raw influencer data.
        """
        pass