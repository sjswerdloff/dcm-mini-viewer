#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test module for MainWindow class using pytest-qt plugin.
"""

from typing import List

import numpy as np
import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QPushButton, QRadioButton

from dcm_mini_viewer.config.preferences_manager import PreferencesManager
from dcm_mini_viewer.dicom.dicom_handler import DicomHandler
from dcm_mini_viewer.ui.main_window import MainWindow

# Add the parent directory to the path to import the application modules
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def preferences_manager() -> PreferencesManager:
    """Fixture for PreferencesManager."""
    # Create a test preferences manager
    manager = PreferencesManager()
    yield manager
    manager.close()


@pytest.fixture
def main_window(qtbot, preferences_manager) -> MainWindow:
    """Fixture for MainWindow."""
    window = MainWindow(preferences_manager)
    qtbot.addWidget(window)
    yield window
    window.close()


def test_main_window_initializes(main_window: MainWindow) -> None:
    """Test if MainWindow initializes properly."""
    assert main_window.windowTitle() == "dcm-mini-viewer"
    assert main_window.size().width() == 800
    assert main_window.size().height() == 600
    assert main_window.image_label is not None
    assert main_window.metadata_list is not None
    assert main_window.window_level_widget is not None


def test_window_level_widget_initializes(main_window: MainWindow) -> None:
    """Test if WindowLevelWidget initializes with correct default values."""
    window_level_widget = main_window.window_level_widget
    assert window_level_widget is not None

    window_value, level_value = window_level_widget.get_window_level()
    assert window_value == 2000
    assert level_value == 1000


def test_window_level_slider_changes(qtbot, main_window: MainWindow) -> None:
    """Test if WindowLevelWidget sliders change values properly."""
    window_level_widget = main_window.window_level_widget

    # Initial values
    assert window_level_widget.window_value == 2000
    assert window_level_widget.level_value == 1000

    # Change window slider - using direct setValue instead of qtbot.setValue
    window_level_widget.window_slider.setValue(1500)
    qtbot.wait(100)  # Wait for event processing
    assert window_level_widget.window_value == 1500

    # Change level slider
    window_level_widget.level_slider.setValue(500)
    qtbot.wait(100)  # Wait for event processing
    assert window_level_widget.level_value == 500


def test_preset_buttons(qtbot, main_window: MainWindow) -> None:
    """Test if preset buttons set correct window/level values."""
    window_level_widget = main_window.window_level_widget

    # Test brain preset
    qtbot.mouseClick(window_level_widget.brain_button, Qt.LeftButton)
    qtbot.wait(100)  # Wait for event processing
    assert window_level_widget.window_value == 80
    assert window_level_widget.level_value == 40

    # Test bone preset
    qtbot.mouseClick(window_level_widget.bone_button, Qt.LeftButton)
    qtbot.wait(100)  # Wait for event processing
    assert window_level_widget.window_value == 2000
    assert window_level_widget.level_value == 600

    # Test lung preset
    qtbot.mouseClick(window_level_widget.lung_button, Qt.LeftButton)
    qtbot.wait(100)  # Wait for event processing
    assert window_level_widget.window_value == 1500
    assert window_level_widget.level_value == -600

    # Test abdomen preset
    qtbot.mouseClick(window_level_widget.abdomen_button, Qt.LeftButton)
    qtbot.wait(100)  # Wait for event processing
    assert window_level_widget.window_value == 400
    assert window_level_widget.level_value == 50


def test_keyboard_shortcuts(qtbot, main_window: MainWindow, monkeypatch) -> None:
    """Test if keyboard shortcuts work correctly."""
    # Directly call the methods instead of relying on keyboard events
    # This is more reliable for testing

    # Set up initial values
    main_window.window_level_widget.set_window_level(2000, 1000)
    qtbot.wait(100)  # Wait for event processing

    # Test increase window method directly
    main_window.increase_window()
    qtbot.wait(100)  # Wait for event processing
    assert main_window.window_value == 2100

    # Test decrease window method
    main_window.decrease_window()
    qtbot.wait(100)  # Wait for event processing
    assert main_window.window_value == 2000

    # Test increase level method
    main_window.increase_level()
    qtbot.wait(100)  # Wait for event processing
    assert main_window.level_value == 1100

    # Test decrease level method
    main_window.decrease_level()
    qtbot.wait(100)  # Wait for event processing
    assert main_window.level_value == 1000


def test_apply_window_level(qtbot, main_window: MainWindow) -> None:
    """Test if apply_window_level updates the image correctly."""
    # Create a test numpy array
    test_array = np.ones((100, 100), dtype=np.int16) * 1000
    main_window.original_pixel_array = test_array.copy()

    # Set window/level values
    main_window.window_value = 2000
    main_window.level_value = 1000

    # Apply window/level
    main_window.apply_window_level()
    qtbot.wait(100)  # Wait for event processing

    # Check if the image is displayed
    assert main_window.image_label.pixmap() is not None


def test_show_window_level_help(qtbot, main_window: MainWindow, monkeypatch) -> None:
    """Test if window/level help dialog shows correctly."""
    # Mock QMessageBox.information
    messages = []

    def mock_information(parent, title, text):
        messages.append((title, text))
        return QMessageBox.Ok

    monkeypatch.setattr(QMessageBox, "information", mock_information)

    # Call the method
    main_window.show_window_level_help()

    # Check if the message box was shown with the correct title
    assert len(messages) == 1
    assert messages[0][0] == "Window/Level Help"


def test_show_about_dialog(qtbot, main_window: MainWindow, monkeypatch) -> None:
    """Test if about dialog shows correctly."""
    # Mock QMessageBox.about
    messages = []

    def mock_about(parent, title, text):
        messages.append((title, text))

    monkeypatch.setattr(QMessageBox, "about", mock_about)

    # Call the method
    main_window.show_about_dialog()

    # Check if the message box was shown with the correct title
    assert len(messages) == 1
    assert messages[0][0] == "About dcm-mini-viewer"


def test_set_window_level_range(qtbot, main_window: MainWindow) -> None:
    """Test if set_window_level_range updates slider ranges correctly."""
    window_level_widget = main_window.window_level_widget

    # Set new range
    window_level_widget.set_window_level_range(10, 5000, -2000, 2000)

    # Check if ranges are updated
    assert window_level_widget.window_slider.minimum() == 10
    assert window_level_widget.window_slider.maximum() == 5000
    assert window_level_widget.level_slider.minimum() == -2000
    assert window_level_widget.level_slider.maximum() == 2000


def test_open_dicom_file(qtbot, main_window: MainWindow, mocker) -> None:
    """Test if open_dicom_file works correctly."""
    # Mock QFileDialog.getOpenFileName
    mocker.patch.object(QFileDialog, "getOpenFileName", return_value=("/path/to/test.dcm", "DICOM Files (*.dcm)"))

    # Mock DicomHandler methods
    mocker.patch.object(DicomHandler, "load_file", return_value=(True, None))

    mocker.patch.object(DicomHandler, "validate_elements", return_value=(True, []))

    mocker.patch.object(DicomHandler, "get_pixel_array", return_value=np.ones((100, 100), dtype=np.int16) * 1000)

    mocker.patch.object(
        DicomHandler, "get_metadata", return_value={"BitsStored": "16", "WindowCenter": "1000", "WindowWidth": "2000"}
    )

    # Call the method
    main_window.open_dicom_file()
    qtbot.wait(100)  # Wait for event processing

    # Check if the status bar message is updated
    assert "Loaded /path/to/test.dcm" in main_window.statusBar().currentMessage()


def test_invalid_dicom_file(qtbot, main_window: MainWindow, mocker) -> None:
    """Test handling of invalid DICOM files."""
    # Mock QFileDialog.getOpenFileName
    mocker.patch.object(QFileDialog, "getOpenFileName", return_value=("/path/to/invalid.dcm", "DICOM Files (*.dcm)"))

    # Mock DicomHandler.load_file
    mocker.patch.object(DicomHandler, "load_file", return_value=(False, "Invalid DICOM file"))

    # Mock QMessageBox.critical
    messages = []

    def mock_critical(parent, title, text):
        messages.append((title, text))
        return QMessageBox.Ok

    mocker.patch.object(QMessageBox, "critical", side_effect=mock_critical)

    # Call the method
    main_window.open_dicom_file()
    qtbot.wait(100)  # Wait for event processing

    # Check if the error message was shown
    assert len(messages) == 1
    assert messages[0][0] == "Error"
    assert messages[0][1] == "Invalid DICOM file"


# def test_missing_dicom_elements(qtbot, main_window: MainWindow, mocker) -> None:
#     """Test handling of DICOM files with missing elements."""
#     # Mock QFileDialog.getOpenFileName
#     mocker.patch.object(
#         QFileDialog,
#         "getOpenFileName",
#         return_value=("/path/to/test.dcm", "DICOM Files (*.dcm)")
#     )
#     # Mock DicomHandler methods
#     mocker.patch.object(
#         DicomHandler,
#         "load_file",
#         return_value=(True, None)
#     )
#     mocker.patch.object(
#         DicomHandler,
#         "validate_elements",
#         return_value=(False, ["PatientID", "StudyInstanceUID"])
#     )
#     # Create a mock ElementDialog that will be returned by any ElementDialog constructor
#     mock_dialog = mocker.Mock()
#     mock_dialog.exec.return_value = True
#     mock_dialog.get_action.return_value = ElementDialog.ABORT
#     # Call the method
#     main_window.open_dicom_file()
#     qtbot.wait(100)  # Wait for event processing
#     # Check that the dialog was shown and the action was queried
#  #   mock_dialog.exec.assert_called_once()
#  #   mock_dialog.get_action.assert_called_once()
#     # Check that the file was not loaded (no pixmap)
#     assert main_window.image_label.pixmap() is None or main_window.image_label.text() == "No image loaded"


def handle_element_dialog(qtbot):
    # Find the active modal dialog
    dialog = QApplication.activeModalWidget()

    # Verify it's the expected dialog
    print(dialog)
    if dialog and "ElementDialog" in dialog.__class__.__name__:
        # Find and click the Abort radio button
        print("Found Element Dialog")
        list_of_radio_buttons: List[QRadioButton] = dialog.findChildren(QRadioButton)
        list_of_names = [x.objectName() for x in list_of_radio_buttons]
        print(list_of_names)
        list_of_text = [x.text() for x in list_of_radio_buttons]
        print(list_of_text)
        list_of_push_buttons: List[QPushButton] = dialog.findChildren(QPushButton)
        list_of_names = [x.objectName() for x in list_of_push_buttons]
        print(list_of_names)
        list_of_text = [x.text() for x in list_of_push_buttons]
        print(list_of_text)
        if abort_button := next((button for button in list_of_radio_buttons if button.text().startswith("Abort")), None):
            qtbot.mouseClick(abort_button, Qt.LeftButton)

        # Find and click the OK button
        if ok_button := next((button for button in list_of_push_buttons if button.text().startswith("OK")), None):
            qtbot.mouseClick(ok_button, Qt.LeftButton)


def test_missing_dicom_elements(qtbot, main_window, mocker):
    # Set up to trigger the dialog
    main_window.image_label.clear()
    # Mock QFileDialog.getOpenFileName
    mocker.patch.object(QFileDialog, "getOpenFileName", return_value=("/path/to/test.dcm", "DICOM Files (*.dcm)"))

    # Mock DicomHandler methods
    mocker.patch.object(DicomHandler, "load_file", return_value=(True, None))

    mocker.patch.object(DicomHandler, "validate_elements", return_value=(False, ["PatientID", "StudyInstanceUID"]))

    # Start the operation that will show the dialog
    # Use a timer to handle the dialog after it appears
    QTimer.singleShot(500, lambda: handle_element_dialog(qtbot))

    # Call the method that will show the dialog
    main_window.open_dicom_file()

    # Allow time for the dialog interaction to complete
    qtbot.wait(1000)

    # Verify the expected outcome after dialog interaction
    pixmap = main_window.image_label.pixmap()
    assert pixmap is None or pixmap.isNull(), "Expected pixmap to be None or empty"


def test_window_level_signals(qtbot, main_window: MainWindow) -> None:
    """Test if window/level signals work correctly."""
    window_level_widget = main_window.window_level_widget

    # Set up signal spy
    with qtbot.waitSignal(window_level_widget.window_level_changed) as signal:
        # Change window value
        window_level_widget.on_window_changed(1500)

    # Check if signal was emitted with correct values
    assert signal.args == [1500, 1000]

    # Set up signal spy for level change
    with qtbot.waitSignal(window_level_widget.window_level_changed) as signal:
        # Change level value
        window_level_widget.on_level_changed(500)

    # Check if signal was emitted with correct values
    assert signal.args == [1500, 500]


def test_closeEvent(qtbot, main_window: MainWindow, mocker) -> None:
    """Test if closeEvent closes the preferences manager correctly."""
    # Mock PreferencesManager.close
    close_mock = mocker.patch.object(PreferencesManager, "close")

    # Close the window
    main_window.close()
    qtbot.wait(100)  # Wait for event processing

    # Check if preferences manager was closed
    close_mock.assert_called_once()


def test_set_window_level(qtbot, main_window: MainWindow) -> None:
    """Test if set_window_level sets values correctly."""
    window_level_widget = main_window.window_level_widget

    # Set new values
    window_level_widget.set_window_level(1500, 500)
    qtbot.wait(100)  # Wait for event processing

    # Check if values are updated
    assert window_level_widget.window_slider.value() == 1500
    assert window_level_widget.level_slider.value() == 500
    assert window_level_widget.window_value == 1500
    assert window_level_widget.level_value == 500


if __name__ == "__main__":
    pytest.main(["-v", __file__])
