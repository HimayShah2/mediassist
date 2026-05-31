"""
NIM API Key Manager for MediAssist Pro.

Manages 7 NVIDIA NIM API keys with role-based routing, health tracking,
rate limiting, cooldown recovery, and offline fallback mode.

Key Roles:
    Key 0 — embed: embedding calls (nvidia/nv-embed-v1)
    Key 1 — fast: fast inference (meta/llama-3.1-8b-instruct)
    Key 2 — standard_a: standard inference primary (meta/llama-3.3-70b-instruct)
    Key 3 — standard_b: standard inference secondary (meta/llama-3.3-70b-instruct)
    Key 4 — medical_a: medical inference primary (google/gemma-2-27b-it)
    Key 5 — medical_b: medical inference secondary (google/gemma-2-27b-it)
    Key 6 — complex: complex/reasoning inference (meta/llama-3.1-405b-instruct)
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from dotenv import load_dotenv


class KeyRole(str, Enum):
    """Enum for NIM API key roles."""

    EMBED = "embed"
    FAST = "fast"
    STANDARD = "standard"
    MEDICAL = "medical"
    COMPLEX = "complex"


# Maps each role to the NVIDIA model to use
ROLE_MODEL_MAP: dict[KeyRole, str] = {
    KeyRole.EMBED: "nvidia/nv-embed-v1",
    KeyRole.FAST: "meta/llama-3.1-8b-instruct",
    KeyRole.STANDARD: "meta/llama-3.3-70b-instruct",
    KeyRole.MEDICAL: "google/gemma-2-27b-it",
    KeyRole.COMPLEX: "meta/llama-3.1-405b-instruct",
}

# Maps each role to primary key index(es) and fallback order
ROLE_KEY_INDICES: dict[KeyRole, list[int]] = {
    KeyRole.EMBED: [0],
    KeyRole.FAST: [1],
    KeyRole.STANDARD: [2, 3],
    KeyRole.MEDICAL: [4, 5],
    KeyRole.COMPLEX: [6],
}

REQUIRED_KEY_COUNT = 7
DEFAULT_RATE_LIMIT_PER_MINUTE = 50
COOLDOWN_SECONDS = 60.0


@dataclass
class KeyState:
    """Tracks the state of a single API key."""

    key: str
    index: int
    healthy: bool = True
    call_count: int = 0
    last_call_time: float = 0.0
    last_failure_time: float = 0.0
    calls_this_minute: int = 0
    minute_window_start: float = 0.0

    def record_call(self) -> None:
        """Record a successful API call for this key."""
        now = time.time()
        self.call_count += 1
        self.last_call_time = now

        # Reset minute window if needed
        if now - self.minute_window_start >= 60.0:
            self.calls_this_minute = 0
            self.minute_window_start = now
        self.calls_this_minute += 1

    def is_rate_limited(self, limit: int = DEFAULT_RATE_LIMIT_PER_MINUTE) -> bool:
        """Check if this key has exceeded its per-minute rate limit."""
        now = time.time()
        if now - self.minute_window_start >= 60.0:
            return False
        return self.calls_this_minute >= limit

    def mark_unhealthy(self) -> None:
        """Mark this key as unhealthy."""
        self.healthy = False
        self.last_failure_time = time.time()

    def check_cooldown_recovery(self, cooldown: float = COOLDOWN_SECONDS) -> bool:
        """Check if cooldown has elapsed and recover if so. Returns True if recovered."""
        if self.healthy:
            return False
        now = time.time()
        if now - self.last_failure_time >= cooldown:
            self.healthy = True
            self.calls_this_minute = 0
            return True
        return False


class NIMKeyManager:
    """
    Manages 7 NVIDIA NIM API keys with role-based routing and health tracking.

    Usage:
        manager = NIMKeyManager()  # loads from .env
        key = manager.get_key(KeyRole.MEDICAL)
        model = manager.model_for_role(KeyRole.MEDICAL)
    """

    def __init__(
        self,
        keys: Optional[list[str]] = None,
        env_path: Optional[str] = None,
        rate_limit: int = DEFAULT_RATE_LIMIT_PER_MINUTE,
        cooldown: float = COOLDOWN_SECONDS,
    ):
        """
        Initialize the key manager.

        Args:
            keys: Optional list of 7 API keys. If None, loads from environment.
            env_path: Optional path to .env file.
            rate_limit: Max calls per minute per key.
            cooldown: Seconds before an unhealthy key is retried.
        """
        self.rate_limit = rate_limit
        self.cooldown = cooldown
        self._offline_mode = False

        if keys is not None:
            raw_keys = keys
        else:
            if env_path:
                load_dotenv(env_path)
            else:
                load_dotenv()
            raw_keys = []
            for i in range(1, 8):
                k = os.environ.get(f"NIM_API_KEY_{i}", "")
                raw_keys.append(k)

        # Validate we have exactly 7 non-empty keys
        non_empty = [k for k in raw_keys if k and k.strip()]
        if len(non_empty) < REQUIRED_KEY_COUNT:
            raise ValueError(
                f"NIM Key Manager requires {REQUIRED_KEY_COUNT} API keys, "
                f"got {len(non_empty)} non-empty keys."
            )

        self._keys: list[KeyState] = [
            KeyState(key=raw_keys[i], index=i) for i in range(REQUIRED_KEY_COUNT)
        ]

    @property
    def offline_mode(self) -> bool:
        """True if all keys are exhausted/unhealthy."""
        return self._offline_mode

    def get_key(self, role: KeyRole) -> str:
        """
        Get an API key for the given role.

        Uses the primary key index for the role. If unhealthy, tries
        fallback indices. If all are unhealthy, checks cooldown recovery.
        If everything is exhausted, enters offline mode.

        Args:
            role: The KeyRole to get a key for.

        Returns:
            API key string.

        Raises:
            RuntimeError: If all keys for the role are exhausted.
        """
        indices = ROLE_KEY_INDICES[role]

        # First pass: try healthy, non-rate-limited keys
        for idx in indices:
            ks = self._keys[idx]
            ks.check_cooldown_recovery(self.cooldown)
            if ks.healthy and not ks.is_rate_limited(self.rate_limit):
                return ks.key

        # Second pass: try healthy but rate-limited keys (still return them)
        for idx in indices:
            ks = self._keys[idx]
            if ks.healthy:
                return ks.key

        # Third pass: check cooldown recovery
        for idx in indices:
            ks = self._keys[idx]
            if ks.check_cooldown_recovery(self.cooldown):
                return ks.key

        # All keys for this role are unhealthy — check if ALL keys are down
        all_unhealthy = all(not ks.healthy for ks in self._keys)
        if all_unhealthy:
            self._offline_mode = True

        raise RuntimeError(
            f"All API keys for role '{role.value}' are exhausted or unhealthy."
        )

    def record_usage(self, role: KeyRole, key_index: Optional[int] = None) -> None:
        """
        Record a successful API call.

        Args:
            role: The role that was used.
            key_index: Optional specific key index. If None, uses first
                       healthy key for the role.
        """
        if key_index is not None:
            self._keys[key_index].record_call()
            return

        indices = ROLE_KEY_INDICES[role]
        for idx in indices:
            if self._keys[idx].healthy:
                self._keys[idx].record_call()
                return

    def mark_unhealthy(self, key_index: int) -> None:
        """Mark a specific key as unhealthy by index."""
        if 0 <= key_index < len(self._keys):
            self._keys[key_index].mark_unhealthy()

    def model_for_role(self, role: KeyRole) -> str:
        """Get the NVIDIA model name for a given role."""
        return ROLE_MODEL_MAP[role]

    def get_key_state(self, index: int) -> KeyState:
        """Get the state of a key by index."""
        return self._keys[index]

    def health_status(self) -> dict[int, bool]:
        """Return health status of all keys as {index: healthy}."""
        return {ks.index: ks.healthy for ks in self._keys}

    def all_keys_healthy(self) -> bool:
        """Check if all keys are healthy."""
        return all(ks.healthy for ks in self._keys)

    def get_consumption(self, index: int) -> int:
        """Get total call count for a key by index."""
        return self._keys[index].call_count
