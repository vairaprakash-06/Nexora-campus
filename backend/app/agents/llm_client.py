import json
import logging
from typing import Dict, Any, Optional, Tuple
from groq import Groq
from backend.app.core.config import settings

logger = logging.getLogger("nexora_campus.llm")

class GroqAgentClient:
    """
    Manages Groq API integration with structured JSON responses,
    resilient error handling, and transparent deterministic fallback.
    """
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.enabled = settings.LLM_ENABLED and bool(self.api_key and self.api_key.strip() != "your_api_key")
        self._client = None

        if self.enabled:
            try:
                self._client = Groq(api_key=self.api_key)
                logger.info(f"Groq API client initialized with model '{self.model}'.")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}. Falling back to deterministic mode.")
                self.enabled = False
        else:
            logger.info("Groq API key not provided or LLM disabled. Running in Deterministic Agent Mode.")

    def is_available(self) -> bool:
        return self.enabled and (self._client is not None)

    def generate_json(self, system_prompt: str, user_prompt: str) -> Tuple[Optional[Dict[str, Any]], bool, Optional[str]]:
        """
        Attempts structured JSON completion via Groq.
        Returns: (data_dict, is_llm_generated, error_str)
        """
        if not self.is_available():
            return None, False, "Groq API key not configured. Using deterministic fallback."

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt + "\n\nYou MUST respond strictly in valid JSON format."},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=2048,
                timeout=15.0
            )
            raw_text = response.choices[0].message.content
            parsed = json.loads(raw_text)
            return parsed, True, None
        except Exception as e:
            logger.warning(f"Groq API call failed: {e}. Falling back to deterministic agent logic.")
            return None, False, str(e)

llm_client = GroqAgentClient()
