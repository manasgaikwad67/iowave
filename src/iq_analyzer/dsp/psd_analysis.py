"""PSD analysis using Welch's method."""

import numpy as np
from scipy.signal import welch, get_window
from typing import Optional, Tuple
from dataclasses import dataclass
from ..models import PSDResult
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class PSDConfig:
    """Configuration for PSD analysis."""

    method: str = "welch"  # welch, periodogram
    nperseg: int = 2048
    noverlap: int = 1024
    nfft: int = 8192
    window: str = "hann"
    scaling: str = "density"  # density, spectrum
    detrend: str = "constant"


def compute_psd(
    iq_data: np.ndarray,
    sample_rate: float,
    config: Optional[PSDConfig] = None,
) -> PSDResult:
    """
    Compute Power Spectral Density using Welch's method.

    For complex IQ signals, this computes the two-sided PSD
    by averaging I and Q channel PSDs.
    """
    if config is None:
        config = PSDConfig()

    # Compute two-sided PSD for complex signal
    freqs, psd = compute_complex_psd(iq_data, sample_rate, config)

    # Convert to dB
    psd_db = 10 * np.log10(psd + 1e-20)

    return PSDResult(
        frequencies=freqs,
        psd=psd,
        psd_db=psd_db,
        sample_rate=sample_rate,
        nperseg=config.nperseg,
        noverlap=config.noverlap,
        window_used=config.window,
        method=config.method,
    )


def compute_complex_psd(
    iq_data: np.ndarray,
    sample_rate: float,
    config: Optional[PSDConfig] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute PSD preserving positive/negative frequency information.

    For complex signals, this returns two-sided PSD.
    """
    if config is None:
        config = PSDConfig()

    # Compute PSD on I and Q separately and combine
    # This preserves the complex nature
    freqs_I, psd_I = welch(
        np.real(iq_data),
        fs=sample_rate,
        window=config.window,
        nperseg=min(config.nperseg, len(iq_data)),
        noverlap=config.noverlap,
        nfft=config.nfft,
        scaling=config.scaling,
        detrend=config.detrend,
        return_onesided=False,
    )

    freqs_Q, psd_Q = welch(
        np.imag(iq_data),
        fs=sample_rate,
        window=config.window,
        nperseg=min(config.nperseg, len(iq_data)),
        noverlap=config.noverlap,
        nfft=config.nfft,
        scaling=config.scaling,
        detrend=config.detrend,
        return_onesided=False,
    )

    # Average I and Q PSD
    psd_combined = (psd_I + psd_Q) / 2

    return freqs_I, psd_combined


def compute_cross_psd(
    iq_data1: np.ndarray,
    iq_data2: np.ndarray,
    sample_rate: float,
    config: Optional[PSDConfig] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute cross-PSD between two signals.

    Useful for coherence analysis.
    """
    from scipy.signal import csd

    if config is None:
        config = PSDConfig()

    freqs, cpsd = csd(
        iq_data1,
        iq_data2,
        fs=sample_rate,
        window=config.window,
        nperseg=min(config.nperseg, len(iq_data1)),
        noverlap=config.noverlap,
        nfft=config.nfft,
        scaling=config.scaling,
        detrend=config.detrend,
    )

    return freqs, cpsd