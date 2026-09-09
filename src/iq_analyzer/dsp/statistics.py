"""Statistical signal analysis."""

import numpy as np
from scipy import stats
from typing import Optional, Tuple
from ..utils import get_logger

logger = get_logger(__name__)


def compute_spectral_moments(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
) -> dict:
    """
    Compute spectral moments (centroid, spread, skewness, kurtosis).

    Args:
        frequencies: Frequency array (positive frequencies only)
        power_spectrum: Power spectrum (linear scale)

    Returns:
        Dictionary with spectral moments
    """
    if len(frequencies) != len(power_spectrum):
        raise ValueError("Frequency and power arrays must have same length")

    # Normalize power spectrum to PDF
    total_power = np.sum(power_spectrum)
    if total_power == 0:
        return {
            "centroid": None,
            "spread": None,
            "skewness": None,
            "kurtosis": None,
        }

    pdf = power_spectrum / total_power

    # Spectral centroid (mean frequency)
    centroid = np.sum(frequencies * pdf)

    # Spectral spread (standard deviation)
    spread = np.sqrt(np.sum((frequencies - centroid) ** 2 * pdf))

    # Spectral skewness
    skewness = np.sum(((frequencies - centroid) / spread) ** 3 * pdf) if spread > 0 else 0

    # Spectral kurtosis
    kurtosis = np.sum(((frequencies - centroid) / spread) ** 4 * pdf) - 3 if spread > 0 else -3

    return {
        "centroid": float(centroid),
        "spread": float(spread),
        "skewness": float(skewness),
        "kurtosis": float(kurtosis),
    }


def compute_spectral_entropy(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
) -> float:
    """
    Compute spectral entropy (measure of spectral flatness/complexity).

    H = -sum(p * log2(p)) where p = normalized power spectrum
    Normalized to [0, 1] where 1 = white noise, 0 = pure tone
    """
    total_power = np.sum(power_spectrum)
    if total_power == 0:
        return 0.0

    pdf = power_spectrum / total_power
    # Avoid log(0)
    pdf = pdf[pdf > 0]

    entropy = -np.sum(pdf * np.log2(pdf))
    max_entropy = np.log2(len(pdf)) if len(pdf) > 0 else 1

    # Normalize to [0, 1]
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

    return float(np.clip(normalized_entropy, 0, 1))


def compute_spectral_flatness(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
) -> float:
    """
    Compute spectral flatness (Wiener entropy).

    Ratio of geometric mean to arithmetic mean of power spectrum.
    1 = flat (white noise), 0 = tonal.
    """
    # Avoid zeros
    ps = power_spectrum[power_spectrum > 0]
    if len(ps) == 0:
        return 0.0

    geo_mean = np.exp(np.mean(np.log(ps)))
    arith_mean = np.mean(ps)

    flatness = geo_mean / arith_mean if arith_mean > 0 else 0
    return float(np.clip(flatness, 0, 1))


def compute_spectral_rolloff(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
    percentile: float = 0.85,
) -> float:
    """
    Compute spectral rolloff frequency.

    Frequency below which the given percentile of total power is contained.
    """
    total_power = np.sum(power_spectrum)
    if total_power == 0:
        return 0.0

    cum_power = np.cumsum(power_spectrum)
    target = percentile * total_power

    idx = np.searchsorted(cum_power, target)
    if idx >= len(frequencies):
        return float(frequencies[-1])
    return float(frequencies[idx])


def compute_peak_to_noise_ratio(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
    peak_frequency: float,
    noise_floor_db: float,
) -> float:
    """
    Compute peak-to-noise ratio for a specific peak.

    Args:
        frequencies: Frequency array
        power_spectrum: Power spectrum (linear)
        peak_frequency: Frequency of the peak
        noise_floor_db: Noise floor in dB

    Returns:
        Peak-to-noise ratio in dB
    """
    peak_idx = np.argmin(np.abs(frequencies - peak_frequency))
    peak_power = power_spectrum[peak_idx]
    peak_power_db = 10 * np.log10(peak_power + 1e-20)

    pnr = peak_power_db - noise_floor_db
    return float(pnr)


def compute_crest_factor(iq_data: np.ndarray) -> float:
    """Compute crest factor (peak/RMS) of signal magnitude."""
    magnitude = np.abs(iq_data)
    rms = np.sqrt(np.mean(magnitude**2))
    peak = np.max(magnitude)
    return float(peak / rms) if rms > 0 else 0.0


def compute_papr(iq_data: np.ndarray) -> float:
    """Compute Peak-to-Average Power Ratio in dB."""
    magnitude = np.abs(iq_data)
    peak_power = np.max(magnitude**2)
    avg_power = np.mean(magnitude**2)
    if avg_power > 0:
        return float(10 * np.log10(peak_power / avg_power))
    return 0.0


def compute_iq_correlation(iq_data: np.ndarray) -> float:
    """Compute correlation between I and Q channels."""
    I = np.real(iq_data)
    Q = np.imag(iq_data)
    corr_matrix = np.corrcoef(I, Q)
    return float(corr_matrix[0, 1])


def estimate_modulation_bandwidth(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
) -> Tuple[float, float]:
    """
    Estimate modulation bandwidth using spectral moments.

    Returns:
        Tuple of (centroid, spread) where spread approximates bandwidth
    """
    moments = compute_spectral_moments(frequencies, power_spectrum)
    return moments["centroid"] or 0, moments["spread"] or 0