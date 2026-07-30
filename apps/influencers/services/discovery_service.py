import logging
from django.utils import timezone
from apps.influencers.models import Influencer
from apps.influencers.services.provider_manager import ProviderManager
from apps.influencers.services import process_influencer_nlp, openrouter_service
from apps.uploads.utils import clean_text, normalize_influencer_dict

logger = logging.getLogger(__name__)

class DiscoveryService:
    @classmethod
    def execute(cls, user, criteria: dict) -> dict:
        provider = ProviderManager.get_active_provider()
        raw_results = provider.search(criteria)
        
        discovered_count = 0
        skipped_count = 0
        processed_count = 0
        
        for raw_data in raw_results:
            try:
                # 1. Normalize Data
                normalized = normalize_influencer_dict(raw_data)
                handle = normalized['handle']
                platform = normalized['platform']
                external_id = normalized['external_id']
                
                if not handle:
                    logger.warning("Skipping record with no handle.")
                    skipped_count += 1
                    continue
                
                # 2. Duplicate Detection
                is_duplicate = False
                if external_id:
                    is_duplicate = Influencer.objects.filter(
                        external_id=external_id, source=provider.name.upper()
                    ).exists()
                
                if not is_duplicate:
                    is_duplicate = Influencer.objects.filter(
                        handle__iexact=handle, platform=platform
                    ).exists()
                
                if is_duplicate:
                    logger.info(f"Duplicate found, skipping: {handle}")
                    skipped_count += 1
                    continue
                
                # 3. Save New Influencer
                influencer = Influencer.objects.create(
                    user=user,
                    upload=None, # Discovered influencers have no upload
                    external_id=external_id,
                    source=provider.name.upper(),
                    discovered_at=timezone.now(),
                    name=normalized['name'],
                    handle=handle,
                    platform=platform,
                    followers=normalized['followers'],
                    following=normalized['following'],
                    total_posts=normalized['total_posts'],
                    bio=normalized['bio'],
                    description=normalized['description'],
                    language=normalized['language'],
                    location=normalized['location'],
                    website=normalized['website'],
                    profile_url=normalized['profile_url'],
                    raw_data=raw_data # Store raw provider response for auditing
                )

                discovered_count += 1
                logger.info(f"Saved new discovered influencer: {influencer.handle}")
                
                # 4. Trigger Existing NLP Engine
                process_influencer_nlp(influencer)
                
                # 5. Trigger Existing AI Classification Engine
                # Note: We pass criteria as a mock SearchCriteria object or None
                openrouter_service.classify_influencer(influencer, criteria=None)
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Failed to process discovered influencer {raw_data.get('handle')}: {str(e)}")
                skipped_count += 1
                continue
                
        return {
            'discovered': discovered_count,
            'skipped': skipped_count,
            'processed': processed_count,
            'provider': provider.name
        }