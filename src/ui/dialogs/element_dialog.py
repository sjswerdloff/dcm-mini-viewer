#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialog for handling missing DICOM elements.
"""
from typing import Dict, List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QGroupBox, QDialogButtonBox,
    QListWidget, QListWidgetItem
)

from utils.logger import get_logger


class ElementDialog(QDialog):
    """
    Dialog for handling missing DICOM elements.
    Allows the user to choose how to proceed when required elements are missing.
    """

    # Action constants
    CONTINUE = 0
    ABORT = 1
    PROVIDE_VALUES = 2

    def __init__(self, missing_elements: List[str], parent=None) -> None:
        """
        Initialize the dialog.

        Args:
            missing_elements: List of missing element names.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.logger = get_logger()
        self.missing_elements = missing_elements
        self.action = self.ABORT
        self.values: Dict[str, str] = {}

        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the dialog user interface."""
        self.setWindowTitle("Missing DICOM Elements")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Information label
        info_label = QLabel(
            "The following required DICOM elements are missing. "
            "Please choose how to proceed:"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # List of missing elements
        elements_list = QListWidget()
        for element in self.missing_elements:
            item = QListWidgetItem(element)
            elements_list.addItem(item)
        layout.addWidget(elements_list)

        # Option group
        option_group = QGroupBox("Options")
        option_layout = QVBoxLayout()

        # Radio buttons for options
        self.rb_continue = QRadioButton("Continue without these elements")
        self.rb_abort = QRadioButton("Abort loading this file")
        self.rb_provide = QRadioButton("Provide values for missing elements")

        # Button group for mutual exclusion
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.rb_continue, self.CONTINUE)
        self.button_group.addButton(self.rb_abort, self.ABORT)
        self.button_group.addButton(self.rb_provide, self.PROVIDE_VALUES)

        # Select abort by default
        self.rb_abort.setChecked(True)

        option_layout.addWidget(self.rb_continue)
        option_layout.addWidget(self.rb_abort)
        option_layout.addWidget(self.rb_provide)
        option_group.setLayout(option_layout)
        layout.addWidget(option_group)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self) -> None:
        """Handle dialog acceptance."""
        self.action = self.button_group.checkedId()
        self.logger.info(f"User chose action {self.action} for missing elements")

        if self.action == self.PROVIDE_VALUES:
            # In a real implementation, this would open another dialog
            # to collect values for each missing element
            self.logger.info("User would provide values for missing elements")
            # For now, we'll just set empty values
            for element in self.missing_elements:
                self.values[element] = ""

        super().accept()

    def get_action(self) -> int:
        """
        Get the selected action.

        Returns:
            int: The selected action.
        """
        return self.action

    def get_values(self) -> Dict[str, str]:
        """
        Get the provided values for missing elements.

        Returns:
            Dict[str, str]: Dictionary of element names and values.
        """
        return self.values
