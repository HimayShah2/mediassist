from pathlib import Path
import hashlib
from loguru import logger
from langchain.schema import Document
from nim.nim_key_manager import NIMKeyManager, ModelRole

from rag.vector_store import ChromaVectorStore
from rag.chunker import Chunker
from rag.document_loader_factory import DocumentLoaderFactory
from rag.embedder import Embedder
from rag.reranker import NIMReranker
from rag.web_search import DuckDuckGoSearcher

class DocumentManager:
    CHUNK_SIZE    = 800
    CHUNK_OVERLAP = 120
    TOP_K_RETRIEVE = 15
    TOP_K_RERANK   = 5
    MIN_SIMILARITY = 0.75

    def __init__(self, key_manager: NIMKeyManager, db_path: str):
        self.key_manager = key_manager
        self.vector_store = ChromaVectorStore(db_path)
        self.chunker = Chunker(chunk_size=self.CHUNK_SIZE, chunk_overlap=self.CHUNK_OVERLAP)
        self.embedder_factory = Embedder(key_manager)
        self.reranker = NIMReranker(key_manager=key_manager, top_n=self.TOP_K_RERANK)
        self.web_searcher = DuckDuckGoSearcher()

    def _get_embedder(self):
        return self.embedder_factory.get_embeddings()

    def _chunk_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def ingest_document(self, file_path: str, collection: str,
                         specialty_tags: list[str] = None,
                         document_type: str = "guideline") -> dict:
        path = Path(file_path)
        loader = DocumentLoaderFactory.get_loader(file_path)

        docs   = loader.load()
        return self._process_and_upsert(docs, path.name, collection, specialty_tags, document_type)

    def ingest_url(self, url: str, collection: str,
                    specialty_tags: list[str] = None,
                    document_type: str = "web_subscription") -> dict:
        from langchain_community.document_loaders import WebBaseLoader
        
        logger.info(f"Ingesting URL: {url} → {collection}")
        loader = WebBaseLoader(url)
        docs = loader.load()
        
        source_name = url.split("//")[-1].replace("/", "_")[:50]
        return self._process_and_upsert(docs, f"URL: {source_name}", collection, specialty_tags, document_type)

    def _process_and_upsert(self, docs, source_name, collection, specialty_tags, document_type):
        chunks = self.chunker.split_documents(docs)
        texts, metas, ids = [], [], []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{source_name}_{i}_{self._chunk_hash(chunk.page_content)}"
            chunk.metadata.update({
                "source_file":    source_name,
                "document_type":  document_type,
                "specialty_tags": ",".join(specialty_tags or []),
                "chunk_index":    i,
                "chunk_id":       chunk_id
            })
            texts.append(chunk.page_content)
            metas.append(chunk.metadata)
            ids.append(chunk_id)

        embedder   = self._get_embedder()
        embeddings = embedder.embed_documents(texts)
        col = self.vector_store.get_or_create_collection(collection)
        col.upsert(documents=texts, embeddings=embeddings, metadatas=metas, ids=ids)
        logger.info(f"Ingested {len(chunks)} chunks from {source_name} → {collection}")
        return {"chunks_added": len(chunks), "collection": collection, "source": source_name}

    async def retrieve(self, query: str, collections: list[str], n_results: int = None, trusted_sites: list[str] = None) -> list[dict]:
        n   = n_results or self.TOP_K_RETRIEVE
        emb = self._get_embedder()
        q_embedding = emb.embed_query(query)
        all_results = []

        for col_name in collections:
            try:
                col = self.vector_store.get_collection(col_name)
                res = col.query(query_embeddings=[q_embedding],
                                n_results=min(n, col.count()))
                if not res["documents"] or not res["documents"][0]:
                    continue
                for doc, meta, dist in zip(res["documents"][0],
                                           res["metadatas"][0],
                                           res["distances"][0]):
                    # Filter by minimum similarity (convert distance to similarity)
                    similarity = 1.0 - dist
                    if similarity >= self.MIN_SIMILARITY:
                        all_results.append({
                            "text": doc, "metadata": meta,
                            "similarity": round(similarity, 4),
                            "collection": col_name
                        })
            except Exception as e:
                logger.warning(f"Collection {col_name} retrieval error: {e}")
                continue

        # If no results found in local RAG, fallback to web search
        if not all_results:
            logger.warning(f"No local results for '{query}'. Falling back to web search.")
            web_results = await self.web_searcher.search(query, trusted_sites=trusted_sites, max_results=5)
            all_results.extend(web_results)

        sorted_results = sorted(all_results, key=lambda x: x["similarity"], reverse=True)
        top_results = sorted_results[:n]
        
        if top_results:
            try:
                docs = [Document(page_content=r["text"], metadata=r["metadata"]) for r in top_results]
                compressed_docs = self.reranker.compress_documents(docs, query)
                
                reranked_results = []
                for doc in compressed_docs:
                    orig = next((r for r in top_results if r["text"] == doc.page_content), None)
                    if orig:
                        orig["rerank_score"] = doc.metadata.get("rerank_score")
                        reranked_results.append(orig)
                
                top_results = reranked_results
            except Exception as e:
                logger.warning(f"Reranking error: {e}")
                top_results = top_results[:self.TOP_K_RERANK]
                
        return top_results

    def get_stats(self) -> dict:
        """Returns collection sizes for admin dashboard."""
        stats = {}
        for col in self.vector_store.list_collections():
            stats[col.name] = col.count()
        return stats
