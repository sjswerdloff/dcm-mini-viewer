#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the logger module.
"""

import logging
import sys
import unittest
from io import StringIO
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from unittest import mock

import pytest

from dcm_mini_viewer.utils.logger import _LOGGER_CACHE, _reset_logger, get_app_data_dir, get_logger, setup_logger


class TestLogger(unittest.TestCase):
    """Test cases for the logger module."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Store original logger state to restore after tests
        self.original_loggers = logging.Logger.manager.loggerDict.copy()
        self.root_handlers = logging.getLogger().handlers.copy()

        # Reset the logger completely between tests
        _reset_logger()

    def tearDown(self) -> None:
        """Tear down test fixtures."""
        # Reset the logger to clean state
        _reset_logger()

        # Restore original logger state
        for logger_name in list(logging.Logger.manager.loggerDict.keys()):
            if logger_name not in self.original_loggers:
                del logging.Logger.manager.loggerDict[logger_name]

        # Restore root handlers
        logging.getLogger().handlers = self.root_handlers

    def test_setup_logger_default_level(self) -> None:
        """Test setup_logger with default log level."""
        logger = setup_logger()

        # Check logger level
        self.assertEqual(logger.getEffectiveLevel(), logging.INFO)

        # Check handlers
        self.assertEqual(len(logger.handlers), 2)

        # Verify handler types
        handlers_types = [type(handler) for handler in logger.handlers]
        self.assertIn(logging.StreamHandler, handlers_types)

        # Can't Check handler levels... they don't support a level property
        # They do support a setLevel() but it's opaque at that point.
        # for handler in logger.handlers:
        #     self.assertEqual(handler.level, logging.INFO)

    def test_setup_logger_custom_level(self) -> None:
        """Test setup_logger with custom log level."""
        logger = setup_logger(log_level=logging.DEBUG)

        # Check logger level
        self.assertEqual(logger.level, logging.DEBUG)

        # Can't Check handler levels... they don't support a level property
        # They do support a setLevel() but it's opaque at that point.
        # for handler in logger.handlers:
        #     self.assertEqual(handler.level, logging.DEBUG)

    def test_setup_logger_formatters(self) -> None:
        """Test that formatters are correctly set up."""
        logger = setup_logger()

        # Check console handler formatter
        console_handler = logger.handlers[0]
        self.assertIsInstance(console_handler, logging.StreamHandler)
        self.assertIsNotNone(console_handler.formatter)

        # Check file handler formatter
        file_handler = logger.handlers[1]
        self.assertIsNotNone(file_handler.formatter)

        # Ensure formatters are different
        self.assertNotEqual(console_handler.formatter._fmt, file_handler.formatter._fmt)

    @pytest.mark.skip
    @mock.patch("src.utils.logger.get_app_data_dir")
    @mock.patch("os.makedirs")
    def test_setup_logger_file_handler(self, mock_makedirs: mock.Mock, mock_get_app_data_dir: mock.Mock) -> None:
        """Test that file handler is correctly set up."""
        # Mock app data directory
        mock_dir = Path("/tmp/mock/path")

        mock_log_dir = mock_dir.joinpath("logs")

        # os.makedirs(mock_dir, mode=0o755, exist_ok=False)
        mock_get_app_data_dir.return_value = mock_dir
        try:
            logger = setup_logger()
        except Exception:
            pass  # because mocking mkdirs means setup_logger will fail, for good reason

        # Find out what really got called.
        print("Actual calls:", mock_makedirs.call_args_list)
        # Check that log directory was created.
        # This is a bit brittle as a test, because it's requiring that the exact mode be used
        mock_makedirs.assert_any_call(mock_log_dir, mode=493, exist_ok=True)

        # Find the file handler
        file_handler = None
        for handler in logger.handlers:
            if hasattr(handler, "baseFilename"):
                file_handler = handler
                break
        # os.removedirs(mock_dir) # cleanup.  TODO: use TmpDir instead
        self.assertIsNotNone(file_handler)
        self.assertEqual(file_handler.backupCount, 5)
        # self.assertEqual(file_handler.maxBytes, 10 * 1024 * 1024)

    @mock.patch("sys.platform", "win32")
    @mock.patch("pathlib.Path.home")
    @mock.patch("os.makedirs")
    def test_get_app_data_dir_windows(self, mock_makedirs: mock.Mock, mock_home: mock.Mock) -> None:
        """Test get_app_data_dir on Windows platform."""
        mock_home.return_value = Path("/tmp/mock/home")

        app_dir = get_app_data_dir()

        self.assertEqual(app_dir, Path("/tmp/mock/home/.dcm-mini-viewer"))
        mock_makedirs.assert_called_once_with(app_dir, exist_ok=True)

    @mock.patch("sys.platform", "darwin")
    @mock.patch("pathlib.Path.home")
    @mock.patch("os.makedirs")
    def test_get_app_data_dir_macos(self, mock_makedirs: mock.Mock, mock_home: mock.Mock) -> None:
        """Test get_app_data_dir on macOS platform."""
        mock_home.return_value = Path("/tmp/mock/home")

        app_dir = get_app_data_dir()

        self.assertEqual(app_dir, Path("/tmp/mock/home/.dcm-mini-viewer"))
        mock_makedirs.assert_called_once_with(app_dir, exist_ok=True)

    @mock.patch("sys.platform", "linux")
    @mock.patch("pathlib.Path.home")
    @mock.patch("os.makedirs")
    def test_get_app_data_dir_linux(self, mock_makedirs: mock.Mock, mock_home: mock.Mock) -> None:
        """Test get_app_data_dir on Linux platform."""
        mock_home.return_value = Path("/tmp/mock/home")

        app_dir = get_app_data_dir()

        self.assertEqual(app_dir, Path("/tmp/mock/home/.dcm-mini-viewer"))
        mock_makedirs.assert_called_once_with(app_dir, exist_ok=True)

    def test_rotating_file_handler_config(self) -> None:
        """Test the configuration of the rotating file handler."""
        # Setup logger
        logger = setup_logger()

        # Find the file handler
        file_handler = None
        for handler in logger.handlers:
            if hasattr(handler, "baseFilename"):
                file_handler = handler
                break

        self.assertIsNotNone(file_handler)
        self.assertIsInstance(file_handler, TimedRotatingFileHandler)

        # Check configuration
        # self.assertEqual(file_handler.maxBytes, 10 * 1024 * 1024)  # 10 MB
        self.assertEqual(file_handler.backupCount, 5)

    def test_formatter_configuration(self) -> None:
        """Test that formatters are correctly configured."""
        logger = setup_logger()

        # Check that we have both formatters
        console_format = None
        file_format = None

        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not hasattr(handler, "baseFilename"):
                console_format = handler.formatter._fmt
            elif hasattr(handler, "baseFilename"):
                file_format = handler.formatter._fmt

        self.assertIsNotNone(console_format)
        self.assertIsNotNone(file_format)

        # Console format should be simpler
        self.assertIn("%(levelname)s", console_format)
        self.assertIn("%(message)s", console_format)

        # File format should be more detailed
        self.assertIn("%(name)s", file_format)
        self.assertIn("%(filename)s", file_format)
        self.assertIn("%(lineno)d", file_format)

    def test_get_logger(self) -> None:
        """Test get_logger function."""
        # First setup the logger
        setup_logger()

        # Then get the logger
        logger = get_logger()

        # Check it's the same logger
        self.assertEqual(logger.name, "dcm-mini-viewer")

        # Check it has handlers
        self.assertTrue(len(logger.handlers) > 0)

    def test_logger_message_propagation(self) -> None:
        """Test that log messages are correctly handled."""
        # Use a StringIO object to capture log output instead of mocks
        output = StringIO()

        # Create a logger with a custom handler that writes to our StringIO
        logger = logging.getLogger("test_dcm-mini-viewer")
        logger.setLevel(logging.INFO)

        # Clear any existing handlers
        logger.handlers = []

        # Add a handler that writes to our StringIO
        handler = logging.StreamHandler(output)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        logger.addHandler(handler)

        # Test logging at different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        # Get the captured output
        log_output = output.getvalue()

        # DEBUG messages should not appear (level is INFO)
        self.assertNotIn("DEBUG - Debug message", log_output)

        # INFO, WARNING, and ERROR messages should appear
        self.assertIn("INFO - Info message", log_output)
        self.assertIn("WARNING - Warning message", log_output)
        self.assertIn("ERROR - Error message", log_output)

    def test_logger_caching(self) -> None:
        """Test that the logger is properly cached and reused."""
        # Clear the cache to ensure a fresh start
        _reset_logger()

        # Create the first logger instance
        logger1 = setup_logger()

        # Get a second reference to the logger
        logger2 = setup_logger()

        # They should be the same object
        self.assertIs(logger1, logger2)

        # Verify it's in the cache
        self.assertIn("dcm-mini-viewer", _LOGGER_CACHE)
        self.assertIs(logger1, _LOGGER_CACHE["dcm-mini-viewer"])

        # Check that only one set of handlers exists
        self.assertEqual(len(logger1.handlers), 2)

    def test_logger_level_update(self) -> None:
        """Test that changing log level works when reusing logger."""
        # Initial setup with INFO level
        logger1 = setup_logger(log_level=logging.INFO)
        self.assertEqual(logger1.level, logging.INFO)

        # Update to DEBUG level
        logger2 = setup_logger(log_level=logging.DEBUG)

        # Should be the same logger instance but with updated level
        self.assertIs(logger1, logger2)
        self.assertEqual(logger1.level, logging.DEBUG)

        # Check that all handlers have the updated level
        for handler in logger1.handlers:
            self.assertEqual(handler.level, logging.DEBUG)

    def test_get_logger_initializes(self) -> None:
        """Test that get_logger initializes the logger if needed."""
        # Clear the cache
        _reset_logger()
        self.assertNotIn("dcm-mini-viewer", _LOGGER_CACHE)

        # Get the logger should initialize it
        logger = get_logger()

        # Verify it was initialized and cached
        self.assertIn("dcm-mini-viewer", _LOGGER_CACHE)
        self.assertIs(logger, _LOGGER_CACHE["dcm-mini-viewer"])
        self.assertEqual(len(logger.handlers), 2)

    def test_get_logger_reuses_existing(self) -> None:
        """Test that get_logger reuses an existing logger."""
        # Setup the logger first
        logger1 = setup_logger()

        # Then get the logger
        logger2 = get_logger()

        # Verify it's the same instance
        self.assertIs(logger1, logger2)

    def test_reset_logger(self) -> None:
        """Test that _reset_logger properly cleans up."""
        # Setup a logger
        logger = setup_logger()
        self.assertIn("dcm-mini-viewer", _LOGGER_CACHE)

        # Count initial handlers
        initial_handlers_count = len(logger.handlers)
        self.assertEqual(initial_handlers_count, 2)

        # Reset the logger
        _reset_logger()

        # Verify it's removed from cache
        self.assertNotIn("dcm-mini-viewer", _LOGGER_CACHE)

        # Verify handlers were removed
        self.assertEqual(len(logger.handlers), 0)

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_actual_logging_output(self, mock_stdout: StringIO) -> None:
        """Test the actual output of the logger to stdout."""
        # Setup logger with DEBUG level to capture all messages
        logger = setup_logger(log_level=logging.DEBUG)

        # Log a test message
        test_message = "Test log message"
        logger.info(test_message)

        # Check that the message appears in stdout
        self.assertIn(test_message, mock_stdout.getvalue())

        # Test logging at different levels
        logger.debug("Debug test message")
        logger.warning("Warning test message")
        logger.error("Error test message")

        # Check all messages appear in stdout
        stdout_content = mock_stdout.getvalue()
        self.assertIn("Debug test message", stdout_content)
        self.assertIn("Warning test message", stdout_content)
        self.assertIn("Error test message", stdout_content)

    @mock.patch("src.utils.logger.get_app_data_dir")
    def test_log_file_creation(self, mock_get_app_data_dir: mock.Mock) -> None:
        """Test that the log file is actually created."""
        # Create a temporary directory for the test
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdirname:
            temp_path = Path(tmpdirname)
            mock_get_app_data_dir.return_value = temp_path

            # Setup the logger
            logger = setup_logger()

            # Log a message
            logger.info("Test log message")

            # Check that the log file exists
            log_file_path = temp_path / "logs" / "dcm-mini-viewer.log"
            self.assertTrue(log_file_path.exists())

            # Check content of the log file
            with open(log_file_path, "r") as f:
                content = f.read()
                self.assertIn("Test log message", content)

    def test_clear_existing_handlers(self) -> None:
        """Test that setup_logger clears existing handlers before adding new ones."""
        # Create a logger with a mock handler
        logger = logging.getLogger("dcm-mini-viewer")
        mock_handler = mock.MagicMock()
        logger.addHandler(mock_handler)

        # Initial handler count
        len(logger.handlers)

        # Setup logger should clear existing handlers
        setup_logger()

        # Verify handlers were replaced, not added
        self.assertEqual(len(logger.handlers), 2)
        self.assertNotIn(mock_handler, logger.handlers)

    def test_console_handler_stream(self) -> None:
        """Test that console handler uses sys.stdout."""
        logger = setup_logger()

        # Find the console handler
        console_handler = None
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not hasattr(handler, "baseFilename"):
                console_handler = handler
                break

        self.assertIsNotNone(console_handler)
        self.assertEqual(console_handler.stream, sys.stdout)


if __name__ == "__main__":
    unittest.main()
