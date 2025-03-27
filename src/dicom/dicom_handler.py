#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DICOM file handler for the OnkoDICOM discovery project.
Handles loading and validating DICOM files.
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pydicom
from pydicom.dataset import Dataset
from pydicom.errors import InvalidDicomError

from src.utils.logger import get_logger


class DicomHandler:
    """
    Handles loading and validating DICOM files.
    """

    # Required DICOM elements to check for
    # This list should be replaced with the actual list from Andrew or Stuart
    # For now, we'll use a placeholder list
    REQUIRED_ELEMENTS = ["PatientName", "PatientID", "Modality", "StudyDate", "PixelData"]

    def __init__(self) -> None:
        """Initialize the DICOM handler."""
        self.logger = get_logger()
        self.dataset: Optional[Dataset] = None

    def load_file(self, file_path: Union[str, Path]) -> Tuple[bool, Optional[str]]:
        """
        Load a DICOM file.

        Args:
            file_path: Path to the DICOM file.

        Returns:
            Tuple[bool, Optional[str]]: Success flag and error message if any.
        """
        file_path_str = str(file_path)
        self.logger.info(f"Loading DICOM file: {file_path_str}")

        if not os.path.exists(file_path_str):
            error_msg = f"File not found: {file_path_str}"
            self.logger.error(error_msg)
            return False, error_msg

        try:
            self.dataset = pydicom.dcmread(file_path_str, force=True)
            self.logger.info(f"Successfully loaded DICOM file: {file_path_str}")
            return True, None
        except InvalidDicomError as e:
            error_msg = f"Invalid DICOM file: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error loading DICOM file: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def validate_elements(self) -> Tuple[bool, List[str]]:
        """
        Validate that the DICOM file contains all required elements.

        Returns:
            Tuple[bool, List[str]]: Success flag and list of missing elements.
        """
        if not self.dataset:
            self.logger.error("No DICOM dataset loaded")
            return False, []

        missing_elements: List[str] = []

        for element in self.REQUIRED_ELEMENTS:
            try:
                _ = self.dataset[element]
            except KeyError:
                missing_elements.append(element)

        if missing_elements:
            self.logger.warning(f"Missing required DICOM elements: {', '.join(missing_elements)}")
            return False, missing_elements

        self.logger.info("All required DICOM elements are present")
        return True, []

    def get_pixel_array(self) -> Optional[object]:
        """
        Get the pixel array from the DICOM dataset.

        Returns:
            Optional[object]: The pixel array or None if not available.
        """
        if not self.dataset or "PixelData" not in self.dataset:
            self.logger.error("No pixel data available")
            return None
        # TODO: identify when byte swap is needed.  It might depend on the architecture
        # of the machine on which this is running.
        need_byte_swap = False
        try:
            if need_byte_swap:
                print(f"ByteSwap: {need_byte_swap}")
                return self.dataset.pixel_array.byteswap(inplace=True)
            return self.dataset.pixel_array
        except Exception as e:
            self.logger.error(f"Error getting pixel array: {str(e)}")
            return None

    def get_metadata(self) -> Dict[str, str]:
        """
        Get metadata from the DICOM dataset.

        Returns:
            Dict[str, str]: Dictionary of metadata.
        """
        metadata: Dict[str, str] = {}

        if not self.dataset:
            return metadata

        # Extract common metadata
        try:
            if hasattr(self.dataset, "PatientName"):
                metadata["PatientName"] = str(self.dataset.PatientName)

            if hasattr(self.dataset, "PatientID"):
                metadata["PatientID"] = str(self.dataset.PatientID)

            if hasattr(self.dataset, "Modality"):
                metadata["Modality"] = str(self.dataset.Modality)

            if hasattr(self.dataset, "StudyDate"):
                metadata["StudyDate"] = str(self.dataset.StudyDate)
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {str(e)}")

        return metadata
