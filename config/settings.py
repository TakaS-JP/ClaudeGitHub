"""Application settings loaded from environment variables."""
import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()


class EmailCategory(str, Enum):
    DELETE = "delete"
    SPAM = "spam"
    SAVE_WORK = "save-work"
    SAVE_PERSONAL = "save-personal"
    SAVE_IMPORTANT = "save-important"
    NEEDS_REPLY = "needs-reply"
    NEWSLETTER = "newsletter-unsubscribe"
    SKIP = "skip"


# Gmail label names for each saved category
CATEGORY_LABEL_MAP: dict[str, str] = {
    EmailCategory.SAVE_WORK: "Work",
    EmailCategory.SAVE_PERSONAL: "Personal",
    EmailCategory.SAVE_IMPORTANT: "Important",
    EmailCategory.NEEDS_REPLY: "Needs Reply",
}

# Local attachment subdirectory for each category
CATEGORY_ATTACHMENT_DIR_MAP: dict[str, str] = {
    EmailCategory.SAVE_WORK: "work",
    EmailCategory.SAVE_PERSONAL: "personal",
    EmailCategory.SAVE_IMPORTANT: "important",
    EmailCategory.NEEDS_REPLY: "important",
    EmailCategory.SKIP: "other",
}


class Settings:
    def __init__(self) -> None:
        self.anthropic_api_key: str = self._require("ANTHROPIC_API_KEY")
        self.google_credentials_file: str = os.getenv(
            "GOOGLE_CREDENTIALS_FILE", "credentials.json"
        )
        self.google_token_file: str = os.getenv(
            "GOOGLE_TOKEN_FILE", "token.json"
        )
        self.max_emails_per_run: int = int(
            os.getenv("MAX_EMAILS_PER_RUN", "30")
        )
        self.max_agent_turns: int = int(os.getenv("MAX_AGENT_TURNS", "60"))
        self.attachment_base_dir: str = os.getenv(
            "ATTACHMENT_BASE_DIR", "attachments"
        )
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

    @staticmethod
    def _require(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(
                f"Required environment variable '{key}' is not set. "
                f"Copy .env.example to .env and fill in the values."
            )
        return value
