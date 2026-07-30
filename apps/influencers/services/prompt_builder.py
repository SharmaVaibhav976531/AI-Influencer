import json
from typing import Optional
from apps.influencers.models import Influencer
from apps.classification.models import SearchCriteria

def build_classification_prompt(influencer: Influencer, criteria: Optional[SearchCriteria] = None) -> str:
    """Builds a strict, JSON-enforcing prompt for the LLM."""
    
    influencer_data = {
        "name": influencer.name,
        "handle": influencer.handle,
        "platform": influencer.platform,
        "followers": influencer.followers,
        "bio": influencer.bio,
        "description": influencer.description,
        "language_detected": influencer.language_detected,
        "extracted_keywords": influencer.extracted_keywords,
        "extracted_entities": influencer.extracted_entities,
        "rule_based_nlp_score": float(influencer.rule_based_score) if influencer.rule_based_score else 0.0
    }
    
    if criteria:
        criteria_text = (
            f"Evaluate against User Criteria:\n"
            f"- Keywords: {criteria.keywords}\n"
            f"- Languages: {criteria.languages}\n"
            f"- Orientation: {criteria.orientation}\n"
            f"- Niches: {criteria.niches}\n"
            f"- Minimum Followers: {criteria.minimum_followers}"
        )
    else:
        criteria_text = (
            "Evaluate against Default Criteria:\n"
            "- Look for positive/supportive orientation.\n"
            "- Relevance to national development, government schemes, and high-quality content.\n"
            "- Professional and constructive language."
        )

    prompt = f"""You are an expert AI Influencer Classification Engine. 
Analyze the following influencer profile and evaluate them based on the provided criteria.

Influencer Data:
{json.dumps(influencer_data, indent=2)}

{criteria_text}

CRITICAL INSTRUCTIONS:
1. You MUST return ONLY a valid JSON object.
2. Do NOT include markdown formatting (like ```json or ```).
3. Do NOT include any explanations, greetings, or text outside the JSON.
4. Ensure all numeric scores are integers between 0 and 100.

The JSON must strictly follow this exact schema:
{{
    "language": "string (e.g., 'Hindi', 'English')",
    "orientation": "string (e.g., 'Supportive', 'Neutral', 'Opposed', 'Unknown')",
    "content_niche": "string (e.g., 'Technology', 'Agriculture', 'General')",
    "matched_keywords": ["string"],
    "government_scheme_mentions": ["string"],
    "development_topics": ["string"],
    "overall_score": 0,
    "confidence_score": 0,
    "recommendation": "string (Must be exactly 'Highly Relevant', 'Relevant', or 'Not Relevant')",
    "reason": "string (concise 2-3 sentence explanation of the score)",
    "summary": "string (brief 1-sentence summary of the influencer's content)"
}}
"""
    return prompt