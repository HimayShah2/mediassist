"""
MediAssist Pro — Database Backup Manager.

Handles creation, listing, and restoration of SQLite database backups.
Backups are timestamped copies stored in ``data/backups/``.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from loguru import logger

from config.settings import settings


class BackupManager:
    """
    Manages database backup lifecycle.

    - ``create_backup()``  — copy the live DB file with a timestamp suffix.
    - ``list_backups()``   — return metadata for all existing backups.
    - ``restore_backup()`` — overwrite the live DB from a backup file.
    """

    def __init__(
        self,
        db_path: str | None = None,
        backup_dir: str | None = None,
    ) -> None:
        self.db_path = Path(db_path or settings.mediassist_db_path)
        self.backup_dir = Path(backup_dir or settings.mediassist_backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    # ── Create ─────────────────────────────────────────────────────────────

    def create_backup(self) -> str:
        """
        Create a timestamped copy of the database file.

        Returns:
            Absolute path to the new backup file.

        Raises:
            FileNotFoundError: If the source database does not exist.
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"mediassist_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(str(self.db_path), str(backup_path))
        logger.info("Backup created: {}", backup_path)

        # Also copy WAL and SHM if present (SQLite WAL mode)
        for suffix in ("-wal", "-shm"):
            wal_path = self.db_path.with_suffix(self.db_path.suffix + suffix)
            if wal_path.exists():
                shutil.copy2(str(wal_path), str(backup_path.with_suffix(backup_path.suffix + suffix)))

        return str(backup_path)

    # ── List ───────────────────────────────────────────────────────────────

    def list_backups(self) -> list[dict[str, str]]:
        """
        Return metadata for every backup in the backup directory.

        Each entry contains:
        - ``filename`` — the backup file name
        - ``path``     — absolute path
        - ``size_mb``  — file size in megabytes (2 decimal places)
        - ``created``  — ISO-format timestamp from the file's mtime

        Results are sorted newest-first.
        """
        backups: list[dict[str, str]] = []
        if not self.backup_dir.exists():
            return backups

        for f in sorted(self.backup_dir.glob("mediassist_backup_*.db"), reverse=True):
            stat = f.stat()
            backups.append(
                {
                    "filename": f.name,
                    "path": str(f.resolve()),
                    "size_mb": f"{stat.st_size / (1024 * 1024):.2f}",
                    "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            )

        return backups

    # ── Restore ────────────────────────────────────────────────────────────

    def restore_backup(self, backup_path: str) -> None:
        """
        Replace the live database with the specified backup.

        A safety backup of the current DB is made first (suffixed ``_pre_restore``).

        Args:
            backup_path: Absolute or relative path to the backup file.

        Raises:
            FileNotFoundError: If the backup file does not exist.
        """
        src = Path(backup_path)
        if not src.exists():
            raise FileNotFoundError(f"Backup file not found: {src}")

        # Safety net: snapshot current DB before overwriting
        if self.db_path.exists():
            safety_name = f"mediassist_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            safety_path = self.backup_dir / safety_name
            shutil.copy2(str(self.db_path), str(safety_path))
            logger.info("Pre-restore safety backup: {}", safety_path)

        shutil.copy2(str(src), str(self.db_path))
        logger.info("Database restored from: {}", src)

        # Restore WAL/SHM companions if they exist beside the backup
        for suffix in ("-wal", "-shm"):
            companion = src.with_suffix(src.suffix + suffix)
            if companion.exists():
                shutil.copy2(str(companion), str(self.db_path.with_suffix(self.db_path.suffix + suffix)))
            else:
                # Remove stale WAL/SHM from the live location
                live_companion = self.db_path.with_suffix(self.db_path.suffix + suffix)
                if live_companion.exists():
                    live_companion.unlink()
