"""
ServerLLMClient — Lightweight API Client for a separate local LLM Server.
Connects to an external server (e.g., LM Studio, Ollama, llama.cpp) running on localhost.
Replaces the heavy, crash-prone embedded PyTorch engine.
"""
import os
import re
import json
import asyncio
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Default to the standard local API port used by LM Studio / llama.cpp / Ollama (OpenAI wrapper)
DEFAULT_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1")
# Default model name can be anything for local servers, usually ignored.
DEFAULT_MODEL = os.getenv("LLM_MODEL", "google/gemma-4-e4b")


def _tighten_question_schema(schema: dict):
    """Best-effort: for the QuestionnaireRound schema, drop the `null` branch from
    a question's `options` so grammar-constrained decoding emits an array (possibly
    empty, which the model validator then repairs) rather than null."""
    try:
        q = schema.get("$defs", {}).get("Question", {})
        opt = q.get("properties", {}).get("options")
        if isinstance(opt, dict) and "anyOf" in opt:
            arr = next((b for b in opt["anyOf"] if b.get("type") == "array"), None)
            if arr:
                q["properties"]["options"] = arr
    except Exception:
        pass


class ServerLLMClient:
    """
    Drop-in replacement for the LocalLLMClient.
    Makes lightweight API calls to a separate local LLM server instead of running PyTorch in memory.
    """

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        logger.info(f"Connecting to standalone local LLM server at {base_url}...")
        self.llm = ChatOpenAI(
            base_url=base_url,
            api_key="not-needed", # Local servers don't require an API key
            model=DEFAULT_MODEL,
            max_tokens=2048,
            temperature=0.1,
            streaming=False
        )

    def _convert_messages(self, messages: list[dict]) -> list:
        """Convert standard dict messages to Langchain message objects."""
        lc_messages = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        return lc_messages

    async def generate_structured(self, response_model, messages, max_tokens=1024, temperature=0.1):
        """Generate a Pydantic-validated structured response.

        Uses llama.cpp's native JSON-schema-constrained decoding when available
        (guarantees valid JSON -> no retries, and a much smaller prompt). Falls
        back to injecting the schema as text if the server rejects response_format.
        """
        schema = response_model.model_json_schema()
        _tighten_question_schema(schema)

        augmented = list(messages)
        hint = "\n\nRespond with a single JSON object only. No prose, no markdown fences."
        if augmented and augmented[0].get("role") == "system":
            augmented[0] = {**augmented[0], "content": augmented[0]["content"] + hint}
        else:
            augmented.insert(0, {"role": "system", "content": hint.strip()})
        lc_messages = self._convert_messages(augmented)

        # --- Attempt 1: grammar-constrained decoding ---
        try:
            constrained = self.llm.bind(
                max_tokens=max_tokens, temperature=temperature,
                response_format={"type": "json_object", "schema": schema},
            )
            response = await constrained.ainvoke(lc_messages)
            return response_model.model_validate_json(self._strip_fences(response.content))
        except Exception as e:
            logger.warning(f"Constrained decoding unavailable/failed ({e}); falling back to prompt schema.")

        # --- Attempt 2: schema in the prompt ---
        schema_str = json.dumps(schema, separators=(",", ":"))
        injected = list(lc_messages)
        from langchain_core.messages import SystemMessage
        injected.insert(0, SystemMessage(content=(
            "You MUST reply with raw JSON matching this schema exactly:\n" + schema_str
        )))
        try:
            model_instance = self.llm.bind(max_tokens=max_tokens, temperature=temperature)
            response = await model_instance.ainvoke(injected)
            return response_model.model_validate_json(self._strip_fences(response.content))
        except Exception as e:
            logger.error(f"Structured generation failed: {e}")
            raise

    @staticmethod
    def _strip_fences(raw: str) -> str:
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
        return raw.strip()

    async def generate_text(self, messages, max_tokens=2048, temperature=0.3):
        """Generate raw text."""
        lc_messages = self._convert_messages(messages)
        try:
            model_instance = self.llm.bind(max_tokens=max_tokens, temperature=temperature)
            response = await model_instance.ainvoke(lc_messages)
            return response.content
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise
