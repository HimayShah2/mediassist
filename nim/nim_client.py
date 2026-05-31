"""
MediAssist Pro — NIM Client.

Wraps AsyncOpenAI to call NVIDIA NIM endpoints with:
- Key rotation via NIMKeyManager
- Structured output via instructor
- Logging of model, key_id, duration_ms
- Temperature locked at 0.1 for medical safety
"""

from __future__ import annotations

import time
from typing import TypeVar

import instructor
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel

from config.settings import settings
from config.llm_provider_manager import ModelRole, LLMProviderManager

T = TypeVar("T", bound=BaseModel)

BASE_URL = "https://integrate.api.nvidia.com/v1"


class NIMClient:
    """
    High-level async client for NVIDIA NIM inference.

    Delegates key selection to :class:`NIMKeyManager` and uses
    :mod:`instructor` for Pydantic-validated structured output.
    """

    def __init__(self, key_manager: LLMProviderManager | None = None) -> None:
        if key_manager is None:
            key_manager = LLMProviderManager(settings.get_nim_keys())
        self._km = key_manager

    # ── Internal helpers ───────────────────────────────────────────────────

    def _make_async_client(self, api_key: str, base_url: str) -> AsyncOpenAI:
        """Build a vanilla AsyncOpenAI pointed at the NIM gateway."""
        return AsyncOpenAI(
            api_key=api_key or "dummy",
            base_url=base_url,
            timeout=120.0,
        )

    def _make_instructor_client(self, api_key: str, base_url: str) -> instructor.AsyncInstructor:
        """Build an instructor-patched AsyncOpenAI client."""
        raw = AsyncOpenAI(
            api_key=api_key or "dummy",
            base_url=base_url,
            timeout=120.0,
        )
        return instructor.from_openai(raw)

    # ── chat ───────────────────────────────────────────────────────────────

    async def chat(
        self,
        role: ModelRole,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ) -> str:
        """
        Send a chat completion request and return the raw text response.

        Args:
            role: The model role (determines model + preferred key).
            messages: OpenAI-format messages list.
            temperature: Sampling temperature (default 0.1 for medical).
            max_tokens: Maximum tokens in the completion.

        Returns:
            The assistant's text reply.

        Raises:
            RuntimeError: If no healthy keys are available.
        """
        api_key_obj = self._km.get_key_for_role(role)
        if api_key_obj is None:
            raise RuntimeError(f"No healthy API keys available for role {role.value}")

        model = self._km.get_model_for_role(role)
        base = api_key_obj.base_url or BASE_URL
        client = self._make_async_client(api_key_obj.key_value, base)

        start = time.perf_counter()
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            duration_ms = (time.perf_counter() - start) * 1000
            content = response.choices[0].message.content or ""
            logger.info(
                "NIM chat | model={} key_id={} duration_ms={:.0f} tokens={}",
                model,
                api_key_obj.key_id,
                duration_ms,
                response.usage.total_tokens if response.usage else "?",
            )
            return content

        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "NIM chat FAILED | model={} key_id={} duration_ms={:.0f} error={}",
                model,
                api_key_obj.key_id,
                duration_ms,
                exc,
            )
            self._km.mark_key_unhealthy(api_key_obj.key_id)
            raise

    # ── structured_chat (instructor) ──────────────────────────────────────

    async def structured_chat(
        self,
        role: ModelRole,
        messages: list[dict[str, str]],
        response_model: type[T],
        temperature: float = 0.1,
        max_tokens: int = 4096,
        max_retries: int = 3,
    ) -> T:
        """
        Send a chat request and parse the response into a Pydantic model.

        Uses the ``instructor`` library to enforce structured output with
        automatic retries on validation failure.

        Args:
            role: The model role.
            messages: OpenAI-format messages list.
            response_model: Pydantic model class for the expected output.
            temperature: Sampling temperature (default 0.1).
            max_tokens: Maximum tokens.
            max_retries: Instructor retry count on validation errors.

        Returns:
            An instance of ``response_model`` populated from the LLM response.
        """
        api_key_obj = self._km.get_key_for_role(role)
        if api_key_obj is None:
            raise RuntimeError(f"No healthy API keys available for role {role.value}")

        model = self._km.get_model_for_role(role)
        base = api_key_obj.base_url or BASE_URL
        client = self._make_instructor_client(api_key_obj.key_value, base)

        start = time.perf_counter()
        try:
            result = await client.chat.completions.create(
                model=model,
                messages=messages,
                response_model=response_model,
                temperature=temperature,
                max_tokens=max_tokens,
                max_retries=max_retries,
            )
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "NIM structured_chat | model={} key_id={} duration_ms={:.0f} response_model={}",
                model,
                api_key_obj.key_id,
                duration_ms,
                response_model.__name__,
            )
            return result

        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "NIM structured_chat FAILED | model={} key_id={} duration_ms={:.0f} error={}",
                model,
                api_key_obj.key_id,
                duration_ms,
                exc,
            )
            self._km.mark_key_unhealthy(api_key_obj.key_id)
            raise

    # ── embed ─────────────────────────────────────────────────────────────

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of texts using the EMBED role model.

        Args:
            texts: Strings to embed.

        Returns:
            A list of embedding vectors (one per input text).
        """
        api_key_obj = self._km.get_key_for_role(ModelRole.EMBED)
        if api_key_obj is None:
            raise RuntimeError("No healthy API keys available for embedding")

        model = self._km.get_model_for_role(ModelRole.EMBED)
        base = api_key_obj.base_url or BASE_URL
        client = self._make_async_client(api_key_obj.key_value, base)

        start = time.perf_counter()
        try:
            response = await client.embeddings.create(
                model=model,
                input=texts,
                encoding_format="float",
                extra_body={"input_type": "query", "truncate": "END"},
            )
            duration_ms = (time.perf_counter() - start) * 1000
            embeddings = [item.embedding for item in response.data]
            logger.info(
                "NIM embed | model={} key_id={} duration_ms={:.0f} texts={}",
                model,
                api_key_obj.key_id,
                duration_ms,
                len(texts),
            )
            return embeddings

        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.error(
                "NIM embed FAILED | model={} key_id={} duration_ms={:.0f} error={}",
                model,
                api_key_obj.key_id,
                duration_ms,
                exc,
            )
            self._km.mark_key_unhealthy(api_key_obj.key_id)
            raise

    # ── Utility ────────────────────────────────────────────────────────────

    def is_offline(self) -> bool:
        """Proxy for key manager offline status."""
        return self._km.is_offline()

    def health_status(self) -> dict[str, object]:
        """Proxy for key manager health summary."""
        return self._km.health_status()
