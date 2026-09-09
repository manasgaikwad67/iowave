"""Tests for validation and preprocessing."""

import pytest
import numpy as np
from pathlib import Path
import tempfile

from iq_analyzer.processing.validation import validate_iq_data, validate_metadata, ValidationResult
from iq_analyzer.processing.preprocessing import preprocess_signal, PreprocessingConfig, estimate_dc_offset
from iq_analyzer.models import SignalMetadata


def test_validate_valid_iq():
    """Test validation of valid IQ data."""
    iq_data = np.random.randn(1000) + 1j * np.random.randn(1000)
    result = validate_iq_data(iq_data, 1e6)
    assert result.is_valid
    assert len(result.errors) == 0


def test_validate_nan_iq():
    """Test validation with NaN values."""
    iq_data = np.random.randn(1000) + 1j * np.random.randn(1000)
    iq_data[10] = np.nan + 1j * 0
    result = validate_iq_data(iq_data, 1e6)
    assert not result.is_valid
    assert any("NaN" in e for e in result.errors)


def test_validate_inf_iq():
    """Test validation with Inf values."""
    iq_data = np.random.randn(1000) + 1j * np.random.randn(1000)
    iq_data[10] = np.inf + 1j * 0
    result = validate_iq_data(iq_data, 1e6)
    assert not result.is_valid
    assert any("Inf" in e for e in result.errors)


def test_validate_all_zero():
    """Test validation of all-zero signal."""
    iq_data = np.zeros(1000, dtype=complex)
    result = validate_iq_data(iq_data, 1e6)
    assert result.is_valid  # Not an error, but warning
    assert any("zeros" in w.lower() for w in result.warnings)


def test_validate_constant():
    """Test validation of constant signal."""
    iq_data = np.full(1000, 1+1j, dtype=complex)
    result = validate_iq_data(iq_data, 1e6)
    assert result.is_valid
    assert any("constant" in w.lower() for w in result.warnings)


def test_validate_wrong_dimension():
    """Test validation of wrong dimensionality."""
    iq_data = np.random.randn(100, 10) + 1j * np.random.randn(100, 10)
    result = validate_iq_data(iq_data, 1e6)
    assert not result.is_valid
    assert any("1-dimensional" in e for e in result.errors)


def test_validate_metadata():
    """Test metadata validation."""
    metadata = SignalMetadata(
        filename="test.iq",
        file_path="/test.iq",
        extension=".iq",
        format="raw_iq",
        sample_rate=1e6,
        num_samples=1000,
        duration=0.001,
        num_channels=2,
        data_type="int16",
        bit_depth=16,
        iq_format="interleaved",
        endianness="little",
    )
    result = validate_metadata(metadata)
    assert result.is_valid


def test_validate_bad_metadata():
    """Test metadata validation with bad values."""
    metadata = SignalMetadata(
        filename="test.iq",
        file_path="/test.iq",
        extension=".iq",
        format="raw_iq",
        sample_rate=-1,  # Invalid
        num_samples=1000,
        duration=0.001,
        num_channels=2,
        data_type="int16",
        bit_depth=16,
        iq_format="interleaved",
        endianness="little",
    )
    result = validate_metadata(metadata)
    assert not result.is_valid
    assert any("sample rate" in e.lower() for e in result.errors)


def test_preprocessing_dc_removal():
    """Test DC offset removal."""
    iq_data = np.ones(1000, dtype=complex) + 0.1j * np.random.randn(1000)
    config = PreprocessingConfig(remove_dc_offset=True, normalize=False)
    processed, metadata, _ = preprocess_signal(iq_data, 1e6, config)

    assert metadata.dc_removed
    assert abs(np.mean(np.real(processed))) < 0.01
    assert abs(np.mean(np.imag(processed))) < 0.01


def test_preprocessing_normalize():
    """Test normalization."""
    iq_data = 5.0 * (np.random.randn(1000) + 1j * np.random.randn(1000))
    config = PreprocessingConfig(normalize=True, remove_dc_offset=False)
    processed, metadata, _ = preprocess_signal(iq_data, 1e6, config)

    assert metadata.normalized
    rms = np.sqrt(np.mean(np.abs(processed)**2))
    assert abs(rms - 1.0) < 0.01


def test_preprocessing_filter():
    """Test filtering."""
    # Signal with low-freq and high-freq components
    t = np.arange(10000) / 1e6
    sig_low = np.exp(1j * 2 * np.pi * 10e3 * t)    # 10 kHz
    sig_high = np.exp(1j * 2 * np.pi * 100e3 * t)  # 100 kHz
    iq_data = sig_low + 0.1 * sig_high

    config = PreprocessingConfig(
        filter_enabled=True,
        filter_type="lowpass",
        low_cut_hz=0,
        high_cut_hz=50e3,
        remove_dc_offset=False,
        normalize=False,
    )
    processed, metadata, _ = preprocess_signal(iq_data, 1e6, config)

    assert metadata.filter_applied
    assert metadata.filter_type == "lowpass"
    # High frequency component should be attenuated
    # Check by computing FFT
    from iq_analyzer.dsp import compute_fft
    fft_result = compute_fft(processed, 1e6)
    # Find power at 100 kHz
    idx_100k = np.argmin(np.abs(fft_result.frequencies - 100e3))
    idx_10k = np.argmin(np.abs(fft_result.frequencies - 10e3))
    # 100 kHz should be lower than 10 kHz
    assert fft_result.magnitude_spectrum[idx_100k] < fft_result.magnitude_spectrum[idx_10k]


def test_preprocessing_resample():
    """Test resampling."""
    iq_data = np.random.randn(10000) + 1j * np.random.randn(10000)
    config = PreprocessingConfig(
        resample_enabled=True,
        target_sample_rate=500000,
        remove_dc_offset=False,
        normalize=False,
    )
    processed, metadata, final_sr = preprocess_signal(iq_data, 1e6, config)

    assert metadata.resampled
    assert metadata.original_sample_rate == 1e6
    assert metadata.final_sample_rate == 500000
    assert final_sr == 500000
    assert len(processed) == 5000  # Half the samples


def test_estimate_dc_offset():
    """Test DC offset estimation."""
    iq_data = 0.5 + 0.3j + 0.1 * (np.random.randn(1000) + 1j * np.random.randn(1000))
    dc_i, dc_q = estimate_dc_offset(iq_data)
    assert abs(dc_i - 0.5) < 0.05
    assert abs(dc_q - 0.3) < 0.05
