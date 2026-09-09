"""Analysis result data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import numpy as np
from .parameter_models import FFTResult, PSDResult


class ModulationType(str, Enum):
    """Supported modulation types for classification."""
    NOISE = "Noise"
    AM = "AM"
    FM = "FM"
    PM = "PM"
    BPSK = "BPSK"
    QPSK = "QPSK"
    PSK8 = "8PSK"
    FSK = "FSK"
    QAM16 = "16QAM"
    UNKNOWN = "Unknown"


@dataclass
class TimeDomainParameters:
    """Time-domain signal parameters."""

    mean_I: float
    mean_Q: float
    rms_I: float
    rms_Q: float
    rms_magnitude: float
    peak_magnitude: float
    peak_to_peak: float
    variance: float
    standard_deviation: float
    crest_factor: float
    papr_db: float
    amplitude_mean: float
    amplitude_std: float
    phase_mean: float
    phase_std: float

    def to_dict(self) -> dict:
        return {
            "mean_I": self.mean_I,
            "mean_Q": self.mean_Q,
            "rms_I": self.rms_I,
            "rms_Q": self.rms_Q,
            "rms_magnitude": self.rms_magnitude,
            "peak_magnitude": self.peak_magnitude,
            "peak_to_peak": self.peak_to_peak,
            "variance": self.variance,
            "standard_deviation": self.standard_deviation,
            "crest_factor": self.crest_factor,
            "papr_db": self.papr_db,
            "amplitude_mean": self.amplitude_mean,
            "amplitude_std": self.amplitude_std,
            "phase_mean": self.phase_mean,
            "phase_std": self.phase_std,
        }


@dataclass
class FrequencyDomainParameters:
    """Frequency-domain signal parameters."""

    fft_size: int
    frequency_resolution: float
    peak_frequency: Optional[float]
    peak_power: Optional[float]
    noise_floor_db: Optional[float]
    signal_power_db: Optional[float]
    snr_db: Optional[float]
    lower_signal_frequency: Optional[float]
    upper_signal_frequency: Optional[float]
    occupied_bandwidth: Optional[float]
    bandwidth_90: Optional[float]
    bandwidth_95: Optional[float]
    bandwidth_99: Optional[float]
    minus_3db_bandwidth: Optional[float]
    spectral_centroid: Optional[float]
    spectral_spread: Optional[float]
    spectral_entropy: Optional[float]
    spectral_flatness: Optional[float]
    number_of_detected_peaks: int

    def to_dict(self) -> dict:
        return {
            "fft_size": self.fft_size,
            "frequency_resolution": self.frequency_resolution,
            "peak_frequency": self.peak_frequency,
            "peak_power": self.peak_power,
            "noise_floor_db": self.noise_floor_db,
            "signal_power_db": self.signal_power_db,
            "snr_db": self.snr_db,
            "lower_signal_frequency": self.lower_signal_frequency,
            "upper_signal_frequency": self.upper_signal_frequency,
            "occupied_bandwidth": self.occupied_bandwidth,
            "bandwidth_90": self.bandwidth_90,
            "bandwidth_95": self.bandwidth_95,
            "bandwidth_99": self.bandwidth_99,
            "minus_3db_bandwidth": self.minus_3db_bandwidth,
            "spectral_centroid": self.spectral_centroid,
            "spectral_spread": self.spectral_spread,
            "spectral_entropy": self.spectral_entropy,
            "spectral_flatness": self.spectral_flatness,
            "number_of_detected_peaks": self.number_of_detected_peaks,
        }


@dataclass
class InstantaneousParameters:
    """Instantaneous signal parameters."""

    instantaneous_frequency_mean: Optional[float]
    instantaneous_frequency_std: Optional[float]
    frequency_deviation: Optional[float]
    instantaneous_amplitude_mean: Optional[float]
    instantaneous_amplitude_std: Optional[float]
    phase_mean: Optional[float]
    phase_std: Optional[float]
    phase_min: Optional[float]
    phase_max: Optional[float]

    def to_dict(self) -> dict:
        return {
            "instantaneous_frequency_mean": self.instantaneous_frequency_mean,
            "instantaneous_frequency_std": self.instantaneous_frequency_std,
            "frequency_deviation": self.frequency_deviation,
            "instantaneous_amplitude_mean": self.instantaneous_amplitude_mean,
            "instantaneous_amplitude_std": self.instantaneous_amplitude_std,
            "phase_mean": self.phase_mean,
            "phase_std": self.phase_std,
            "phase_min": self.phase_min,
            "phase_max": self.phase_max,
        }


@dataclass
class SignalRegion:
    """Detected signal region in frequency domain."""

    lower_frequency: float
    upper_frequency: float
    bandwidth: float
    peak_frequency: float
    peak_power: float
    estimated_snr_db: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "lower_frequency": self.lower_frequency,
            "upper_frequency": self.upper_frequency,
            "bandwidth": self.bandwidth,
            "peak_frequency": self.peak_frequency,
            "peak_power": self.peak_power,
            "estimated_snr_db": self.estimated_snr_db,
        }


@dataclass
class PeakInfo:
    """Spectral peak information."""

    frequency: float
    power: float
    prominence: float
    width_hz: Optional[float] = None
    left_base_hz: Optional[float] = None
    right_base_hz: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "frequency": self.frequency,
            "power": self.power,
            "prominence": self.prominence,
            "width_hz": self.width_hz,
            "left_base_hz": self.left_base_hz,
            "right_base_hz": self.right_base_hz,
        }


@dataclass
class NoiseFloorResult:
    """Noise floor estimation result."""

    noise_floor_db: float
    method: str
    threshold_db: float
    uncertainty_db: Optional[float] = None
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "noise_floor_db": self.noise_floor_db,
            "method": self.method,
            "threshold_db": self.threshold_db,
            "uncertainty_db": self.uncertainty_db,
            "warnings": self.warnings,
        }


@dataclass
class SNRResult:
    """SNR estimation result."""

    snr_db: Optional[float]
    signal_power_db: Optional[float]
    noise_power_db: Optional[float]
    method: str
    assumptions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "snr_db": self.snr_db,
            "signal_power_db": self.signal_power_db,
            "noise_power_db": self.noise_power_db,
            "method": self.method,
            "assumptions": self.assumptions,
            "warnings": self.warnings,
        }


@dataclass
class ClassificationResult:
    """Modulation classification result."""

    predicted_class: ModulationType
    confidence: float
    probabilities: Dict[ModulationType, float]
    model_name: str
    model_version: str
    feature_version: str
    features_used: List[str]
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "predicted_class": self.predicted_class.value,
            "confidence": self.confidence,
            "probabilities": {k.value: v for k, v in self.probabilities.items()},
            "model_name": self.model_name,
            "model_version": self.model_version,
            "feature_version": self.feature_version,
            "features_used": self.features_used,
            "warnings": self.warnings,
        }


@dataclass
class SignalQualityResult:
    """Signal quality assessment result."""

    overall_score: float  # 0-100
    snr_score: float
    frequency_stability_score: float
    amplitude_stability_score: float
    spectral_quality_score: float
    noise_score: float
    explanation: str
    component_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "overall_score": self.overall_score,
            "snr_score": self.snr_score,
            "frequency_stability_score": self.frequency_stability_score,
            "amplitude_stability_score": self.amplitude_stability_score,
            "spectral_quality_score": self.spectral_quality_score,
            "noise_score": self.noise_score,
            "explanation": self.explanation,
            "component_details": self.component_details,
        }


@dataclass
class SpectralFeaturesResult:
    """Computed spectral features."""

    spectral_centroid: Optional[float]
    spectral_spread: Optional[float]
    spectral_skewness: Optional[float]
    spectral_kurtosis: Optional[float]
    spectral_entropy: Optional[float]
    spectral_flatness: Optional[float]
    spectral_rolloff: Optional[float]
    peak_to_noise_ratio: Optional[float]

    def to_dict(self) -> dict:
        return {
            "spectral_centroid": self.spectral_centroid,
            "spectral_spread": self.spectral_spread,
            "spectral_skewness": self.spectral_skewness,
            "spectral_kurtosis": self.spectral_kurtosis,
            "spectral_entropy": self.spectral_entropy,
            "spectral_flatness": self.spectral_flatness,
            "spectral_rolloff": self.spectral_rolloff,
            "peak_to_noise_ratio": self.peak_to_noise_ratio,
        }


@dataclass
class AnalysisResult:
    """Complete analysis result container."""

    # Metadata
    signal_metadata: 'SignalMetadata'
    preprocessing_metadata: 'PreprocessingMetadata'
    analysis_timestamp: datetime
    software_version: str
    configuration_used: Dict[str, Any]

    # Parameter results
    time_domain: Optional[TimeDomainParameters] = None
    frequency_domain: Optional[FrequencyDomainParameters] = None
    instantaneous: Optional[InstantaneousParameters] = None
    spectral_features: Optional[SpectralFeaturesResult] = None

    # Detection results
    detected_peaks: List[PeakInfo] = field(default_factory=list)
    signal_regions: List[SignalRegion] = field(default_factory=list)
    noise_floor: Optional[NoiseFloorResult] = None
    snr_result: Optional[SNRResult] = None

    # Optional results
    classification: Optional[ClassificationResult] = None
    quality_score: Optional[SignalQualityResult] = None

    # Visualization inputs retained from the completed pipeline.
    iq_data: Optional[np.ndarray] = field(default=None, repr=False)
    fft_result: Optional[FFTResult] = field(default=None, repr=False)
    psd_result: Optional[PSDResult] = field(default=None, repr=False)

    # Warnings and info
    warnings: List[str] = field(default_factory=list)
    processing_time_seconds: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "signal_metadata": self.signal_metadata.to_dict(),
            "preprocessing_metadata": self.preprocessing_metadata.to_dict(),
            "analysis_timestamp": self.analysis_timestamp.isoformat(),
            "software_version": self.software_version,
            "configuration_used": self.configuration_used,
            "time_domain": self.time_domain.to_dict() if self.time_domain else None,
            "frequency_domain": self.frequency_domain.to_dict() if self.frequency_domain else None,
            "instantaneous": self.instantaneous.to_dict() if self.instantaneous else None,
            "spectral_features": self.spectral_features.to_dict() if self.spectral_features else None,
            "detected_peaks": [p.to_dict() for p in self.detected_peaks],
            "signal_regions": [r.to_dict() for r in self.signal_regions],
            "noise_floor": self.noise_floor.to_dict() if self.noise_floor else None,
            "snr_result": self.snr_result.to_dict() if self.snr_result else None,
            "classification": self.classification.to_dict() if self.classification else None,
            "quality_score": self.quality_score.to_dict() if self.quality_score else None,
            "warnings": self.warnings,
            "processing_time_seconds": self.processing_time_seconds,
        }


# Forward reference resolution
from .signal_metadata import SignalMetadata, PreprocessingMetadata