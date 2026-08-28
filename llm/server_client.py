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
        """Generate a Pydantic-validated structured response."""
        schema = response_model.model_json_schema()
        schema_str = json.dumps(schema, indent=2)
        json_instruction = (
            f"\n\nYou MUST respond with a valid JSON object matching this schema:\n"
            f"```json\n{schema_str}\n```\n"
            "Output ONLY raw JSON. No markdown fences, no explanation."
        )

        augmented = list(messages)
        if augmented and augmented[0].get("role") == "system":
            augmented[0] = {**augmented[0], "content": augmented[0]["content"] + json_instruction}
        else:
            augmented.insert(0, {"role": "system", "content": json_instruction})

        lc_messages = self._convert_messages(augmented)

        try:
            # We override params per request
            model_instance = self.llm.bind(max_tokens=max_tokens, temperature=temperature)
            
            # Using standard invoke since some local servers don't fully support the native JSON Schema endpoints yet
            response = await model_instance.ainvoke(lc_messages)
            raw = response.content
            
            # Clean up potential markdown formatting wrapping the JSON
            raw = re.sub(r"^```(?:json)?\n?", "", raw.strip())
            raw = re.sub(r"\n?```$", "", raw.strip())
            
            return response_model.model_validate_json(raw)
        except Exception as e:
            logger.error(f"Structured generation failed: {e}")
            raise

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
