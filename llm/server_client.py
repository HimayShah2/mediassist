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
    """Slim the QuestionnaireRound schema before it becomes a decoding grammar.

    Under grammar-constrained decoding the model emits every optional field (as
    null/false), which on a small CPU model blows the token budget and truncates
    the JSON mid-object. We drop rarely-used optional fields entirely and force
    `options` to a plain array so the model doesn't spend tokens on `null`."""
    try:
        defs = schema.get("$defs", {})

        q = defs.get("Question", {})
        qprops = q.get("properties", {})
        for drop in ("body_map_region", "triggers_followup", "round"):
            qprops.pop(drop, None)
        if isinstance(q.get("required"), list):
            q["required"] = [r for r in q["required"] if r in qprops]
        opt = qprops.get("options")
        if isinstance(opt, dict) and "anyOf" in opt:
            arr = next((b for b in opt["anyOf"] if b.get("type") == "array"), None)
            if arr:
                qprops["options"] = arr

        mo = defs.get("MCQOption", {})
        moprops = mo.get("properties", {})
        moprops.pop("differential_indicator", None)
        if isinstance(mo.get("required"), list):
            mo["required"] = [r for r in mo["required"] if r in moprops]
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

        Attempt 1 uses JSON-syntax mode only (fast). Attempt 2 adds full
        schema-grammar constrained decoding (slower but guarantees the shape).
        """
        schema = response_model.model_json_schema()
        _tighten_question_schema(schema)
        schema_str = json.dumps(schema, separators=(",", ":"))

        augmented = list(messages)
        hint = ("\n\nReply with ONE compact JSON object matching this schema (no whitespace, "
                "no newlines, no markdown fences, no prose):\n" + schema_str)
        if augmented and augmented[0].get("role") == "system":
            augmented[0] = {**augmented[0], "content": augmented[0]["content"] + hint}
        else:
            augmented.insert(0, {"role": "system", "content": hint.strip()})
        lc_messages = self._convert_messages(augmented)

        # --- Attempt 1: JSON-syntax mode only (fast) ---
        try:
            fast = self.llm.bind(max_tokens=max_tokens, temperature=temperature,
                                 response_format={"type": "json_object"})
            response = await fast.ainvoke(lc_messages)
            return response_model.model_validate_json(self._strip_fences(response.content))
        except Exception as e:
            logger.warning(f"Fast JSON parse failed ({str(e)[:150]}); retrying grammar-constrained.")

        # --- Attempt 2: full schema-grammar constrained decoding ---
        try:
            constrained = self.llm.bind(
                max_tokens=max_tokens, temperature=temperature,
                response_format={"type": "json_object", "schema": schema},
            )
            response = await constrained.ainvoke(lc_messages)
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
