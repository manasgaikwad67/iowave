"""Feature extraction for modulation classification."""

import numpy as np
from typing import List, Dict, Optional
from dataclasses import dataclass
from scipy import stats
from ..dsp import (
    compute_spectral_moments,
    compute_spectral_entropy,
    compute_spectral_flatness,
    compute_spectral_rolloff,
    compute_crest_factor,
    compute_papr,
    compute_iq_correlation,
    compute_psd,
    PSDConfig,
)
from ..models import TimeDomainParameters, FrequencyDomainParameters, InstantaneousParameters
from ..utils import get_logger
from ..config import settings

logger = get_logger(__name__)


@dataclass
class FeatureConfig:
    """Configuration for feature extraction."""

    include_spectral: bool = True
    include_temporal: bool = True
    include_modulation: bool = True
    include_constellation: bool = True
    rolloff_percentile: float = 0.85


def extract_features(
    iq_data: np.ndarray,
    sample_rate: float,
    time_domain: Optional[TimeDomainParameters] = None,
    freq_domain: Optional[FrequencyDomainParameters] = None,
    instantaneous: Optional[InstantaneousParameters] = None,
    config: Optional[FeatureConfig] = None,
) -> Dict[str, float]:
    """
    Extract comprehensive feature vector for modulation classification.

    Args:
        iq_data: Complex IQ signal
        sample_rate: Sample rate in Hz
        time_domain: Pre-computed time domain parameters
        freq_domain: Pre-computed frequency domain parameters
        instantaneous: Pre-computed instantaneous parameters
        config: Feature extraction configuration

    Returns:
        Dictionary of feature name -> value
    """
    if config is None:
        config = FeatureConfig()

    features = {}

    # Temporal features
    if config.include_temporal:
        temporal = extract_temporal_features(iq_data, sample_rate, time_domain)
        features.update(temporal)

    # Spectral features
    if config.include_spectral:
        spectral = extract_spectral_features(iq_data, sample_rate, freq_domain, config)
        features.update(spectral)

    # Modulation-specific features
    if config.include_modulation:
        mod = extract_modulation_features(iq_data, sample_rate, instantaneous)
        features.update(mod)

    # Constellation features
    if config.include_constellation:
        const = extract_constellation_features(iq_data)
        features.update(const)

    return features


def extract_temporal_features(
    iq_data: np.ndarray,
    sample_rate: float,
    time_domain: Optional[TimeDomainParameters] = None,
) -> Dict[str, float]:
    """Extract temporal/time-domain features."""
    features = {}

    if time_domain is None:
        # Compute on the fly
        I = np.real(iq_data)
        Q = np.imag(iq_data)
        mag = np.abs(iq_data)
        phase = np.angle(iq_data)

        features["mean_I"] = float(np.mean(I))
        features["mean_Q"] = float(np.mean(Q))
        features["std_I"] = float(np.std(I))
        features["std_Q"] = float(np.std(Q))
        features["rms_magnitude"] = float(np.sqrt(np.mean(mag**2)))
        features["mean_magnitude"] = float(np.mean(mag))
        features["std_magnitude"] = float(np.std(mag))
        features["mean_phase"] = float(np.mean(phase))
        features["std_phase"] = float(np.std(phase))
    else:
        features["mean_I"] = time_domain.mean_I
        features["mean_Q"] = time_domain.mean_Q
        features["rms_magnitude"] = time_domain.rms_magnitude
        features["mean_magnitude"] = time_domain.amplitude_mean
        features["std_magnitude"] = time_domain.amplitude_std
        features["mean_phase"] = time_domain.phase_mean
        features["std_phase"] = time_domain.phase_std

    # Crest factor and PAPR
    features["crest_factor"] = compute_crest_factor(iq_data)
    features["papr_db"] = compute_papr(iq_data)

    # I/Q correlation
    features["iq_correlation"] = compute_iq_correlation(iq_data)

    # Amplitude distribution moments
    mag = np.abs(iq_data)
    features["amplitude_skewness"] = float(stats.skew(mag))
    features["amplitude_kurtosis"] = float(stats.kurtosis(mag))

    # Phase distribution moments
    phase = np.angle(iq_data)
    features["phase_skewness"] = float(stats.skew(phase))
    features["phase_kurtosis"] = float(stats.kurtosis(phase))

    return features


