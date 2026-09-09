"""FFT analysis module."""

import numpy as np
from scipy.signal import get_window
from typing import Optional, Tuple
from dataclasses import dataclass
from ..models import FFTResult
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class FFTConfig:
    """Configuration for FFT analysis."""

    size: int = 8192
    zero_padding: bool = True
    window: str = "hann"  # hann, hamming, blackman, bartlett, flattop
    fftshift: bool = True


def compute_fft(
    iq_data: np.ndarray,
    sample_rate: float,
    config: Optional[FFTConfig] = None,
) -> FFTResult:
    """
    Compute FFT of complex IQ signal.

    Args:
        iq_data: Complex IQ signal
        sample_rate: Sample rate in Hz
        config: FFT configuration

    Returns:
        FFTResult with frequencies and spectra
    """
    if config is None:
        config = FFTConfig()

    n_samples = len(iq_data)
    nfft = config.size

    # Apply window
    if n_samples <= nfft:
        window = get_window(config.window, n_samples)
        windowed = iq_data * window
        if config.zero_padding and n_samples < nfft:
            # Zero pad
            padded = np.zeros(nfft, dtype=np.complex128)
            padded[:n_samples] = windowed
            windowed = padded
    else:
        # Truncate or use multiple segments
        window = get_window(config.window, nfft)
        windowed = iq_data[:nfft] * window

    # Compute FFT
    fft_result = np.fft.fft(windowed)

    if config.fftshift:
        fft_result = np.fft.fftshift(fft_result)
        frequencies = np.fft.fftshift(np.fft.fftfreq(nfft, 1 / sample_rate))
    else:
        frequencies = np.fft.fftfreq(nfft, 1 / sample_rate)

    # Compute spectra
    magnitude_spectrum = np.abs(fft_result)
    power_spectrum = magnitude_spectrum**2
    phase_spectrum = np.angle(fft_result)

    return FFTResult(
        frequencies=frequencies,
        magnitude_spectrum=magnitude_spectrum,
        power_spectrum=power_spectrum,
        phase_spectrum=phase_spectrum,
        fft_size=nfft,
        sample_rate=sample_rate,
        window_used=config.window,
    )


def compute_fft_positive_only(
    iq_data: np.ndarray,
    sample_rate: float,
    config: Optional[FFTConfig] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute FFT and return only positive frequencies.

    Returns:
        Tuple of (frequencies, magnitude, power, phase) for positive frequencies only
    """
    result = compute_fft(iq_data, sample_rate, config)

    # Get positive frequencies only
    nfft = config.size if config else 8192
    pos_mask = result.frequencies >= 0

    return (
        result.frequencies[pos_mask],
        result.magnitude_spectrum[pos_mask],
        result.power_spectrum[pos_mask],
        result.phase_spectrum[pos_mask],
    )


def find_fft_peaks(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
    prominence_db: float = 10.0,
    min_distance_hz: float = 10000,
    min_height_db: float = -60.0,
) -> list:
    """
    Find peaks in FFT power spectrum.

    Args:
        frequencies: Frequency array
        power_spectrum: Power spectrum (linear scale)
        prominence_db: Minimum prominence in dB
        min_distance_hz: Minimum distance between peaks in Hz
        min_height_db: Minimum peak height in dB

    Returns:
        List of peak dictionaries
    """
    from scipy.signal import find_peaks

    # Convert to dB
    power_db = 10 * np.log10(power_spectrum + 1e-20)

    # Find peaks
    min_height_linear = 10 ** (min_height_db / 10)
    min_distance_bins = int(min_distance_hz / (frequencies[1] - frequencies[0])) if len(frequencies) > 1 else 1

    peaks, properties = find_peaks(
        power_spectrum,
        height=min_height_linear,
        distance=min_distance_bins,
        prominence=10 ** (prominence_db / 10),
    )

    peak_list = []
    for i, peak_idx in enumerate(peaks):
        peak_list.append({
            "frequency": float(frequencies[peak_idx]),
            "power_db": float(power_db[peak_idx]),
            "power_linear": float(power_spectrum[peak_idx]),
            "prominence_db": float(10 * np.log10(properties["prominences"][i] + 1e-20)),
            "width_hz": float(properties.get("widths", [0])[i] * (frequencies[1] - frequencies[0])) if "widths" in properties else None,
        })

    # Sort by power descending
    peak_list.sort(key=lambda x: x["power_db"], reverse=True)

    return peak_list


def estimate_noise_floor_from_fft(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
    method: str = "percentile",
    percentile: float = 10.0,
) -> float:
    """
    Estimate noise floor from FFT power spectrum.

    Args:
        frequencies: Frequency array
        power_spectrum: Power spectrum (linear)
        method: Estimation method ('percentile', 'median', 'minimum')
        percentile: Percentile for percentile method

    Returns:
        Noise floor in dB
    """
    power_db = 10 * np.log10(power_spectrum + 1e-20)

    if method == "percentile":
        noise_floor = np.percentile(power_db, percentile)
    elif method == "median":
        noise_floor = np.median(power_db)
    elif method == "minimum":
        noise_floor = np.min(power_db)
    else:
        raise ValueError(f"Unknown method: {method}")

    return float(noise_floor)