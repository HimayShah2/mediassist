import os
from loguru import logger
from langchain_openai import OpenAIEmbeddings

# Default to the standard local API port used by LM Studio / Ollama
DEFAULT_BASE_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1")

class Embedder:
    def __init__(self):
        logger.info("Connecting to Standalone Local Embeddings Server...")
        self.embed_fn = OpenAIEmbeddings(
            base_url=DEFAULT_BASE_URL,
            api_key="not-needed",
            model=os.getenv("LLM_EMBED_MODEL", "google/gemma-4-e4b"),
            # Local llama.cpp / LM Studio servers expect raw text, not pre-tokenised
            # integer arrays. Disable langchain's tiktoken pre-tokenisation.
            check_embedding_ctx_length=False,
            tiktoken_enabled=False,
        )

    def get_embeddings(self):
        return self.embed_fn
