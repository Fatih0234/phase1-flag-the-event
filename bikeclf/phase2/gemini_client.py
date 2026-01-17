"""Gemini API client wrapper for Phase 2 with Phase2ClassificationOutput."""
import time
from typing import Optional, Tuple
from google import genai
from pydantic import ValidationError
from bikeclf.schema import Phase2ClassificationOutput
from bikeclf.config import APIConfig


class Phase2GeminiClient:
    """Client for Gemini API with Phase 2 structured output (9-way categorization)."""

    def __init__(self, config: APIConfig):
        """Initialize client with API configuration.

        Args:
            config: APIConfig with Google API key
        """
        self.config = config
        self.client = genai.Client(api_key=config.api_key)

    def classify(
        self,
        prompt: str,
        model_id: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> Tuple[Optional[Phase2ClassificationOutput], int, Optional[str]]:
        """Classify with Phase 2 output schema (9 categories).

        Args:
            prompt: Full prompt with system instructions and user message
            model_id: Gemini model identifier
            temperature: Sampling temperature (0.0 for determinism)
            max_tokens: Maximum output tokens

        Returns:
            Tuple of (output, latency_ms, error):
            - output: Phase2ClassificationOutput if successful, None if failed
            - latency_ms: Request latency in milliseconds
            - error: Error message if failed, None if successful
        """
        start_time = time.time()

        try:
            response = self.client.models.generate_content(
                model=model_id,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": Phase2ClassificationOutput.model_json_schema(),
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )

            latency_ms = int((time.time() - start_time) * 1000)
            output = Phase2ClassificationOutput.model_validate_json(response.text)
            return output, latency_ms, None

        except ValidationError as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return None, latency_ms, f"Validation error: {str(e)}"

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return None, latency_ms, f"API error: {str(e)}"

    def classify_with_retry(
        self,
        prompt: str,
        model_id: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> Tuple[Optional[Phase2ClassificationOutput], int, int, Optional[str]]:
        """Classify with retry and repair prompt on validation errors.

        Args:
            prompt: Full prompt with system instructions and user message
            model_id: Gemini model identifier
            temperature: Sampling temperature
            max_tokens: Maximum output tokens

        Returns:
            Tuple of (output, total_latency_ms, attempts, error):
            - output: Phase2ClassificationOutput if successful, None if all attempts failed
            - total_latency_ms: Sum of all attempt latencies
            - attempts: Number of attempts made (1 or 2)
            - error: Final error message if all attempts failed, None if successful
        """
        # First attempt
        output, latency, error = self.classify(prompt, model_id, temperature, max_tokens)

        if output is not None:
            return output, latency, 1, None

        # Retry with category-specific repair prompt
        repair_prompt = (
            f"{prompt}\n\n"
            "IMPORTANT: The previous response had validation errors. "
            "Your JSON must match this schema:\n"
            "- category: EXACTLY one of the 9 predefined category strings (German text with special characters)\n"
            "- evidence: array of strings (max 10, each <200 chars)\n"
            "- reasoning: single sentence (max 500 chars)\n"
            "- confidence: number 0.0-1.0\n"
            "Provide ONLY the JSON object."
        )

        output2, latency2, error2 = self.classify(repair_prompt, model_id, temperature, max_tokens)
        total_latency = latency + latency2

        if output2 is not None:
            return output2, total_latency, 2, None
        else:
            return None, total_latency, 2, error2 or error
