"""DSP module."""

from .time_domain import (
    analyze_time_domain,
    compute_amplitude_phase,
    compute_instantaneous_power,
    detect_clipping,
    compute_autocorrelation,
)
from .fft_analysis import (
    compute_fft,
    compute_fft_positive_only,
    find_fft_peaks,
    estimate_noise_floor_from_fft,
    FFTConfig,
)
from .psd_analysis import (
    compute_psd,
    compute_complex_psd,
    compute_cross_psd,
    PSDConfig,
)
from .peak_detection import (
    detect_peaks,
    find_dominant_peak,
    merge_nearby_peaks,
    PeakDetectionConfig,
)
from .bandwidth import (
    estimate_occupied_bandwidth,
    estimate_minus_3db_bandwidth,
    estimate_bandwidth,
    find_signal_edges,
    BandwidthConfig,
)
from .noise_analysis import (
    estimate_noise_floor,
    estimate_noise_power,
    NoiseFloorConfig,
)
from .snr import (
    estimate_snr,
    estimate_snr_spectral,
    estimate_snr_time_domain,
    SNRConfig,
)
from .instantaneous_frequency import (
    compute_instantaneous_frequency,
    analyze_instantaneous_frequency,
    detect_frequency_drift,
    InstantaneousFrequencyConfig,
)
from .statistics import (
    compute_spectral_moments,
    compute_spectral_entropy,
    compute_spectral_flatness,
    compute_spectral_rolloff,
    compute_peak_to_noise_ratio,
    compute_crest_factor,
    compute_papr,
    compute_iq_correlation,
    estimate_modulation_bandwidth,
)

__all__ = [
    # time_domain
    "analyze_time_domain",
    "compute_amplitude_phase",
    "compute_instantaneous_power",
    "detect_clipping",
    "compute_autocorrelation",
    # fft_analysis
    "compute_fft",
    "compute_fft_positive_only",
    "find_fft_peaks",
    "estimate_noise_floor_from_fft",
    "FFTConfig",
    # psd_analysis
    "compute_psd",
    "compute_complex_psd",
    "compute_cross_psd",
    "PSDConfig",
    # peak_detection
    "detect_peaks",
    "find_dominant_peak",
    "merge_nearby_peaks",
    "PeakDetectionConfig",
    # bandwidth
    "estimate_occupied_bandwidth",
    "estimate_minus_3db_bandwidth",
    "estimate_bandwidth",
    "find_signal_edges",
    "BandwidthConfig",
    # noise_analysis
    "estimate_noise_floor",
    "estimate_noise_power",
    "NoiseFloorConfig",
    # snr
    "estimate_snr",
    "estimate_snr_spectral",
    "estimate_snr_time_domain",
    "SNRConfig",
    # instantaneous_frequency
    "compute_instantaneous_frequency",
    "analyze_instantaneous_frequency",
    "detect_frequency_drift",
    "InstantaneousFrequencyConfig",
    # statistics
    "compute_spectral_moments",
    "compute_spectral_entropy",
    "compute_spectral_flatness",
    "compute_spectral_rolloff",
    "compute_peak_to_noise_ratio",
    "compute_crest_factor",
    "compute_papr",
    "compute_iq_correlation",
    "estimate_modulation_bandwidth",
]