"""Logging utilities."""

import logging
import sys
from pathlib import Path
from typing import Optional
from ..config import settings


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """Set up centralized logging configuration."""
    config = settings.get_section("logging")
    log_level = level or config.get("level", "INFO")
    fmt = format_string or config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console = config.get("console", True)
    file_path = log_file or config.get("file")

    logger = logging.getLogger("iq_analyzer")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.handlers.clear()

    formatter = logging.Formatter(fmt)

    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if file_path:
        file_handler = logging.FileHandler(file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"iq_analyzer.{name}")


# Initialize default logger
logger = setup_logging()