import time
import logging
from openai import OpenAI
from django.conf import settings
from .prompt_builder import build_classification_prompt
from .response_parser import parse_ai_response

logger = logging.getLogger(__name__)

class OpenRouterService:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.model = settings.OPENROUTER_MODEL_NAME
        self.timeout = settings.OPENROUTER_TIMEOUT
        self.max_retries = settings.OPENROUTER_MAX_RETRIES

    def classify_influencer(self, influencer, criteria=None) -> dict:
        """Calls OpenRouter to classify an influencer, with exponential backoff retries."""
        prompt = build_classification_prompt(influencer, criteria)
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a strict JSON-only API. Return ONLY valid JSON. No markdown, no explanations."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    timeout=self.timeout,
                    extra_body={
                        "reasoning": {
                            "enabled": True
                        }
                    }
                )
                
                processing_time = time.time() - start_time
                response_text = response.choices[0].message.content
                
                logger.info(f"AI Response received for {influencer.handle} in {processing_time:.2f}s (Attempt {attempt + 1})")
                
                parsed_data = parse_ai_response(response_text)
                parsed_data['processing_time_seconds'] = round(processing_time, 2)
                parsed_data['ai_model_name'] = self.model
                
                return parsed_data
                
            except Exception as e:
                logger.warning(f"AI Classification attempt {attempt + 1} failed for {influencer.handle}: {str(e)}")
                if attempt < self.max_retries - 1:
                    sleep_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"AI Classification permanently failed for {influencer.handle} after {self.max_retries} retries.")
                    raise

# Singleton instance to reuse the HTTP connection pool
openrouter_service = OpenRouterService()