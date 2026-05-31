from langchain_openai import OpenAIEmbeddings
from nim.nim_key_manager import NIMKeyManager, ModelRole

class Embedder:
    def __init__(self, key_manager: NIMKeyManager):
        self.key_manager = key_manager
        
    def get_embeddings(self) -> OpenAIEmbeddings:
        key = self.key_manager.get_key_for_role(ModelRole.EMBED)
        base = "https://integrate.api.nvidia.com/v1"
        return OpenAIEmbeddings(
            model=self.key_manager.get_model_for_role(ModelRole.EMBED),
            api_key=key.key_value,
            base_url=base,
            check_embedding_ctx_length=False  # Crucial: prevents tiktoken from parsing strings to token arrays
        )
