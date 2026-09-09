"""Waveform visualization."""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple
from ..utils import format_duration, format_sample_rate
from ..config import settings


def plot_waveform(
    iq_data: np.ndarray,
    sample_rate: float,
    max_points: int = 10000,
    title: str = "I/Q Waveform",
    figsize: Tuple[float, float] = (10, 6),
) -> plt.Figure:
    """
    Plot I and Q waveforms.

    Args:
        iq_data: Complex IQ signal
        sample_rate: Sample rate in Hz
        max_points: Maximum points to plot (for performance)
        title: Plot title
        figsize: Figure size

    Returns:
        Matplotlib figure
    """
    n_samples = len(iq_data)

    # Downsample for visualization if needed
    if n_samples > max_points:
        step = n_samples // max_points
        indices = np.arange(0, n_samples, step)
        iq_plot = iq_data[indices]
        time_axis = indices / sample_rate
    else:
        iq_plot = iq_data
        time_axis = np.arange(n_samples) / sample_rate

    I = np.real(iq_plot)
    Q = np.imag(iq_plot)

    fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=True)

    # I channel
    axes[0].plot(time_axis, I, 'b-', linewidth=0.5, alpha=0.8)
    axes[0].set_ylabel('Amplitude (I)')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_title(f'{title} - In-Phase')

    # Q channel
    axes[1].plot(time_axis, Q, 'r-', linewidth=0.5, alpha=0.8)
    axes[1].set_ylabel('Amplitude (Q)')
    axes[1].set_xlabel('Time (s)')
    axes[1].grid(True, alpha=0.3)
    axes[1].set_title(f'{title} - Quadrature')

    fig.suptitle(f'{title} ({format_duration(n_samples/sample_rate)}, {format_sample_rate(sample_rate)})')
    fig.tight_layout()

    return fig


def plot_magnitude_phase(
    iq_data: np.ndarray,
    sample_rate: float,
    max_points: int = 10000,
    title: str = "Magnitude and Phase",
    figsize: Tuple[float, float] = (10, 6),
) -> plt.Figure:
    """
    Plot magnitude and phase waveforms.

    Args:
        iq_data: Complex IQ signal
        sample_rate: Sample rate in Hz
        max_points: Maximum points to plot
        title: Plot title
        figsize: Figure size

    Returns:
        Matplotlib figure
    """
    n_samples = len(iq_data)

    if n_samples > max_points:
        step = n_samples // max_points
        indices = np.arange(0, n_samples, step)
        iq_plot = iq_data[indices]
        time_axis = indices / sample_rate
    else:
        iq_plot = iq_data
        time_axis = np.arange(n_samples) / sample_rate

    magnitude = np.abs(iq_plot)
    phase = np.angle(iq_plot)

    fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=True)

    # Magnitude
    axes[0].plot(time_axis, magnitude, 'g-', linewidth=0.5, alpha=0.8)
    axes[0].set_ylabel('Magnitude')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_title(f'{title} - Magnitude')

    # Phase
    axes[1].plot(time_axis, phase, 'm-', linewidth=0.5, alpha=0.8)
    axes[1].set_ylabel('Phase (rad)')
    axes[1].set_xlabel('Time (s)')
    axes[1].grid(True, alpha=0.3)
    axes[1].set_title(f'{title} - Phase')
    axes[1].set_ylim(-np.pi, np.pi)

    fig.suptitle(f'{title} ({format_duration(n_samples/sample_rate)}, {format_sample_rate(sample_rate)})')
    fig.tight_layout()

    return fig