#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main window for the OnkoDICOM discovery project.
"""
import os
from typing import Dict, Optional

import numpy as np
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QPixmap, QImage
from PySide6.QtWidgets import (
    QMainWindow, QToolBar, QFileDialog, QLabel,
    QVBoxLayout, QWidget, QScrollArea, QMessageBox,
    QStatusBar, QDockWidget, QListWidget, QListWidgetItem
)

from src.config.preferences_manager import PreferencesManager
from src.dicom.dicom_handler import DicomHandler
from src.ui.dialogs.element_dialog import ElementDialog
from src.utils.logger import get_logger


class MainWindow(QMainWindow):
    """
    Main application window.
    """

    def __init__(self, preferences_manager: PreferencesManager, parent=None) -> None:
        """
        Initialize the main window.

        Args:
            preferences_manager: Preferences manager instance.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.logger = get_logger()
        self.preferences_manager = preferences_manager
        self.dicom_handler = DicomHandler()

        self.image_label: Optional[QLabel] = None
        self.metadata_list: Optional[QListWidget] = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the main window user interface."""
        self.setWindowTitle("OnkoDICOM Discovery")
        self.resize(800, 600)

        # Set up central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout for central widget
        layout = QVBoxLayout(central_widget)

        # Scroll area for image
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Label for displaying the image
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        scroll_area.setWidget(self.image_label)

        # Add scroll area to layout
        layout.addWidget(scroll_area)

        # Set up metadata dock widget
        metadata_dock = QDockWidget("DICOM Metadata", self)
        metadata_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # Create metadata list widget
        self.metadata_list = QListWidget()
        metadata_dock.setWidget(self.metadata_list)

        # Add dock widget to main window
        self.addDockWidget(Qt.RightDockWidgetArea, metadata_dock)

        # Set up menu bar
        self.setup_menu()

        # Set up toolbar
        self.setup_toolbar()

        # Set up status bar
        self.statusBar().showMessage("Ready")

    def setup_menu(self) -> None:
        """Set up the menu bar."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")

        # Open action
        open_action = QAction("&Open DICOM", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open a DICOM file")
        open_action.triggered.connect(self.open_dicom_file)
        file_menu.addAction(open_action)

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = self.menuBar().addMenu("&Help")

        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("Show about dialog")
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def setup_toolbar(self) -> None:
        """Set up the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Open action
        open_action = QAction("Open DICOM", self)
        open_action.setStatusTip("Open a DICOM file")
        open_action.triggered.connect(self.open_dicom_file)
        toolbar.addAction(open_action)

    @Slot()
    def open_dicom_file(self) -> None:
        """Open a DICOM file dialog and load the selected file."""
        self.logger.info("Opening DICOM file dialog")

        # Get the default directory from preferences
        default_dir = self.preferences_manager.get_preference(
            "dicom_directory",
            os.path.expanduser("~/Documents")
        )

        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open DICOM File",
            default_dir,
            "DICOM Files (*.dcm);;All Files (*)"
        )

        if not file_path:
            self.logger.info("No file selected")
            return

        # Update the default directory preference
        self.preferences_manager.set_preference(
            "dicom_directory",
            os.path.dirname(file_path)
        )

        # Load the DICOM file
        success, error_msg = self.dicom_handler.load_file(file_path)

        if not success:
            QMessageBox.critical(self, "Error", error_msg or "Unknown error")
            return

        # Validate required elements
        valid, missing_elements = self.dicom_handler.validate_elements()

        if not valid:
            # Show missing elements dialog
            dialog = ElementDialog(missing_elements, self)
            if dialog.exec():
                action = dialog.get_action()

                if action == ElementDialog.ABORT:
                    self.logger.info("User aborted loading file")
                    return

                if action == ElementDialog.PROVIDE_VALUES:
                    values = dialog.get_values()
                    self.logger.info(f"User provided values: {values}")
                    # In a real implementation, these values would be added to the dataset
            else:
                # Dialog was cancelled
                self.logger.info("User cancelled element dialog")
                return

        # Display the image
        self.display_dicom_image()

        # Display metadata
        self.display_metadata()

        # Update status bar
        self.statusBar().showMessage(f"Loaded {file_path}")

    def display_dicom_image(self) -> None:
        """Display the DICOM image in the image label."""
        if not self.image_label:
            return

        # Get pixel array
        pixel_array = self.dicom_handler.get_pixel_array()

        if pixel_array is None:
            self.image_label.setText("No image data available")
            return

        # Normalize the pixel array for display
        try:
            # Convert to 8-bit unsigned integer
            if pixel_array.dtype != np.uint8:
                pixel_min = pixel_array.min()
                pixel_max = pixel_array.max()

                if pixel_min == pixel_max:
                    normalized = np.zeros_like(pixel_array, dtype=np.uint8)
                else:
                    normalized = (
                        ((pixel_array - pixel_min) / (pixel_max - pixel_min)) * 255
                    ).astype(np.uint8)
            else:
                normalized = pixel_array

            # Create QImage from numpy array
            height, width = normalized.shape
            bytes_per_line = width

            # Create QImage (grayscale)
            q_image = QImage(
                normalized.data,
                width,
                height,
                bytes_per_line,
                QImage.Format_Grayscale8
            )

            # Create QPixmap from QImage
            pixmap = QPixmap.fromImage(q_image)

            # Set the pixmap to the label
            self.image_label.setPixmap(pixmap)
            self.image_label.setScaledContents(True)

        except Exception as e:
            self.logger.error(f"Error displaying image: {str(e)}")
            self.image_label.setText(f"Error displaying image: {str(e)}")

    def display_metadata(self) -> None:
        """Display DICOM metadata in the metadata list."""
        if not self.metadata_list:
            return

        # Clear existing metadata
        self.metadata_list.clear()

        # Get metadata
        metadata = self.dicom_handler.get_metadata()

        # Add metadata items to list
        for key, value in metadata.items():
            item = QListWidgetItem(f"{key}: {value}")
            self.metadata_list.addItem(item)

    @Slot()
    def show_about_dialog(self) -> None:
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About OnkoDICOM Discovery",
            "OnkoDICOM Discovery Project\n"
            "A small application for viewing DICOM files\n"
            "Part of the OnkoDICOM project"
        )

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        self.logger.info("Application closing")
        # Close the preferences database connection
        self.preferences_manager.close()
        super().closeEvent(event)