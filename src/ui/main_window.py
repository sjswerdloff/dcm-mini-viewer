#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main window for the dcm-mini-viewer project with window/level functionality.
"""

import os
from typing import Optional, Tuple

import numpy as np
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from src.config.preferences_manager import PreferencesManager
from src.dicom.dicom_handler import DicomHandler
from src.ui.dialogs.element_dialog import ElementDialog
from src.utils.logger import get_logger


class WindowLevelWidget(QWidget):
    """
    Widget for controlling window/level (contrast/brightness) of DICOM images.
    """

    # pylint: disable=too-many-instance-attributes
    # Signals for when window or level changes
    window_level_changed = Signal(int, int)

    def __init__(self, parent=None) -> None:
        """
        Initialize the window/level widget.

        Args:
            parent: Parent widget.
        """
        super().__init__(parent)

        self.window_value: int = 2000
        self.level_value: int = 1000

        self.window_min: int = 1
        self.window_max: int = 4000
        self.level_min: int = -1000
        self.level_max: int = 3000

        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the widget UI."""
        # Create layout
        layout = QVBoxLayout(self)

        # Create group box for window/level controls
        group_box = QGroupBox("Window/Level Controls")
        group_layout = QGridLayout()

        # Window slider
        window_label = QLabel("Window:")
        self.window_slider = QSlider(Qt.Horizontal)
        self.window_slider.setMinimum(self.window_min)
        self.window_slider.setMaximum(self.window_max)
        self.window_slider.setValue(self.window_value)
        self.window_slider.setTickPosition(QSlider.TicksBelow)
        self.window_slider.setTickInterval(500)

        self.window_value_label = QLabel(f"{self.window_value}")

        # Level slider
        level_label = QLabel("Level:")
        self.level_slider = QSlider(Qt.Horizontal)
        self.level_slider.setMinimum(self.level_min)
        self.level_slider.setMaximum(self.level_max)
        self.level_slider.setValue(self.level_value)
        self.level_slider.setTickPosition(QSlider.TicksBelow)
        self.level_slider.setTickInterval(500)

        self.level_value_label = QLabel(f"{self.level_value}")

        # Connect signals
        self.window_slider.valueChanged.connect(self.on_window_changed)
        self.level_slider.valueChanged.connect(self.on_level_changed)

        # Add widgets to layout
        group_layout.addWidget(window_label, 0, 0)
        group_layout.addWidget(self.window_slider, 0, 1)
        group_layout.addWidget(self.window_value_label, 0, 2)

        group_layout.addWidget(level_label, 1, 0)
        group_layout.addWidget(self.level_slider, 1, 1)
        group_layout.addWidget(self.level_value_label, 1, 2)

        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

        # Add preset buttons
        presets_box = QGroupBox("Presets")
        presets_layout = QHBoxLayout()

        # Common DICOM window/level presets
        self.brain_button = QPushButton("Brain")
        self.brain_button.clicked.connect(lambda: self.apply_preset(80, 40))
        presets_layout.addWidget(self.brain_button)

        self.bone_button = QPushButton("Bone")
        self.bone_button.clicked.connect(lambda: self.apply_preset(2000, 600))
        presets_layout.addWidget(self.bone_button)

        self.lung_button = QPushButton("Lung")
        self.lung_button.clicked.connect(lambda: self.apply_preset(1500, -600))
        presets_layout.addWidget(self.lung_button)

        self.abdomen_button = QPushButton("Abdomen")
        self.abdomen_button.clicked.connect(lambda: self.apply_preset(400, 50))
        presets_layout.addWidget(self.abdomen_button)

        presets_box.setLayout(presets_layout)
        layout.addWidget(presets_box)

        # Add shortcut information
        info_label = QLabel(
            "Keyboard Shortcuts:\n"
            + "→: Increase Window\n"
            + "←: Decrease Window\n"
            + "↑: Increase Level\n"
            + "↓: Decrease Level"
        )
        layout.addWidget(info_label)

    @Slot(int)
    def on_window_changed(self, value: int) -> None:
        """
        Handle window value change.

        Args:
            value: New window value.
        """
        self.window_value = value
        self.window_value_label.setText(f"{value}")
        self.window_level_changed.emit(self.window_value, self.level_value)

    @Slot(int)
    def on_level_changed(self, value: int) -> None:
        """
        Handle level value change.

        Args:
            value: New level value.
        """
        self.level_value = value
        self.level_value_label.setText(f"{value}")
        self.window_level_changed.emit(self.window_value, self.level_value)

    def apply_preset(self, window: int, level: int) -> None:
        """
        Apply a window/level preset.

        Args:
            window: Window value.
            level: Level value.
        """
        # Update sliders (which will trigger the change signals)
        self.window_slider.setValue(window)
        self.level_slider.setValue(level)

    def get_window_level(self) -> Tuple[int, int]:
        """
        Get current window/level values.

        Returns:
            Tuple of (window, level) values.
        """
        return self.window_value, self.level_value

    def set_window_level(self, window: int, level: int) -> None:
        """
        Set window/level values.

        Args:
            window: Window value.
            level: Level value.
        """
        # Update sliders (which will trigger the change signals)
        self.window_slider.setValue(window)
        self.level_slider.setValue(level)

    def set_window_level_range(self, window_min: int, window_max: int, level_min: int, level_max: int) -> None:
        """
        Set range for window/level sliders.

        Args:
            window_min: Minimum window value.
            window_max: Maximum window value.
            level_min: Minimum level value.
            level_max: Maximum level value.
        """
        self.window_min = window_min
        self.window_max = window_max
        self.level_min = level_min
        self.level_max = level_max

        self.window_slider.setMinimum(window_min)
        self.window_slider.setMaximum(window_max)
        self.level_slider.setMinimum(level_min)
        self.level_slider.setMaximum(level_max)


