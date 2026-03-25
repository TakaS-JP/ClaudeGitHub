"""Entry point for the Email Management AI Agent."""
import argparse
import sys

import anthropic
from dotenv import load_dotenv

from agent.loop import EmailAgentLoop
from agent.tool_handlers import ToolHandlers
from auth.gmail_auth import get_gmail_service
from config.settings import Settings
from gmail.client import GmailClient
from storage.attachment_store import AttachmentStore
from utils.logger import setup_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI Email Management Agent — classifies, organises and replies to Gmail."
    )
    parser.add_argument(
        "--max-emails",
        type=int,
        default=None,
        help="Maximum number of emails to process (overrides .env MAX_EMAILS_PER_RUN).",
    )
    parser.add_argument(
        "--query",
        type=str,
        default="is:unread",
        help="Gmail search query to select emails (default: 'is:unread').",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List emails only — do not delete, label, or create drafts.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    try:
        config = Settings()
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(1)

    logger = setup_logger(config.log_level)
    logger.info("=== Email Management Agent starting ===")

    if args.dry_run:
        logger.info("DRY RUN mode — no changes will be made to Gmail.")

    # Build dependencies
    try:
        gmail_service = get_gmail_service(
            credentials_file=config.google_credentials_file,
            token_file=config.google_token_file,
        )
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        sys.exit(1)

    gmail_client = GmailClient(gmail_service)
    attachment_store = AttachmentStore(config.attachment_base_dir)
    tool_handlers = ToolHandlers(gmail_client, attachment_store)
    anthropic_client = anthropic.Anthropic(api_key=config.anthropic_api_key)

    max_emails = args.max_emails or config.max_emails_per_run

    agent = EmailAgentLoop(
        anthropic_client=anthropic_client,
        tool_handlers=tool_handlers,
        max_emails=max_emails,
        max_turns=config.max_agent_turns,
    )

    summary = agent.run()

    # Print final summary to stdout
    print("\n" + "=" * 50)
    print("SESSION COMPLETE")
    print("=" * 50)
    print(f"  Processed   : {summary.processed}")
    print(f"  Deleted     : {summary.deleted}")
    print(f"  Saved (Work): {summary.saved_work}")
    print(f"  Saved (Pers): {summary.saved_personal}")
    print(f"  Saved (Imp) : {summary.saved_important}")
    print(f"  Drafts      : {summary.drafts_created}")
    print(f"  Flagged     : {summary.flagged}")
    print(f"  Skipped     : {summary.skipped}")
    print("=" * 50)


if __name__ == "__main__":
    main()
