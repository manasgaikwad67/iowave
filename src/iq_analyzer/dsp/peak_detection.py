"""Peak detection in frequency domain."""

import numpy as np
from scipy.signal import find_peaks
from typing import Optional, List
from dataclasses import dataclass
from ..models import PeakInfo
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class PeakDetectionConfig:
    """Configuration for peak detection."""

    prominence_db: float = 10.0
    min_distance_hz: float = 10000
    min_height_db: float = -60.0
    width_hz: Optional[float] = None
    threshold_db: Optional[float] = None
    max_peaks: int = 20


def detect_peaks(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
    config: Optional[PeakDetectionConfig] = None,
) -> List[PeakInfo]:
    """
    Detect peaks in power spectrum.

    Args:
        frequencies: Frequency array
        power_spectrum: Power spectrum (linear scale)
        config: Peak detection configuration

    Returns:
        List of PeakInfo objects, sorted by prominence
    """
    if config is None:
        config = PeakDetectionConfig()

    if len(frequencies) != len(power_spectrum):
        raise ValueError("Frequency and power arrays must have same length")

    if len(frequencies) < 3:
        return []

    # Convert to dB for peak detection
    power_db = 10 * np.log10(power_spectrum + 1e-20)

    # Frequency resolution
    freq_res = frequencies[1] - frequencies[0] if len(frequencies) > 1 else 1.0

    # Convert parameters to bins
    min_distance_bins = max(1, int(config.min_distance_hz / freq_res))
    width_bins = None
    if config.width_hz is not None:
        width_bins = max(1, int(config.width_hz / freq_res))

    # Find peaks in dB domain
    # min_height in dB
    min_height_db = config.min_height_db
    # prominence in dB
    prominence_db = config.prominence_db

    peaks, properties = find_peaks(
        power_db,
        height=min_height_db,
        distance=min_distance_bins,
        prominence=prominence_db,
        width=width_bins,
    )

    # Create PeakInfo objects
    peak_list = []
    for i, peak_idx in enumerate(peaks):
        # Get peak properties from dB domain
        prom_db = properties["prominences"][i] if "prominences" in properties else 0
        left_base = properties["left_bases"][i] if "left_bases" in properties else peak_idx
        right_base = properties["right_bases"][i] if "right_bases" in properties else peak_idx

        width = properties["widths"][i] if "widths" in properties else 0
        width_hz = width * freq_res if width > 0 else None

        peak_info = PeakInfo(
            frequency=float(frequencies[peak_idx]),
            power=float(power_spectrum[peak_idx]),
            prominence=float(prom_db),
            width_hz=float(width_hz) if width_hz else None,
            left_base_hz=float(frequencies[left_base]) if left_base < len(frequencies) else None,
            right_base_hz=float(frequencies[right_base]) if right_base < len(frequencies) else None,
        )
        peak_list.append(peak_info)

    # Sort by prominence descending
    peak_list.sort(key=lambda p: p.prominence, reverse=True)

    # Limit number of peaks
    if config.max_peaks and len(peak_list) > config.max_peaks:
        peak_list = peak_list[:config.max_peaks]

    return peak_list


def find_dominant_peak(
    frequencies: np.ndarray,
    power_spectrum: np.ndarray,
) -> Optional[PeakInfo]:
    """Find the single dominant peak."""
    peaks = detect_peaks(frequencies, power_spectrum)
    return peaks[0] if peaks else None


def merge_nearby_peaks(
    peaks: List[PeakInfo],
    merge_distance_hz: float = 5000,
) -> List[PeakInfo]:
    """Merge peaks that are close to each other."""
    if not peaks:
        return []

    # Sort by frequency
    peaks = sorted(peaks, key=lambda p: p.frequency)

    merged = [peaks[0]]
    for peak in peaks[1:]:
        last = merged[-1]
        if peak.frequency - last.frequency <= merge_distance_hz:
            # Merge: keep the stronger one
            if peak.power > last.power:
                merged[-1] = peak
        else:
            merged.append(peak)

    return merged