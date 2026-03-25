"""Structured logging setup for the email management agent."""
import logging
import sys


def setup_logger(level: str = "INFO") -> logging.Logger:
    """Configure root logger and return the application logger.

    Log format::

        2026-03-25 14:01:02 [INFO ] email_agent | Starting session...

    Args:
        level: One of ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``.

    Returns:
        The ``email_agent`` logger instance.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-5s] %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(numeric_level)
    # Avoid adding duplicate handlers when tests re-import the module
    if not root.handlers:
        root.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return logging.getLogger("email_agent")
