#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Preferences manager for the mini-dcm-viewer project.
Handles reading and writing preferences to a SQLite database.
"""
import os
import sqlite3
from typing import Any, Dict, Optional

from src.utils.logger import get_app_data_dir, get_logger


class PreferencesManager:
    """
    Manages application preferences stored in a SQLite database.
    """

    def __init__(self) -> None:
        """Initialize the preferences manager."""
        self.logger = get_logger()
        self.app_data_dir = get_app_data_dir()
        self.db_path = self.app_data_dir / "preferences.db"
        self.connection: Optional[sqlite3.Connection] = None
        self.preferences: Dict[str, Any] = {}

    def initialize(self) -> None:
        """
        Initialize the preferences database.
        Creates the database and tables if they don't exist.
        """
        self.logger.info("Initializing preferences database")

        try:
            # Create the database connection
            self.connection = sqlite3.connect(str(self.db_path))
            cursor = self.connection.cursor()

            # Create the preferences table if it doesn't exist
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """
            )

            # Commit changes
            self.connection.commit()

            # Load preferences
            self.load_preferences()

            self.logger.info("Preferences database initialized")
        except sqlite3.Error as e:
            self.logger.error(f"Error initializing preferences database: {str(e)}")
            raise

    def load_preferences(self) -> None:
        """
        Load all preferences from the database into memory.
        """
        if not self.connection:
            self.logger.error("Database connection not initialized")
            return

        self.logger.info("Loading preferences from database")

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT key, value FROM preferences")

            # Clear existing preferences
            self.preferences.clear()

            # Load preferences from database
            for key, value in cursor.fetchall():
                self.preferences[key] = value

            # Set default preferences if not set
            if "dicom_directory" not in self.preferences:
                default_dicom_dir = os.path.expanduser("~/Documents")
                self.set_preference("dicom_directory", default_dicom_dir)

            self.logger.info(f"Loaded {len(self.preferences)} preferences")
        except sqlite3.Error as e:
            self.logger.error(f"Error loading preferences: {str(e)}")
            raise

    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a preference value by key.

        Args:
            key: The preference key.
            default: The default value if the key doesn't exist.

        Returns:
            Any: The preference value, or the default if not found.
        """
        return self.preferences.get(key, default)

    def set_preference(self, key: str, value: Any) -> None:
        """
        Set a preference value by key.

        Args:
            key: The preference key.
            value: The preference value.
        """
        if not self.connection:
            self.logger.error("Database connection not initialized")
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)", (key, str(value)))
            self.connection.commit()

            # Update in-memory preferences
            self.preferences[key] = value

            self.logger.info(f"Set preference: {key} = {value}")
        except sqlite3.Error as e:
            self.logger.error(f"Error setting preference {key}: {str(e)}")
            raise

    def close(self) -> None:
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            self.logger.info("Preferences database connection closed")
