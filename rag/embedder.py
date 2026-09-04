import os
from loguru import logger


class _OnnxMiniLMEmbeddings:
    """LangChain-style embedding wrapper around chromadb's bundled ONNX MiniLM
    (all-MiniLM-L6-v2, 384-dim). Runs locally on CPU via onnxruntime — no server,
    no torch. Model downloads once (~80 MB) then is cached."""

    def __init__(self):
        from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2
        self._ef = ONNXMiniLM_L6_V2()

    def embed_documents(self, texts):
        return [list(map(float, v)) for v in self._ef(list(texts))]

    def embed_query(self, text):
        return list(map(float, self._ef([text])[0]))


class _ServerEmbeddings:
    """Fallback: OpenAI-compatible embeddings from the local LLM server
    (only works if that server was started with --embedding true)."""

    def __init__(self):
        from langchain_openai import OpenAIEmbeddings
        base = os.getenv("LLM_BASE_URL", "http://127.0.0.1:1234/v1")
        self._e = OpenAIEmbeddings(
            base_url=base, api_key="not-needed",
            model=os.getenv("LLM_EMBED_MODEL", "google/gemma-4-e4b"),
            check_embedding_ctx_length=False, tiktoken_enabled=False,
        )

    def embed_documents(self, texts):
        return self._e.embed_documents(list(texts))

    def embed_query(self, text):
        return self._e.embed_query(text)


class Embedder:
    def __init__(self):
        self._impl = None
        try:
            self._impl = _OnnxMiniLMEmbeddings()
            logger.info("Embeddings: local ONNX MiniLM-L6-v2 (CPU, no server).")
        except Exception as e:
            logger.warning(f"ONNX MiniLM embeddings unavailable ({e}); trying LLM server embeddings.")
            try:
                self._impl = _ServerEmbeddings()
            except Exception as e2:
                logger.error(f"No embedding backend available: {e2}")
                self._impl = None

    def get_embeddings(self):
        if self._impl is None:
            raise RuntimeError("No embedding backend is available.")
        return self._impl
