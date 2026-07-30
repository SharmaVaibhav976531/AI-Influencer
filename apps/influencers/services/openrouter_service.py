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

    def classify_influencer(self, influencer, criteria=None, stage_callback=None) -> dict:
        """Calls OpenRouter to classify an influencer, with exponential backoff retries and stage callbacks."""
        prompt = build_classification_prompt(influencer, criteria)
        if stage_callback:
            stage_callback("Prompt Generated")
        logger.info("✓ Prompt Generated")
        
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                if stage_callback:
                    stage_callback("Sending Request")
                logger.info("✓ Request Sent")
                
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
                
                if stage_callback:
                    stage_callback("Response Received")
                logger.info("✓ Response Received")
                
                processing_time = time.time() - start_time
                response_text = response.choices[0].message.content
                
                if stage_callback:
                    stage_callback("Parsing Response")
                logger.info("✓ JSON Parsed")
                
                parsed_data = parse_ai_response(response_text)
                parsed_data['processing_time_seconds'] = round(processing_time, 2)
                parsed_data['ai_model_name'] = self.model
                
                return parsed_data
                
            except Exception as e:
                err_msg = str(e)
                attempt_num = attempt + 1
                status_code = getattr(e, 'status_code', 'Error')
                logger.warning(f"Retry {attempt_num}/{self.max_retries}\nReason: {err_msg}")
                
                if stage_callback:
                    stage_callback("Retry", {
                        "attempt": attempt_num,
                        "max_retries": self.max_retries,
                        "reason": err_msg,
                        "status_code": status_code,
                        "retries_left": self.max_retries - attempt_num
                    })
                
                if attempt < self.max_retries - 1:
                    sleep_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    time.sleep(sleep_time)
                else:
                    logger.error(f"FAILED\nReason: {err_msg}")
                    raise


# Singleton instance to reuse the HTTP connection pool
openrouter_service = OpenRouterService()