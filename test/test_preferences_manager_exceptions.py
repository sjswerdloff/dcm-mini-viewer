#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests specifically for exception handling in the preferences manager.
"""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pytest

from src.config.preferences_manager import PreferencesManager


class TestPreferencesManagerNotInitialized(unittest.TestCase):
    """Test case for operations when database is not initialized."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.TemporaryDirectory()

        # Mock the get_app_data_dir function to return our temporary directory
        self.patcher = mock.patch("src.config.preferences_manager.get_app_data_dir", return_value=Path(self.temp_dir.name))
        self.mock_get_app_data_dir = self.patcher.start()

        # Mock the logger to prevent actual logging during tests
        self.logger_patcher = mock.patch("src.config.preferences_manager.get_logger", return_value=mock.MagicMock())
        self.mock_logger = self.logger_patcher.start()

        # Create a fresh preferences manager instance with no connection
        self.preferences_manager = PreferencesManager()
        self.preferences_manager.connection = None

    def tearDown(self) -> None:
        """Tear down test fixtures."""
        # Stop the patchers
        self.patcher.stop()
        self.logger_patcher.stop()

        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def test_load_preferences_not_initialized(self) -> None:
        """Test loading preferences when the database is not initialized."""
        # Should log an error but not raise an exception
        self.preferences_manager.load_preferences()

        # Verify preferences is empty
        self.assertEqual(self.preferences_manager.preferences, {})

        # Verify error was logged
        self.preferences_manager.logger.error.assert_called_once_with("Database connection not initialized")

    def test_set_preference_not_initialized(self) -> None:
        """Test setting a preference when the database is not initialized."""
        # Should log an error but not raise an exception
        self.preferences_manager.set_preference("test_key", "test_value")

        # Verify preference was not set
        self.assertEqual(self.preferences_manager.get_preference("test_key", None), None)

        # Verify error was logged
        self.preferences_manager.logger.error.assert_called_once_with("Database connection not initialized")


class TestPreferencesManagerSqliteErrors(unittest.TestCase):
    """Test case for SQLite error handling."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.TemporaryDirectory()

        # Mock the get_app_data_dir function to return our temporary directory
        self.patcher = mock.patch("src.config.preferences_manager.get_app_data_dir", return_value=Path(self.temp_dir.name))
        self.mock_get_app_data_dir = self.patcher.start()

        # Mock the logger to prevent actual logging during tests
        self.logger_patcher = mock.patch("src.config.preferences_manager.get_logger", return_value=mock.MagicMock())
        self.mock_logger = self.logger_patcher.start()

    def tearDown(self) -> None:
        """Tear down test fixtures."""
        # Stop the patchers
        self.patcher.stop()
        self.logger_patcher.stop()

        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def test_initialize_sqlite_error(self) -> None:
        """Test handling of sqlite3.Error during initialization."""
        # Create a preferences manager instance
        preferences_manager = PreferencesManager()

        # Create a mock for sqlite3.connect that raises an error
        with mock.patch("src.config.preferences_manager.sqlite3.connect", side_effect=sqlite3.Error("Mock database error")):
            # Should raise the sqlite3.Error
            with self.assertRaises(sqlite3.Error):
                preferences_manager.initialize()

            # Verify error was logged
            preferences_manager.logger.error.assert_called_once()

    def test_load_preferences_sqlite_error(self) -> None:
        """Test handling of sqlite3.Error during load_preferences."""
        # Create a preferences manager with a mocked connection
        preferences_manager = PreferencesManager()

        # Create a mock connection and cursor
        mock_conn = mock.MagicMock()
        mock_cursor = mock.MagicMock()

        # Configure cursor to raise error on SELECT
        def mock_execute(query, *args):
            if query.strip().startswith("SELECT"):
                raise sqlite3.Error("Mock database error")

        mock_cursor.execute.side_effect = mock_execute
        mock_conn.cursor.return_value = mock_cursor

        # Inject the mocked connection
        preferences_manager.connection = mock_conn

        # Should raise the sqlite3.Error
        with self.assertRaises(sqlite3.Error):
            preferences_manager.load_preferences()

        # Verify error was logged
        preferences_manager.logger.error.assert_called_once()

    def test_set_preference_sqlite_error(self) -> None:
        """Test handling of sqlite3.Error during set_preference."""
        # Create a preferences manager with a mocked connection
        preferences_manager = PreferencesManager()

        # Create a mock connection and cursor
        mock_conn = mock.MagicMock()
        mock_cursor = mock.MagicMock()

        # Configure cursor to raise error on INSERT/UPDATE
        def mock_execute(query, *args):
            if query.strip().startswith("INSERT") or query.strip().startswith("UPDATE"):
                raise sqlite3.Error("Mock database error")

        mock_cursor.execute.side_effect = mock_execute
        mock_conn.cursor.return_value = mock_cursor

        # Inject the mocked connection
        preferences_manager.connection = mock_conn

        # Should raise the sqlite3.Error
        with self.assertRaises(sqlite3.Error):
            preferences_manager.set_preference("test_key", "test_value")

        # Verify error was logged
        preferences_manager.logger.error.assert_called_once()

    def test_database_corruption_scenario(self) -> None:
        """Test a scenario where the database becomes corrupted after initialization."""
        # Create a fresh preferences manager instance
        preferences_manager = PreferencesManager()

        # Initialize a real sqlite database in memory for this test
        preferences_manager.db_path = ":memory:"
        preferences_manager.initialize()

        # Set a preference successfully
        preferences_manager.set_preference("key1", "value1")

        # Close the connection
        preferences_manager.connection.close()

        # Replace with a mock connection that simulates corruption
        mock_conn = mock.MagicMock()
        mock_cursor = mock.MagicMock()
        mock_cursor.execute.side_effect = sqlite3.DatabaseError("Database is corrupted")
        mock_conn.cursor.return_value = mock_cursor

        # Inject the corrupted connection
        preferences_manager.connection = mock_conn

        # Attempt to set a preference should raise DatabaseError
        with self.assertRaises(sqlite3.DatabaseError):
            preferences_manager.set_preference("key2", "value2")

        # Verify error was logged
        preferences_manager.logger.error.assert_called_once()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
