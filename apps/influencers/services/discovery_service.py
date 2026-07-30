import logging
from django.utils import timezone
from apps.influencers.models import Influencer
from apps.influencers.services.provider_manager import ProviderManager
from apps.influencers.services import process_influencer_nlp, openrouter_service
from apps.uploads.utils import clean_text

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
                handle = clean_text(raw_data.get('handle', ''))
                platform = raw_data.get('platform', 'OTHER').upper()
                external_id = raw_data.get('external_id')
                
                if not handle:
                    logger.warning("Skipping record with no handle.")
                    skipped_count += 1
                    continue
                
                # 2. Duplicate Detection
                is_duplicate = False
                if external_id:
                    is_duplicate = Influencer.objects.filter(
                        external_id=external_id, source=provider.name
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
                    name=clean_text(raw_data.get('name', '')),
                    handle=handle,
                    platform=platform,
                    followers=int(raw_data.get('followers', 0)),
                    following=int(raw_data.get('following', 0)),
                    total_posts=int(raw_data.get('posts', 0)),
                    bio=clean_text(raw_data.get('bio', '')),
                    description=clean_text(raw_data.get('description', '')),
                    language=clean_text(raw_data.get('language', '')),
                    location=clean_text(raw_data.get('location', '')),
                    website=clean_text(raw_data.get('website', '')),
                    profile_url=clean_text(raw_data.get('profile_url', '')),
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