"""Gemini API client with structured output support."""
import time
from typing import Optional, Tuple
from google import genai
from pydantic import ValidationError
from bikeclf.schema import ClassificationOutput
from bikeclf.config import APIConfig


class GeminiClient:
    """Client for Gemini API with structured output and retry logic."""

    def __init__(self, config: APIConfig):
        """Initialize Gemini client.

        Args:
            config: API configuration with credentials
        """
        self.config = config
        self.client = genai.Client(api_key=config.api_key)

    def classify(
        self,
        prompt: str,
        model_id: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> Tuple[Optional[ClassificationOutput], int, Optional[str]]:
        """Classify a report with structured output.

        Args:
            prompt: Complete prompt with system instructions and user message
            model_id: Model identifier (e.g., 'gemini-2.0-flash-001')
            temperature: Sampling temperature (0.0 for determinism)
            max_tokens: Maximum output tokens

        Returns:
            Tuple of (output, latency_ms, error_message):
            - output: Parsed ClassificationOutput or None if failed
            - latency_ms: Time taken in milliseconds
            - error_message: Error description if failed, else None
        """
        start_time = time.time()

        try:
            # Use structured output with JSON schema
            response = self.client.models.generate_content(
                model=model_id,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": ClassificationOutput.model_json_schema(),
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                },
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Parse and validate response with Pydantic
            output = ClassificationOutput.model_validate_json(response.text)
            return output, latency_ms, None

        except ValidationError as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Validation error: {str(e)}"
            return None, latency_ms, error_msg

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_msg = f"API error: {str(e)}"
            return None, latency_ms, error_msg

    def classify_with_retry(
        self,
        prompt: str,
        model_id: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> Tuple[Optional[ClassificationOutput], int, int, Optional[str]]:
        """Classify with single retry on validation failure.

        This implements a repair prompt strategy: if the first attempt fails
        validation, we retry with additional schema instructions.

        Args:
            prompt: Complete prompt
            model_id: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum output tokens

        Returns:
            Tuple of (output, latency_ms, attempts, error_message):
            - output: Parsed ClassificationOutput or None if both attempts failed
            - latency_ms: Total time taken across all attempts
            - attempts: Number of attempts made (1 or 2)
            - error_message: Error description if failed, else None
        """
        # First attempt
        output, latency, error = self.classify(
            prompt, model_id, temperature, max_tokens
        )

        if output is not None:
            return output, latency, 1, None

        # Retry with repair prompt (add explicit schema reminder)
        repair_prompt = (
            f"{prompt}\n\n"
            "IMPORTANT: The previous response had validation errors. "
            "Please ensure your JSON response EXACTLY matches the required schema:\n"
            "- label: must be exactly 'true', 'false', or 'uncertain' (lowercase)\n"
            "- evidence: array of strings (max 10 items, each under 200 characters)\n"
            "- reasoning: single sentence string (max 500 characters)\n"
            "- confidence: number between 0.0 and 1.0 (inclusive)\n\n"
            "Provide ONLY the JSON object, no additional text."
        )

        output, latency2, error2 = self.classify(
            repair_prompt, model_id, temperature, max_tokens
        )

        total_latency = latency + latency2

        if output is not None:
            return output, total_latency, 2, None
        else:
            # Return the more recent error
            return None, total_latency, 2, error2 or error
