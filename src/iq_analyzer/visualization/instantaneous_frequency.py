"""Phase and instantaneous frequency visualization."""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple
from ..utils import format_duration, format_sample_rate
from ..config import settings


def plot_instantaneous_frequency(
    inst_freq: np.ndarray,
    sample_rate: float,
    time_axis: Optional[np.ndarray] = None,
    title: str = "Instantaneous Frequency",
    figsize: Tuple[float, float] = (10, 4),
    center_freq: Optional[float] = None,
) -> plt.Figure:
    """
    Plot instantaneous frequency over time.

    Args:
        inst_freq: Instantaneous frequency array (Hz)
        sample_rate: Sample rate in Hz
        time_axis: Time axis array (optional)
        title: Plot title
        figsize: Figure size
        center_freq: Center frequency for relative display

    Returns:
        Matplotlib figure
    """
    if time_axis is None:
        time_axis = np.arange(len(inst_freq)) / sample_rate

    fig, ax = plt.subplots(figsize=figsize)

    # Mask NaN values
    valid = ~np.isnan(inst_freq)
    if not np.any(valid):
        ax.text(0.5, 0.5, 'No valid instantaneous frequency data', ha='center', va='center', transform=ax.transAxes)
        return fig

    if center_freq is not None:
        # Plot relative frequency
        freq_plot = (inst_freq[valid] - center_freq) / 1e3  # kHz offset
        ylabel = 'Frequency Offset (kHz)'
    else:
        freq_plot = inst_freq[valid] / 1e6  # MHz
        ylabel = 'Frequency (MHz)'

    time_valid = time_axis[valid]
    ax.plot(time_valid, freq_plot, 'b-', linewidth=0.5, alpha=0.7)

    ax.set_xlabel('Time (s)')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)

    # Add statistics text
    mean_freq = np.nanmean(inst_freq)
    std_freq = np.nanstd(inst_freq)
    if center_freq is not None:
        stats_text = f'Mean offset: {(mean_freq - center_freq)/1e3:.1f} kHz, Std: {std_freq/1e3:.1f} kHz'
    else:
        stats_text = f'Mean: {mean_freq/1e6:.3f} MHz, Std: {std_freq/1e6:.3f} MHz'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, va='top', fontsize=9,
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    fig.tight_layout()
    return fig


def plot_phase_analysis(
    iq_data: np.ndarray,
    sample_rate: float,
    max_points: int = 10000,
    title: str = "Phase Analysis",
    figsize: Tuple[float, float] = (12, 8),
) -> plt.Figure:
    """
    Comprehensive phase analysis plots.

    Args:
        iq_data: Complex IQ signal
        sample_rate: Sample rate in Hz
        max_points: Maximum points for time-domain plots
        title: Plot title
        figsize: Figure size

    Returns:
        Matplotlib figure
    """
    n_samples = len(iq_data)

    # Downsample
    if n_samples > max_points:
        step = n_samples // max_points
        indices = np.arange(0, n_samples, step)
        iq_plot = iq_data[indices]
        time_axis = indices / sample_rate
    else:
        iq_plot = iq_data
        time_axis = np.arange(n_samples) / sample_rate

    phase = np.angle(iq_plot)
    phase_unwrapped = np.unwrap(phase)

    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

    # Wrapped phase
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(time_axis, phase, 'b-', linewidth=0.3, alpha=0.7)
    ax1.set_ylabel('Phase (rad)')
    ax1.set_title('Wrapped Phase')
    ax1.set_ylim(-np.pi, np.pi)
    ax1.grid(True, alpha=0.3)

    # Unwrapped phase
    ax2 = fig.add_subplot(gs[0, 1], sharex=ax1)
    ax2.plot(time_axis, phase_unwrapped, 'r-', linewidth=0.3, alpha=0.7)
    ax2.set_ylabel('Phase (rad)')
    ax2.set_title('Unwrapped Phase')
    ax2.grid(True, alpha=0.3)

    # Phase difference (instantaneous frequency proxy)
    ax3 = fig.add_subplot(gs[1, 0], sharex=ax1)
    phase_diff = np.diff(phase_unwrapped)
    time_diff = time_axis[:-1]
    ax3.plot(time_diff, phase_diff, 'g-', linewidth=0.3, alpha=0.7)
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('ΔPhase (rad/sample)')
    ax3.set_title('Phase Difference')
    ax3.grid(True, alpha=0.3)

    # Phase histogram
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.hist(phase, bins=100, edgecolor='black', alpha=0.7, density=True)
    ax4.set_xlabel('Phase (rad)')
    ax4.set_ylabel('Density')
    ax4.set_title('Phase Distribution')
    ax4.grid(True, alpha=0.3)

    fig.suptitle(f'{title} ({format_duration(n_samples/sample_rate)}, {format_sample_rate(sample_rate)})')
    fig.tight_layout()
    return fig