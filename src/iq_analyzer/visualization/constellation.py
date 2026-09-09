"""Constellation diagram visualization."""

import numpy as np
import matplotlib.pyplot as plt
from typing import Optional, Tuple
from ..models import ConstellationResult
from ..config import settings


def plot_constellation(
    iq_data: np.ndarray,
    max_points: int = 50000,
    title: str = "I/Q Constellation",
    figsize: Tuple[float, float] = (6, 6),
    normalize: bool = True,
    show_density: bool = False,
    alpha: float = 0.5,
) -> plt.Figure:
    """
    Plot I/Q constellation diagram.

    Args:
        iq_data: Complex IQ signal
        max_points: Maximum points to plot
        title: Plot title
        figsize: Figure size
        normalize: Whether to normalize constellation to unit circle
        show_density: Whether to use density-based coloring
        alpha: Point transparency

    Returns:
        Matplotlib figure
    """
    n_samples = len(iq_data)

    # Subsample for visualization
    if n_samples > max_points:
        indices = np.random.choice(n_samples, max_points, replace=False)
        iq_plot = iq_data[indices]
    else:
        iq_plot = iq_data

    I = np.real(iq_plot)
    Q = np.imag(iq_plot)

    if normalize:
        # Normalize to unit power
        rms = np.sqrt(np.mean(I**2 + Q**2))
        if rms > 0:
            I = I / rms
            Q = Q / rms

    fig, ax = plt.subplots(figsize=figsize)

    if show_density:
        # Use 2D histogram for density
        h = ax.hist2d(I, Q, bins=100, cmap='viridis', cmin=1)
        fig.colorbar(h[3], ax=ax, label='Count')
    else:
        ax.scatter(I, Q, s=1, alpha=alpha, c='blue', edgecolors='none')

    ax.set_xlabel('In-Phase (I)')
    ax.set_ylabel('Quadrature (Q)')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.axvline(x=0, color='k', linewidth=0.5)
    ax.set_aspect('equal', adjustable='box')

    # Add unit circle for reference if normalized
    if normalize:
        circle = plt.Circle((0, 0), 1, fill=False, color='red', linestyle='--', alpha=0.5)
        ax.add_patch(circle)

    fig.tight_layout()
    return fig


def plot_constellation_with_stats(
    constellation_result: ConstellationResult,
    title: str = "Constellation Analysis",
    figsize: Tuple[float, float] = (10, 5),
) -> plt.Figure:
    """
    Plot constellation with statistics.

    Args:
        constellation_result: ConstellationResult object
        title: Plot title
        figsize: Figure size

    Returns:
        Matplotlib figure
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # Constellation
    I = constellation_result.I
    Q = constellation_result.Q

    axes[0].scatter(I, Q, s=1, alpha=0.5, c='blue', edgecolors='none')
    axes[0].set_xlabel('I')
    axes[0].set_ylabel('Q')
    axes[0].set_title('Constellation Diagram')
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=0, color='k', linewidth=0.5)
    axes[0].axvline(x=0, color='k', linewidth=0.5)
    axes[0].set_aspect('equal', adjustable='box')

    # Mark centroid
    axes[0].plot(constellation_result.centroid_I, constellation_result.centroid_Q,
                'rx', markersize=10, markeredgewidth=2, label='Centroid')
    axes[0].legend()

    # Radius histogram
    radius = np.sqrt((I - constellation_result.centroid_I)**2 + (Q - constellation_result.centroid_Q)**2)
    axes[1].hist(radius, bins=50, edgecolor='black', alpha=0.7)
    axes[1].axvline(constellation_result.radius_mean, color='r', linestyle='--', label=f'Mean: {constellation_result.radius_mean:.3f}')
    axes[1].axvline(constellation_result.radius_mean + constellation_result.radius_std, color='g', linestyle=':', label=f'+1σ')
    axes[1].axvline(constellation_result.radius_mean - constellation_result.radius_std, color='g', linestyle=':', label=f'-1σ')
    axes[1].set_xlabel('Radius')
    axes[1].set_ylabel('Count')
    axes[1].set_title('Radius Distribution')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    fig.suptitle(title)
    fig.tight_layout()
    return fig