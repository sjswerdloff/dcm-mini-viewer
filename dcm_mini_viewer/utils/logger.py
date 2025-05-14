#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging configuration for the dcm-mini-viewer project.
"""

import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Dict

# Cache for initialized loggers
_LOGGER_CACHE: Dict[str, logging.Logger] = {}


def setup_logger(log_level: int = logging.INFO) -> logging.Logger:
    """
    Setup the application logger with console and file handlers.

    Args:
        log_level: The logging level to use.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Use cached logger if already initialized
    if "dcm-mini-viewer" in _LOGGER_CACHE:
        logger = _LOGGER_CACHE["dcm-mini-viewer"]
        # Update the log level if different
        if logger.getEffectiveLevel() != log_level:
            logger.setLevel(log_level)
            for handler in logger.handlers:
                handler.setLevel(log_level)
        return logger

    # Create logger
    logger = logging.getLogger("dcm-mini-viewer")
    logger.setLevel(log_level)

    # Clear any existing handlers
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    # Create formatters
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s")

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Create file handler in user's home directory

    log_dir = Path(get_app_data_dir().joinpath("logs"))
    os.makedirs(log_dir, mode=0o755, exist_ok=True)

    log_path = Path(log_dir.joinpath("dcm-mini-viewer.log"))
    if not log_path.exists():
        log_path.touch(mode=0o622, exist_ok=True)
    if not log_path.exists():
        print(f"WTF? {log_path} not created by touch")

    # file_handler = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=5)  # 10 MB

    file_handler = TimedRotatingFileHandler(log_path, when="midnight", backupCount=5)  # 10 MB

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # don't set a formatter until the handler has been added to the logger.
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    logger.info("Logger initialized")

    # Cache the logger
    _LOGGER_CACHE["dcm-mini-viewer"] = logger

    return logger


def get_app_data_dir() -> Path:
    """
    Get the platform-specific application data directory.

    Returns:
        Path: Path to the application data directory.
    """
    home_dir = Path.home()

    app_data_dir = home_dir / ".dcm-mini-viewer"
    # Create directory if it doesn't exist
    os.makedirs(app_data_dir, exist_ok=True)

    return app_data_dir


def get_logger() -> logging.Logger:
    """
    Get the application logger.

    Returns:
        logging.Logger: Application logger instance.
    """
    # Initialize logger if not already done
    if "dcm-mini-viewer" not in _LOGGER_CACHE:
        setup_logger()

    return _LOGGER_CACHE["dcm-mini-viewer"]


# For testing purposes only, not part of public API
def _reset_logger() -> None:
    """
    Reset the logger cache (primarily for testing purposes).
    """
    if "dcm-mini-viewer" in _LOGGER_CACHE:
        logger = _LOGGER_CACHE["dcm-mini-viewer"]
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        del _LOGGER_CACHE["dcm-mini-viewer"]
