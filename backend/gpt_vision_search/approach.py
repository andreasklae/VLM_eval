"""GPT Vision + Search approach - visual analysis with conditional web search augmentation."""

from __future__ import annotations

import asyncio
import base64
import json
import re
import time
from typing import Literal

from openai import AzureOpenAI, OpenAI

from ..base import ImageRecognitionApproach, RecognitionResult
from ..config import get_settings
from ..metadata import ImageMetadata
from ..schema import RecognitionOutput, build_full_record, extract_primary, clean_json_response
from . import search_wikipedia, search_google, search_web


# If visual_confidence from stage 1 is at or above this threshold, skip web search
SEARCH_CONFIDENCE_THRESHOLD = 0.75


DESCRIPTION_SYSTEM_PROMPT = """You are an expert visual analyst. Your task is to look at an image and produce two things:

1. A **tentative identification** of what is depicted, along with a **visual confidence score** (0.0–1.0) reflecting how certain you are based on visual evidence alone — before any external search.

2. A **detailed visual description** of the image content that could be used to search for and verify the identification.

## Visual confidence calibration

- **0.9–1.0**: You are nearly certain of the specific name (e.g., recognizing the Eiffel Tower or the Mona Lisa).
- **0.7–0.9**: You are fairly confident but would benefit from confirmation.
- **0.5–0.7**: You have a plausible guess but significant uncertainty remains.
- **0.0–0.5**: You can describe the subject type/style but cannot identify it specifically.

## Context interpretation

If GPS coordinates or a location name is provided, this tells you where the **photographer** was standing — NOT necessarily what is depicted.

If nearby places are listed, treat them as supporting context only. They may or may not be what is depicted.

## Output format (JSON)

{
    "visual_confidence": 0.0–1.0,
    "tentative_identification": "Brief description of what you think this likely is",
    "description": "Comprehensive visual description — architecture, style, materials, setting, lighting, surroundings, notable features",
    "subject_type": "landmark|building|artwork|monument|natural_feature|viewpoint|other",
    "search_terms": ["term1", "term2", "term3"],
    "architectural_style": "Style if applicable (Gothic, Baroque, etc.)"
}

No preamble. Only the JSON."""


AGGREGATION_SYSTEM_PROMPT = """You are an expert visual analyst tasked with producing a final structured identification of an image.

You have been given:
1. A visual analysis of the image (PRIMARY source)
2. Web search results (SUPPLEMENTARY source)

## Priority rules

- Your PRIMARY task is to analyze the image visually. Search results are supplementary confirmation only.
- If the visual analysis has high confidence (above 0.75), use search results only to enrich factual detail (dates, creator, history, dimensions) — NOT to change the identification.
- If the visual analysis has low confidence (below 0.75), search results may help disambiguate between candidates.
- If search results contradict your visual assessment, explain the conflict and justify your final decision. Do not blindly follow search results.
- A correct generic description is more valuable than a confidently wrong specific identification.

## Output format

Respond with a valid JSON object matching the RecognitionOutput schema exactly:

{
    "description": "Full comprehensive description of the image",
    "photographer_location": [{"name": "...", "confidence": 0.0}],
    "subject_location": [{"name": "...", "confidence": 0.0}],
    "entities": [{"name": "...", "type": "landmark|building|monument|artwork|...", "confidence": 0.0, "notes": null}]
}

Allowed entity types: landmark, building, monument, artwork, architectural_style, cultural_site, natural_feature, religious_site, public_space, infrastructure, transport_hub, viewpoint, district, signage, other

No preamble. Only the JSON."""


