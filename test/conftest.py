#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration for logger tests.
"""
import logging
import os
from pathlib import Path
from typing import Iterator

import pytest

# Import from refactored module
from src.utils.logger import _reset_logger


@pytest.fixture(autouse=True)
def reset_logging() -> Iterator[None]:
    """
    Reset logging configuration before and after each test.

    This ensures tests don't interfere with each other's logging setup.
    """
    # Store original logger state
    original_loggers = logging.Logger.manager.loggerDict.copy()
    root_handlers = logging.getLogger().handlers.copy()

    # Reset the logger completely
    _reset_logger()

    # Provide the test with a clean logging environment
    yield

    # Reset again after test
    _reset_logger()

    # Restore original state after test completes
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        if logger_name not in original_loggers:
            del logging.Logger.manager.loggerDict[logger_name]

    # Restore root handlers
    logging.getLogger().handlers = root_handlers


@pytest.fixture
def temp_app_dir(tmpdir: Path) -> Iterator[Path]:
    """
    Create a temporary application directory for testing.

    Args:
        tmpdir: Pytest fixture providing a temporary directory

    Yields:
        Path: Path to the temporary directory
    """
    # Create a temporary directory structure
    app_dir = Path(tmpdir) / ".onkodicom"
    log_dir = app_dir / "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Provide the directory to the test
    yield app_dir

    # No cleanup needed as tmpdir is automatically cleaned by pytest