class MainWindow(QMainWindow):
    """
    Main application window with window/level functionality.
    """

    # pylint: disable=too-many-instance-attributes
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

        # For window/level functionality
        self.window_level_widget: Optional[WindowLevelWidget] = None
        self.original_pixel_array: Optional[np.ndarray] = None
        self.window_value: int = 2000
        self.level_value: int = 1000

        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the main window user interface."""
        self.setWindowTitle("dcm-mini-viewer")
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

        # Set up window/level widget
        self.window_level_widget = WindowLevelWidget()
        self.window_level_widget.window_level_changed.connect(self.on_window_level_changed)

        # Add window/level widget to a dock widget
        window_level_dock = QDockWidget("Window/Level", self)
        window_level_dock.setWidget(self.window_level_widget)
        window_level_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, window_level_dock)

        # Set up menu bar
        self.setup_menu()
        self.menuBar().setVisible(True)

        # Set up toolbar
        self.setup_toolbar()

        # Set up keyboard shortcuts
        self.setup_shortcuts()

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

        # Window/Level menu
        wl_menu = self.menuBar().addMenu("&Window/Level")

        # Presets submenu
        presets_menu = wl_menu.addMenu("&Presets")

        # Brain preset
        brain_action = QAction("&Brain", self)
        brain_action.setStatusTip("Apply brain preset (W:80, L:40)")
        brain_action.triggered.connect(lambda: self.window_level_widget.apply_preset(80, 40))
        presets_menu.addAction(brain_action)

        # Bone preset
        bone_action = QAction("B&one", self)
        bone_action.setStatusTip("Apply bone preset (W:2000, L:600)")
        bone_action.triggered.connect(lambda: self.window_level_widget.apply_preset(2000, 600))
        presets_menu.addAction(bone_action)

        # Lung preset
        lung_action = QAction("&Lung", self)
        lung_action.setStatusTip("Apply lung preset (W:1500, L:-600)")
        lung_action.triggered.connect(lambda: self.window_level_widget.apply_preset(1500, -600))
        presets_menu.addAction(lung_action)

        # Abdomen preset
        abdomen_action = QAction("&Abdomen", self)
        abdomen_action.setStatusTip("Apply abdomen preset (W:400, L:50)")
        abdomen_action.triggered.connect(lambda: self.window_level_widget.apply_preset(400, 50))
        presets_menu.addAction(abdomen_action)

        # Reset action
        wl_menu.addSeparator()
        reset_action = QAction("&Reset to Default", self)
        reset_action.setStatusTip("Reset window/level to default values")
        reset_action.triggered.connect(lambda: self.window_level_widget.set_window_level(2000, 1000))
        wl_menu.addAction(reset_action)

        # Help menu
        help_menu = self.menuBar().addMenu("&Help")

        # Add Window/Level help action
        wl_help_action = QAction("Window/Level &Help", self)
        wl_help_action.setStatusTip("Show window/level help")
        wl_help_action.triggered.connect(self.show_window_level_help)
        help_menu.addAction(wl_help_action)

        # About action
        about_action = QAction("&About", self)
        about_action.setStatusTip("Show about dialog")
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

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

    @Slot(int, int)
    def on_window_level_changed(self, window: int, level: int) -> None:
        """
        Handle window/level change.

        Args:
            window: New window value.
            level: New level value.
        """
        self.window_value = window
        self.level_value = level
        self.apply_window_level()

    def increase_window(self) -> None:
        """Increase window value (widen the window)."""
        if self.window_level_widget:
            new_window = min(self.window_value + 100, self.window_level_widget.window_max)
            self.window_level_widget.set_window_level(new_window, self.level_value)

    def decrease_window(self) -> None:
        """Decrease window value (narrow the window)."""
        if self.window_level_widget:
            new_window = max(self.window_value - 100, self.window_level_widget.window_min)
            self.window_level_widget.set_window_level(new_window, self.level_value)

    def increase_level(self) -> None:
        """Increase level value (brighten the image)."""
        if self.window_level_widget:
            new_level = min(self.level_value + 100, self.window_level_widget.level_max)
            self.window_level_widget.set_window_level(self.window_value, new_level)

    def decrease_level(self):
        """Decrease level value (darken the image)."""
        if self.window_level_widget:
            new_level = max(self.level_value - 100, self.window_level_widget.level_min)
            self.window_level_widget.set_window_level(self.window_value, new_level)

    @Slot()
    def show_window_level_help(self) -> None:
        """Show help dialog for window/level functionality."""
        QMessageBox.information(
            self,
            "Window/Level Help",
            "Window/Level Controls:\n\n"
            "Window: Controls the contrast of the image\n"
            "- Higher values: Lower contrast\n"
            "- Lower values: Higher contrast\n\n"
            "Level: Controls the brightness of the image\n"
            "- Higher values: Brighter image\n"
            "- Lower values: Darker image\n\n"
            "Keyboard Shortcuts:\n"
            "- Right Arrow: Increase Window (decrease contrast)\n"
            "- Left Arrow: Decrease Window (increase contrast)\n"
            "- Up Arrow: Increase Level (brighten)\n"
            "- Down Arrow: Decrease Level (darken)\n\n"
            "Common Presets:\n"
            "- Brain: W:80, L:40\n"
            "- Bone: W:2000, L:600\n"
            "- Lung: W:1500, L:-600\n"
            "- Abdomen: W:400, L:50",
        )

    @Slot()
    def show_about_dialog(self) -> None:
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About dcm-mini-viewer",
            "dcm-mini-viewer Project\nA small application for viewing DICOM files with window/level functionality\n",
        )

    @Slot()
    def open_dicom_file(self) -> None:
        """Open a DICOM file dialog and load the selected file."""
        self.logger.info("Opening DICOM file dialog")

        # Get the default directory from preferences
        default_dir = self.preferences_manager.get_preference("dicom_directory", os.path.expanduser("~/Documents"))

        # Open file dialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Open DICOM File", default_dir, "DICOM Files (*.dcm);;All Files (*)")

        if not file_path:
            self.logger.info("No file selected")
            return

        # Update the default directory preference
        self.preferences_manager.set_preference("dicom_directory", os.path.dirname(file_path))

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
        """Display the DICOM image in the image label with window/level functionality."""
        if not self.image_label:
            return

        # Get pixel array
        pixel_array = self.dicom_handler.get_pixel_array()

        if pixel_array is None:
            self.image_label.setText("No image data available")
            return

        # Store original pixel array for windowing
        self.original_pixel_array = pixel_array.copy()

        # Set appropriate window/level range based on bit depth
        if self.window_level_widget:
            try:
                # Get bit depth from DICOM metadata
                bits_stored = self.dicom_handler.get_metadata().get("BitsStored", 16)
                bits_stored = int(bits_stored) if bits_stored else 16

                # Calculate range based on bit depth
                max_value = 2**bits_stored - 1

                # Set range for window/level sliders
                window_max = max_value
                level_max = max_value // 2
                level_min = -level_max

                self.window_level_widget.set_window_level_range(1, window_max, level_min, level_max)

                # Initialize window/level based on DICOM window center/width if available
                window_center = self.dicom_handler.get_metadata().get("WindowCenter")
                window_width = self.dicom_handler.get_metadata().get("WindowWidth")

                if window_center and window_width:
                    try:
                        # Convert to integers
                        window_center = int(float(window_center))
                        window_width = int(float(window_width))

                        # Set initial window/level values
                        self.window_level_widget.set_window_level(window_width, window_center)
                    except (ValueError, TypeError):
                        # Use default values if conversion fails
                        self.window_level_widget.set_window_level(2000, 1000)
                else:
                    # Use default values
                    self.window_level_widget.set_window_level(2000, 1000)
            except Exception as e:  # pylint: disable=broad-except
                self.logger.error(f"Error setting window/level range: {str(e)}")

        # Apply window/level
        self.apply_window_level()

    def setup_toolbar(self) -> None:
        """Set up the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        self.logger.info("Application closing")
        # Close the preferences database connection
        self.preferences_manager.close()
        super().closeEvent(event)

    def setup_shortcuts(self):
        """Set up keyboard shortcuts for window/level adjustments."""
        # Window increase/decrease
        window_increase = QAction("Increase Window", self)
        window_increase.setShortcut(QKeySequence(Qt.Key_Right))
        window_increase.triggered.connect(self.increase_window)
        self.addAction(window_increase)

        window_decrease = QAction("Decrease Window", self)
        window_decrease.setShortcut(QKeySequence(Qt.Key_Left))
        window_decrease.triggered.connect(self.decrease_window)
        self.addAction(window_decrease)

        # Level increase/decrease
        level_increase = QAction("Increase Level", self)
        level_increase.setShortcut(QKeySequence(Qt.Key_Up))
        level_increase.triggered.connect(self.increase_level)
        self.addAction(level_increase)

        level_decrease = QAction("Decrease Level", self)
        level_decrease.setShortcut(QKeySequence(Qt.Key_Down))
        level_decrease.triggered.connect(self.decrease_level)
        self.addAction(level_decrease)

    def display_dicom_image_with_window_level(self):
        """Display the DICOM image with window/level adjustments."""
        if not self.image_label:
            return

        # Get pixel array
        pixel_array = self.dicom_handler.get_pixel_array()

        if pixel_array is None:
            self.image_label.setText("No image data available")
            return

        # Store original pixel array for windowing
        self.original_pixel_array = pixel_array.copy()

        # Apply window/level
        if hasattr(self, "window_level_widget"):
            self.window_value, self.level_value = self.window_level_widget.get_window_level()
            self.apply_window_level()

    # Add method to apply window/level
    def apply_window_level(self):
        """Apply window/level to the image and display it."""
        if self.original_pixel_array is None or not self.image_label:
            return

        # Get window/level values
        window = self.window_value
        level = self.level_value

        # Calculate min and max values for windowing
        min_value = level - window / 2
        max_value = level + window / 2

        # Apply window/level
        windowed = np.clip(self.original_pixel_array, min_value, max_value)

        # Normalize to 8-bit (0-255)
        if min_value == max_value:
            normalized = np.zeros_like(windowed, dtype=np.uint8)
        else:
            normalized = (((windowed - min_value) / (max_value - min_value)) * 255).astype(np.uint8)

        # Create QImage from numpy array
        height, width = normalized.shape
        bytes_per_line = width

        # Create QImage (grayscale)
        q_image = QImage(normalized.data, width, height, bytes_per_line, QImage.Format_Grayscale8)

        # Create QPixmap from QImage
        pixmap = QPixmap.fromImage(q_image)

        # Set the pixmap to the label
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)

        # Update status bar
        self.statusBar().showMessage(f"Window: {window}, Level: {level}")
