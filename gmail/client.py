"""Gmail API wrapper providing all operations needed by the agent."""
from __future__ import annotations

import base64
import email as email_lib
import logging
import re
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from googleapiclient.errors import HttpError

from gmail.models import AttachmentMeta, EmailMessage, MessageSummary

logger = logging.getLogger(__name__)

_HEADER_RE = re.compile(r"[^\x20-\x7E]")  # non-ASCII chars in header values


def _get_header(headers: list[dict], name: str) -> str:
    """Return the first value matching *name* (case-insensitive), or ''."""
    name_lower = name.lower()
    for h in headers:
        if h.get("name", "").lower() == name_lower:
            return h.get("value", "")
    return ""


def _parse_date(raw: str) -> datetime:
    """Best-effort parse of an RFC 2822 date string."""
    try:
        import email.utils as email_utils

        tup = email_utils.parsedate_tz(raw)
        if tup:
            ts = email_utils.mktime_tz(tup)
            return datetime.fromtimestamp(ts, tz=timezone.utc)
    except Exception:
        pass
    return datetime.now(tz=timezone.utc)


def _decode_body(part: dict) -> str:
    """Base64url-decode a message part body."""
    data = part.get("body", {}).get("data", "")
    if not data:
        return ""
    try:
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    except Exception:
        return ""


def _extract_body(payload: dict) -> tuple[str, str]:
    """Recursively extract plain-text and HTML body from a MIME payload."""
    text_parts: list[str] = []
    html_parts: list[str] = []

    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":
        text_parts.append(_decode_body(payload))
    elif mime_type == "text/html":
        html_parts.append(_decode_body(payload))
    elif mime_type.startswith("multipart/"):
        for part in payload.get("parts", []):
            t, h = _extract_body(part)
            text_parts.append(t)
            html_parts.append(h)

    return "".join(text_parts), "".join(html_parts)


def _collect_attachments(payload: dict) -> list[AttachmentMeta]:
    """Walk the MIME tree and collect attachment metadata."""
    attachments: list[AttachmentMeta] = []
    filename = payload.get("filename")
    body = payload.get("body", {})
    attachment_id = body.get("attachmentId")

    if filename and attachment_id:
        attachments.append(
            AttachmentMeta(
                filename=filename,
                mime_type=payload.get("mimeType", "application/octet-stream"),
                size=body.get("size", 0),
                attachment_id=attachment_id,
            )
        )

    for part in payload.get("parts", []):
        attachments.extend(_collect_attachments(part))

    return attachments


