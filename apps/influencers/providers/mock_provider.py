import random
from typing import List, Dict, Any
from .base_provider import BaseProvider

class MockProvider(BaseProvider):
    """Simulates an external API response for testing the discovery pipeline."""
    
    @property
    def name(self) -> str:
        return "mock"

    def search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Simulate network delay
        import time
        time.sleep(1)
        
        platform = criteria.get('platform', 'INSTAGRAM').upper()
        keywords = criteria.get('keywords', 'technology')
        min_followers = int(criteria.get('min_followers', 10000))
        
        # Generate 3-5 mock records based on criteria
        num_results = random.randint(3, 5)
        results = []
        
        mock_names = ["Rahul Tech", "Priya Digital", "Amit Innovates", "Sneha Codes", "Vikram Develops"]
        mock_handles = ["rahul_tech_official", "priya.digital", "amit_innovates", "sneha_codes", "vikram_dev"]
        mock_bios = [
            f"Passionate about {keywords} and Digital India. Sharing daily tech tips.",
            f"Exploring {keywords}, Startup India, and innovation. Let's build Viksit Bharat.",
            f"Tech enthusiast discussing {keywords}, Skill India, and modern development."
        ]
        
        for i in range(num_results):
            followers = random.randint(min_followers, min_followers * 5)
            results.append({
                "external_id": f"mock_{platform.lower()}_{random.randint(1000, 9999)}",
                "name": mock_names[i % len(mock_names)],
                "handle": f"{mock_handles[i % len(mock_handles)]}_{random.randint(10, 99)}",
                "platform": platform,
                "followers": followers,
                "following": random.randint(100, 1000),
                "posts": random.randint(50, 500),
                "bio": random.choice(mock_bios),
                "description": f"Full-time content creator focusing on {keywords} and national development.",
                "language": "Hindi" if random.random() > 0.5 else "English",
                "location": "New Delhi, India",
                "website": f"https://example.com/{mock_handles[i]}",
                "profile_url": f"https://{platform.lower()}.com/{mock_handles[i]}"
            })
            
        return results