"""Raw IQ file loader."""

import numpy as np
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass
from ..models import SignalMetadata
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class IQLoadResult:
    """Result of raw IQ file loading."""

    iq_data: np.ndarray  # Complex IQ samples
    sample_rate: float
    metadata: SignalMetadata
    warnings: List[str]


class IQFormat:
    """Supported raw IQ data formats."""

    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    FLOAT32 = "float32"
    FLOAT64 = "float64"

    @classmethod
    def all(cls) -> List[str]:
        return [cls.INT8, cls.INT16, cls.INT32, cls.FLOAT32, cls.FLOAT64]

    @classmethod
    def get_dtype(cls, format_str: str) -> np.dtype:
        mapping = {
            cls.INT8: np.int8,
            cls.INT16: np.int16,
            cls.INT32: np.int32,
            cls.FLOAT32: np.float32,
            cls.FLOAT64: np.float64,
        }
        if format_str not in mapping:
            raise ValueError(f"Unsupported IQ format: {format_str}")
        return mapping[format_str]

    @classmethod
    def get_max_value(cls, format_str: str) -> float:
        """Get maximum value for normalization."""
        if format_str in [cls.INT8, cls.INT16, cls.INT32]:
            dtype = cls.get_dtype(format_str)
            return float(np.iinfo(dtype).max)
        return 1.0


class Endianness:
    """Supported endianness options."""

    LITTLE = "little"
    BIG = "big"

    @classmethod
    def all(cls) -> List[str]:
        return [cls.LITTLE, cls.BIG]


class IQLayout:
    """Supported IQ data layouts."""

    INTERLEAVED = "interleaved"  # I,Q,I,Q,I,Q...
    SEPARATE_I_Q = "separate_i_q"  # All I samples, then all Q samples

    @classmethod
    def all(cls) -> List[str]:
        return [cls.INTERLEAVED, cls.SEPARATE_I_Q]


def load_raw_iq(
    file_path: Path,
    sample_rate: float,
    dtype: str = "int16",
    endianness: str = "little",
    iq_layout: str = "interleaved",
    offset_bytes: int = 0,
    max_samples: Optional[int] = None,
) -> IQLoadResult:
    """
    Load raw IQ file with specified parameters.

    Args:
        file_path: Path to raw IQ file
        sample_rate: Sample rate in Hz (required for raw IQ)
        dtype: Data type (int8, int16, int32, float32, float64)
        endianness: Endianness (little, big)
        iq_layout: IQ layout (interleaved, separate_i_q)
        offset_bytes: Byte offset to start reading
        max_samples: Maximum number of IQ samples to load

    Returns:
        IQLoadResult with IQ data and metadata
    """
    path = Path(file_path)
    warnings = []

    # Validate parameters
    if sample_rate <= 0:
        raise ValueError("Sample rate must be positive for raw IQ files")

    try:
        np_dtype = IQFormat.get_dtype(dtype)
    except ValueError as e:
        warnings.append(str(e))
        np_dtype = np.int16
        dtype = "int16"

    if endianness not in Endianness.all():
        warnings.append(f"Unknown endianness: {endianness}, using little")
        endianness = Endianness.LITTLE

    if iq_layout not in IQLayout.all():
        warnings.append(f"Unknown IQ layout: {iq_layout}, using interleaved")
        iq_layout = IQLayout.INTERLEAVED

    # Determine numpy dtype with endianness
    # Create dtype instance first, then apply endianness
    dtype_instance = np.dtype(np_dtype)
    if endianness == Endianness.BIG:
        np_dtype = dtype_instance.newbyteorder(">")
    else:
        np_dtype = dtype_instance.newbyteorder("<")

    # Read file
    try:
        with open(path, "rb") as f:
            if offset_bytes > 0:
                f.seek(offset_bytes)
            raw_data = f.read()
    except Exception as e:
        raise IOError(f"Failed to read file: {e}")

    if len(raw_data) == 0:
        raise ValueError("File is empty")

    # Convert to numpy array
    itemsize = np_dtype.itemsize
    total_samples = len(raw_data) // itemsize

    if max_samples is not None:
        total_samples = min(total_samples, max_samples * (2 if iq_layout == IQLayout.INTERLEAVED else 1))

    total_samples = total_samples * itemsize
    raw_data = raw_data[:total_samples]
    data = np.frombuffer(raw_data, dtype=np_dtype)

    # Convert to float and normalize
    if np.issubdtype(np_dtype, np.integer):
        max_val = IQFormat.get_max_value(dtype)
        data = data.astype(np.float64) / max_val
    else:
        data = data.astype(np.float64)

    # Parse IQ layout
    if iq_layout == IQLayout.INTERLEAVED:
        if len(data) % 2 != 0:
            warnings.append("Odd number of samples in interleaved format, dropping last sample")
            data = data[:-1]
        n_iq_samples = len(data) // 2
        I = data[0::2]
        Q = data[1::2]
    else:  # separate_i_q
        if len(data) % 2 != 0:
            warnings.append("Odd number of samples in separate I/Q format, dropping last sample")
            data = data[:-1]
        half = len(data) // 2
        I = data[:half]
        Q = data[half:]
        n_iq_samples = half

    iq_data = I + 1j * Q

    # Create metadata
    duration = n_iq_samples / sample_rate
    bit_depth = itemsize * 8

    metadata = SignalMetadata(
        filename=path.name,
        file_path=str(path),
        extension=path.suffix.lower(),
        format="raw_iq",
        sample_rate=sample_rate,
        num_samples=n_iq_samples,
        duration=duration,
        num_channels=2,
        data_type=dtype,
        bit_depth=bit_depth,
        iq_format=iq_layout,
        endianness=endianness,
        scale_factor=1.0,
        warnings=warnings,
    )

    logger.info(
        f"Loaded raw IQ: {path.name}, {dtype}, {endianness}, {iq_layout}, "
        f"{sample_rate/1e6:.3f} MHz, {n_iq_samples} samples"
    )

    return IQLoadResult(
        iq_data=iq_data,
        sample_rate=sample_rate,
        metadata=metadata,
        warnings=warnings,
    )


