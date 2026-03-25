"""Implementations for every tool the agent can call."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from config.settings import (
    CATEGORY_ATTACHMENT_DIR_MAP,
    CATEGORY_LABEL_MAP,
    EmailCategory,
)
from gmail.client import GmailClient
from storage.attachment_store import AttachmentStore

logger = logging.getLogger(__name__)


@dataclass
class ActionRecord:
    email_id: str
    subject: str
    sender: str
    category: str
    action: str
    reasoning: str
    attachments_saved: list[str] = field(default_factory=list)
    draft_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))


@dataclass
class SessionSummary:
    processed: int = 0
    deleted: int = 0
    saved_work: int = 0
    saved_personal: int = 0
    saved_important: int = 0
    drafts_created: int = 0
    flagged: int = 0
    skipped: int = 0
    newsletters: int = 0
    action_log: list[ActionRecord] = field(default_factory=list)


class ToolHandlers:
    """Stateful handler that executes each agent tool call."""

    def __init__(
        self,
        gmail: GmailClient,
        store: AttachmentStore,
    ) -> None:
        self._gmail = gmail
        self._store = store
        self._summary = SessionSummary()
        # email_id → category string (set by classify_and_act)
        self._category_map: dict[str, str] = {}
        # email_id → EmailMessage (cached after get_email_content)
        self._message_cache: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Tool: list_emails
    # ------------------------------------------------------------------

    def handle_list_emails(
        self,
        max_results: int = 20,
        query: str = "is:unread",
    ) -> dict:
        max_results = min(int(max_results), 50)
        summaries = self._gmail.list_messages(query=query, max_results=max_results)
        result = []
        for s in summaries:
            result.append(
                {
                    "id": s.id,
                    "subject": s.subject,
                    "sender": s.sender,
                    "date": s.date.isoformat(),
                    "snippet": s.snippet,
                    "has_attachments": s.has_attachments,
                    "label_ids": s.label_ids,
                }
            )
        logger.info("[TOOL] list_emails → %d messages", len(result))
        return {"emails": result, "count": len(result)}

    # ------------------------------------------------------------------
    # Tool: get_email_content
    # ------------------------------------------------------------------

    def handle_get_email_content(self, email_id: str) -> dict:
        if email_id in self._message_cache:
            msg = self._message_cache[email_id]
        else:
            msg = self._gmail.get_message(email_id)
            if msg is None:
                return {"success": False, "error": f"Message {email_id} not found"}
            self._message_cache[email_id] = msg

        logger.info("[TOOL] get_email_content(%s) → '%s'", email_id, msg.subject)
        return {
            "success": True,
            "id": msg.id,
            "subject": msg.subject,
            "sender": msg.sender,
            "recipients": msg.recipients,
            "date": msg.date.isoformat(),
            "snippet": msg.snippet,
            "body_text": msg.body_text,
            "attachments": [
                {
                    "filename": a.filename,
                    "mime_type": a.mime_type,
                    "size": a.size,
                    "attachment_id": a.attachment_id,
                }
                for a in msg.attachments
            ],
        }

    # ------------------------------------------------------------------
    # Tool: classify_and_act
    # ------------------------------------------------------------------

    def handle_classify_and_act(
        self,
        email_id: str,
        category: str,
        reasoning: str,
    ) -> dict:
        self._category_map[email_id] = category

        # Retrieve subject/sender for the log (best-effort)
        subject, sender = "", ""
        if email_id in self._message_cache:
            msg = self._message_cache[email_id]
            subject, sender = msg.subject, msg.sender

        record = ActionRecord(
            email_id=email_id,
            subject=subject,
            sender=sender,
            category=category,
            action="classify",
            reasoning=reasoning,
        )
        self._summary.action_log.append(record)
        logger.info(
            "[ACTION] classify(%s) → %s | %s", email_id, category, reasoning
        )
        return {"success": True, "category_applied": category}

    # ------------------------------------------------------------------
    # Tool: delete_email
    # ------------------------------------------------------------------

    def handle_delete_email(
        self,
        email_id: str,
        permanent: bool = False,
    ) -> dict:
        if email_id not in self._category_map:
            return {
                "success": False,
                "error": "classify_and_act must be called before delete_email",
            }

        if permanent:
            self._gmail.delete_message_permanent(email_id)
            action = "permanently_deleted"
        else:
            self._gmail.trash_message(email_id)
            action = "trashed"

        self._summary.deleted += 1
        self._summary.processed += 1
        self._update_last_record(email_id, action)
        logger.info("[ACTION] delete(%s) permanent=%s", email_id, permanent)
        return {"success": True, "action": action, "email_id": email_id}

    # ------------------------------------------------------------------
    # Tool: apply_label
    # ------------------------------------------------------------------

    def handle_apply_label(
        self,
        email_id: str,
        label_name: str,
        archive: bool = True,
    ) -> dict:
        if email_id not in self._category_map:
            return {
                "success": False,
                "error": "classify_and_act must be called before apply_label",
            }

        label_id = self._gmail.get_or_create_label(label_name)
        if not label_id:
            return {"success": False, "error": f"Could not create label '{label_name}'"}

        self._gmail.apply_label(email_id, label_id, archive=archive)

        category = self._category_map.get(email_id, "")
        if category == EmailCategory.SAVE_WORK:
            self._summary.saved_work += 1
        elif category == EmailCategory.SAVE_PERSONAL:
            self._summary.saved_personal += 1
        elif category in (EmailCategory.SAVE_IMPORTANT, EmailCategory.NEEDS_REPLY):
            self._summary.saved_important += 1

        self._summary.processed += 1
        self._update_last_record(email_id, f"labelled:{label_name}")
        logger.info("[ACTION] apply_label(%s, '%s')", email_id, label_name)
        return {"success": True, "label_id": label_id, "label_name": label_name}

    # ------------------------------------------------------------------
    # Tool: download_attachments
    # ------------------------------------------------------------------

    def handle_download_attachments(
        self,
        email_id: str,
        category: str,
    ) -> dict:
        msg = self._message_cache.get(email_id)
        if msg is None:
            msg = self._gmail.get_message(email_id)
            if msg is None:
                return {"success": False, "error": f"Message {email_id} not found"}
            self._message_cache[email_id] = msg

        saved_files = []
        for att in msg.attachments:
            data = self._gmail.get_attachment(email_id, att.attachment_id)
            if not data:
                logger.warning("Empty attachment data for %s", att.filename)
                continue
            path = self._store.save_attachment(
                data=data,
                filename=att.filename,
                category=category,
                email_id=email_id,
            )
            saved_files.append(
                {"filename": att.filename, "local_path": str(path), "size_bytes": len(data)}
            )
            logger.info("[ACTION] saved attachment %s → %s", att.filename, path)

        # Attach file paths to the matching action record
        for rec in reversed(self._summary.action_log):
            if rec.email_id == email_id:
                rec.attachments_saved = [f["local_path"] for f in saved_files]
                break

        return {"success": True, "saved_files": saved_files}

    # ------------------------------------------------------------------
    # Tool: create_draft_reply
    # ------------------------------------------------------------------

    def handle_create_draft_reply(
        self,
        email_id: str,
        reply_body: str,
        reply_tone: str = "professional",
    ) -> dict:
        msg = self._message_cache.get(email_id)
        if msg is None:
            msg = self._gmail.get_message(email_id)
            if msg is None:
                return {"success": False, "error": f"Message {email_id} not found"}
            self._message_cache[email_id] = msg

        subject = msg.subject
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"

        draft_id = self._gmail.create_draft(
            to=msg.sender,
            subject=subject,
            body=reply_body,
            reply_to_id=email_id,
            thread_id=msg.thread_id,
        )
        if draft_id:
            self._summary.drafts_created += 1
            for rec in reversed(self._summary.action_log):
                if rec.email_id == email_id:
                    rec.draft_id = draft_id
                    break
            logger.info("[ACTION] create_draft(%s) → draft_id=%s", email_id, draft_id)
            return {"success": True, "draft_id": draft_id}
        return {"success": False, "error": "Draft creation failed — check logs"}

    # ------------------------------------------------------------------
    # Tool: mark_as_read
    # ------------------------------------------------------------------

    def handle_mark_as_read(self, email_id: str) -> dict:
        self._gmail.mark_as_read(email_id)
        logger.info("[ACTION] mark_as_read(%s)", email_id)
        return {"success": True}

    # ------------------------------------------------------------------
    # Tool: get_processing_summary
    # ------------------------------------------------------------------

    def handle_get_processing_summary(self) -> dict:
        s = self._summary
        return {
            "processed": s.processed,
            "deleted": s.deleted,
            "saved_work": s.saved_work,
            "saved_personal": s.saved_personal,
            "saved_important": s.saved_important,
            "drafts_created": s.drafts_created,
            "flagged": s.flagged,
            "skipped": s.skipped,
            "newsletters": s.newsletters,
        }

    # ------------------------------------------------------------------
    # Tool: flag_for_human_review
    # ------------------------------------------------------------------

    def handle_flag_for_human_review(self, email_id: str, reason: str) -> dict:
        label_id = self._gmail.get_or_create_label("Needs Review")
        if label_id:
            self._gmail.apply_label(email_id, label_id, archive=False)

        self._summary.flagged += 1
        logger.info("[ACTION] flag_for_review(%s) reason=%s", email_id, reason)
        return {"success": True, "reason": reason}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _update_last_record(self, email_id: str, action: str) -> None:
        """Update the action field of the most recent record for email_id."""
        for rec in reversed(self._summary.action_log):
            if rec.email_id == email_id:
                rec.action = action
                return

    def get_session_summary(self) -> SessionSummary:
        return self._summary
