"""Saves email attachments to categorised local directories."""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Characters not allowed in filenames on common operating systems
_UNSAFE = re.compile(r'[/\\:*?"<>|\x00-\x1f]')
_MAX_FILENAME_LEN = 200


class AttachmentStore:
    """Persists attachment bytes to ``{base_dir}/{category}/{email_id}/{filename}``."""

    def __init__(self, base_dir: str = "attachments") -> None:
        self._base = Path(base_dir)

    def save_attachment(
        self,
        data: bytes,
        filename: str,
        category: str,
        email_id: str,
    ) -> Path:
        """Write *data* to disk and return the absolute path.

        Args:
            data: Raw bytes of the attachment.
            filename: Original filename from the email.
            category: Subdirectory name (``work``, ``personal``, etc.).
            email_id: Gmail message ID — used as a sub-folder so that
                multiple attachments from the same email stay together.

        Returns:
            The absolute :class:`Path` of the written file.
        """
        safe_name = self._sanitize(filename)
        dest_dir = self._base / category / email_id
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest = dest_dir / safe_name
        # Avoid silently overwriting an existing file with a different name
        if dest.exists():
            stem = Path(safe_name).stem
            suffix = Path(safe_name).suffix
            dest = dest_dir / f"{stem}_dup{suffix}"

        dest.write_bytes(data)
        logger.debug("Wrote %d bytes → %s", len(data), dest)
        return dest.resolve()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _sanitize(filename: str) -> str:
        """Remove path-traversal and OS-unsafe characters from *filename*."""
        # Strip directory component (path traversal)
        name = os.path.basename(filename)
        # Replace unsafe characters with underscores
        name = _UNSAFE.sub("_", name)
        # Trim to a safe length
        if len(name) > _MAX_FILENAME_LEN:
            stem = Path(name).stem[: _MAX_FILENAME_LEN - 10]
            suffix = Path(name).suffix[:10]
            name = stem + suffix
        return name or "attachment"
