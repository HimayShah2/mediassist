from typing import Optional, Sequence, Any
import httpx
from langchain.callbacks.manager import Callbacks
from langchain.retrievers.document_compressors.base import BaseDocumentCompressor
from langchain.schema import Document
from pydantic import PrivateAttr, Field
from nim.nim_key_manager import NIMKeyManager, ModelRole

class NIMReranker(BaseDocumentCompressor):
    key_manager: Any = Field(description="Key manager for NIM")
    top_n: int = Field(default=5, description="Number of documents to return")
    _base_url: str = PrivateAttr(default="https://integrate.api.nvidia.com/v1")

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        if not documents:
            return []

        key = self.key_manager.get_key_for_role(ModelRole.RERANK)
        model = self.key_manager.get_model_for_role(ModelRole.RERANK)

        headers = {
            "Authorization": f"Bearer {key.key_value}",
            "Content-Type": "application/json"
        }
        
        texts = [doc.page_content for doc in documents]
        
        payload = {
            "model": model,
            "query": {"text": query},
            "passages": [{"text": text} for text in texts]
        }
        
        with httpx.Client(timeout=45.0) as client:
            base = self._base_url
            response = client.post(f"{base}/ranking", headers=headers, json=payload)
            response.raise_for_status()
            
            results = response.json()
            
        rankings = results.get("rankings", [])
        
        reranked_docs = []
        for rank in rankings:
            idx = rank["index"]
            score = rank["logit"]
            doc = documents[idx]
            new_doc = Document(page_content=doc.page_content, metadata=doc.metadata.copy())
            new_doc.metadata["rerank_score"] = score
            reranked_docs.append(new_doc)
            
        return reranked_docs[:self.top_n]
