"""Structured logging for the Construction Contract Ledger system."""
import logging


def setup_ledger_logger(level: str = "INFO") -> logging.Logger:
    """
    Configure and return the root logger for the ledger system.
    Uses the same format as the existing utils/logger.py in this repo.
    """
    log_level = getattr(logging, level, logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-5s] %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger("construction_ledger")
    logger.setLevel(log_level)

    if not logger.handlers:
        logger.addHandler(handler)

    logger.propagate = False
    return logger