class GmailClient:
    """Thin wrapper around the Gmail v1 API service object."""

    def __init__(self, service) -> None:
        self._svc = service
        self._label_cache: dict[str, str] = {}  # name → label_id
        self._user_email: str | None = None

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_messages(
        self,
        query: str = "is:unread",
        max_results: int = 20,
    ) -> list[MessageSummary]:
        """Return lightweight summaries for messages matching *query*."""
        try:
            resp = (
                self._svc.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )
        except HttpError as exc:
            logger.error("list_messages failed: %s", exc)
            return []

        raw_ids = resp.get("messages", [])
        summaries: list[MessageSummary] = []

        for item in raw_ids:
            try:
                meta = (
                    self._svc.users()
                    .messages()
                    .get(userId="me", id=item["id"], format="metadata")
                    .execute()
                )
                headers = meta.get("payload", {}).get("headers", [])
                label_ids = meta.get("labelIds", [])
                has_att = any(
                    p.get("filename")
                    for p in meta.get("payload", {}).get("parts", [])
                )
                summaries.append(
                    MessageSummary(
                        id=meta["id"],
                        subject=_get_header(headers, "Subject") or "(no subject)",
                        sender=_get_header(headers, "From"),
                        date=_parse_date(_get_header(headers, "Date")),
                        snippet=meta.get("snippet", ""),
                        has_attachments=has_att,
                        label_ids=label_ids,
                    )
                )
            except HttpError as exc:
                logger.warning("Could not fetch metadata for %s: %s", item["id"], exc)

        return summaries

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    def get_message(self, message_id: str) -> EmailMessage | None:
        """Fetch the full message including body and attachment metadata."""
        try:
            msg = (
                self._svc.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )
        except HttpError as exc:
            logger.error("get_message(%s) failed: %s", message_id, exc)
            return None

        payload = msg.get("payload", {})
        headers = payload.get("headers", [])
        body_text, body_html = _extract_body(payload)
        attachments = _collect_attachments(payload)

        to_raw = _get_header(headers, "To")
        recipients = [r.strip() for r in to_raw.split(",") if r.strip()]

        return EmailMessage(
            id=msg["id"],
            thread_id=msg.get("threadId", ""),
            subject=_get_header(headers, "Subject") or "(no subject)",
            sender=_get_header(headers, "From"),
            recipients=recipients,
            date=_parse_date(_get_header(headers, "Date")),
            snippet=msg.get("snippet", ""),
            body_text=body_text[:8000],  # cap to keep context manageable
            body_html="",              # omit HTML from agent context
            label_ids=msg.get("labelIds", []),
            attachments=attachments,
        )

    # ------------------------------------------------------------------
    # Labels
    # ------------------------------------------------------------------

    def list_labels(self) -> list[dict]:
        """Return all labels for the authenticated user."""
        try:
            resp = self._svc.users().labels().list(userId="me").execute()
            return resp.get("labels", [])
        except HttpError as exc:
            logger.error("list_labels failed: %s", exc)
            return []

    def get_or_create_label(self, name: str) -> str:
        """Return the label_id for *name*, creating the label if necessary."""
        if name in self._label_cache:
            return self._label_cache[name]

        # Populate cache from existing labels
        for lbl in self.list_labels():
            self._label_cache[lbl["name"]] = lbl["id"]

        if name not in self._label_cache:
            try:
                new_lbl = (
                    self._svc.users()
                    .labels()
                    .create(
                        userId="me",
                        body={
                            "name": name,
                            "labelListVisibility": "labelShow",
                            "messageListVisibility": "show",
                        },
                    )
                    .execute()
                )
                self._label_cache[name] = new_lbl["id"]
                logger.info("Created Gmail label '%s'", name)
            except HttpError as exc:
                logger.error("create_label('%s') failed: %s", name, exc)
                return ""

        return self._label_cache[name]

    def apply_label(
        self,
        message_id: str,
        label_id: str,
        archive: bool = True,
    ) -> None:
        """Apply *label_id* to a message, optionally removing it from INBOX."""
        body: dict = {"addLabelIds": [label_id]}
        if archive:
            body["removeLabelIds"] = ["INBOX"]
        try:
            self._svc.users().messages().modify(
                userId="me", id=message_id, body=body
            ).execute()
        except HttpError as exc:
            logger.error("apply_label(%s) failed: %s", message_id, exc)

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    def trash_message(self, message_id: str) -> None:
        """Move a message to the Trash."""
        try:
            self._svc.users().messages().trash(
                userId="me", id=message_id
            ).execute()
        except HttpError as exc:
            logger.error("trash_message(%s) failed: %s", message_id, exc)

    def delete_message_permanent(self, message_id: str) -> None:
        """Permanently delete a message (bypasses Trash — irreversible)."""
        try:
            self._svc.users().messages().delete(
                userId="me", id=message_id
            ).execute()
        except HttpError as exc:
            logger.error("delete_message_permanent(%s) failed: %s", message_id, exc)

    # ------------------------------------------------------------------
    # Mark as read
    # ------------------------------------------------------------------

    def mark_as_read(self, message_id: str) -> None:
        """Remove the UNREAD label from a message."""
        try:
            self._svc.users().messages().modify(
                userId="me",
                id=message_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
        except HttpError as exc:
            logger.error("mark_as_read(%s) failed: %s", message_id, exc)

    # ------------------------------------------------------------------
    # Attachments
    # ------------------------------------------------------------------

    def get_attachment(self, message_id: str, attachment_id: str) -> bytes:
        """Download and decode an attachment's binary data."""
        try:
            resp = (
                self._svc.users()
                .messages()
                .attachments()
                .get(userId="me", messageId=message_id, id=attachment_id)
                .execute()
            )
            data = resp.get("data", "")
            return base64.urlsafe_b64decode(data + "==")
        except HttpError as exc:
            logger.error(
                "get_attachment(%s, %s) failed: %s", message_id, attachment_id, exc
            )
            return b""

    # ------------------------------------------------------------------
    # Drafts
    # ------------------------------------------------------------------

    def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        reply_to_id: str,
        thread_id: str | None = None,
    ) -> str:
        """Create a draft reply.

        Returns the draft ID on success, or '' on failure.
        """
        msg = MIMEMultipart()
        msg["To"] = to
        msg["Subject"] = subject
        msg["In-Reply-To"] = reply_to_id
        msg["References"] = reply_to_id
        msg.attach(MIMEText(body, "plain", "utf-8"))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        draft_body: dict = {"message": {"raw": raw}}
        if thread_id:
            draft_body["message"]["threadId"] = thread_id

        try:
            result = (
                self._svc.users()
                .drafts()
                .create(userId="me", body=draft_body)
                .execute()
            )
            return result.get("id", "")
        except HttpError as exc:
            logger.error("create_draft failed: %s", exc)
            return ""

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------

    def get_user_email(self) -> str:
        """Return the authenticated user's email address (cached)."""
        if self._user_email:
            return self._user_email
        try:
            profile = (
                self._svc.users().getProfile(userId="me").execute()
            )
            self._user_email = profile.get("emailAddress", "")
        except HttpError as exc:
            logger.error("getProfile failed: %s", exc)
            self._user_email = ""
        return self._user_email
