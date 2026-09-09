"""Unit conversion and formatting utilities."""

import numpy as np
from typing import Union, Tuple


def hz_to_khz(hz: float) -> float:
    """Convert Hz to kHz."""
    return hz / 1e3


def hz_to_mhz(hz: float) -> float:
    """Convert Hz to MHz."""
    return hz / 1e6


def hz_to_ghz(hz: float) -> float:
    """Convert Hz to GHz."""
    return hz / 1e9


def format_frequency(hz: float, precision: int = 3) -> str:
    """Format frequency with appropriate unit."""
    if hz >= 1e9:
        return f"{hz / 1e9:.{precision}f} GHz"
    elif hz >= 1e6:
        return f"{hz / 1e6:.{precision}f} MHz"
    elif hz >= 1e3:
        return f"{hz / 1e3:.{precision}f} kHz"
    else:
        return f"{hz:.{precision}f} Hz"


def format_sample_rate(sps: float) -> str:
    """Format sample rate with appropriate unit."""
    if sps >= 1e9:
        return f"{sps / 1e9:.3f} GS/s"
    elif sps >= 1e6:
        return f"{sps / 1e6:.3f} MS/s"
    elif sps >= 1e3:
        return f"{sps / 1e3:.3f} kS/s"
    else:
        return f"{sps:.3f} S/s"


def format_duration(seconds: float, precision: int = 3) -> str:
    """Format duration with appropriate unit."""
    if seconds >= 3600:
        return f"{seconds / 3600:.{precision}f} h"
    elif seconds >= 60:
        return f"{seconds / 60:.{precision}f} min"
    elif seconds >= 1:
        return f"{seconds:.{precision}f} s"
    elif seconds >= 1e-3:
        return f"{seconds * 1e3:.{precision}f} ms"
    elif seconds >= 1e-6:
        return f"{seconds * 1e6:.{precision}f} µs"
    else:
        return f"{seconds * 1e9:.{precision}f} ns"


def format_data_size(bytes_: int) -> str:
    """Format data size with appropriate unit."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_ < 1024:
            return f"{bytes_:.2f} {unit}"
        bytes_ /= 1024
    return f"{bytes_:.2f} PB"


def db_to_linear(db: float) -> float:
    """Convert dB to linear scale."""
    return 10 ** (db / 10)


def linear_to_db(linear: float) -> float:
    """Convert linear scale to dB."""
    if linear <= 0:
        return -np.inf
    return 10 * np.log10(linear)


def amplitude_to_db(amplitude: float) -> float:
    """Convert amplitude to dB (20*log10)."""
    if amplitude <= 0:
        return -np.inf
    return 20 * np.log10(amplitude)


def db_to_amplitude(db: float) -> float:
    """Convert dB to amplitude."""
    return 10 ** (db / 20)


def ppm_to_hz(ppm: float, center_freq_hz: float) -> float:
    """Convert ppm to Hz at a given center frequency."""
    return ppm * center_freq_hz / 1e6


def hz_to_ppm(hz: float, center_freq_hz: float) -> float:
    """Convert Hz to ppm at a given center frequency."""
    if center_freq_hz == 0:
        return float('inf')
    return hz * 1e6 / center_freq_hz


def format_db(value: float, precision: int = 1) -> str:
    """Format dB value."""
    if np.isinf(value) and value < 0:
        return "-∞ dB"
    return f"{value:.{precision}f} dB"


def format_percent(value: float, precision: int = 1) -> str:
    """Format percentage value."""
    return f"{value * 100:.{precision}f}%"


def get_frequency_axis(sample_rate: float, nfft: int, fftshift: bool = True) -> np.ndarray:
    """Generate frequency axis for FFT."""
    if fftshift:
        return np.fft.fftshift(np.fft.fftfreq(nfft, 1 / sample_rate))
    else:
        return np.fft.fftfreq(nfft, 1 / sample_rate)[: nfft // 2]


def get_positive_frequency_axis(sample_rate: float, nfft: int) -> np.ndarray:
    """Generate positive frequency axis for FFT."""
    return np.fft.fftfreq(nfft, 1 / sample_rate)[: nfft // 2]