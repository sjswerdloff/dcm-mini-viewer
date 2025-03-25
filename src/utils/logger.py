#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging configuration for the OnkoDICOM discovery project.
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logger(log_level: int = logging.INFO) -> logging.Logger:
    """
    Setup the application logger with console and file handlers.

    Args:
        log_level: The logging level to use.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Create logger
    logger = logging.getLogger("onkodicom")
    logger.setLevel(log_level)

    # Create formatters
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)

    # Create file handler in user's home directory
    log_dir = get_app_data_dir() / "logs"
    os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_dir / "onkodicom.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info("Logger initialized")

    return logger


def get_app_data_dir() -> Path:
    """
    Get the platform-specific application data directory.

    Returns:
        Path: Path to the application data directory.
    """
    home_dir = Path.home()

    if sys.platform == "win32":
        # Windows
        app_data_dir = home_dir / ".onkodicom"
    elif sys.platform == "darwin":
        # macOS
        app_data_dir = home_dir / ".onkodicom"
    else:
        # Linux/Unix
        app_data_dir = home_dir / ".onkodicom"

    # Create directory if it doesn't exist
    os.makedirs(app_data_dir, exist_ok=True)

    return app_data_dir


def get_logger() -> logging.Logger:
    """
    Get the application logger.

    Returns:
        logging.Logger: Application logger instance.
    """
    return logging.getLogger("onkodicom")
