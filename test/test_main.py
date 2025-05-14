#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the main.py module.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication
from dcm_mini_viewer import main

from dcm_mini_viewer.config.preferences_manager import PreferencesManager
from dcm_mini_viewer.ui.main_window import MainWindow


@pytest.fixture
def mock_logger():
    """Fixture to provide a mock logger."""
    with patch("src.main.setup_logger") as mock_setup_logger:
        mock_logger = MagicMock()
        mock_setup_logger.return_value = mock_logger
        yield mock_logger


@pytest.fixture
def mock_preferences_manager():
    """Fixture to provide a mock preferences manager."""
    with patch("src.main.PreferencesManager") as mock_pref_manager_class:
        mock_manager = MagicMock(spec=PreferencesManager)
        mock_pref_manager_class.return_value = mock_manager
        yield mock_manager


@pytest.fixture
def mock_main_window():
    """Fixture to provide a mock main window."""
    with patch("src.main.MainWindow") as mock_window_class:
        mock_window = MagicMock(spec=MainWindow)
        mock_window_class.return_value = mock_window
        yield mock_window


class TestMain:
    """Test cases for the main module."""

    def test_main_with_default_args(self, qtbot, mock_logger, mock_preferences_manager, mock_main_window):
        """Test the main function with default arguments."""
        # Prepare the test
        with patch("src.main.QApplication") as mock_app_class:
            mock_app = MagicMock(spec=QApplication)
            mock_app_class.return_value = mock_app
            mock_app.exec.return_value = 0

            # Execute the function
            result = main.main()

            # Verify the results
            assert result == 0
            mock_logger.info.assert_any_call("Starting dcm-mini-viewer application")
            mock_logger.info.assert_any_call("Application initialized. Starting event loop.")
            mock_app_class.assert_called_once_with(sys.argv)
            mock_app.setApplicationName.assert_called_once_with("dcm-mini-viewer")
            mock_preferences_manager.initialize.assert_called_once()
            mock_main_window.show.assert_called_once()
            mock_app.exec.assert_called_once()

    def test_main_with_custom_args(self, qtbot, mock_logger, mock_preferences_manager, mock_main_window):
        """Test the main function with custom arguments."""
        # Prepare the test
        custom_args = ["--debug", "--config=test.cfg"]

        with patch("src.main.QApplication") as mock_app_class:
            mock_app = MagicMock(spec=QApplication)
            mock_app_class.return_value = mock_app
            mock_app.exec.return_value = 0

            # Execute the function
            result = main.main(custom_args)

            # Verify the results
            assert result == 0
            mock_logger.info.assert_any_call("Starting dcm-mini-viewer application")
            mock_app.setApplicationName.assert_called_once_with("dcm-mini-viewer")
            mock_preferences_manager.initialize.assert_called_once()

    def test_qapplication_creation(self, qtbot, mock_logger, mock_preferences_manager, mock_main_window):
        """Test the QApplication creation and configuration."""
        with patch("src.main.QApplication") as mock_app_class:
            mock_app = MagicMock(spec=QApplication)
            mock_app_class.return_value = mock_app
            mock_app.exec.return_value = 0

            main.main()

            mock_app_class.assert_called_once_with(sys.argv)
            mock_app.setApplicationName.assert_called_once_with("dcm-mini-viewer")

    def test_main_window_creation(self, qtbot, mock_logger, mock_preferences_manager):
        """Test the MainWindow creation with correct parameters."""
        with patch("src.main.QApplication") as mock_app_class, patch("src.main.MainWindow") as mock_window_class:
            mock_app = MagicMock(spec=QApplication)
            mock_app_class.return_value = mock_app
            mock_app.exec.return_value = 0

            mock_window = MagicMock(spec=MainWindow)
            mock_window_class.return_value = mock_window

            main.main()

            mock_window_class.assert_called_once_with(mock_preferences_manager)
            mock_window.show.assert_called_once()

    def test_application_exit_code(self, qtbot, mock_logger, mock_preferences_manager, mock_main_window):
        """Test that the application exit code is correctly returned."""
        expected_exit_code = 42

        with patch("src.main.QApplication") as mock_app_class:
            mock_app = MagicMock(spec=QApplication)
            mock_app_class.return_value = mock_app
            mock_app.exec.return_value = expected_exit_code

            result = main.main()

            assert result == expected_exit_code
            mock_app.exec.assert_called_once()

    def test_main_script_execution(self, qtbot, mock_logger, mock_preferences_manager, mock_main_window):
        """Test the script execution when run as __main__."""
        with patch("sys.exit") as mock_sys_exit, patch("src.main.QApplication", MagicMock()) as mock_app_class:
            # Configure QApplication mock to prevent instantiation conflicts
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_app.exec.return_value = 0

            # Execute the main function and call sys.exit with its return value,
            # simulating the behavior of `if __name__ == "__main__": sys.exit(main())`
            return_value = main.main()
            mock_sys_exit(return_value)

            # Verify sys.exit was called with the correct value (0)
            mock_sys_exit.assert_called_once_with(0)
