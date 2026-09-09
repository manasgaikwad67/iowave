"""Time-domain signal analysis."""

import numpy as np
from typing import Optional, Tuple
from ..models import TimeDomainParameters
from ..utils import get_logger

logger = get_logger(__name__)


def analyze_time_domain(iq_data: np.ndarray) -> TimeDomainParameters:
    """
    Compute time-domain parameters for complex IQ signal.

    Args:
        iq_data: Complex IQ signal (I + jQ)

    Returns:
        TimeDomainParameters with all computed metrics
    """
    I = np.real(iq_data)
    Q = np.imag(iq_data)

    # Basic statistics
    mean_I = float(np.mean(I))
    mean_Q = float(np.mean(Q))

    # RMS values
    rms_I = float(np.sqrt(np.mean(I**2)))
    rms_Q = float(np.sqrt(np.mean(Q**2)))

    # Magnitude
    magnitude = np.abs(iq_data)
    rms_magnitude = float(np.sqrt(np.mean(magnitude**2)))
    peak_magnitude = float(np.max(magnitude))
    peak_to_peak = float(np.max(magnitude) - np.min(magnitude))

    # Variance and standard deviation of magnitude
    variance = float(np.var(magnitude))
    standard_deviation = float(np.std(magnitude))

    # Crest factor = peak / RMS
    crest_factor = peak_magnitude / rms_magnitude if rms_magnitude > 0 else 0.0

    # PAPR (Peak-to-Average Power Ratio) in dB
    # PAPR = 10 * log10(peak_power / average_power)
    # peak_power = peak_magnitude^2
    # average_power = rms_magnitude^2
    if rms_magnitude > 0:
        papr_db = 10 * np.log10((peak_magnitude**2) / (rms_magnitude**2))
    else:
        papr_db = 0.0

    # Amplitude statistics
    amplitude_mean = float(np.mean(magnitude))
    amplitude_std = float(np.std(magnitude))

    # Phase statistics
    phase = np.angle(iq_data)
    phase_mean = float(np.mean(phase))
    phase_std = float(np.std(phase))

    return TimeDomainParameters(
        mean_I=mean_I,
        mean_Q=mean_Q,
        rms_I=rms_I,
        rms_Q=rms_Q,
        rms_magnitude=rms_magnitude,
        peak_magnitude=peak_magnitude,
        peak_to_peak=peak_to_peak,
        variance=variance,
        standard_deviation=standard_deviation,
        crest_factor=crest_factor,
        papr_db=float(papr_db),
        amplitude_mean=amplitude_mean,
        amplitude_std=amplitude_std,
        phase_mean=phase_mean,
        phase_std=phase_std,
    )


def compute_amplitude_phase(iq_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Compute amplitude and phase from IQ data."""
    amplitude = np.abs(iq_data)
    phase = np.angle(iq_data)
    return amplitude, phase


def compute_instantaneous_power(iq_data: np.ndarray) -> np.ndarray:
    """Compute instantaneous power (|x[n]|^2)."""
    return np.abs(iq_data) ** 2


def detect_clipping(iq_data: np.ndarray, threshold: float = 0.99) -> dict:
    """Detect signal clipping."""
    magnitude = np.abs(iq_data)
    max_mag = np.max(magnitude)

    if max_mag == 0:
        return {"clipped": False, "percentage": 0.0, "max_magnitude": 0.0}

    clipped_samples = np.sum(magnitude >= threshold * max_mag)
    percentage = 100 * clipped_samples / len(magnitude)

    return {
        "clipped": percentage > 0.1,  # More than 0.1% clipped
        "percentage": float(percentage),
        "max_magnitude": float(max_mag),
        "threshold": threshold,
    }


def compute_autocorrelation(iq_data: np.ndarray, max_lag: Optional[int] = None) -> np.ndarray:
    """Compute autocorrelation of complex signal."""
    if max_lag is None:
        max_lag = min(len(iq_data) // 4, 1000)

    # Use FFT-based autocorrelation for efficiency
    n = len(iq_data)
    nfft = 1
    while nfft < 2 * n:
        nfft <<= 1

    fft_data = np.fft.fft(iq_data, nfft)
    psd = np.abs(fft_data) ** 2
    autocorr = np.fft.ifft(psd).real[:max_lag] / n

    return autocorr