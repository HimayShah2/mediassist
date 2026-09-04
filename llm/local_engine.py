"""
LocalLlamaClient — in-process LLM using llama-cpp-python directly.

No separate server, no HTTP port, no subprocess. This is what a non-technical
user gets: they run one executable and everything works. Power users can still
set LLM_BASE_URL to use an external OpenAI-compatible server (see AppController).
"""
import os
import re
import json
import threading
from loguru import logger

from .model_bootstrap import resolve_model_path

_LOCK = threading.Lock()


class LocalLlamaClient:
    _llm = None  # class-level: load the model once per process

    def __init__(self, model_path: str = None, n_ctx: int = 4096):
        self.model_path = model_path or resolve_model_path()
        self.n_ctx = n_ctx
        if LocalLlamaClient._llm is None:
            self._load()

    def _load(self):
        from llama_cpp import Llama
        logger.info(f"Loading local model: {self.model_path}")
        n_threads = max(2, (os.cpu_count() or 4) - 2)
        LocalLlamaClient._llm = Llama(
            model_path=self.model_path,
            n_ctx=self.n_ctx,
            n_threads=n_threads,
            n_batch=512,
            verbose=False,
        )
        logger.info("Local model ready.")

    # ------------------------------------------------------------------ #
    @property
    def llm(self):
        if LocalLlamaClient._llm is None:
            self._load()
        return LocalLlamaClient._llm

    @staticmethod
    def _strip_fences(raw: str) -> str:
        raw = (raw or "").strip()
        raw = re.sub(r"^```(?:json)?\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
        return raw.strip()

    def _chat(self, messages, max_tokens, temperature, response_format=None):
        kwargs = dict(messages=messages, max_tokens=max_tokens, temperature=temperature)
        if response_format:
            kwargs["response_format"] = response_format
        with _LOCK:  # llama_cpp.Llama is not safe for concurrent calls
            out = self.llm.create_chat_completion(**kwargs)
        return out["choices"][0]["message"]["content"]

    async def generate_structured(self, response_model, messages, max_tokens=1024, temperature=0.1):
        schema = response_model.model_json_schema()
        try:
            from llm.server_client import _tighten_question_schema
            _tighten_question_schema(schema)
        except Exception:
            pass

        schema_str = json.dumps(schema, separators=(",", ":"))
        msgs = list(messages)
        hint = ("\n\nReply with ONE compact JSON object matching this schema (no whitespace, "
                "no newlines, no markdown fences, no prose):\n" + schema_str)
        if msgs and msgs[0].get("role") == "system":
            msgs = [{**msgs[0], "content": msgs[0]["content"] + hint}] + msgs[1:]
        else:
            msgs = [{"role": "system", "content": hint.strip()}] + msgs

        # Attempt 1: JSON-syntax mode only (no schema grammar) — ~4x faster on a
        # small CPU model; pydantic + the model validators catch structural issues.
        try:
            raw = self._chat(msgs, max_tokens, temperature,
                             response_format={"type": "json_object"})
            return response_model.model_validate_json(self._strip_fences(raw))
        except Exception as e:
            logger.warning(f"Fast JSON parse failed ({str(e)[:150]}); retrying with grammar-constrained decode.")

        # Attempt 2: full grammar-constrained decode — slower but guarantees the shape.
        raw = self._chat(msgs, max_tokens, temperature,
                         response_format={"type": "json_object", "schema": schema})
        return response_model.model_validate_json(self._strip_fences(raw))

    async def generate_text(self, messages, max_tokens=2048, temperature=0.3):
        return self._chat(list(messages), max_tokens, temperature)
