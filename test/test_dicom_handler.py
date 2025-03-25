#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the DICOM handler.
"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pydicom
import pytest
from pydicom.dataset import Dataset, FileDataset

from src.dicom.dicom_handler import DicomHandler


class TestDicomHandler(unittest.TestCase):
    """Test case for the DicomHandler class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.dicom_handler = DicomHandler()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dicom_path = os.path.join(self.temp_dir.name, "test.dcm")

        # Create a minimal DICOM dataset for testing
        self.create_test_dicom_file()

    def tearDown(self) -> None:
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def create_test_dicom_file(self) -> None:
        """Create a minimal DICOM file for testing."""
        # Create a basic dataset
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'  # CT Image Storage
        file_meta.MediaStorageSOPInstanceUID = '1.2.3'
        file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.1'  # Explicit VR Little Endian

        ds = FileDataset(
            self.temp_dicom_path,
            {},
            file_meta=file_meta,
            preamble=b"\0" * 128
        )

        # Add some metadata
        ds.PatientName = "Test^Patient"
        ds.PatientID = "12345"
        ds.Modality = "CT"
        ds.StudyDate = "20230101"

        # Create a small pixel array
        pixel_array = np.zeros((10, 10), dtype=np.uint16)
        ds.PixelData = pixel_array.tobytes()
        ds.Rows = 10
        ds.Columns = 10
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 0

        # Save the dataset
        ds.save_as(self.temp_dicom_path)

    def test_load_file(self) -> None:
        """Test loading a DICOM file."""
        # Load the test DICOM file
        success, error = self.dicom_handler.load_file(self.temp_dicom_path)

        # Check that the file was loaded successfully
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertIsNotNone(self.dicom_handler.dataset)

    def test_load_nonexistent_file(self) -> None:
        """Test loading a nonexistent file."""
        # Try to load a nonexistent file
        success, error = self.dicom_handler.load_file("/nonexistent/file.dcm")

        # Check that the operation failed
        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertIn("File not found", error)

    def test_validate_elements(self) -> None:
        """Test validating DICOM elements."""
        # Load the test DICOM file
        self.dicom_handler.load_file(self.temp_dicom_path)

        # Original required elements
        original_elements = self.dicom_handler.REQUIRED_ELEMENTS.copy()

        # Set required elements to what we know exists in our test file
        self.dicom_handler.REQUIRED_ELEMENTS = [
            "PatientName",
            "PatientID",
            "Modality",
            "StudyDate",
            "PixelData"
        ]

        # Validate elements
        valid, missing = self.dicom_handler.validate_elements()

        # Check that all required elements are present
        self.assertTrue(valid)
        self.assertEqual(len(missing), 0)

        # Restore original required elements
        self.dicom_handler.REQUIRED_ELEMENTS = original_elements

    def test_validate_missing_elements(self) -> None:
        """Test validating DICOM elements with missing elements."""
        # Load the test DICOM file
        self.dicom_handler.load_file(self.temp_dicom_path)

        # Original required elements
        original_elements = self.dicom_handler.REQUIRED_ELEMENTS.copy()

        # Set required elements to include one that doesn't exist in our test file
        self.dicom_handler.REQUIRED_ELEMENTS = [
            "PatientName",
            "PatientID",
            "NonexistentElement"
        ]

        # Validate elements
        valid, missing = self.dicom_handler.validate_elements()

        # Check that validation failed and the missing element is reported
        self.assertFalse(valid)
        self.assertIn("NonexistentElement", missing)

        # Restore original required elements
        self.dicom_handler.REQUIRED_ELEMENTS = original_elements

    def test_get_pixel_array(self) -> None:
        """Test getting the pixel array."""
        # Load the test DICOM file
        self.dicom_handler.load_file(self.temp_dicom_path)

        # Get the pixel array
        pixel_array = self.dicom_handler.get_pixel_array()

        # Check that a pixel array was returned
        self.assertIsNotNone(pixel_array)
        self.assertEqual(pixel_array.shape, (10, 10))

    def test_get_metadata(self) -> None:
        """Test getting metadata."""
        # Load the test DICOM file
        self.dicom_handler.load_file(self.temp_dicom_path)

        # Get metadata
        metadata = self.dicom_handler.get_metadata()

        # Check that metadata was returned
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata["PatientName"], "Test^Patient")
        self.assertEqual(metadata["PatientID"], "12345")
        self.assertEqual(metadata["Modality"], "CT")
        self.assertEqual(metadata["StudyDate"], "20230101")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
