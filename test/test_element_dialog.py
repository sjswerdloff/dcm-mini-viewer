#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the ElementDialog class.
"""

from typing import Dict, List
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialogButtonBox, QListWidget

from dcm_mini_viewer.ui.dialogs.element_dialog import ElementDialog


@pytest.mark.usefixtures("qtbot")
class TestElementDialog:
    """Test cases for the ElementDialog class."""

    @pytest.fixture
    def missing_elements(self) -> List[str]:
        """Fixture providing a list of missing DICOM elements."""
        return ["PatientName", "PatientID", "StudyDate"]

    @pytest.fixture
    def dialog(self, qtbot, missing_elements: List[str]):
        """Fixture providing an initialized ElementDialog instance."""
        with patch("src.ui.dialogs.element_dialog.get_logger") as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            dialog = ElementDialog(missing_elements)
            qtbot.addWidget(dialog)
            dialog.mock_logger = mock_logger  # Store for test assertions
            return dialog

    def test_dialog_initialization(self, dialog: ElementDialog, missing_elements: List[str]) -> None:
        """Test initialization of the dialog."""
        # Check if the dialog was initialized properly
        assert dialog.windowTitle() == "Missing DICOM Elements"
        assert dialog.missing_elements == missing_elements
        assert dialog.action == ElementDialog.ABORT
        assert dialog.values == {}

        # Check if radio buttons are properly set up
        assert dialog.rb_abort.isChecked()
        assert not dialog.rb_continue.isChecked()
        assert not dialog.rb_provide.isChecked()

        # Check if button group contains all radio buttons
        assert dialog.button_group.button(ElementDialog.CONTINUE) == dialog.rb_continue
        assert dialog.button_group.button(ElementDialog.ABORT) == dialog.rb_abort
        assert dialog.button_group.button(ElementDialog.PROVIDE_VALUES) == dialog.rb_provide

    def test_continue_action(self, qtbot, dialog: ElementDialog) -> None:
        """Test selecting the 'Continue' action."""
        # Select the continue option
        dialog.rb_continue.setChecked(True)

        # Simulate clicking the OK button
        buttons = dialog.findChild(QDialogButtonBox)
        qtbot.mouseClick(buttons.button(QDialogButtonBox.Ok), Qt.LeftButton)

        # Check if the action was updated correctly
        assert dialog.get_action() == ElementDialog.CONTINUE
        assert dialog.get_values() == {}
        dialog.mock_logger.info.assert_called_with(f"User chose action {ElementDialog.CONTINUE} for missing elements")

    def test_abort_action(self, qtbot, dialog: ElementDialog) -> None:
        """Test selecting the 'Abort' action (default)."""
        # The abort option is already selected by default

        # Simulate clicking the OK button
        buttons = dialog.findChild(QDialogButtonBox)
        qtbot.mouseClick(buttons.button(QDialogButtonBox.Ok), Qt.LeftButton)

        # Check if the action was updated correctly
        assert dialog.get_action() == ElementDialog.ABORT
        assert dialog.get_values() == {}
        dialog.mock_logger.info.assert_called_with(f"User chose action {ElementDialog.ABORT} for missing elements")

    def test_provide_values_action(self, qtbot, dialog: ElementDialog, missing_elements: List[str]) -> None:
        """Test selecting the 'Provide values' action."""
        # Select the provide values option
        dialog.rb_provide.setChecked(True)

        # Simulate clicking the OK button
        buttons = dialog.findChild(QDialogButtonBox)
        qtbot.mouseClick(buttons.button(QDialogButtonBox.Ok), Qt.LeftButton)

        # Check if the action was updated correctly
        assert dialog.get_action() == ElementDialog.PROVIDE_VALUES

        # Check if empty values were created for each missing element
        expected_values: Dict[str, str] = {element: "" for element in missing_elements}
        assert dialog.get_values() == expected_values

        # Check logger calls
        dialog.mock_logger.info.assert_any_call(f"User chose action {ElementDialog.PROVIDE_VALUES} for missing elements")
        dialog.mock_logger.info.assert_any_call("User would provide values for missing elements")

    def test_reject(self, qtbot, dialog: ElementDialog) -> None:
        """Test rejecting the dialog."""
        # Get the initial values
        initial_action = dialog.get_action()
        initial_values = dialog.get_values()

        # Simulate clicking the Cancel button
        buttons = dialog.findChild(QDialogButtonBox)
        with patch.object(dialog, "reject") as mock_reject:
            qtbot.mouseClick(buttons.button(QDialogButtonBox.Cancel), Qt.LeftButton)
            mock_reject.assert_called_once()

        # Check if values remain unchanged
        assert dialog.get_action() == initial_action
        assert dialog.get_values() == initial_values

    def test_list_widget_items(self, dialog: ElementDialog, missing_elements: List[str]) -> None:
        """Test if list widget contains all missing element items."""
        # Find the list widget and check its contents
        list_widget = dialog.findChild(QListWidget)
        assert list_widget.count() == len(missing_elements)

        # Check each item in the list
        for i, element in enumerate(missing_elements):
            item = list_widget.item(i)
            assert item.text() == element


if __name__ == "__main__":
    pytest.main(["-v", "test_element_dialog.py"])
