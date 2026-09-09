"""Instantaneous frequency analysis."""

import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass
from ..models import InstantaneousParameters
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class InstantaneousFrequencyConfig:
    """Configuration for instantaneous frequency computation."""

    amplitude_threshold: float = 0.01  # Relative to max amplitude
    unwrap_phase: bool = True
    differentiation_method: str = "central"  # forward, central, backward
    smooth_window: int = 0  # Moving average window (0 = no smoothing)


def compute_instantaneous_frequency(
    iq_data: np.ndarray,
    sample_rate: float,
    config: Optional[InstantaneousFrequencyConfig] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute instantaneous frequency, amplitude, and phase from IQ signal.

    Uses: f[n] = fs/(2π) * d(φ[n])/dn where φ[n] = atan2(Q[n], I[n])

    Args:
        iq_data: Complex IQ signal
        sample_rate: Sample rate in Hz
        config: Configuration

    Returns:
        Tuple of (instantaneous_frequency, instantaneous_amplitude, unwrapped_phase)
    """
    if config is None:
        config = InstantaneousFrequencyConfig()

    # Compute amplitude and phase
    amplitude = np.abs(iq_data)
    phase = np.angle(iq_data)

    # Amplitude threshold mask
    max_amp = np.max(amplitude)
    threshold = config.amplitude_threshold * max_amp
    valid_mask = amplitude >= threshold

    if not np.any(valid_mask):
        logger.warning("No samples above amplitude threshold for instantaneous frequency")
        return np.array([]), np.array([]), np.array([])

    # Unwrap phase
    if config.unwrap_phase:
        phase = np.unwrap(phase)

    # Differentiate phase
    if config.differentiation_method == "forward":
        phase_diff = np.diff(phase, prepend=phase[0])
    elif config.differentiation_method == "central":
        phase_diff = np.gradient(phase)
    elif config.differentiation_method == "backward":
        phase_diff = np.diff(phase, append=phase[-1])
    else:
        raise ValueError(f"Unknown differentiation method: {config.differentiation_method}")

    # Instantaneous frequency: f = fs/(2π) * dφ/dn
    inst_freq = sample_rate / (2 * np.pi) * phase_diff

    # Apply amplitude mask - set invalid regions to NaN
    inst_freq_masked = inst_freq.copy()
    inst_freq_masked[~valid_mask] = np.nan

    # Optional smoothing
    if config.smooth_window > 1:
        from scipy.signal import savgol_filter
        try:
            inst_freq_masked = savgol_filter(
                inst_freq_masked, config.smooth_window, 2, mode="nearest"
            )
        except Exception:
            pass  # Smoothing failed, use unsmoothed

    return inst_freq_masked, amplitude, phase


def analyze_instantaneous_frequency(
    iq_data: np.ndarray,
    sample_rate: float,
    config: Optional[InstantaneousFrequencyConfig] = None,
) -> InstantaneousParameters:
    """
    Analyze instantaneous frequency statistics.

    Returns:
        InstantaneousParameters with statistics
    """
    inst_freq, inst_amp, phase = compute_instantaneous_frequency(
        iq_data, sample_rate, config
    )

    # Remove NaN for statistics
    valid_freq = inst_freq[~np.isnan(inst_freq)]
    valid_amp = inst_amp[~np.isnan(inst_amp)]

    if len(valid_freq) == 0:
        return InstantaneousParameters(
            instantaneous_frequency_mean=None,
            instantaneous_frequency_std=None,
            frequency_deviation=None,
            instantaneous_amplitude_mean=None,
            instantaneous_amplitude_std=None,
            phase_mean=None,
            phase_std=None,
            phase_min=None,
            phase_max=None,
        )

    # Frequency statistics
    freq_mean = float(np.mean(valid_freq))
    freq_std = float(np.std(valid_freq))
    freq_median = float(np.median(valid_freq))
    freq_min = float(np.min(valid_freq))
    freq_max = float(np.max(valid_freq))
    freq_deviation = float(freq_max - freq_min)  # Peak-to-peak deviation

    # Robust frequency deviation (excluding outliers)
    if len(valid_freq) > 10:
        q25, q75 = np.percentile(valid_freq, [25, 75])
        iqr = q75 - q25
        lower = q25 - 1.5 * iqr
        upper = q75 + 1.5 * iqr
        robust_freq = valid_freq[(valid_freq >= lower) & (valid_freq <= upper)]
        if len(robust_freq) > 0:
            freq_deviation = float(np.max(robust_freq) - np.min(robust_freq))

    # Amplitude statistics
    amp_mean = float(np.mean(valid_amp))
    amp_std = float(np.std(valid_amp))

    # Phase statistics
    phase_mean = float(np.mean(phase))
    phase_std = float(np.std(phase))
    phase_min = float(np.min(phase))
    phase_max = float(np.max(phase))

    return InstantaneousParameters(
        instantaneous_frequency_mean=freq_mean,
        instantaneous_frequency_std=freq_std,
        frequency_deviation=freq_deviation,
        instantaneous_amplitude_mean=amp_mean,
        instantaneous_amplitude_std=amp_std,
        phase_mean=phase_mean,
        phase_std=phase_std,
        phase_min=phase_min,
        phase_max=phase_max,
    )


def detect_frequency_drift(
    inst_freq: np.ndarray,
    sample_rate: float,
    window_size: int = 1000,
) -> dict:
    """
    Detect frequency drift over time.

    Args:
        inst_freq: Instantaneous frequency array
        sample_rate: Sample rate in Hz
        window_size: Window size for local statistics

    Returns:
        Dictionary with drift statistics
    """
    valid = inst_freq[~np.isnan(inst_freq)]
    if len(valid) < window_size:
        return {"drift_detected": False, "reason": "Insufficient data"}

    # Compute local mean frequency in windows
    n_windows = len(valid) // window_size
    local_means = []

    for i in range(n_windows):
        start = i * window_size
        end = start + window_size
        local_means.append(np.mean(valid[start:end]))

    local_means = np.array(local_means)

    # Linear fit to detect drift
    x = np.arange(len(local_means))
    coeffs = np.polyfit(x, local_means, 1)
    drift_rate = coeffs[0]  # Hz per window

    # Convert to Hz/s
    window_duration = window_size / sample_rate
    drift_hz_per_sec = drift_rate / window_duration

    return {
        "drift_detected": abs(drift_hz_per_sec) > 1.0,  # Threshold
        "drift_rate_hz_per_sec": float(drift_hz_per_sec),
        "local_means": local_means.tolist(),
        "window_duration_sec": window_duration,
    }