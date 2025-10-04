"""Logging utilities for Smart Stadium backend."""

from __future__ import annotations

import logging
from logging import Logger
from pathlib import Path

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def configure_logging(log_dir: Path, environment: str) -> None:
    """Configure root logging handlers."""

    log_dir.mkdir(parents=True, exist_ok=True)

    handlers: list[logging.Handler] = []

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if environment == "development" else logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handlers.append(console_handler)

    file_handler = logging.FileHandler(log_dir / "smart_stadium.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handlers.append(file_handler)

    logging.basicConfig(level=logging.DEBUG, handlers=handlers)


def get_logger(name: str) -> Logger:
    return logging.getLogger(name)
