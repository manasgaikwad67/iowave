"""Spectrogram visualization."""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple
from ..models import SpectrogramResult
from ..config import settings
from ..utils import format_frequency, format_duration


def plot_spectrogram(
    spectrogram_result,
    title: str = "Spectrogram",
    figsize: Tuple[float, float] = (10, 6),
    max_freq_hz: Optional[float] = None,
    colormap: str = "viridis",
    dynamic_range_db: float = 60,
) -> plt.Figure:
    """
    Plot spectrogram.

    Args:
        spectrogram_result: SpectrogramResult object
        title: Plot title
        figsize: Figure size
        max_freq_hz: Maximum frequency to display
        colormap: Matplotlib colormap
        dynamic_range_db: Dynamic range in dB for color scaling

    Returns:
        Matplotlib figure
    """
    freq = spectrogram_result.frequencies
    times = spectrogram_result.times
    spec = spectrogram_result.spectrogram

    # Convert to dB
    spec_db = 10 * np.log10(spec + 1e-20)

    # Frequency limit
    if max_freq_hz is not None:
        freq_mask = freq <= max_freq_hz
        freq = freq[freq_mask]
        spec_db = spec_db[freq_mask, :]

    freq_mhz = freq / 1e6

    # Dynamic range clipping
    vmax = np.max(spec_db)
    vmin = vmax - dynamic_range_db

    fig, ax = plt.subplots(figsize=figsize)

    im = ax.pcolormesh(times, freq_mhz, spec_db, shading='gouraud', cmap=colormap, vmin=vmin, vmax=vmax)

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Frequency (MHz)')
    ax.set_title(f'{title} (NFFT={spectrogram_result.nperseg}, overlap={spectrogram_result.noverlap})')

    # Colorbar
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Power (dB)')

    fig.tight_layout()
    return fig


def plot_spectrogram_with_waveform(
    iq_data: np.ndarray,
    sample_rate: float,
    spectrogram_result,
    title: str = "Signal Analysis",
    figsize: Tuple[float, float] = (12, 8),
    max_points_waveform: int = 5000,
) -> plt.Figure:
    """
    Plot waveform and spectrogram together.

    Args:
        iq_data: Complex IQ signal
        sample_rate: Sample rate in Hz
        spectrogram_result: SpectrogramResult object
        title: Plot title
        figsize: Figure size
        max_points_waveform: Max points for waveform plot

    Returns:
        Matplotlib figure
    """
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 1, height_ratios=[1, 1, 2], hspace=0.3)

    # Waveform - magnitude
    n_samples = len(iq_data)
    if n_samples > max_points_waveform:
        step = n_samples // max_points_waveform
        indices = np.arange(0, n_samples, step)
        time_axis = indices / sample_rate
        mag = np.abs(iq_data[indices])
    else:
        time_axis = np.arange(n_samples) / sample_rate
        mag = np.abs(iq_data)

    ax1 = fig.add_subplot(gs[0])
    ax1.plot(time_axis, mag, 'b-', linewidth=0.3, alpha=0.7)
    ax1.set_ylabel('Magnitude')
    ax1.set_title('Signal Magnitude')
    ax1.grid(True, alpha=0.3)

    # Waveform - phase
    if n_samples > max_points_waveform:
        phase = np.angle(iq_data[indices])
    else:
        phase = np.angle(iq_data)

    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.plot(time_axis, phase, 'r-', linewidth=0.3, alpha=0.7)
    ax2.set_ylabel('Phase (rad)')
    ax2.set_title('Signal Phase')
    ax2.set_ylim(-np.pi, np.pi)
    ax2.grid(True, alpha=0.3)

    # Spectrogram
    freq = spectrogram_result.frequencies
    times = spectrogram_result.times
    spec = spectrogram_result.spectrogram
    spec_db = 10 * np.log10(spec + 1e-20)
    freq_mhz = freq / 1e6

    vmax = np.max(spec_db)
    vmin = vmax - 60

    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    im = ax3.pcolormesh(times, freq_mhz, spec_db, shading='gouraud', cmap='viridis', vmin=vmin, vmax=vmax)
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Frequency (MHz)')
    ax3.set_title('Spectrogram')

    fig.colorbar(im, ax=ax3, label='Power (dB)')
    fig.suptitle(f'{title} ({format_duration(n_samples/sample_rate)}, {sample_rate/1e6:.2f} MHz)')
    fig.tight_layout()

    return fig