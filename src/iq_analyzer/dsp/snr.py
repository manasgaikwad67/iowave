"""SNR estimation."""

import numpy as np
from typing import Optional, List, Tuple
from dataclasses import dataclass
from ..models import SNRResult, SignalRegion
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class SNRConfig:
    """Configuration for SNR estimation."""

    method: str = "spectral"  # spectral, time_domain
    signal_region_margin_hz: float = 5000
    noise_region_selection: str = "automatic"  # automatic, manual
    min_noise_bins: int = 100


def estimate_snr_spectral(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
    signal_regions: List[SignalRegion],
    noise_floor_db: float,
    config: Optional[SNRConfig] = None,
) -> SNRResult:
    """
    Estimate SNR from spectral domain.

    Args:
        frequencies: Frequency array
        power_spectrum: Power spectrum (linear)
        signal_regions: Detected signal regions
        noise_floor_db: Noise floor in dB
        config: SNR configuration

    Returns:
        SNRResult with SNR estimate
    """
    if config is None:
        config = SNRConfig()

    warnings = []
    assumptions = [
        "Signal and noise are additive",
        "Noise is stationary and white within signal band",
        "Signal regions are correctly identified",
    ]

    if not signal_regions:
        warnings.append("No signal regions detected, cannot estimate SNR")
        return SNRResult(
            snr_db=None,
            signal_power_db=None,
            noise_power_db=None,
            method="spectral",
            assumptions=assumptions,
            warnings=warnings,
        )

    # Use the strongest signal region
    main_region = max(signal_regions, key=lambda r: r.peak_power)

    # Signal power: integrate PSD over signal region
    freq_res = frequencies[1] - frequencies[0] if len(frequencies) > 1 else 1.0
    signal_mask = (frequencies >= main_region.lower_frequency) & (
        frequencies <= main_region.upper_frequency
    )

    if not np.any(signal_mask):
        warnings.append("Signal region has no frequency bins")
        return SNRResult(
            snr_db=None,
            signal_power_db=None,
            noise_power_db=None,
            method="spectral",
            assumptions=assumptions,
            warnings=warnings,
        )

    signal_power = np.sum(power_spectrum[signal_mask]) * freq_res
    signal_power_db = 10 * np.log10(signal_power + 1e-20)

    # Noise power: use noise floor density * signal bandwidth
    noise_power_density = 10 ** (noise_floor_db / 10)
    signal_bw = main_region.upper_frequency - main_region.lower_frequency
    noise_power = noise_power_density * signal_bw
    noise_power_db = 10 * np.log10(noise_power + 1e-20)

    # SNR
    snr_db = signal_power_db - noise_power_db

    # Also compute per-region SNR if multiple regions
    region_snrs = []
    for region in signal_regions:
        region_mask = (frequencies >= region.lower_frequency) & (
            frequencies <= region.upper_frequency
        )
        if np.any(region_mask):
            region_signal = np.sum(power_spectrum[region_mask]) * freq_res
            region_signal_db = 10 * np.log10(region_signal + 1e-20)
            region_noise = noise_power_density * (region.upper_frequency - region.lower_frequency)
            region_noise_db = 10 * np.log10(region_noise + 1e-20)
            region_snrs.append(region_signal_db - region_noise_db)

    assumptions.append(f"Used {len(signal_regions)} signal region(s) for estimation")

    return SNRResult(
        snr_db=float(snr_db),
        signal_power_db=float(signal_power_db),
        noise_power_db=float(noise_power_db),
        method="spectral",
        assumptions=assumptions,
        warnings=warnings,
    )


def estimate_snr_time_domain(
    iq_data: np.ndarray,
    signal_region: Optional[Tuple[int, int]] = None,
) -> SNRResult:
    """
    Estimate SNR from time domain (requires known signal+noise and noise-only segments).

    This is a placeholder - in practice requires a known noise reference.
    """
    warnings = ["Time-domain SNR estimation requires noise reference segment"]
    assumptions = [
        "Noise is stationary",
        "Signal and noise are uncorrelated",
        "Noise reference segment is available",
    ]

    return SNRResult(
        snr_db=None,
        signal_power_db=None,
        noise_power_db=None,
        method="time_domain",
        assumptions=assumptions,
        warnings=warnings,
    )


def estimate_snr(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
    signal_regions: List[SignalRegion],
    noise_floor_db: float,
    config: Optional[SNRConfig] = None,
) -> SNRResult:
    """
    Main SNR estimation function.

    Args:
        frequencies: Frequency array
        power_spectrum: Power spectrum (linear)
        signal_regions: Detected signal regions
        noise_floor_db: Noise floor in dB
        config: SNR configuration

    Returns:
        SNRResult
    """
    if config is None:
        config = SNRConfig()

    if config.method == "spectral":
        return estimate_snr_spectral(frequencies, power_spectrum, signal_regions, noise_floor_db, config)
    elif config.method == "time_domain":
        return estimate_snr_time_domain(None)
    else:
        raise ValueError(f"Unknown SNR method: {config.method}")