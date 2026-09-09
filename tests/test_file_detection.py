"""Tests for file detection."""

import pytest
import tempfile
from pathlib import Path
import struct

from iq_analyzer.io.file_detector import detect_file_type, FileType
from iq_analyzer.processing.validation import validate_file


def test_detect_wav():
    """Test WAV file detection."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        # Write minimal valid WAV header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36))  # File size - 8
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))  # fmt chunk size
        f.write(struct.pack("<H", 1))   # PCM
        f.write(struct.pack("<H", 2))   # 2 channels
        f.write(struct.pack("<I", 44100))  # Sample rate
        f.write(struct.pack("<I", 176400)) # Byte rate
        f.write(struct.pack("<H", 4))   # Block align
        f.write(struct.pack("<H", 16))  # Bits per sample
        f.write(b"data")
        f.write(struct.pack("<I", 0))   # Data size
        f.flush()

        result = detect_file_type(Path(f.name))
        assert result.file_type == FileType.WAV
        assert result.confidence == 1.0
        assert result.extension == ".wav"


def test_detect_raw_iq_by_extension():
    """Test raw IQ detection by extension."""
    with tempfile.NamedTemporaryFile(suffix=".iq", delete=False) as f:
        f.write(b"\x00" * 100)
        f.flush()

        result = detect_file_type(Path(f.name))
        assert result.file_type == FileType.RAW_IQ
        assert result.confidence == 0.7
        assert "sample_rate" in result.suggested_params


def test_validate_readable_file():
    """Test file validation for readable file."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test data")
        f.flush()

    result = validate_file(Path(f.name))
    assert result.is_valid
    assert len(result.errors) == 0


def test_validate_nonexistent_file():
    """Test file validation for nonexistent file."""
    result = validate_file(Path("/nonexistent/file.iq"))
    assert not result.is_valid
    assert len(result.errors) > 0
    assert "does not exist" in result.errors[0]


def test_validate_empty_file():
    """Test file validation for empty file."""
    # Create an explicitly empty file
    with tempfile.NamedTemporaryFile(delete=False) as f:
        pass  # Don't write anything, just create the file
    
    # Get the file path before the context manager closes
    filepath = Path(f.name)
    
    # Verify file size is 0
    assert filepath.stat().st_size == 0
    
    # Now validate it - should return error, not warning
    result = validate_file(filepath)
    assert not result.is_valid
    assert len(result.errors) > 0
    assert "empty" in result.errors[0].lower()
