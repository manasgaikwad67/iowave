"""Input validation utilities."""

import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass
from ..models import SignalMetadata
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of input validation."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]


def validate_file(file_path: Path) -> ValidationResult:
    """Validate that a file exists and is readable."""
    errors = []
    warnings = []

    if not file_path.exists():
        errors.append(f"File does not exist: {file_path}")
        return ValidationResult(False, errors, warnings)

    if not file_path.is_file():
        errors.append(f"Path is not a file: {file_path}")
        return ValidationResult(False, errors, warnings)

    try:
        file_size = file_path.stat().st_size
        if file_size == 0:
            errors.append("File is empty")
            return ValidationResult(False, errors, warnings)

        # Check file size against configured limit
        from ..config import settings
        max_mb = settings.get("file_loading.max_file_size_mb", 500)
        if file_size > max_mb * 1024 * 1024:
            warnings.append(f"File size ({file_size / (1024*1024):.1f} MB) exceeds limit ({max_mb} MB)")

        # Try to read first few bytes
        with open(file_path, "rb") as f:
            f.read(1024)

    except PermissionError:
        errors.append(f"Permission denied: {file_path}")
    except Exception as e:
        errors.append(f"Error reading file: {e}")

    return ValidationResult(len(errors) == 0, errors, warnings)


def validate_iq_data(
    iq_data: np.ndarray,
    sample_rate: float,
    min_samples: int = 10,
) -> ValidationResult:
    """Validate IQ data array."""
    errors = []
    warnings = []

    if iq_data is None:
        errors.append("IQ data is None")
        return ValidationResult(False, errors, warnings)

    if not isinstance(iq_data, np.ndarray):
        errors.append(f"IQ data is not a numpy array: {type(iq_data)}")
        return ValidationResult(False, errors, warnings)

    if iq_data.ndim != 1:
        errors.append(f"IQ data must be 1-dimensional, got {iq_data.ndim}D")
        return ValidationResult(False, errors, warnings)

    if len(iq_data) < min_samples:
        errors.append(f"Insufficient samples: {len(iq_data)} < {min_samples}")

    if not np.iscomplexobj(iq_data):
        warnings.append("IQ data is not complex type, converting")
        iq_data = iq_data.astype(np.complex128)

    # Check for NaN and Inf
    nan_count = np.sum(np.isnan(iq_data))
    inf_count = np.sum(np.isinf(iq_data))
    if nan_count > 0:
        errors.append(f"IQ data contains {nan_count} NaN values")
    if inf_count > 0:
        errors.append(f"IQ data contains {inf_count} Inf values")

    # Check for all zeros
    if np.all(iq_data == 0):
        warnings.append("IQ data is all zeros")

    # Check for constant signal
    if np.all(iq_data == iq_data[0]):
        warnings.append("IQ data is constant (no variation)")

    # Check for extreme clipping (for normalized data)
    if np.max(np.abs(iq_data)) >= 0.99:
        clipped = np.sum(np.abs(iq_data) >= 0.99)
        if clipped > len(iq_data) * 0.01:  # More than 1% clipped
            warnings.append(f"Possible clipping detected: {clipped} samples at max amplitude")

    # Check sample rate
    if sample_rate <= 0:
        errors.append(f"Invalid sample rate: {sample_rate}")
    elif sample_rate < 100:
        warnings.append(f"Very low sample rate: {sample_rate} Hz")
    elif sample_rate > 1e9:
        warnings.append(f"Very high sample rate: {sample_rate} Hz")

    # Check I/Q balance
    I = np.real(iq_data)
    Q = np.imag(iq_data)
    iq_ratio = np.std(I) / (np.std(Q) + 1e-10)
    if iq_ratio > 10 or iq_ratio < 0.1:
        warnings.append(f"I/Q amplitude imbalance detected: ratio = {iq_ratio:.2f}")

    return ValidationResult(len(errors) == 0, errors, warnings)


def validate_metadata(metadata: SignalMetadata) -> ValidationResult:
    """Validate signal metadata."""
    errors = []
    warnings = []

    if metadata.sample_rate <= 0:
        errors.append(f"Invalid sample rate: {metadata.sample_rate}")

    if metadata.num_samples <= 0:
        errors.append(f"Invalid number of samples: {metadata.num_samples}")

    if metadata.num_channels <= 0:
        errors.append(f"Invalid number of channels: {metadata.num_channels}")

    if metadata.duration <= 0:
        errors.append(f"Invalid duration: {metadata.duration}")

    if metadata.bit_depth not in [8, 16, 24, 32, 64]:
        warnings.append(f"Unusual bit depth: {metadata.bit_depth}")

    # Check consistency
    expected_duration = metadata.num_samples / metadata.sample_rate
    if abs(metadata.duration - expected_duration) > 1e-3:
        warnings.append(
            f"Duration inconsistency: metadata={metadata.duration:.3f}s, "
            f"calculated={expected_duration:.3f}s"
        )

    return ValidationResult(len(errors) == 0, errors, warnings)


def validate_preprocessing_params(params: dict) -> ValidationResult:
    """Validate preprocessing parameters."""
    errors = []
    warnings = []

    # Filter validation
    if params.get("filter_enabled", False):
        ftype = params.get("filter_type", "bandpass")
        low = params.get("low_cut_hz", 0)
        high = params.get("high_cut_hz", 0)

        if ftype in ["lowpass", "bandpass"]:
            if low <= 0:
                errors.append("Low cut frequency must be positive")
        if ftype in ["highpass", "bandpass"]:
            if high <= 0:
                errors.append("High cut frequency must be positive")
        if ftype == "bandpass":
            if low >= high:
                errors.append("Low cut must be less than high cut for bandpass")

        # Check against Nyquist
        # (sample rate would need to be passed separately)

    # Resample validation
    if params.get("resample_enabled", False):
        target = params.get("target_sample_rate", 0)
        if target <= 0:
            errors.append("Target sample rate must be positive")

    return ValidationResult(len(errors) == 0, errors, warnings)