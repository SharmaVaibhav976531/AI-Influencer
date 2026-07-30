import json
import re

def parse_ai_response(response_text: str) -> dict:
    """
    Validates and cleans the AI response, ensuring it is valid JSON.
    Strips markdown code blocks if the model ignores instructions.
    """
    if not response_text:
        raise ValueError("Empty response received from AI.")
    
    # Strip markdown code blocks (e.g., ```json ... ```)
    cleaned_text = re.sub(r'^```json\s*', '', response_text, flags=re.MULTILINE | re.IGNORECASE)
    cleaned_text = re.sub(r'\s*```$', '', cleaned_text, flags=re.MULTILINE)
    cleaned_text = cleaned_text.strip()
    
    try:
        data = json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON returned by AI: {str(e)}. Raw text: {cleaned_text[:200]}")
    
    # Validate required keys
    required_keys = ["overall_score", "confidence_score", "recommendation", "reason"]
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        raise ValueError(f"Missing required keys in AI response: {', '.join(missing_keys)}")
        
    return data