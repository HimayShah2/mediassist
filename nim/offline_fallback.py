"""
MediAssist Pro — Offline LLM Fallback.

Provides a local LLM via llama-cpp-python when NIM is unreachable.
Gracefully degrades: if the model file is not present, all calls
return a safe fallback message rather than crashing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from loguru import logger

from config.settings import settings


class OfflineLLM:
    """
    Offline inference using a local GGUF model via ``llama-cpp-python``.

    Attributes:
        model_path: Path to the ``.gguf`` model file.
    """

    def __init__(self, model_path: str | None = None) -> None:
        self.model_path = model_path or settings.offline_model_path
        self._llm: Optional[object] = None  # lazy-loaded Llama instance
        self._available: Optional[bool] = None  # cached probe result

    # ── Public API ─────────────────────────────────────────────────────────

    def is_available(self) -> bool:
        """
        Check whether the local model can be loaded.

        The result is cached after the first probe so repeated calls are cheap.
        """
        if self._available is not None:
            return self._available

        model_file = Path(self.model_path)
        if not model_file.exists():
            logger.warning(
                "Offline model file not found: {}  — offline fallback disabled",
                self.model_path,
            )
            self._available = False
            return False

        try:
            self._load_model()
            self._available = True
            logger.info("Offline LLM loaded successfully from {}", self.model_path)
        except Exception as exc:
            logger.error("Failed to load offline model: {}", exc)
            self._available = False

        return self._available

    def chat(self, messages: list[dict[str, str]]) -> str:
        """
        Run inference on the local model with an OpenAI-style messages list.

        Args:
            messages: List of ``{"role": ..., "content": ...}`` dicts.

        Returns:
            The model's text reply, or a safe fallback string when the model
            is unavailable.
        """
        if not self.is_available():
            return (
                "[Offline Mode] The AI assistant is currently unavailable. "
                "Please consult a healthcare professional for medical guidance."
            )

        try:
            prompt = self._format_prompt(messages)
            result = self._llm(  # type: ignore[operator]
                prompt,
                max_tokens=1024,
                temperature=0.1,
                top_p=0.9,
                stop=["</s>", "[INST]", "[/INST]"],
                echo=False,
            )
            text: str = result["choices"][0]["text"].strip()  # type: ignore[index]
            logger.info("Offline LLM responded ({} chars)", len(text))
            return text

        except Exception as exc:
            logger.error("Offline LLM inference error: {}", exc)
            return (
                "[Offline Mode] An error occurred during local inference. "
                "Please consult a healthcare professional for medical guidance."
            )

    # ── Internals ──────────────────────────────────────────────────────────

    def _load_model(self) -> None:
        """Lazy-load the Llama model if not already loaded."""
        if self._llm is not None:
            return

        try:
            from llama_cpp import Llama  # type: ignore[import-untyped]
        except ImportError:
            raise ImportError(
                "llama-cpp-python is not installed. "
                "Install it with:  pip install llama-cpp-python"
            )

        self._llm = Llama(
            model_path=self.model_path,
            n_ctx=4096,
            n_threads=4,
            n_gpu_layers=0,  # CPU-only for maximum portability
            verbose=False,
        )

    @staticmethod
    def _format_prompt(messages: list[dict[str, str]]) -> str:
        """
        Convert OpenAI-style messages into a Mistral-instruct prompt.

        Format::

            <s>[INST] {system}

            {user_message} [/INST]
        """
        system_parts: list[str] = []
        user_parts: list[str] = []
        assistant_parts: list[str] = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_parts.append(content)
            elif role == "user":
                user_parts.append(content)
            elif role == "assistant":
                assistant_parts.append(content)

        system_text = "\n".join(system_parts)
        prompt_parts: list[str] = ["<s>"]

        # Build multi-turn conversation
        all_user = list(user_parts)
        all_assistant = list(assistant_parts)

        for i, user_msg in enumerate(all_user):
            inst_content = user_msg
            if i == 0 and system_text:
                inst_content = f"{system_text}\n\n{user_msg}"
            prompt_parts.append(f"[INST] {inst_content} [/INST]")
            if i < len(all_assistant):
                prompt_parts.append(f" {all_assistant[i]}</s>")

        return "".join(prompt_parts)