def extract_spectral_features(
    iq_data: np.ndarray,
    sample_rate: float,
    freq_domain: Optional[FrequencyDomainParameters] = None,
    config: Optional[FeatureConfig] = None,
) -> Dict[str, float]:
    """Extract spectral/frequency-domain features."""
    features = {}

    if freq_domain is not None:
        features["spectral_centroid"] = freq_domain.spectral_centroid or 0
        features["spectral_spread"] = freq_domain.spectral_spread or 0
        features["spectral_entropy"] = freq_domain.spectral_entropy or 0
        features["spectral_flatness"] = freq_domain.spectral_flatness or 0
        features["peak_frequency"] = freq_domain.peak_frequency or 0
        features["peak_power_db"] = freq_domain.peak_power or 0
        features["noise_floor_db"] = freq_domain.noise_floor_db or 0
        features["snr_db"] = freq_domain.snr_db or 0
        features["occupied_bw_90"] = freq_domain.bandwidth_90 or 0
        features["occupied_bw_95"] = freq_domain.bandwidth_95 or 0
        features["occupied_bw_99"] = freq_domain.bandwidth_99 or 0
        features["minus_3db_bw"] = freq_domain.minus_3db_bandwidth or 0
        features["num_peaks"] = freq_domain.number_of_detected_peaks
    else:
        # Compute from scratch using PSD
        from ..dsp import compute_psd, compute_spectral_moments, compute_spectral_entropy, compute_spectral_flatness, compute_spectral_rolloff
        from ..config import settings

        psd_config = PSDConfig(
            nperseg=settings.get("psd.nperseg", 2048),
            noverlap=settings.get("psd.noverlap", 1024),
            nfft=settings.get("psd.nfft", 8192),
            window=settings.get("psd.window", "hann"),
        )
        psd_result = compute_psd(iq_data, sample_rate, psd_config)

        moments = compute_spectral_moments(psd_result.frequencies, psd_result.psd)
        features["spectral_centroid"] = moments["centroid"] or 0
        features["spectral_spread"] = moments["spread"] or 0
        features["spectral_skewness"] = moments["skewness"] or 0
        features["spectral_kurtosis"] = moments["kurtosis"] or 0

        features["spectral_entropy"] = compute_spectral_entropy(psd_result.frequencies, psd_result.psd)
        features["spectral_flatness"] = compute_spectral_flatness(psd_result.frequencies, psd_result.psd)
        features["spectral_rolloff"] = compute_spectral_rolloff(psd_result.frequencies, psd_result.psd, config.rolloff_percentile if config else 0.85)

        # Peak info
        from ..dsp import find_fft_peaks
        peaks = find_fft_peaks(psd_result.frequencies, psd_result.psd)
        features["num_peaks"] = len(peaks)
        if peaks:
            features["peak_frequency"] = peaks[0].frequency
            features["peak_power_db"] = 10 * np.log10(peaks[0].power + 1e-20)

    return features


def extract_modulation_features(
    iq_data: np.ndarray,
    sample_rate: float,
    instantaneous: Optional[InstantaneousParameters] = None,
) -> Dict[str, float]:
    """Extract modulation-specific features."""
    features = {}

    # Instantaneous frequency features
    if instantaneous is not None:
        features["inst_freq_mean"] = instantaneous.instantaneous_frequency_mean or 0
        features["inst_freq_std"] = instantaneous.instantaneous_frequency_std or 0
        features["freq_deviation"] = instantaneous.frequency_deviation or 0
        features["inst_amp_mean"] = instantaneous.instantaneous_amplitude_mean or 0
        features["inst_amp_std"] = instantaneous.instantaneous_amplitude_std or 0
    else:
        # Compute on the fly
        from ..dsp import analyze_instantaneous_frequency
        inst = analyze_instantaneous_frequency(iq_data, sample_rate)
        features["inst_freq_mean"] = inst.instantaneous_frequency_mean or 0
        features["inst_freq_std"] = inst.instantaneous_frequency_std or 0
        features["freq_deviation"] = inst.frequency_deviation or 0
        features["inst_amp_mean"] = inst.instantaneous_amplitude_mean or 0
        features["inst_amp_std"] = inst.instantaneous_amplitude_std or 0

    # Phase discontinuity detection (for PSK)
    phase = np.angle(iq_data)
    phase_diff = np.diff(np.unwrap(phase))
    features["phase_diff_mean"] = float(np.mean(phase_diff))
    features["phase_diff_std"] = float(np.std(phase_diff))
    features["phase_diff_max"] = float(np.max(np.abs(phase_diff)))

    # Amplitude transitions (for ASK/QAM)
    mag = np.abs(iq_data)
    mag_diff = np.diff(mag)
    features["mag_diff_mean"] = float(np.mean(mag_diff))
    features["mag_diff_std"] = float(np.std(mag_diff))

    # Zero crossings in I and Q
    I = np.real(iq_data)
    Q = np.imag(iq_data)
    features["I_zero_crossings"] = np.sum(np.diff(np.signbit(I)))
    features["Q_zero_crossings"] = np.sum(np.diff(np.signbit(Q)))

    return features


