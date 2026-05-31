"""
MediAssist Pro — PII Field Encryption.

Uses Fernet symmetric encryption from the ``cryptography`` library to
encrypt / decrypt sensitive PII fields (national_id, contact_number, etc.).
The key is loaded from settings or auto-generated and persisted.
"""

from __future__ import annotations

import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from loguru import logger
import keyring

from config.settings import settings

SERVICE_NAME = "MediAssistPro"
USERNAME = "field_encryption_key"

class FieldEncryptor:
    """
    Encrypt and decrypt individual string fields using Fernet.

    The encryption key is resolved in this order:
    1. ``settings.field_encryption_key`` (from env / .env)
    2. Windows Credential Manager via `keyring`
    3. Auto-generated and stored in Windows Credential Manager
    """

    def __init__(self, key: str | None = None) -> None:
        resolved_key = key or self._resolve_key()
        self._fernet = Fernet(resolved_key.encode() if isinstance(resolved_key, str) else resolved_key)
        logger.debug("FieldEncryptor initialised")

    # ── Public API ─────────────────────────────────────────────────────────

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string and return a URL-safe base64 ciphertext.

        Returns the original string unchanged if it is empty.
        """
        if not plaintext:
            return plaintext
        token = self._fernet.encrypt(plaintext.encode("utf-8"))
        return token.decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a Fernet ciphertext token back to plaintext.

        Returns the original string unchanged if it is empty.
        Logs a warning and returns ``"[DECRYPTION_ERROR]"`` on failure.
        """
        if not ciphertext:
            return ciphertext
        try:
            plaintext = self._fernet.decrypt(ciphertext.encode("utf-8"))
            return plaintext.decode("utf-8")
        except InvalidToken:
            logger.warning("Decryption failed — possible key mismatch or corrupted data")
            return "[DECRYPTION_ERROR]"

    # ── Key resolution ─────────────────────────────────────────────────────

    @staticmethod
    def _resolve_key() -> str:
        """Resolve the Fernet key from settings, keyring, or auto-generate."""
        # 1. From settings / env var
        if settings.field_encryption_key:
            logger.debug("Using encryption key from settings")
            return settings.field_encryption_key

        # 2. From Keyring
        stored = keyring.get_password(SERVICE_NAME, USERNAME)
        if stored:
            logger.debug("Using encryption key from Windows Credential Manager")
            return stored

        # 3. Auto-generate and persist
        new_key = Fernet.generate_key().decode("utf-8")
        keyring.set_password(SERVICE_NAME, USERNAME, new_key)
        logger.info("Generated new encryption key and stored in Windows Credential Manager")
        return new_key

    # ── Helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def generate_key() -> str:
        """Generate a fresh Fernet key (useful for admin tooling)."""
        return Fernet.generate_key().decode("utf-8")
