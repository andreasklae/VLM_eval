"""Google Gemini vision approach using Google AI Studio API (GenAI SDK)."""

from __future__ import annotations

import logging
import time
from typing import Literal

logger = logging.getLogger(__name__)

from ..base import ImageRecognitionApproach, RecognitionResult
from ..config import get_settings
from ..metadata import ImageMetadata
from ..schema import (
    RecognitionOutput, build_full_record, extract_primary,
    VISION_SYSTEM_PROMPT, build_vision_user_prompt, clean_json_response,
)


class GeminiVisionApproach(ImageRecognitionApproach):
    """
    Image recognition using Google Gemini via Google AI Studio (google-genai SDK).

    Uses Gemini 3 series: fast (gemini-3-flash-preview) and strong (gemini-3-pro-preview).
    Both support image input and structured JSON output via response_json_schema.
    Follows Google's structured output docs: pass Pydantic.model_json_schema() directly;
    the API ignores unsupported JSON Schema properties (e.g. default, title).
    """

    def __init__(self, model_variant: Literal["fast", "strong"] = "strong"):
        self.model_variant = model_variant
        self._client = None

    @property
    def name(self) -> str:
        suffix = "fast" if self.model_variant == "fast" else "strong"
        return f"Gemini Vision ({suffix})"

    def _get_model_id(self) -> str:
        settings = get_settings()
        if self.model_variant == "fast":
            return settings.gemini_model_fast
        return settings.gemini_model_strong

    def _get_client(self):
        """Get or create the GenAI Client (lazy initialization)."""
        if self._client is None:
            from google import genai
            settings = get_settings()
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client

    def is_available(self) -> bool:
        settings = get_settings()
        return settings.gemini_available

    def _build_user_prompt(self, metadata: ImageMetadata | None) -> str:
        return build_vision_user_prompt(metadata)

    async def recognize(
        self,
        image_data: bytes,
        mime_type: str,
        metadata: ImageMetadata | None = None,
    ) -> RecognitionResult:
        """Identify landmark using Google Gemini with structured output (response_json_schema)."""
        settings = get_settings()
        if not settings.gemini_available:
            return RecognitionResult(
                approach=self.name,
                identified=None,
                confidence=None,
                error="Gemini API key not configured (set GEMINI_API_KEY)",
            )

        start_time = time.time()

        try:
            from google.genai import types

            user_prompt = self._build_user_prompt(metadata)
            model_id = self._get_model_id()
            client = self._get_client()
            logger.info("[%s] Calling model=%s (image_size=%d bytes)", self.name, model_id, len(image_data))

            # Multimodal contents: text + image (per Google structured output docs)
            contents = [
                types.Part.from_text(text=user_prompt),
                types.Part.from_bytes(data=image_data, mime_type=mime_type),
            ]

            # config: system_instruction + structured output (Pydantic schema passed directly)
            # max_output_tokens=32768 to avoid truncation (structured JSON with many
            # entities and long descriptions can exceed 16k tokens)
            config = types.GenerateContentConfig(
                system_instruction=VISION_SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_json_schema=RecognitionOutput.model_json_schema(),
                temperature=0.2,
                max_output_tokens=32768,
            )

            # Use async client to avoid blocking the event loop
            response = await client.aio.models.generate_content(
                model=model_id,
                contents=contents,
                config=config,
            )

            # Prefer SDK-parsed output when response_json_schema was used; else parse JSON from text
            ai_output = getattr(response, "parsed", None)
            if not isinstance(ai_output, RecognitionOutput):
                raw_text = getattr(response, "text", None) or ""
                if not raw_text and getattr(response, "candidates", None) and len(response.candidates) > 0:
                    content = response.candidates[0].content
                    if getattr(content, "parts", None) and len(content.parts) > 0:
                        raw_text = getattr(content.parts[0], "text", None) or ""
                raw_text = clean_json_response(raw_text)
                try:
                    ai_output = RecognitionOutput.model_validate_json(raw_text)
                except Exception as parse_err:
                    # Truncated or invalid JSON (e.g. max_output_tokens hit)
                    if "EOF while parsing" in str(parse_err) or "json_invalid" in str(parse_err):
                        raise ValueError(
                            f"Gemini response was truncated or invalid JSON (model may have hit token limit). "
                            f"Original error: {parse_err}"
                        ) from parse_err
                    raise

            processing_ms = int((time.time() - start_time) * 1000)
            full_record = build_full_record(
                approach_name=self.name,
                model_id=model_id,
                metadata=metadata,
                user_prompt=user_prompt,
                ai_output=ai_output,
                processing_time_ms=processing_ms,
            )

            primary_id, primary_conf = extract_primary(ai_output)

            return RecognitionResult(
                approach=self.name,
                identified=primary_id,
                confidence=primary_conf,
                details=full_record,
            )

        except Exception as e:
            return RecognitionResult(
                approach=self.name,
                identified=None,
                confidence=None,
                error=str(e),
                details={"processing_time_ms": int((time.time() - start_time) * 1000)},
            )