class GPTVisionSearchApproach(ImageRecognitionApproach):
    """
    Two-stage identification: visual analysis followed by conditional web search.

    Stage 1: GPT vision produces a detailed description and visual confidence score.
    Stage 2 (conditional): If visual confidence < SEARCH_CONFIDENCE_THRESHOLD,
    run web searches to augment the identification. Otherwise skip search entirely.
    Stage 3: GPT aggregates visual analysis + search results into a final RecognitionOutput.
    """

    def __init__(self, model_variant: Literal["fast", "strong"] = "strong"):
        self.model_variant = model_variant
        self._client_direct: OpenAI | None = None
        self._client_azure: AzureOpenAI | None = None

    @property
    def name(self) -> str:
        suffix = "fast" if self.model_variant == "fast" else "strong"
        return f"GPT Vision + Search ({suffix})"

    def _get_model_id(self) -> str:
        """Return model identifier, preferring Direct OpenAI over Azure."""
        settings = get_settings()
        if settings.use_direct_openai:
            return "gpt-5-nano" if self.model_variant == "fast" else "gpt-5"
        if settings.use_azure_openai:
            if self.model_variant == "fast":
                return settings.azure_openai_deployment_fast
            return settings.azure_openai_deployment
        return "gpt-4o-mini" if self.model_variant == "fast" else "gpt-4o"

    def is_available(self) -> bool:
        return get_settings().gpt_vision_available

    def _get_client(self) -> AzureOpenAI | OpenAI:
        """Get client, preferring Direct OpenAI over Azure (matches GPT Vision Direct routing)."""
        settings = get_settings()
        if settings.use_direct_openai:
            if self._client_direct is None:
                self._client_direct = OpenAI(api_key=settings.openai_direct_api_key)
            return self._client_direct
        if settings.use_azure_openai:
            if self._client_azure is None:
                self._client_azure = AzureOpenAI(
                    api_key=settings.azure_openai_api_key,
                    api_version=settings.azure_openai_api_version,
                    azure_endpoint=settings.azure_openai_endpoint,
                )
            return self._client_azure
        # Fallback: direct OpenAI with whatever key is available
        if self._client_direct is None:
            self._client_direct = OpenAI(api_key=settings.openai_direct_api_key)
        return self._client_direct

    def _build_description_user_prompt(self, metadata: ImageMetadata | None) -> str:
        """Build stage-1 user prompt with optional location and nearby context."""
        prompt = "Analyze this image. Provide your tentative identification, visual confidence, and a detailed description."

        if metadata:
            if metadata.location_info:
                loc = metadata.location_info
                addr = loc.formatted_address or (
                    f"{metadata.gps_latitude:.6f}, {metadata.gps_longitude:.6f}"
                    if metadata.gps_latitude is not None
                    else None
                )
                if addr:
                    prompt += f"\n\nPhotographer location context: {addr}"
            elif metadata.gps_latitude is not None and metadata.gps_longitude is not None:
                prompt += (
                    f"\n\nPhotographer GPS coordinates: "
                    f"{metadata.gps_latitude:.6f}, {metadata.gps_longitude:.6f}"
                )

            nearby = getattr(metadata, "nearby_places", None)
            if nearby:
                lines = []
                for p in nearby[:20]:
                    line = f"- {p.name} ({p.type.replace('_', ' ')}, {p.distance_meters}m away"
                    if p.rating:
                        line += f", rated {p.rating:.1f}"
                    line += ")"
                    lines.append(line)
                prompt += "\n\nNearby places within 2 km:\n" + "\n".join(lines)

        return prompt

    async def _get_description(
        self, image_data: bytes, mime_type: str, metadata: ImageMetadata | None = None
    ) -> dict:
        """Stage 1: Get visual description and confidence score."""
        b64_image = base64.b64encode(image_data).decode("utf-8")
        client = self._get_client()
        model_id = self._get_model_id()
        user_prompt = self._build_description_user_prompt(metadata)

        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": DESCRIPTION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{b64_image}"
                            },
                        },
                    ],
                },
            ],
            max_completion_tokens=800,
        )

        content = response.choices[0].message.content or ""
        try:
            json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(content)
        except json.JSONDecodeError:
            # Return minimal structure with zero confidence so search will run
            return {
                "visual_confidence": 0.0,
                "tentative_identification": "",
                "description": content,
                "search_terms": [],
            }

    async def _search_all_backends(
        self, description: dict, metadata: ImageMetadata | None = None
    ) -> dict:
        """Run searches across all available backends in parallel."""
        search_terms = description.get("search_terms", [])
        main_description = description.get("description", "")
        tentative = description.get("tentative_identification", "")

        # Build search query
        if search_terms:
            primary_query = search_terms[0]
        elif tentative:
            primary_query = tentative
        else:
            primary_query = main_description[:150]

        style = description.get("architectural_style", "")
        if style:
            primary_query = f"{style} {primary_query}"

        # Add location context
        if metadata and metadata.location_info:
            loc = metadata.location_info
            location_parts = []
            if loc.city:
                location_parts.append(loc.city)
            if loc.county and loc.county != loc.city:
                location_parts.append(loc.county)
            if loc.country:
                location_parts.append(loc.country)
            if location_parts:
                primary_query = f"{primary_query} near {', '.join(location_parts)}"

        results: dict = {
            "wikipedia": [],
            "google": [],
            "web": [],
            "vector": [],
        }

        tasks = []
        tasks.append(("wikipedia", search_wikipedia.search_wikipedia(primary_query)))
        if search_google.is_available():
            tasks.append(("google", search_google.search_google(primary_query)))
        if search_web.is_available():
            tasks.append(("web", search_web.search_web(primary_query)))
        # search_vector is planned but not yet implemented; skip for now

        for name, coro in tasks:
            try:
                results[name] = await coro
            except Exception as e:
                results[name] = []
                results[f"{name}_error"] = str(e)

        return results

    def _format_search_results(self, search_results: dict) -> str:
        """Format search results as a readable string for the aggregation prompt."""
        lines = []
        for source in ("wikipedia", "google", "web", "vector"):
            for result in search_results.get(source, [])[:3]:
                score = getattr(result, "score", None)
                title = getattr(result, "title", str(result))
                score_str = f" (score: {score:.2f})" if score is not None else ""
                lines.append(f"- [{source}] {title}{score_str}")
        return "\n".join(lines) if lines else "No search results found."

    async def _aggregate_results(
        self,
        image_data: bytes,
        mime_type: str,
        description: dict,
        search_results: dict | None,
        metadata: ImageMetadata | None,
    ) -> RecognitionOutput:
        """
        Stage 3: Aggregate visual analysis and search results into a final RecognitionOutput.
        Uses structured output forcing via .parse() or fallback to json_object.
        """
        b64_image = base64.b64encode(image_data).decode("utf-8")
        client = self._get_client()
        model_id = self._get_model_id()

        visual_confidence = description.get("visual_confidence", 0.0)
        tentative = description.get("tentative_identification", "")
        desc_text = description.get("description", "")

        # Build aggregation user prompt
        search_section = ""
        if search_results:
            formatted = self._format_search_results(search_results)
            search_section = f"\n\n## Search results\n{formatted}"
        else:
            search_section = "\n\n## Search results\nNo search was performed (visual confidence was high enough)."

        location_section = ""
        if metadata and metadata.location_info:
            loc = metadata.location_info
            addr = loc.formatted_address
            if addr:
                location_section = f"\n\n## Photographer location\n{addr}"
        elif metadata and metadata.gps_latitude is not None:
            location_section = (
                f"\n\n## Photographer location\n"
                f"GPS: {metadata.gps_latitude:.6f}, {metadata.gps_longitude:.6f}"
            )

        nearby_section = ""
        nearby = getattr(metadata, "nearby_places", None) if metadata else None
        if nearby:
            lines = []
            for p in nearby[:15]:
                line = f"- {p.name} ({p.type.replace('_', ' ')}, {p.distance_meters}m)"
                lines.append(line)
            nearby_section = "\n\n## Nearby places (within 2 km)\n" + "\n".join(lines)

        user_prompt = (
            f"## Visual analysis\n"
            f"Visual confidence: {visual_confidence:.2f}\n"
            f"Tentative identification: {tentative or '(not identified)'}\n\n"
            f"Description: {desc_text}"
            f"{location_section}"
            f"{nearby_section}"
            f"{search_section}"
            f"\n\nNow produce the final structured identification."
        )

        # Attempt structured output via .parse()
        try:
            response = client.beta.chat.completions.parse(
                model=model_id,
                messages=[
                    {"role": "system", "content": AGGREGATION_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{b64_image}"
                                },
                            },
                        ],
                    },
                ],
                response_format=RecognitionOutput,
                max_completion_tokens=16384,
            )
            result = response.choices[0].message.parsed
            if result is not None:
                return result
        except Exception:
            pass

        # Fallback path
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": AGGREGATION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{b64_image}"
                            },
                        },
                    ],
                },
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=16384,
        )
        raw = clean_json_response(response.choices[0].message.content or "{}")
        return RecognitionOutput.model_validate_json(raw)

    async def recognize(
        self,
        image_data: bytes,
        mime_type: str,
        metadata: ImageMetadata | None = None,
    ) -> RecognitionResult:
        """Identify landmark using conditional visual-analysis + search approach."""
        if not self.is_available():
            return RecognitionResult(
                approach=self.name,
                identified=None,
                confidence=None,
                error="GPT Vision not available. Check AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY.",
            )

        start_time = time.time()
        model_id = self._get_model_id()

        try:
            # Stage 1: Visual description + confidence score
            description = await self._get_description(image_data, mime_type, metadata)
            visual_confidence = description.get("visual_confidence", 0.0)

            # Stage 2 (conditional): Search only if visual confidence is below threshold
            search_results = None
            search_skipped = visual_confidence >= SEARCH_CONFIDENCE_THRESHOLD
            if not search_skipped:
                search_results = await self._search_all_backends(description, metadata)

            # Stage 3: Aggregation into final structured output
            ai_output = await self._aggregate_results(
                image_data, mime_type, description, search_results, metadata
            )

            processing_ms = int((time.time() - start_time) * 1000)

            # Build user_prompt summary for the record
            user_prompt_summary = (
                f"[Stage 1] Visual description + confidence. "
                f"visual_confidence={visual_confidence:.2f}. "
                f"search_skipped={search_skipped}."
            )

            full_record = build_full_record(
                approach_name=self.name,
                model_id=model_id,
                metadata=metadata,
                user_prompt=user_prompt_summary,
                ai_output=ai_output,
                processing_time_ms=processing_ms,
            )

            # Add search-specific metadata to the record
            full_record["visual_confidence"] = visual_confidence
            full_record["search_skipped"] = search_skipped
            full_record["search_threshold"] = SEARCH_CONFIDENCE_THRESHOLD
            if search_results is not None:
                full_record["search_backends_used"] = [
                    k for k, v in search_results.items()
                    if isinstance(v, list) and len(v) > 0
                ]
            else:
                full_record["search_backends_used"] = []

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
