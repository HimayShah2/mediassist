import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any
from loguru import logger

class ModelRole(str, Enum):
    EMBED = "embed"
    RERANK = "rerank"
    FAST = "fast"
    STANDARD = "standard"
    MEDICAL = "medical"
    COMPLEX = "complex"
    EFFICIENT = "efficient"
    CODER = "coder"
    FALLBACK = "fallback"

@dataclass
class APIKey:
    key_id: int
    key_value: str
    provider: str
    base_url: Optional[str] = None
    is_healthy: bool = True
    last_failure_time: float = 0.0
    failure_count: int = 0
    total_calls: int = 0
    last_used_time: float = 0.0

    def mark_unhealthy(self) -> None:
        self.is_healthy = False
        self.last_failure_time = time.time()
        self.failure_count += 1
        logger.warning(f"{self.provider} API key {self.key_id} marked unhealthy")

    def maybe_recover(self) -> None:
        if not self.is_healthy:
            if time.time() - self.last_failure_time >= 120.0:
                self.is_healthy = True
                logger.info(f"{self.provider} API key {self.key_id} recovered")

    def record_use(self) -> None:
        self.total_calls += 1
        self.last_used_time = time.time()

class LLMProviderManager:
    def __init__(self, api_keys: list[Any]) -> None:
        self._keys: list[APIKey] = []
        for idx, k in enumerate(api_keys):
            if isinstance(k, dict):
                self._keys.append(APIKey(
                    key_id=idx+1, 
                    provider=k.get("provider", "Unknown"), 
                    key_value=k.get("key", ""),
                    base_url=k.get("base_url")
                ))
            elif isinstance(k, str) and k:
                self._keys.append(APIKey(key_id=idx+1, provider="NVIDIA NIM", key_value=k))
        
        self._key_map = {k.key_id: k for k in self._keys}
        logger.info(f"LLMProviderManager initialised with {len(self._keys)} multi-provider keys")

    def get_key_for_role(self, role: ModelRole) -> Optional[APIKey]:
        for k in self._keys:
            k.maybe_recover()
            
        healthy = [k for k in self._keys if k.is_healthy]
        if healthy:
            chosen = min(healthy, key=lambda k: k.last_used_time)
            chosen.record_use()
            return chosen
        return None

    def get_model_for_role(self, role: ModelRole) -> str:
        ROLE_MODEL_MAP = {
            ModelRole.EMBED: "nvidia/nv-embedqa-e5-v5",
            ModelRole.RERANK: "nvidia/nv-rerankqa-mistral-4b-v3",
            ModelRole.FAST: "meta/llama3-8b-instruct",
            ModelRole.STANDARD: "meta/llama3-70b-instruct",
            ModelRole.MEDICAL: "meta/llama3-70b-instruct",
            ModelRole.COMPLEX: "meta/llama3-70b-instruct",
            ModelRole.EFFICIENT: "meta/llama3-8b-instruct",
            ModelRole.CODER: "meta/llama3-70b-instruct",
            ModelRole.FALLBACK: "meta/llama3-8b-instruct",
        }
        return ROLE_MODEL_MAP.get(role, "meta/llama3-8b-instruct")

    def mark_key_unhealthy(self, key_id: int) -> None:
        if key_id in self._key_map:
            self._key_map[key_id].mark_unhealthy()

    def is_offline(self) -> bool:
        for k in self._keys:
            k.maybe_recover()
        return not any(k.is_healthy for k in self._keys)

    def health_status(self) -> dict[str, object]:
        for k in self._keys:
            k.maybe_recover()
        unhealthy_ids = [k.key_id for k in self._keys if not k.is_healthy]
        return {
            "total_keys": len(self._keys),
            "healthy_keys": len(self._keys) - len(unhealthy_ids),
            "unhealthy_keys": unhealthy_ids,
            "total_calls": sum(k.total_calls for k in self._keys),
            "is_offline": self.is_offline(),
        }
