"""Spectrum visualization."""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple
from ..models import FFTResult, PSDResult, PeakInfo
from ..utils import format_frequency
from ..config import settings


def plot_fft(
    fft_result,
    title: str = "FFT Spectrum",
    figsize: Tuple[float, float] = (10, 6),
    show_peaks: bool = True,
    peaks: Optional[list] = None,
) -> plt.Figure:
    """
    Plot FFT magnitude spectrum.

    Args:
        fft_result: FFTResult object
        title: Plot title
        figsize: Figure size
        show_peaks: Whether to mark detected peaks
        peaks: List of PeakInfo objects

    Returns:
        Matplotlib figure
    """
    freq = fft_result.frequencies
    mag = fft_result.magnitude_spectrum

    # Convert to MHz for display
    freq_mhz = freq / 1e6

    fig, ax = plt.subplots(figsize=figsize)

    # Plot magnitude in dB
    mag_db = 20 * np.log10(mag + 1e-20)
    ax.plot(freq_mhz, mag_db, 'b-', linewidth=0.5, alpha=0.8)

    # Mark peaks
    if show_peaks and peaks:
        for peak in peaks:
            peak_freq_mhz = peak.frequency / 1e6
            peak_mag_db = 20 * np.log10(peak.power + 1e-20) / 2  # power is linear, convert
            ax.plot(peak_freq_mhz, peak_mag_db, 'ro', markersize=6)
            ax.annotate(f'{peak_freq_mhz:.3f} MHz',
                       xy=(peak_freq_mhz, peak_mag_db),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, color='red')

    ax.set_xlabel('Frequency (MHz)')
    ax.set_ylabel('Magnitude (dB)')
    ax.set_title(f'{title} (NFFT={fft_result.fft_size}, window={fft_result.window_used})')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    return fig


def plot_psd(
    psd_result,
    title: str = "Power Spectral Density",
    figsize: Tuple[float, float] = (10, 6),
    show_noise_floor: bool = True,
    noise_floor_db: Optional[float] = None,
) -> plt.Figure:
    """
    Plot PSD.

    Args:
        psd_result: PSDResult object
        title: Plot title
        figsize: Figure size
        show_noise_floor: Whether to show noise floor line
        noise_floor_db: Noise floor in dB

    Returns:
        Matplotlib figure
    """
    freq = psd_result.frequencies
    psd_db = psd_result.psd_db

    freq_mhz = freq / 1e6

    fig, ax = plt.subplots(figsize=figsize)

    ax.plot(freq_mhz, psd_db, 'b-', linewidth=0.5, alpha=0.8)

    # Noise floor line
    if show_noise_floor and noise_floor_db is not None:
        ax.axhline(y=noise_floor_db, color='r', linestyle='--', linewidth=1, alpha=0.7, label=f'Noise Floor: {noise_floor_db:.1f} dB')
        ax.legend()

    ax.set_xlabel('Frequency (MHz)')
    ax.set_ylabel('PSD (dB/Hz)')
    ax.set_title(f'{title} (method={psd_result.method}, nperseg={psd_result.nperseg})')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    return fig


def plot_spectrum_combined(
    fft_result,
    psd_result,
    peaks: Optional[list] = None,
    noise_floor_db: Optional[float] = None,
    title: str = "Frequency Domain Analysis",
    figsize: Tuple[float, float] = (12, 8),
) -> plt.Figure:
    """
    Plot combined FFT and PSD.

    Returns:
        Matplotlib figure with subplots
    """
    fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=True)

    # FFT
    freq_mhz = fft_result.frequencies / 1e6
    mag_db = 20 * np.log10(fft_result.magnitude_spectrum + 1e-20)
    axes[0].plot(freq_mhz, mag_db, 'b-', linewidth=0.5, alpha=0.8)

    if peaks:
        for peak in peaks:
            pf_mhz = peak.frequency / 1e6
            pm_db = 20 * np.log10(peak.power + 1e-20) / 2
            axes[0].plot(pf_mhz, pm_db, 'ro', markersize=5)

    axes[0].set_ylabel('Magnitude (dB)')
    axes[0].set_title('FFT Spectrum')
    axes[0].grid(True, alpha=0.3)

    # PSD
    psd_freq_mhz = psd_result.frequencies / 1e6
    axes[1].plot(psd_freq_mhz, psd_result.psd_db, 'g-', linewidth=0.5, alpha=0.8)

    if noise_floor_db is not None:
        axes[1].axhline(y=noise_floor_db, color='r', linestyle='--', linewidth=1, alpha=0.7, label=f'Noise Floor: {noise_floor_db:.1f} dB')
        axes[1].legend()

    axes[1].set_xlabel('Frequency (MHz)')
    axes[1].set_ylabel('PSD (dB/Hz)')
    axes[1].set_title('Power Spectral Density (Welch)')
    axes[1].grid(True, alpha=0.3)

    fig.suptitle(title)
    fig.tight_layout()

    return fig