import os
import json
import numpy as np
from loguru import logger

class ChromaVectorStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(self.db_path, exist_ok=True)
        self.db_file = os.path.join(self.db_path, "vectors_v2.json")
        self.collections = {}
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.collections = json.load(f)
                logger.info(f"Loaded PurePython Vector Store from {self.db_file}")
            except Exception as e:
                logger.error(f"Failed to load vector store: {e}")

    def _save(self):
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.collections, f)
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")

    def get_or_create_collection(self, name: str):
        if name not in self.collections:
            self.collections[name] = {"documents": [], "embeddings": [], "metadatas": [], "ids": []}
            self._save()
        return CollectionProxy(self, name)

    def get_collection(self, name: str):
        if name not in self.collections:
            raise ValueError(f"Collection {name} not found")
        return CollectionProxy(self, name)

    def list_collections(self):
        class _Col:
            def __init__(self, n, proxy):
                self.name = n
                self._proxy = proxy
            def count(self):
                return self._proxy.count()
        return [_Col(name, CollectionProxy(self, name)) for name in self.collections.keys()]

class CollectionProxy:
    def __init__(self, store: ChromaVectorStore, name: str):
        self.store = store
        self.name = name

    def upsert(self, documents, embeddings, metadatas, ids):
        col = self.store.collections[self.name]
        for doc, emb, meta, doc_id in zip(documents, embeddings, metadatas, ids):
            if doc_id in col["ids"]:
                idx = col["ids"].index(doc_id)
                col["documents"][idx] = doc
                col["embeddings"][idx] = emb
                col["metadatas"][idx] = meta
            else:
                col["ids"].append(doc_id)
                col["documents"].append(doc)
                col["embeddings"].append(emb)
                col["metadatas"].append(meta)
        self.store._save()

    def query(self, query_embeddings, n_results=10):
        col = self.store.collections[self.name]
        if not col["embeddings"]:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        A = np.array(query_embeddings[0])
        B = np.array(col["embeddings"])
        
        A_norm = np.linalg.norm(A)
        B_norms = np.linalg.norm(B, axis=1)
        
        # cosine similarity
        similarities = np.dot(B, A) / (A_norm * B_norms + 1e-9)
        # convert similarity to distance (0 = identical, 2 = opposite)
        distances = 1.0 - similarities
        
        top_indices = np.argsort(distances)[:n_results]
        
        return {
            "documents": [[col["documents"][i] for i in top_indices]],
            "metadatas": [[col["metadatas"][i] for i in top_indices]],
            "distances": [[float(distances[i]) for i in top_indices]]
        }

    def count(self):
        return len(self.store.collections[self.name]["ids"])
