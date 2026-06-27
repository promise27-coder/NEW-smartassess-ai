"""Logging configuration for the SmartAssess AI backend."""

import logging as standard_logging


LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging(debug: bool = False) -> None:
    """Configure standard application logging."""
    log_level = standard_logging.DEBUG if debug else standard_logging.INFO
    standard_logging.basicConfig(level=log_level, format=LOG_FORMAT)
