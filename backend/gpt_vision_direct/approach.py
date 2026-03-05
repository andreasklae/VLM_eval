"""GPT Vision Direct approach - identifies landmarks directly using OpenAI/Azure OpenAI vision."""

from __future__ import annotations

import base64
import logging
import time
from typing import Literal

from openai import AzureOpenAI, OpenAI

logger = logging.getLogger(__name__)

from ..base import ImageRecognitionApproach, RecognitionResult
from ..config import get_settings
from ..metadata import ImageMetadata
from ..schema import (
    RecognitionOutput, build_full_record, extract_primary,
    VISION_SYSTEM_PROMPT, build_vision_user_prompt, clean_json_response,
)


def _has_metadata_enrichment(metadata: ImageMetadata | None) -> bool:
    """True if this request has location or nearby places (longer prompt → use direct OpenAI to avoid Azure rate limits)."""
    if metadata is None:
        return False
    return bool(metadata.location_info) or bool(getattr(metadata, "nearby_places", None))


class GPTVisionDirectApproach(ImageRecognitionApproach):
    """
    Identifies landmarks directly using OpenAI or Azure OpenAI vision capabilities.

    With metadata (location/nearby places): uses direct OpenAI to avoid Azure rate limits.
    Without metadata: uses Azure. Supports fast (gpt-5-nano) and strong (gpt-5) variants.
    """

    def __init__(self, model_variant: Literal["fast", "strong"] = "strong"):
        self.model_variant = model_variant
        self._client_direct: OpenAI | None = None
        self._client_azure: AzureOpenAI | None = None

    @property
    def name(self) -> str:
        suffix = "fast" if self.model_variant == "fast" else "strong"
        return f"GPT Vision Direct ({suffix})"

    def _get_model_id(self, metadata: ImageMetadata | None) -> str:
        """Return model identifier for this request (direct vs Azure depends on metadata)."""
        settings = get_settings()
        use_direct = settings.use_direct_openai_for_vision(_has_metadata_enrichment(metadata))
        if use_direct:
            return "gpt-5-nano" if self.model_variant == "fast" else "gpt-5"
        if self.model_variant == "fast":
            return settings.azure_openai_deployment_fast
        return settings.azure_openai_deployment

    def is_available(self) -> bool:
        return get_settings().gpt_vision_available

    def _get_client(self, metadata: ImageMetadata | None) -> AzureOpenAI | OpenAI:
        """Get client for this request: direct OpenAI when metadata present, else Azure."""
        settings = get_settings()
        use_direct = settings.use_direct_openai_for_vision(_has_metadata_enrichment(metadata))
        if use_direct:
            if self._client_direct is None:
                self._client_direct = OpenAI(api_key=settings.openai_direct_api_key)
            return self._client_direct
        if self._client_azure is None:
            self._client_azure = AzureOpenAI(
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
                azure_endpoint=settings.azure_openai_endpoint,
            )
        return self._client_azure

    def _build_user_prompt(self, metadata: ImageMetadata | None) -> str:
        return build_vision_user_prompt(metadata)

    async def recognize(
        self,
        image_data: bytes,
        mime_type: str,
        metadata: ImageMetadata | None = None,
    ) -> RecognitionResult:
        """Identify landmark in image using GPT vision with structured output forcing."""
        if not self.is_available():
            return RecognitionResult(
                approach=self.name,
                identified=None,
                confidence=None,
                error="GPT Vision not available. Set OPENAI_DIRECT_API_KEY (direct) or AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY.",
            )

        start_time = time.time()

        try:
            b64_image = base64.b64encode(image_data).decode("utf-8")
            model_id = self._get_model_id(metadata)
            user_prompt = self._build_user_prompt(metadata)
            client = self._get_client(metadata)
            logger.info("[%s] Calling model=%s (image_size=%d bytes)", self.name, model_id, len(image_data))

            messages = [
                {"role": "system", "content": VISION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{b64_image}"},
                        },
                    ],
                },
            ]

            # Attempt structured output via .parse() (requires SDK >= 1.40 and
            # Azure API version >= 2024-08-01-preview / direct OpenAI gpt-4o-2024-08-06+)
            ai_output = None
            try:
                response = client.beta.chat.completions.parse(
                    model=model_id,
                    messages=messages,
                    response_format=RecognitionOutput,
                    max_completion_tokens=16384,
                )
                ai_output = response.choices[0].message.parsed

            except Exception as parse_exc:
                # Fallback: json_object mode — guaranteed pure JSON, no schema enforcement
                logger.info("[%s] Structured output (.parse()) failed (%s), falling back to json_object mode", self.name, type(parse_exc).__name__)
                response = client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    response_format={"type": "json_object"},
                    max_completion_tokens=16384,
                )
                raw = clean_json_response(response.choices[0].message.content or "")
                ai_output = RecognitionOutput.model_validate_json(raw)

            if ai_output is None:
                return RecognitionResult(
                    approach=self.name,
                    identified=None,
                    confidence=None,
                    error="Empty or unparseable response from GPT",
                )

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
