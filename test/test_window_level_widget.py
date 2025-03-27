#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the WindowLevelWidget class.
"""
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from src.ui.main_window import WindowLevelWidget


@pytest.mark.usefixtures("qtbot")
class TestWindowLevelWidget:
    """Test cases for the WindowLevelWidget class."""

    @pytest.fixture
    def widget(self, qtbot):
        """Fixture providing an initialized WindowLevelWidget instance."""
        widget = WindowLevelWidget()
        qtbot.addWidget(widget)
        return widget

    def test_widget_initialization(self, widget: WindowLevelWidget) -> None:
        """Test initialization of the widget."""
        # Check initial values
        assert widget.window_value == 2000
        assert widget.level_value == 1000

        # Check slider ranges
        assert widget.window_min == 1
        assert widget.window_max == 4000
        assert widget.level_min == -1000
        assert widget.level_max == 3000

        # Check slider initial values
        assert widget.window_slider.value() == 2000
        assert widget.level_slider.value() == 1000

        # Check slider ranges match widget ranges
        assert widget.window_slider.minimum() == widget.window_min
        assert widget.window_slider.maximum() == widget.window_max
        assert widget.level_slider.minimum() == widget.level_min
        assert widget.level_slider.maximum() == widget.level_max

        # Check value labels
        assert widget.window_value_label.text() == "2000"
        assert widget.level_value_label.text() == "1000"

        # Check presence of preset buttons
        brain_button = widget.findChild(QPushButton, "brain_button")
        bone_button = widget.findChild(QPushButton, "bone_button")
        lung_button = widget.findChild(QPushButton, "lung_button")
        abdomen_button = widget.findChild(QPushButton, "abdomen_button")

        assert brain_button is not None or widget.brain_button is not None
        assert bone_button is not None or widget.bone_button is not None
        assert lung_button is not None or widget.lung_button is not None
        assert abdomen_button is not None or widget.abdomen_button is not None

    def test_window_slider_change(self, qtbot, widget: WindowLevelWidget) -> None:
        """Test changing the window slider updates values and emits signal."""
        # Set up signal spy
        with qtbot.waitSignal(widget.window_level_changed) as blocker:
            # Change the window slider value
            widget.window_slider.setValue(3000)

        # Check if signal was emitted with correct parameters
        assert blocker.args == [3000, 1000]

        # Check if widget values were updated
        assert widget.window_value == 3000
        assert widget.level_value == 1000
        assert widget.window_value_label.text() == "3000"

    def test_level_slider_change(self, qtbot, widget: WindowLevelWidget) -> None:
        """Test changing the level slider updates values and emits signal."""
        # Set up signal spy
        with qtbot.waitSignal(widget.window_level_changed) as blocker:
            # Change the level slider value
            widget.level_slider.setValue(500)

        # Check if signal was emitted with correct parameters
        assert blocker.args == [2000, 500]

        # Check if widget values were updated
        assert widget.window_value == 2000
        assert widget.level_value == 500
        assert widget.level_value_label.text() == "500"

    def test_brain_preset(self, qtbot, widget: WindowLevelWidget) -> None:
        """Test applying the brain preset."""
        # Click the brain preset button
        qtbot.mouseClick(widget.brain_button, Qt.LeftButton)

        # Check if values were updated correctly
        assert widget.window_value == 80
        assert widget.level_value == 40
        assert widget.window_slider.value() == 80
        assert widget.level_slider.value() == 40
        assert widget.window_value_label.text() == "80"
        assert widget.level_value_label.text() == "40"

    def test_bone_preset(self, qtbot, widget: WindowLevelWidget) -> None:
        """Test applying the bone preset."""
        # Click the bone preset button
        qtbot.mouseClick(widget.bone_button, Qt.LeftButton)

        # Check if values were updated correctly
        assert widget.window_value == 2000
        assert widget.level_value == 600
        assert widget.window_slider.value() == 2000
        assert widget.level_slider.value() == 600
        assert widget.window_value_label.text() == "2000"
        assert widget.level_value_label.text() == "600"

    def test_lung_preset(self, qtbot, widget: WindowLevelWidget) -> None:
        """Test applying the lung preset."""
        # Click the lung preset button
        qtbot.mouseClick(widget.lung_button, Qt.LeftButton)

        # Check if values were updated correctly
        assert widget.window_value == 1500
        assert widget.level_value == -600
        assert widget.window_slider.value() == 1500
        assert widget.level_slider.value() == -600
        assert widget.window_value_label.text() == "1500"
        assert widget.level_value_label.text() == "-600"

    def test_abdomen_preset(self, qtbot, widget: WindowLevelWidget) -> None:
        """Test applying the abdomen preset."""
        # Click the abdomen preset button
        qtbot.mouseClick(widget.abdomen_button, Qt.LeftButton)

        # Check if values were updated correctly
        assert widget.window_value == 400
        assert widget.level_value == 50
        assert widget.window_slider.value() == 400
        assert widget.level_slider.value() == 50
        assert widget.window_value_label.text() == "400"
        assert widget.level_value_label.text() == "50"

    def test_get_window_level(self, widget: WindowLevelWidget) -> None:
        """Test getting window/level values."""
        # Get initial values
        window, level = widget.get_window_level()

        # Check if values match expected values
        assert window == 2000
        assert level == 1000

        # Change values and check again
        widget.window_value = 1500
        widget.level_value = 500

        window, level = widget.get_window_level()
        assert window == 1500
        assert level == 500

    def test_set_window_level(self, widget: WindowLevelWidget) -> None:
        """Test setting window/level values."""
        # Set new values
        widget.set_window_level(1500, 500)

        # Check if widget values were updated
        assert widget.window_value == 1500
        assert widget.level_value == 500
        assert widget.window_slider.value() == 1500
        assert widget.level_slider.value() == 500
        assert widget.window_value_label.text() == "1500"
        assert widget.level_value_label.text() == "500"

    def test_apply_preset(self, widget: WindowLevelWidget) -> None:
        """Test applying a custom preset."""
        # Apply a custom preset
        widget.apply_preset(1800, 900)

        # Check if values were updated correctly
        assert widget.window_value == 1800
        assert widget.level_value == 900
        assert widget.window_slider.value() == 1800
        assert widget.level_slider.value() == 900
        assert widget.window_value_label.text() == "1800"
        assert widget.level_value_label.text() == "900"

    def test_set_window_level_range(self, widget: WindowLevelWidget) -> None:
        """Test setting window/level range."""
        # Set new range
        widget.set_window_level_range(10, 5000, -2000, 4000)

        # Check if ranges were updated
        assert widget.window_min == 10
        assert widget.window_max == 5000
        assert widget.level_min == -2000
        assert widget.level_max == 4000

        # Check if slider ranges were updated
        assert widget.window_slider.minimum() == 10
        assert widget.window_slider.maximum() == 5000
        assert widget.level_slider.minimum() == -2000
        assert widget.level_slider.maximum() == 4000

        # Values should remain unchanged
        assert widget.window_value == 2000
        assert widget.level_value == 1000

    def test_signal_emission(self, qtbot, widget: WindowLevelWidget) -> None:
        """Test that signals are emitted correctly when values change."""
        # Connect a mock function to the signal
        mock_callback = MagicMock()
        widget.window_level_changed.connect(mock_callback)

        # Change window value
        widget.window_slider.setValue(3000)

        # Check if callback was called with correct parameters
        mock_callback.assert_called_with(3000, 1000)
        mock_callback.reset_mock()

        # Change level value
        widget.level_slider.setValue(500)

        # Check if callback was called with correct parameters
        mock_callback.assert_called_with(3000, 500)
        mock_callback.reset_mock()

        # Apply preset
        widget.apply_preset(1500, 800)

        # Check if callback was called twice (once for window, once for level)
        assert mock_callback.call_count == 2
        # Last call should be with the final values
        mock_callback.assert_called_with(1500, 800)

    def test_slider_boundaries(self, widget: WindowLevelWidget) -> None:
        """Test that values stay within boundaries when setting sliders."""
        # Try setting values beyond boundaries
        widget.window_slider.setValue(widget.window_max + 100)
        widget.level_slider.setValue(widget.level_max + 100)

        # Check that values are clamped to maximum
        assert widget.window_value == widget.window_max
        assert widget.level_value == widget.level_max

        # Try setting values below boundaries
        widget.window_slider.setValue(widget.window_min - 100)
        widget.level_slider.setValue(widget.level_min - 100)

        # Check that values are clamped to minimum
        assert widget.window_value == widget.window_min
        assert widget.level_value == widget.level_min


if __name__ == "__main__":
    pytest.main(["-v", "test_window_level_widget.py"])
