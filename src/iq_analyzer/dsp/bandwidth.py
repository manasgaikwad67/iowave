"""Bandwidth estimation."""

import numpy as np
from typing import Optional, List, Tuple
from dataclasses import dataclass
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class BandwidthConfig:
    """Configuration for bandwidth estimation."""

    method: str = "occupied"  # occupied, minus_3db
    percentages: List[float] = None  # e.g., [90, 95, 99]
    interpolation: bool = True

    def __post_init__(self):
        if self.percentages is None:
            self.percentages = [90.0, 95.0, 99.0]


def estimate_occupied_bandwidth(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
    percentages: List[float] = None,
) -> dict:
    """
    Estimate occupied bandwidth containing given percentage of total power.

    Args:
        frequencies: Frequency array (must be monotonically increasing)
        power_spectrum: Power spectrum (linear scale)
        percentages: List of percentages (e.g., [90, 95, 99])

    Returns:
        Dictionary with bandwidths for each percentage
    """
    if percentages is None:
        percentages = [90.0, 95.0, 99.0]

    if len(frequencies) != len(power_spectrum):
        raise ValueError("Frequency and power arrays must have same length")

    # Total power
    total_power = np.sum(power_spectrum)
    if total_power == 0:
        return {f"bw_{p}": None for p in percentages}

    # Cumulative power
    cum_power = np.cumsum(power_spectrum)
    cum_percent = 100 * cum_power / total_power

    results = {}
    freq_res = frequencies[1] - frequencies[0] if len(frequencies) > 1 else 1.0

    for p in percentages:
        # Find first index where cumulative power exceeds p%
        target = p / 100.0 * total_power
        idx_upper = np.searchsorted(cum_power, target, side="left")
        idx_lower = np.searchsorted(cum_power, total_power - target, side="right") - 1

        if idx_upper < len(frequencies) and idx_lower >= 0:
            bw = frequencies[idx_upper] - frequencies[idx_lower]
            results[f"bw_{int(p)}"] = float(bw)
        else:
            results[f"bw_{int(p)}"] = None

    return results


def estimate_minus_3db_bandwidth(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
    peak_frequency: Optional[float] = None,
) -> Optional[float]:
    """
    Estimate -3 dB bandwidth around the peak.

    Args:
        frequencies: Frequency array
        power_spectrum: Power spectrum (linear)
        peak_frequency: Known peak frequency (optional)

    Returns:
        -3 dB bandwidth in Hz, or None if not found
    """
    if len(frequencies) != len(power_spectrum):
        raise ValueError("Frequency and power arrays must have same length")

    # Find peak if not provided
    if peak_frequency is None:
        peak_idx = np.argmax(power_spectrum)
        peak_frequency = frequencies[peak_idx]
        peak_power = power_spectrum[peak_idx]
    else:
        peak_idx = np.argmin(np.abs(frequencies - peak_frequency))
        peak_power = power_spectrum[peak_idx]

    # -3 dB threshold
    threshold = peak_power / 2  # -3 dB = half power

    # Find lower crossing
    lower_idx = peak_idx
    while lower_idx > 0 and power_spectrum[lower_idx] > threshold:
        lower_idx -= 1

    # Find upper crossing
    upper_idx = peak_idx
    while upper_idx < len(power_spectrum) - 1 and power_spectrum[upper_idx] > threshold:
        upper_idx += 1

    if lower_idx == peak_idx and upper_idx == peak_idx:
        # Peak is below threshold (shouldn't happen)
        return None

    # Linear interpolation for better accuracy
    if lower_idx < peak_idx and power_spectrum[lower_idx] < threshold < power_spectrum[lower_idx + 1]:
        # Interpolate
        t = (threshold - power_spectrum[lower_idx]) / (power_spectrum[lower_idx + 1] - power_spectrum[lower_idx])
        lower_freq = frequencies[lower_idx] + t * (frequencies[lower_idx + 1] - frequencies[lower_idx])
    else:
        lower_freq = frequencies[lower_idx]

    if upper_idx > peak_idx and power_spectrum[upper_idx] < threshold < power_spectrum[upper_idx - 1]:
        t = (threshold - power_spectrum[upper_idx]) / (power_spectrum[upper_idx - 1] - power_spectrum[upper_idx])
        upper_freq = frequencies[upper_idx] + t * (frequencies[upper_idx - 1] - frequencies[upper_idx])
    else:
        upper_freq = frequencies[upper_idx]

    bandwidth = upper_freq - lower_freq
    return float(max(0, bandwidth))


def estimate_bandwidth(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
    config: Optional[BandwidthConfig] = None,
) -> dict:
    """
    Estimate bandwidth using configured method.

    Returns:
        Dictionary with all bandwidth estimates
    """
    if config is None:
        config = BandwidthConfig()

    results = {}

    if config.method == "occupied" or config.method == "both":
        occupied = estimate_occupied_bandwidth(frequencies, power_spectrum, config.percentages)
        results.update(occupied)

    if config.method == "minus_3db" or config.method == "both":
        minus_3db = estimate_minus_3db_bandwidth(frequencies, power_spectrum)
        results["minus_3db_bandwidth"] = minus_3db

    return results


def find_signal_edges(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
    noise_floor_db: float,
    margin_db: float = 3.0,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Find lower and upper edges of signal region above noise floor.

    Args:
        frequencies: Frequency array
        power_spectrum: Power spectrum (linear)
        noise_floor_db: Noise floor in dB
        margin_db: Margin above noise floor in dB

    Returns:
        Tuple of (lower_frequency, upper_frequency) or (None, None)
    """
    power_db = 10 * np.log10(power_spectrum + 1e-20)
    threshold = noise_floor_db + margin_db

    # Find regions above threshold
    above = power_db > threshold

    if not np.any(above):
        return None, None

    # Find contiguous regions
    indices = np.where(above)[0]
    if len(indices) == 0:
        return None, None

    lower_freq = float(frequencies[indices[0]])
    upper_freq = float(frequencies[indices[-1]])

    return lower_freq, upper_freq