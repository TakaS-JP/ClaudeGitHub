"""Data-classes representing Gmail messages and attachments."""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AttachmentMeta:
    """Metadata for a single email attachment (no binary data)."""

    filename: str
    mime_type: str
    size: int
    attachment_id: str


@dataclass
class EmailMessage:
    """Full representation of a Gmail message including decoded body."""

    id: str
    thread_id: str
    subject: str
    sender: str
    recipients: list[str]
    date: datetime
    snippet: str
    body_text: str
    body_html: str
    label_ids: list[str]
    attachments: list[AttachmentMeta] = field(default_factory=list)


@dataclass
class MessageSummary:
    """Lightweight summary returned by list_messages (no body fetch)."""

    id: str
    subject: str
    sender: str
    date: datetime
    snippet: str
    has_attachments: bool
    label_ids: list[str]
