"""Signal preprocessing pipeline."""

import numpy as np
from scipy import signal
from typing import Optional, List, Tuple
from dataclasses import dataclass
from ..models import PreprocessingMetadata
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class PreprocessingConfig:
    """Configuration for preprocessing pipeline."""

    remove_nan_inf: bool = True
    remove_dc_offset: bool = True
    normalize: bool = False
    detrend: bool = False
    filter_enabled: bool = False
    filter_type: str = "bandpass"  # lowpass, highpass, bandpass, notch
    low_cut_hz: float = 1000
    high_cut_hz: float = 100000
    filter_order: int = 4
    filter_design: str = "sos"  # sos, ba
    resample_enabled: bool = False
    target_sample_rate: float = 1024000
    decimation_factor: int = 1


def preprocess_signal(
    iq_data: np.ndarray,
    sample_rate: float,
    config: Optional[PreprocessingConfig] = None,
) -> Tuple[np.ndarray, PreprocessingMetadata, float]:
    """
    Apply preprocessing pipeline to IQ signal.

    Args:
        iq_data: Complex IQ signal
        sample_rate: Sample rate in Hz
        config: Preprocessing configuration

    Returns:
        Tuple of (processed_signal, preprocessing_metadata, final_sample_rate)
    """
    if config is None:
        config = PreprocessingConfig()

    original_sample_rate = sample_rate
    original_length = len(iq_data)
    processed = iq_data.copy()
    metadata = PreprocessingMetadata()
    warnings = []

    # Stage 1: Remove NaN/Inf
    if config.remove_nan_inf:
        processed, removed = _remove_nan_inf(processed)
        if removed > 0:
            metadata.number_of_samples_removed += removed
            warnings.append(f"Removed {removed} NaN/Inf samples")

    # Stage 2: Remove DC offset
    if config.remove_dc_offset:
        processed = _remove_dc_offset(processed)
        metadata.dc_removed = True

    # Stage 3: Normalize
    if config.normalize:
        processed = _normalize(processed)
        metadata.normalized = True

    # Stage 4: Detrend
    if config.detrend:
        processed = _detrend(processed)

    # Stage 5: Filter
    if config.filter_enabled:
        processed, sample_rate = _apply_filter(
            processed,
            sample_rate,
            config.filter_type,
            config.low_cut_hz,
            config.high_cut_hz,
            config.filter_order,
            config.filter_design,
        )
        metadata.filter_applied = True
        metadata.filter_type = config.filter_type
        metadata.low_cut = config.low_cut_hz
        metadata.high_cut = config.high_cut_hz
        metadata.final_sample_rate = sample_rate

    # Stage 6: Resample
    if config.resample_enabled and config.target_sample_rate != sample_rate:
        processed, sample_rate = _resample(processed, sample_rate, config.target_sample_rate)
        metadata.resampled = True
        metadata.original_sample_rate = original_sample_rate
        metadata.final_sample_rate = sample_rate

    # Stage 7: Decimation
    if config.decimation_factor > 1:
        processed, sample_rate = _decimate(processed, sample_rate, config.decimation_factor)
        metadata.resampled = True
        if metadata.original_sample_rate is None:
            metadata.original_sample_rate = original_sample_rate
        metadata.final_sample_rate = sample_rate

    metadata.warnings = warnings

    if metadata.final_sample_rate is None:
        metadata.final_sample_rate = sample_rate

    logger.debug(
        f"Preprocessing complete: {original_length} -> {len(processed)} samples, "
        f"{original_sample_rate/1e6:.3f} -> {sample_rate/1e6:.3f} MHz"
    )

    return processed, metadata, sample_rate


def _remove_nan_inf(data: np.ndarray) -> Tuple[np.ndarray, int]:
    """Remove NaN and Inf values from signal."""
    mask = np.isfinite(data)
    removed = np.sum(~mask)
    if removed > 0:
        return data[mask], removed
    return data, 0


def _remove_dc_offset(data: np.ndarray) -> np.ndarray:
    """Remove DC offset from I and Q channels independently."""
    I = np.real(data)
    Q = np.imag(data)
    I = I - np.mean(I)
    Q = Q - np.mean(Q)
    return I + 1j * Q


def _normalize(data: np.ndarray) -> np.ndarray:
    """Normalize signal to unit RMS."""
    rms = np.sqrt(np.mean(np.abs(data) ** 2))
    if rms > 0:
        return data / rms
    return data