def estimate_iq_params(file_path: Path, sample_rate: float) -> dict:
    """
    Attempt to estimate IQ parameters by analyzing file content.
    This is heuristic and not guaranteed to be correct.
    """
    path = Path(file_path)
    file_size = path.stat().st_size

    suggestions = {
        "sample_rate": sample_rate,
        "dtype": "int16",
        "endianness": "little",
        "iq_layout": "interleaved",
        "warnings": [],
    }

    # Try different formats and see which gives reasonable I/Q statistics
    best_score = -1
    best_params = None

    for dtype in IQFormat.all():
        for endianness in Endianness.all():
            for iq_layout in IQLayout.all():
                try:
                    result = load_raw_iq(
                        path,
                        sample_rate=sample_rate,
                        dtype=dtype,
                        endianness=endianness,
                        iq_layout=iq_layout,
                        max_samples=10000,
                    )
                    # Score based on I/Q balance and range
                    iq = result.iq_data
                    I = np.real(iq)
                    Q = np.imag(iq)

                    # Check for reasonable range
                    i_range = np.max(I) - np.min(I)
                    q_range = np.max(Q) - np.min(Q)

                    # Check balance
                    balance = 1.0 - abs(np.std(I) - np.std(Q)) / (np.std(I) + np.std(Q) + 1e-10)

                    # Check for DC offset
                    dc_i = abs(np.mean(I))
                    dc_q = abs(np.mean(Q))
                    dc_penalty = (dc_i + dc_q) / 2

                    score = balance * 0.5 + min(i_range, q_range) * 0.5 - dc_penalty

                    if score > best_score:
                        best_score = score
                        best_params = {
                            "dtype": dtype,
                            "endianness": endianness,
                            "iq_layout": iq_layout,
                        }
                except Exception:
                    continue

    if best_params:
        suggestions.update(best_params)
        suggestions["warnings"].append(
            f"Auto-detected parameters (heuristic): {best_params}. "
            "Please verify manually."
        )
    else:
        suggestions["warnings"].append("Could not auto-detect parameters, using defaults")

    return suggestions