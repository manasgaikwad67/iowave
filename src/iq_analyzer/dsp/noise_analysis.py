"""Noise floor estimation."""

import numpy as np
from scipy.signal import find_peaks
from typing import Optional, List, Tuple
from dataclasses import dataclass
from ..models import NoiseFloorResult
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class NoiseFloorConfig:
    """Configuration for noise floor estimation."""

    method: str = "percentile_excluding_peaks"  # percentile, median, percentile_excluding_peaks, iterative
    percentile: float = 10.0
    peak_prominence_db: float = 10.0
    peak_min_distance_hz: float = 10000
    exclusion_margin_hz: float = 5000
    max_iterations: int = 5


def estimate_noise_floor(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
    config: Optional[NoiseFloorConfig] = None,
) -> NoiseFloorResult:
    """
    Estimate noise floor from power spectrum.

    Args:
        frequencies: Frequency array
        power_spectrum: Power spectrum (linear scale)
        config: Noise floor estimation configuration

    Returns:
        NoiseFloorResult with noise floor estimate and metadata
    """
    if config is None:
        config = NoiseFloorConfig()

    power_db = 10 * np.log10(power_spectrum + 1e-20)
    warnings = []

    if config.method == "percentile":
        noise_floor = float(np.percentile(power_db, config.percentile))
        threshold = noise_floor
        method_desc = f"percentile_{config.percentile}"

    elif config.method == "median":
        noise_floor = float(np.median(power_db))
        threshold = noise_floor
        method_desc = "median"

    elif config.method == "percentile_excluding_peaks":
        # Detect and exclude peaks
        noise_floor, threshold = _estimate_excluding_peaks(
            frequencies, power_db, config
        )
        method_desc = "percentile_excluding_peaks"

    elif config.method == "iterative":
        noise_floor, threshold = _estimate_iterative(
            frequencies, power_db, config
        )
        method_desc = "iterative"

    else:
        raise ValueError(f"Unknown noise floor method: {config.method}")

    # Estimate uncertainty
    uncertainty = _estimate_uncertainty(power_db, noise_floor)

    return NoiseFloorResult(
        noise_floor_db=noise_floor,
        method=method_desc,
        threshold_db=threshold,
        uncertainty_db=uncertainty,
        warnings=warnings,
    )


def _estimate_excluding_peaks(
    frequencies: np.ndarray,
    power_db: np.ndarray,
    config: NoiseFloorConfig,
) -> Tuple[float, float]:
    """Estimate noise floor excluding detected peaks."""
    # Find peaks
    freq_res = frequencies[1] - frequencies[0] if len(frequencies) > 1 else 1.0
    min_dist = max(1, int(config.peak_min_distance_hz / freq_res))

    peaks, _ = find_peaks(
        10 ** (power_db / 10),  # Convert back to linear for find_peaks
        distance=min_dist,
        prominence=10 ** (config.peak_prominence_db / 10),
    )

    # Create mask excluding peaks and margins
    margin_bins = max(1, int(config.exclusion_margin_hz / freq_res))
    mask = np.ones_like(power_db, dtype=bool)

    for peak_idx in peaks:
        start = max(0, peak_idx - margin_bins)
        end = min(len(power_db), peak_idx + margin_bins + 1)
        mask[start:end] = False

    # Use percentile of non-peak regions
    noise_samples = power_db[mask]
    if len(noise_samples) == 0:
        # Fallback to overall percentile
        return float(np.percentile(power_db, config.percentile)), float(np.percentile(power_db, config.percentile))

    noise_floor = float(np.percentile(noise_samples, config.percentile))
    threshold = noise_floor

    return noise_floor, threshold


def _estimate_iterative(
    frequencies: np.ndarray,
    power_db: np.ndarray,
    config: NoiseFloorConfig,
) -> Tuple[float, float]:
    """Iteratively estimate noise floor by excluding outliers."""
    noise_samples = power_db.copy()

    for iteration in range(config.max_iterations):
        # Estimate current noise floor
        current_floor = np.percentile(noise_samples, config.percentile)

        # Exclude samples significantly above noise floor
        # Use 10 dB as outlier threshold
        threshold = current_floor + 10
        new_samples = noise_samples[noise_samples <= threshold]

        if len(new_samples) == len(noise_samples):
            # Converged
            break

        if len(new_samples) < 10:
            # Too few samples, stop
            break

        noise_samples = new_samples

    noise_floor = float(np.percentile(noise_samples, config.percentile))
    threshold = noise_floor + 10

    return noise_floor, threshold


def _estimate_uncertainty(power_db: np.ndarray, noise_floor_db: float) -> float:
    """Estimate uncertainty of noise floor estimate."""
    # Standard deviation of samples near noise floor
    near_floor = power_db[(power_db >= noise_floor_db - 3) & (power_db <= noise_floor_db + 3)]
    if len(near_floor) > 1:
        return float(np.std(near_floor))
    return 0.0


def estimate_noise_power(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
    noise_floor_db: float,
    signal_regions: List[Tuple[float, float]] = None,
) -> float:
    """
    Estimate total noise power by integrating noise floor.

    Args:
        frequencies: Frequency array
        power_spectrum: Power spectrum (linear)
        noise_floor_db: Noise floor in dB
        signal_regions: List of (low, high) frequency ranges to exclude

    Returns:
        Noise power in linear scale
    """
    if signal_regions is None:
        # Integrate entire spectrum assuming noise floor is constant
        noise_power_linear = 10 ** (noise_floor_db / 10)
        bw = frequencies[-1] - frequencies[0]
        return noise_power_linear * bw

    # Integrate only non-signal regions
    total_noise_power = 0.0
    freq_res = frequencies[1] - frequencies[0] if len(frequencies) > 1 else 1.0

    # Create mask for signal regions
    signal_mask = np.zeros_like(frequencies, dtype=bool)
    for low, high in signal_regions:
        signal_mask |= (frequencies >= low) & (frequencies <= high)

    # Noise regions
    noise_mask = ~signal_mask
    if np.any(noise_mask):
        noise_power = np.sum(power_spectrum[noise_mask]) * freq_res
        return float(noise_power)

    return 0.0