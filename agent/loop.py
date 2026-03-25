"""Core agentic loop: calls Claude with tool_use and drives the session."""
from __future__ import annotations

import json
import logging
from datetime import date

import anthropic

from agent.tool_handlers import SessionSummary, ToolHandlers
from agent.tools import AGENT_TOOLS

logger = logging.getLogger(__name__)

MODEL = "claude-opus-4-6"

SYSTEM_PROMPT = """You are an autonomous email management agent. Your job is to \
process a user's Gmail inbox efficiently and accurately.

Today's date: {today}

## Your workflow for each session
1. Call list_emails to get an overview of unread messages.
2. For each email, decide how to handle it (see categories below).
3. If the snippet is insufficient to classify, call get_email_content first.
4. ALWAYS call classify_and_act BEFORE any delete_email or apply_label call.
5. After classifying, take the appropriate action(s):
   - delete / spam / newsletter-unsubscribe → call delete_email
   - save-work  → apply_label("Work")    + download_attachments if any
   - save-personal → apply_label("Personal") + download_attachments if any
   - save-important → apply_label("Important") + download_attachments if any
   - needs-reply → apply_label("Needs Reply") + create_draft_reply \
+ download_attachments if any
   - skip → do nothing extra (just mark as read)
6. ALWAYS call mark_as_read after finishing an email.
7. Call get_processing_summary periodically to track progress.
8. When done, provide a brief final summary.

## Category definitions
- **delete**: automated system notifications, expired promotions, delivery receipts, \
unwanted newsletters (already unsubscribed), low-value one-way announcements.
- **spam**: phishing attempts, unsolicited bulk commercial email, suspicious senders.
- **save-work**: professional correspondence, client emails, invoices, receipts, \
work tool notifications that require action.
- **save-personal**: messages from friends or family, personal services, \
hobby-related correspondence.
- **save-important**: legal notices, financial statements, government correspondence, \
medical information, anything time-sensitive with legal/financial consequences.
- **needs-reply**: emails that contain an explicit question addressed to you, \
a meeting invitation requiring a response, or any message clearly awaiting your reply.
- **newsletter-unsubscribe**: newsletters you no longer want; delete them and log \
the sender for future unsubscribe.
- **skip**: genuinely ambiguous emails where you cannot determine intent with \
reasonable confidence; leave for the human owner.

## Rules
- Never permanently delete (permanent=true) unless the email is confirmed spam/phishing.
- Bias toward save over delete when uncertain — use 'skip' rather than wrongly deleting.
- When creating a draft reply, write a complete, courteous response in the same \
language as the original email.
- For attachment storage categories: work → "work", personal → "personal", \
important/needs-reply → "important", skip → "other".
"""


class EmailAgentLoop:
    """Drives the Claude tool-use loop for a single email-management session."""

    def __init__(
        self,
        anthropic_client: anthropic.Anthropic,
        tool_handlers: ToolHandlers,
        max_emails: int = 30,
        max_turns: int = 60,
    ) -> None:
        self._client = anthropic_client
        self._handlers = tool_handlers
        self._max_emails = max_emails
        self._max_turns = max_turns

        self._dispatch: dict = {
            "list_emails": self._handlers.handle_list_emails,
            "get_email_content": self._handlers.handle_get_email_content,
            "classify_and_act": self._handlers.handle_classify_and_act,
            "delete_email": self._handlers.handle_delete_email,
            "apply_label": self._handlers.handle_apply_label,
            "download_attachments": self._handlers.handle_download_attachments,
            "create_draft_reply": self._handlers.handle_create_draft_reply,
            "mark_as_read": self._handlers.handle_mark_as_read,
            "get_processing_summary": self._handlers.handle_get_processing_summary,
            "flag_for_human_review": self._handlers.handle_flag_for_human_review,
        }

    def run(self) -> SessionSummary:
        """Run the full session until Claude finishes or the turn limit is hit."""
        system = SYSTEM_PROMPT.format(today=date.today().isoformat())
        initial_message = (
            f"Process up to {self._max_emails} unread emails in my Gmail inbox. "
            "Start by listing them, then handle each one according to your instructions. "
            "Work through all of them before giving the final summary."
        )

        messages: list[dict] = [{"role": "user", "content": initial_message}]

        logger.info(
            "[AGENT] Session started — processing up to %d emails", self._max_emails
        )

        for turn in range(self._max_turns):
            response = self._client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=system,
                tools=AGENT_TOOLS,
                messages=messages,
            )

            # Append assistant message to history
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                logger.info("[AGENT] Claude finished on turn %d", turn + 1)
                # Print Claude's final text
                for block in response.content:
                    if hasattr(block, "type") and block.type == "text":
                        logger.info("[AGENT] Final message: %s", block.text)
                break

            if response.stop_reason == "tool_use":
                tool_results = self._process_tool_calls(response.content)
                messages.append({"role": "user", "content": tool_results})
                continue

            # Unexpected stop reason
            logger.warning("[AGENT] Unexpected stop_reason: %s", response.stop_reason)
            break
        else:
            logger.warning("[AGENT] Reached max_turns (%d) safety limit", self._max_turns)

        summary = self._handlers.get_session_summary()
        self._log_summary(summary)
        return summary

    def _process_tool_calls(self, content: list) -> list[dict]:
        """Execute all tool_use blocks and return tool_result content blocks."""
        tool_results = []
        for block in content:
            if not (hasattr(block, "type") and block.type == "tool_use"):
                continue

            tool_name: str = block.name
            tool_input: dict = block.input
            tool_use_id: str = block.id

            handler = self._dispatch.get(tool_name)
            if handler is None:
                result = {"error": f"Unknown tool: {tool_name}"}
            else:
                try:
                    result = handler(**tool_input)
                except Exception as exc:
                    logger.error("[TOOL] %s crashed: %s", tool_name, exc, exc_info=True)
                    result = {"success": False, "error": str(exc)}

            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                }
            )

        return tool_results

    @staticmethod
    def _log_summary(summary: SessionSummary) -> None:
        logger.info(
            "[SUMMARY] processed=%d deleted=%d work=%d personal=%d "
            "important=%d drafts=%d flagged=%d skipped=%d newsletters=%d",
            summary.processed,
            summary.deleted,
            summary.saved_work,
            summary.saved_personal,
            summary.saved_important,
            summary.drafts_created,
            summary.flagged,
            summary.skipped,
            summary.newsletters,
        )
