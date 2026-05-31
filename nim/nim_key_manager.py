"""
MediAssist Pro — NIM API Key Manager (Blueprint §5.3).

Manages a pool of 7 NVIDIA NIM API keys, assigns them to model roles
with affinity, tracks health, and provides round-robin failover.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from loguru import logger


# ═══════════════════════════════════════════════════════════════════════════
# Model Roles
# ═══════════════════════════════════════════════════════════════════════════
class ModelRole(str, Enum):
    """Roles that map to specific NIM model endpoints."""

    EMBED = "embed"
    RERANK = "rerank"
    FAST = "fast"
    STANDARD = "standard"
    MEDICAL = "medical"
    COMPLEX = "complex"
    EFFICIENT = "efficient"
    CODER = "coder"
    FALLBACK = "fallback"


# ═══════════════════════════════════════════════════════════════════════════
# Role → Model mapping
# ═══════════════════════════════════════════════════════════════════════════
ROLE_MODEL_MAP: dict[ModelRole, str] = {
    ModelRole.EMBED: "nvidia/nv-embed-v1",
    ModelRole.RERANK: "nvidia/nv-rerank-qa-mistral-4b:1",
    ModelRole.FAST: "meta/llama-3.3-8b-instruct",
    ModelRole.STANDARD: "meta/llama-3.3-70b-instruct",
    ModelRole.MEDICAL: "nvidia/llama-3.1-nemotron-70b-instruct",
    ModelRole.COMPLEX: "z-ai/glm-5.1",
    ModelRole.EFFICIENT: "minimaxai/minimax-m2.1",
    ModelRole.CODER: "qwen/qwen2.5-coder-32b-instruct",
    ModelRole.FALLBACK: "mistralai/mixtral-8x7b-instruct-v0.1",
}


# ═══════════════════════════════════════════════════════════════════════════
# Role → preferred key indices (1-based, matching NIM_API_KEY_N)
# Distributes load across the 7 keys so heavy roles don't starve others.
# ═══════════════════════════════════════════════════════════════════════════
ROLE_KEY_AFFINITY: dict[ModelRole, list[int]] = {
    ModelRole.EMBED: [1, 2],
    ModelRole.RERANK: [2, 3],
    ModelRole.FAST: [3, 4],
    ModelRole.STANDARD: [4, 5],
    ModelRole.MEDICAL: [5, 6],
    ModelRole.COMPLEX: [6, 7],
    ModelRole.EFFICIENT: [7, 1],
    ModelRole.CODER: [1, 2],
    ModelRole.FALLBACK: [2, 3],
}

# Cooldown period (seconds) before an unhealthy key is retried
_HEALTH_COOLDOWN_SECONDS = 120.0


# ═══════════════════════════════════════════════════════════════════════════
# APIKey dataclass
# ═══════════════════════════════════════════════════════════════════════════
@dataclass
class APIKey:
    """Tracks the runtime state of a single NIM API key."""

    key_id: int
    key_value: str
    is_healthy: bool = True
    last_failure_time: float = 0.0
    failure_count: int = 0
    total_calls: int = 0
    last_used_time: float = 0.0

    def mark_unhealthy(self) -> None:
        """Flag this key as unhealthy after a failure."""
        self.is_healthy = False
        self.last_failure_time = time.time()
        self.failure_count += 1
        logger.warning(
            "API key {} marked unhealthy (failures={})",
            self.key_id,
            self.failure_count,
        )

    def maybe_recover(self) -> None:
        """Re-enable the key if the cooldown period has elapsed."""
        if not self.is_healthy:
            elapsed = time.time() - self.last_failure_time
            if elapsed >= _HEALTH_COOLDOWN_SECONDS:
                self.is_healthy = True
                logger.info(
                    "API key {} recovered after {:.0f}s cooldown",
                    self.key_id,
                    elapsed,
                )

    def record_use(self) -> None:
        """Increment counters after a successful use."""
        self.total_calls += 1
        self.last_used_time = time.time()


# ═══════════════════════════════════════════════════════════════════════════
# NIMKeyManager
# ═══════════════════════════════════════════════════════════════════════════
class NIMKeyManager:
    """
    Manages a pool of NVIDIA NIM API keys.

    - Assigns keys to roles using affinity preferences.
    - Falls back to any healthy key when preferred keys are exhausted.
    - Tracks health and auto-recovers after cooldown.
    """

    def __init__(self, api_keys: list[str]) -> None:
        """
        Args:
            api_keys: Ordered list of NIM API key strings (index 0 → key_id 1).
        """
        if not api_keys:
            logger.warning("NIMKeyManager initialised with no API keys — running in offline-only mode")

        self._keys: list[APIKey] = [
            APIKey(key_id=idx + 1, key_value=key)
            for idx, key in enumerate(api_keys)
            if key  # skip empty strings
        ]
        self._key_map: dict[int, APIKey] = {k.key_id: k for k in self._keys}
        logger.info("NIMKeyManager initialised with {} keys", len(self._keys))

    # ── Public API ─────────────────────────────────────────────────────────

    def get_key_for_role(self, role: ModelRole) -> Optional[APIKey]:
        """
        Return the best available API key for *role*.

        Preference order:
        1. Healthy keys in the role's affinity list (round-robin by usage).
        2. Any healthy key (least recently used).
        3. ``None`` if all keys are down.
        """
        # Attempt recovery on cooldown-eligible keys
        for k in self._keys:
            k.maybe_recover()

        affinity_ids = ROLE_KEY_AFFINITY.get(role, [])

        # 1. Try affinity keys
        affinity_candidates = [
            self._key_map[kid]
            for kid in affinity_ids
            if kid in self._key_map and self._key_map[kid].is_healthy
        ]
        if affinity_candidates:
            chosen = min(affinity_candidates, key=lambda k: k.last_used_time)
            chosen.record_use()
            logger.debug(
                "Role {} → affinity key {} (calls={})",
                role.value,
                chosen.key_id,
                chosen.total_calls,
            )
            return chosen

        # 2. Fallback to any healthy key
        healthy = [k for k in self._keys if k.is_healthy]
        if healthy:
            chosen = min(healthy, key=lambda k: k.last_used_time)
            chosen.record_use()
            logger.debug(
                "Role {} → fallback key {} (calls={})",
                role.value,
                chosen.key_id,
                chosen.total_calls,
            )
            return chosen

        logger.error("No healthy API keys available for role {}", role.value)
        return None

    def get_model_for_role(self, role: ModelRole) -> str:
        """Return the NIM model identifier for *role*."""
        model = ROLE_MODEL_MAP.get(role)
        if model is None:
            raise ValueError(f"Unknown model role: {role}")
        return model

    def mark_key_unhealthy(self, key_id: int) -> None:
        """Mark a specific key as unhealthy by its 1-based ID."""
        api_key = self._key_map.get(key_id)
        if api_key:
            api_key.mark_unhealthy()
        else:
            logger.warning("Attempted to mark unknown key_id={} unhealthy", key_id)

    def is_offline(self) -> bool:
        """Return ``True`` when **no** healthy keys exist."""
        for k in self._keys:
            k.maybe_recover()
        return not any(k.is_healthy for k in self._keys)

    def health_status(self) -> dict[str, object]:
        """
        Return a summary dict suitable for display in a status bar.

        Example::

            {
                "total_keys": 7,
                "healthy_keys": 5,
                "unhealthy_keys": [3, 6],
                "total_calls": 142,
                "is_offline": False,
            }
        """
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

    # ── Internals ──────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        healthy = sum(1 for k in self._keys if k.is_healthy)
        return f"<NIMKeyManager keys={len(self._keys)} healthy={healthy}>"
