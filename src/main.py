#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for the OnkoDICOM discovery project.
This module initializes the application, sets up logging,
and starts the main UI.
"""
import sys
from typing import List, Optional

from PySide6.QtWidgets import QApplication

from src.config.preferences_manager import PreferencesManager
from ui.main_window import MainWindow
from utils.logger import setup_logger


def main(args: Optional[List[str]] = None) -> int:
    """
    Main application entry point.

    Args:
        args: Command-line arguments.

    Returns:
        int: Exit code.
    """
    if args is None:
        args = sys.argv[1:]

    # Setup logging
    logger = setup_logger()
    logger.info("Starting OnkoDICOM discovery application")

    # Initialize QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("OnkoDICOM Discovery")

    # Initialize preferences manager
    preferences_manager = PreferencesManager()
    preferences_manager.initialize()

    # Create and show main window
    main_window = MainWindow(preferences_manager)
    main_window.show()

    # Execute application
    logger.info("Application initialized. Starting event loop.")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
