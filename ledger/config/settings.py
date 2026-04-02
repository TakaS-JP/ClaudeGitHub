"""Configuration for the Construction Contract Ledger system."""
import os


class LedgerSettings:
    """
    Runtime configuration loaded from environment variables.
    All settings have sensible defaults — no required env vars.
    """

    def __init__(self) -> None:
        self.db_path: str = os.getenv(
            "LEDGER_DB_PATH", "ledger_data/ledger.db"
        )
        self.log_level: str = os.getenv("LEDGER_LOG_LEVEL", "INFO").upper()
        self.date_format: str = "%Y-%m-%d"
        self.currency_symbol: str = "¥"
