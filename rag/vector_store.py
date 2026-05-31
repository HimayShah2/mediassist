import chromadb
from chromadb.config import Settings

class ChromaVectorStore:
    def __init__(self, db_path: str):
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
    def get_or_create_collection(self, collection_name: str):
        return self.client.get_or_create_collection(collection_name)
        
    def get_collection(self, collection_name: str):
        return self.client.get_collection(collection_name)
        
    def list_collections(self):
        return self.client.list_collections()