def extract_constellation_features(iq_data: np.ndarray) -> Dict[str, float]:
    """Extract constellation-based features."""
    features = {}

    I = np.real(iq_data)
    Q = np.imag(iq_data)

    # Centroid
    centroid_I = float(np.mean(I))
    centroid_Q = float(np.mean(Q))
    features["constellation_centroid_I"] = centroid_I
    features["constellation_centroid_Q"] = centroid_Q

    # Radius statistics
    radius = np.sqrt((I - centroid_I)**2 + (Q - centroid_Q)**2)
    features["constellation_radius_mean"] = float(np.mean(radius))
    features["constellation_radius_std"] = float(np.std(radius))
    features["constellation_radius_max"] = float(np.max(radius))

    # Phase statistics around centroid
    phase = np.angle((I - centroid_I) + 1j * (Q - centroid_Q))
    features["constellation_phase_mean"] = float(np.mean(phase))
    features["constellation_phase_std"] = float(np.std(phase))

    # Number of distinct clusters (rough estimate using radius quantiles)
    # This is a simple heuristic
    radius_sorted = np.sort(radius)
    n_samples = len(radius_sorted)
    if n_samples > 100:
        # Look for gaps in radius distribution
        radius_diff = np.diff(radius_sorted)
        large_gaps = np.sum(radius_diff > 3 * np.median(radius_diff))
        features["constellation_num_rings"] = int(large_gaps + 1)
    else:
        features["constellation_num_rings"] = 1

    # Constellation bounding box
    features["constellation_I_min"] = float(np.min(I))
    features["constellation_I_max"] = float(np.max(I))
    features["constellation_Q_min"] = float(np.min(Q))
    features["constellation_Q_max"] = float(np.max(Q))
    features["constellation_I_range"] = float(np.max(I) - np.min(I))
    features["constellation_Q_range"] = float(np.max(Q) - np.min(Q))

    return features


def get_feature_names(config: Optional[FeatureConfig] = None) -> List[str]:
    """Get list of all feature names for a given configuration."""
    # This is a reference list - actual features depend on data
    names = []

    if config is None:
        config = FeatureConfig()

    if config.include_temporal:
        names.extend([
            "mean_I", "mean_Q", "std_I", "std_Q", "rms_magnitude",
            "mean_magnitude", "std_magnitude", "mean_phase", "std_phase",
            "crest_factor", "papr_db", "iq_correlation",
            "amplitude_skewness", "amplitude_kurtosis",
            "phase_skewness", "phase_kurtosis",
        ])

    if config.include_spectral:
        names.extend([
            "spectral_centroid", "spectral_spread", "spectral_skewness", "spectral_kurtosis",
            "spectral_entropy", "spectral_flatness", "spectral_rolloff",
            "peak_frequency", "peak_power_db", "noise_floor_db", "snr_db",
            "occupied_bw_90", "occupied_bw_95", "occupied_bw_99", "minus_3db_bw",
            "num_peaks",
        ])

    if config.include_modulation:
        names.extend([
            "inst_freq_mean", "inst_freq_std", "freq_deviation",
            "inst_amp_mean", "inst_amp_std",
            "phase_diff_mean", "phase_diff_std", "phase_diff_max",
            "mag_diff_mean", "mag_diff_std",
            "I_zero_crossings", "Q_zero_crossings",
        ])

    if config.include_constellation:
        names.extend([
            "constellation_centroid_I", "constellation_centroid_Q",
            "constellation_radius_mean", "constellation_radius_std", "constellation_radius_max",
            "constellation_phase_mean", "constellation_phase_std",
            "constellation_num_rings",
            "constellation_I_min", "constellation_I_max",
            "constellation_Q_min", "constellation_Q_max",
            "constellation_I_range", "constellation_Q_range",
        ])

    return names