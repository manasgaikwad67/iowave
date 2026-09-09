"""Tests for IQ loader."""

import pytest
import tempfile
import numpy as np
from pathlib import Path

from iq_analyzer.io.iq_loader import load_raw_iq, IQFormat, Endianness, IQLayout


def create_test_iq(filepath, n_samples=10000, dtype="int16", endianness="little", iq_layout="interleaved"):
    """Create a test raw IQ file."""
    # Generate test signal: complex exponential
    t = np.arange(n_samples)
    freq = 0.1  # Normalized frequency
    signal = np.exp(1j * 2 * np.pi * freq * t)
    I = np.real(signal)
    Q = np.imag(signal)

    if iq_layout == "interleaved":
        data = np.empty(2 * n_samples, dtype=np.float64)
        data[0::2] = I
        data[1::2] = Q
    else:
        data = np.concatenate([I, Q])

    # Convert to target dtype
    if dtype == "int16":
        data = np.int16(data * 32767)
    elif dtype == "float32":
        data = data.astype(np.float32)

    # Apply endianness
    if endianness == "big":
        data = data.astype(data.dtype.newbyteorder(">"))
    else:
        data = data.astype(data.dtype.newbyteorder("<"))

    data.tofile(filepath)


def test_load_interleaved_int16():
    """Test loading interleaved int16 IQ."""
    with tempfile.NamedTemporaryFile(suffix=".iq", delete=False) as f:
        create_test_iq(f.name, n_samples=10000, dtype="int16", endianness="little", iq_layout="interleaved")
        result = load_raw_iq(Path(f.name), sample_rate=2000000, dtype="int16", endianness="little", iq_layout="interleaved")

    assert result.iq_data is not None
    assert len(result.iq_data) == 10000
    assert result.sample_rate == 2000000
    assert result.metadata.data_type == "int16"
    assert result.metadata.iq_format == "interleaved"
    assert result.metadata.endianness == "little"


def test_load_separate_iq():
    """Test loading separate I/Q blocks."""
    with tempfile.NamedTemporaryFile(suffix=".iq", delete=False) as f:
        create_test_iq(f.name, n_samples=10000, dtype="int16", endianness="little", iq_layout="separate_i_q")
        result = load_raw_iq(Path(f.name), sample_rate=2000000, dtype="int16", endianness="little", iq_layout="separate_i_q")

    assert result.iq_data is not None
    assert len(result.iq_data) == 10000
    assert result.metadata.iq_format == "separate_i_q"


def test_load_big_endian():
    """Test loading big-endian data."""
    with tempfile.NamedTemporaryFile(suffix=".iq", delete=False) as f:
        create_test_iq(f.name, n_samples=10000, dtype="int16", endianness="big", iq_layout="interleaved")
        result = load_raw_iq(Path(f.name), sample_rate=2000000, dtype="int16", endianness="big", iq_layout="interleaved")

    assert result.iq_data is not None
    assert result.metadata.endianness == "big"


def test_load_float32():
    """Test loading float32 data."""
    with tempfile.NamedTemporaryFile(suffix=".iq", delete=False) as f:
        create_test_iq(f.name, n_samples=10000, dtype="float32", endianness="little", iq_layout="interleaved")
        result = load_raw_iq(Path(f.name), sample_rate=2000000, dtype="float32", endianness="little", iq_layout="interleaved")

    assert result.iq_data is not None
    assert result.metadata.data_type == "float32"
    assert result.metadata.bit_depth == 32


def test_invalid_sample_rate():
    """Test that raw IQ requires sample rate."""
    with tempfile.NamedTemporaryFile(suffix=".iq", delete=False) as f:
        create_test_iq(f.name)
        with pytest.raises(ValueError, match="Sample rate must be positive"):
            load_raw_iq(Path(f.name), sample_rate=0)


def test_wrong_dtype():
    """Test loading with wrong dtype - should produce garbage but not crash."""
    with tempfile.NamedTemporaryFile(suffix=".iq", delete=False) as f:
        create_test_iq(f.name, dtype="int16")
        # Try to load as float32 - should produce garbage but not crash
        result = load_raw_iq(Path(f.name), sample_rate=2000000, dtype="float32")
        # The data will be garbage but no warning is generated for dtype mismatch
        # This is expected behavior - user must specify correct dtype
        assert result.iq_data is not None
        assert len(result.iq_data) > 0
