import logging
from django.utils import timezone
from apps.influencers.models import Influencer
from apps.influencers.utils import clean_text_for_nlp, detect_language, extract_nlp_features, calculate_rule_based_score

logger = logging.getLogger(__name__)

def process_influencer_nlp(influencer: Influencer) -> None:
    try:
        raw_text = " ".join(filter(None, [influencer.bio, influencer.description]))
        
        if not raw_text or len(raw_text.strip()) < 5:
            influencer.language_detected = "Unknown"
            influencer.nlp_processed_at = timezone.now()
            influencer.save(update_fields=['language_detected', 'nlp_processed_at'])
            return

        clean_text = clean_text_for_nlp(raw_text)
        lang_result = detect_language(clean_text)
        nlp_features = extract_nlp_features(clean_text)
        
        score_result = calculate_rule_based_score(
            nlp_features["keywords"], 
            nlp_features["entities"], 
            lang_result["code"]
        )
        
        influencer.language_detected = lang_result["name"]
        influencer.language_confidence = lang_result["confidence"]
        influencer.extracted_keywords = nlp_features["keywords"][:50]
        influencer.extracted_entities = nlp_features["entities"]
        influencer.rule_based_score = score_result["overall_score"]
        influencer.nlp_matched_groups = score_result["matched_groups"]
        influencer.nlp_matched_keywords = score_result["matched_keywords"]
        influencer.nlp_processed_at = timezone.now()
        
        influencer.save(update_fields=[
            'language_detected', 'language_confidence', 'extracted_keywords',
            'extracted_entities', 'rule_based_score', 'nlp_matched_groups',
            'nlp_matched_keywords', 'nlp_processed_at'
        ])
        
    except Exception as e:
        logger.error(f"NLP processing failed for influencer {influencer.id}: {str(e)}")
        raise

def batch_process_nlp(user=None):
    """Process all influencers that haven't been processed yet."""
    queryset = Influencer.objects.filter(nlp_processed_at__isnull=True)
    if user:
        queryset = queryset.filter(upload__user=user)
        
    count = 0
    for influencer in queryset.iterator():
        try:
            process_influencer_nlp(influencer)
            count += 1
        except Exception as e:
            logger.error(f"Failed to process influencer {influencer.id}: {e}")
            continue
            
    return count