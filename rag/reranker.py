from loguru import logger
from flashrank import Ranker, RerankRequest

class CrossEncoderReranker:
    def __init__(self, model_name="ms-marco-TinyBERT-L-2-v2"):
        logger.info(f"Loading FlashRank Reranker: {model_name}")
        self.ranker = Ranker(model_name=model_name)

    def rerank(self, query: str, documents: list[dict], top_k: int = 5) -> list[dict]:
        """
        Reranks a list of documents based on a query using FlashRank.
        Expects documents as a list of dicts with 'text' and 'metadata' keys.
        """
        if not documents:
            return []

        # FlashRank expects a list of dicts with 'id' and 'text'
        passages = []
        for i, doc in enumerate(documents):
            passages.append({
                "id": i,
                "text": doc["text"],
                "metadata": doc["metadata"]
            })

        rerank_request = RerankRequest(query=query, passages=passages)
        results = self.ranker.rerank(rerank_request)

        # results is a list of dicts sorted by score, containing the original keys plus 'score'
        reranked_docs = []
        for res in results[:top_k]:
            reranked_docs.append({
                "text": res["text"],
                "metadata": res["metadata"],
                "score": res.get("score", 0.0)
            })

        return reranked_docs
