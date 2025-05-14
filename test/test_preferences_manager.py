#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the preferences manager.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pytest

from dcm_mini_viewer.config.preferences_manager import PreferencesManager


class TestPreferencesManager(unittest.TestCase):
    """Test case for the PreferencesManager class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.TemporaryDirectory()

        # Mock the get_app_data_dir function to return our temporary directory
        self.patcher = mock.patch("src.config.preferences_manager.get_app_data_dir", return_value=Path(self.temp_dir.name))
        self.mock_get_app_data_dir = self.patcher.start()

        # Create an instance of the preferences manager
        self.preferences_manager = PreferencesManager()

    def tearDown(self) -> None:
        """Tear down test fixtures."""
        # Stop the patcher
        self.patcher.stop()

        # Close the preferences manager
        self.preferences_manager.close()

        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def test_initialize(self) -> None:
        """Test initializing the preferences manager."""
        # Initialize the preferences manager
        self.preferences_manager.initialize()

        # Check that the database file was created
        db_path = Path(self.temp_dir.name) / "preferences.db"
        self.assertTrue(os.path.exists(db_path))

        # Check that the connection was established
        self.assertIsNotNone(self.preferences_manager.connection)

    def test_set_get_preference(self) -> None:
        """Test setting and getting preferences."""
        # Initialize the preferences manager
        self.preferences_manager.initialize()

        # Set a preference
        self.preferences_manager.set_preference("test_key", "test_value")

        # Get the preference
        value = self.preferences_manager.get_preference("test_key")

        # Check that the value is correct
        self.assertEqual(value, "test_value")

    def test_get_nonexistent_preference(self) -> None:
        """Test getting a nonexistent preference."""
        # Initialize the preferences manager
        self.preferences_manager.initialize()

        # Get a nonexistent preference with a default value
        value = self.preferences_manager.get_preference("nonexistent_key", "default_value")

        # Check that the default value was returned
        self.assertEqual(value, "default_value")

    def test_load_preferences(self) -> None:
        """Test loading preferences from the database."""
        # Initialize the preferences manager
        self.preferences_manager.initialize()

        # Set preferences
        self.preferences_manager.set_preference("key1", "value1")
        self.preferences_manager.set_preference("key2", "value2")

        # Create a new preferences manager instance to load from the database
        new_preferences_manager = PreferencesManager()
        new_preferences_manager.initialize()

        # Check that the preferences were loaded
        self.assertEqual(new_preferences_manager.get_preference("key1"), "value1")
        self.assertEqual(new_preferences_manager.get_preference("key2"), "value2")

        # Clean up
        new_preferences_manager.close()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