def _detrend(data: np.ndarray) -> np.ndarray:
    """Remove linear trend from I and Q channels."""
    I = signal.detrend(np.real(data))
    Q = signal.detrend(np.imag(data))
    return I + 1j * Q


def _apply_filter(
    data: np.ndarray,
    sample_rate: float,
    filter_type: str,
    low_cut: float,
    high_cut: float,
    order: int,
    design: str,
) -> Tuple[np.ndarray, float]:
    """Apply digital filter to signal."""
    nyquist = sample_rate / 2

    if filter_type == "lowpass":
        if high_cut >= nyquist:
            high_cut = nyquist * 0.99
        sos = signal.butter(order, high_cut / nyquist, btype="low", output="sos")
    elif filter_type == "highpass":
        if low_cut >= nyquist:
            low_cut = nyquist * 0.01
        sos = signal.butter(order, low_cut / nyquist, btype="high", output="sos")
    elif filter_type == "bandpass":
        if low_cut >= nyquist:
            low_cut = nyquist * 0.01
        if high_cut >= nyquist:
            high_cut = nyquist * 0.99
        if low_cut >= high_cut:
            raise ValueError("Low cut must be less than high cut")
        sos = signal.butter(order, [low_cut / nyquist, high_cut / nyquist], btype="band", output="sos")
    elif filter_type == "notch":
        # Notch filter at specific frequency
        if low_cut >= nyquist:
            low_cut = nyquist * 0.5
        Q = 30  # Quality factor
        sos = signal.iirnotch(low_cut / nyquist, Q, output="sos")
    else:
        raise ValueError(f"Unknown filter type: {filter_type}")

    if design == "sos":
        I = signal.sosfilt(sos, np.real(data))
        Q = signal.sosfilt(sos, np.imag(data))
    else:
        b, a = signal.sos2tf(sos)
        I = signal.filtfilt(b, a, np.real(data))
        Q = signal.filtfilt(b, a, np.imag(data))

    return I + 1j * Q, sample_rate


def _resample(
    data: np.ndarray,
    original_rate: float,
    target_rate: float,
) -> Tuple[np.ndarray, float]:
    """Resample signal to target sample rate."""
    if target_rate == original_rate:
        return data, original_rate

    # Calculate resampling ratio
    up = int(target_rate)
    down = int(original_rate)

    # Simplify ratio
    from math import gcd
    g = gcd(up, down)
    up //= g
    down //= g

    # Limit ratio to avoid excessive computation
    if up > 1000 or down > 1000:
        # Use polyphase resampling
        from scipy.signal import resample_poly
        resampled = resample_poly(data, up, down)
    else:
        from scipy.signal import resample_poly
        resampled = resample_poly(data, up, down)

    return resampled, target_rate


def _decimate(
    data: np.ndarray,
    sample_rate: float,
    factor: int,
) -> Tuple[np.ndarray, float]:
    """Decimate signal by integer factor."""
    if factor <= 1:
        return data, sample_rate

    # Use scipy decimate with zero-phase filtering
    I = signal.decimate(np.real(data), factor, zero_phase=True)
    Q = signal.decimate(np.imag(data), factor, zero_phase=True)

    new_rate = sample_rate / factor
    return I + 1j * Q, new_rate


def estimate_dc_offset(iq_data: np.ndarray) -> Tuple[float, float]:
    """Estimate DC offset of I and Q channels."""
    return float(np.mean(np.real(iq_data))), float(np.mean(np.imag(iq_data)))


def estimate_iq_imbalance(iq_data: np.ndarray) -> Tuple[float, float]:
    """
    Estimate I/Q amplitude and phase imbalance.

    Returns:
        amplitude_imbalance_db, phase_imbalance_deg
    """
    I = np.real(iq_data)
    Q = np.imag(iq_data)

    # Amplitude imbalance
    std_I = np.std(I)
    std_Q = np.std(Q)
    amp_imbalance = 20 * np.log10(std_I / std_Q) if std_Q > 0 else float("inf")

    # Phase imbalance (deviation from 90 degrees)
    # Using correlation method
    corr = np.corrcoef(I, Q)[0, 1]
    # For perfect quadrature, corr should be 0
    phase_imbalance = np.arcsin(corr) * 180 / np.pi if abs(corr) < 1 else 0

    return float(amp_imbalance), float(phase_imbalance)