"""Analysis pipeline orchestration."""

import time
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from ..models import (
    AnalysisResult,
    SignalMetadata,
    PreprocessingMetadata,
    TimeDomainParameters,
    FrequencyDomainParameters,
    InstantaneousParameters,
    SpectralFeaturesResult,
    SignalRegion,
    PeakInfo,
    NoiseFloorResult,
    SNRResult,
    ClassificationResult,
    SignalQualityResult,
    ModulationType,
)
from ..io import detect_file_type, load_wav, load_raw_iq, FileType
from ..processing import validate_iq_data, preprocess_signal, PreprocessingConfig
from ..dsp import (
    analyze_time_domain,
    compute_fft,
    compute_psd,
    detect_peaks,
    estimate_noise_floor,
    estimate_bandwidth,
    find_signal_edges,
    estimate_snr,
    analyze_instantaneous_frequency,
    compute_spectral_moments,
    compute_spectral_entropy,
    compute_spectral_flatness,
    compute_spectral_rolloff,
    compute_peak_to_noise_ratio,
    FFTConfig,
    PSDConfig,
    PeakDetectionConfig,
    BandwidthConfig,
    NoiseFloorConfig,
    SNRConfig,
    InstantaneousFrequencyConfig,
)
from ..features import extract_features, FeatureConfig
from ..classification import predict_single, ClassifierConfig, ModulationClassifier
from ..quality import compute_signal_quality, QualityScoreConfig
from ..config import settings
from ..utils import get_logger, get_performance_monitor

logger = get_logger(__name__)


@dataclass
class PipelineConfig:
    """Complete pipeline configuration."""

    # Preprocessing
    preprocessing: PreprocessingConfig = None

    # FFT
    fft: FFTConfig = None

    # PSD
    psd: PSDConfig = None

    # Peak detection
    peak_detection: PeakDetectionConfig = None

    # Bandwidth
    bandwidth: BandwidthConfig = None

    # Noise floor
    noise_floor: NoiseFloorConfig = None

    # SNR
    snr: SNRConfig = None

    # Instantaneous frequency
    instantaneous_frequency: InstantaneousFrequencyConfig = None

    # Features
    features: FeatureConfig = None

    # Classification
    classifier: ClassifierConfig = None

    # Quality score
    quality_score: QualityScoreConfig = None

    def __post_init__(self):
        if self.preprocessing is None:
            self.preprocessing = PreprocessingConfig()
        if self.fft is None:
            self.fft = FFTConfig()
        if self.psd is None:
            self.psd = PSDConfig()
        if self.peak_detection is None:
            self.peak_detection = PeakDetectionConfig()
        if self.bandwidth is None:
            self.bandwidth = BandwidthConfig()
        if self.noise_floor is None:
            self.noise_floor = NoiseFloorConfig()
        if self.snr is None:
            self.snr = SNRConfig()
        if self.instantaneous_frequency is None:
            self.instantaneous_frequency = InstantaneousFrequencyConfig()
        if self.features is None:
            self.features = FeatureConfig()
        if self.classifier is None:
            self.classifier = ClassifierConfig()
        if self.quality_score is None:
            self.quality_score = QualityScoreConfig()


def create_pipeline_config_from_settings() -> PipelineConfig:
    """Create pipeline config from global settings."""
    config = PipelineConfig()

    # Preprocessing
    config.preprocessing = PreprocessingConfig(
        remove_nan_inf=settings.get("preprocessing.remove_nan_inf", True),
        remove_dc_offset=settings.get("preprocessing.remove_dc_offset", True),
        normalize=settings.get("preprocessing.normalize", False),
        detrend=settings.get("preprocessing.detrend", False),
        filter_enabled=settings.get("preprocessing.filter_enabled", False),
        filter_type=settings.get("preprocessing.filter_type", "bandpass"),
        low_cut_hz=settings.get("preprocessing.low_cut_hz", 1000),
        high_cut_hz=settings.get("preprocessing.high_cut_hz", 100000),
        filter_order=settings.get("preprocessing.filter_order", 4),
        filter_design=settings.get("preprocessing.filter_design", "sos"),
        resample_enabled=settings.get("preprocessing.resample_enabled", False),
        target_sample_rate=settings.get("preprocessing.target_sample_rate", 1024000),
        decimation_factor=settings.get("preprocessing.decimation_factor", 1),
    )

    # FFT
    config.fft = FFTConfig(
        size=settings.get("fft.size", 8192),
        zero_padding=settings.get("fft.zero_padding", True),
        window=settings.get("fft.window", "hann"),
        fftshift=settings.get("fft.fftshift", True),
    )

    # PSD
    config.psd = PSDConfig(
        method=settings.get("psd.method", "welch"),
        nperseg=settings.get("psd.nperseg", 2048),
        noverlap=settings.get("psd.noverlap", 1024),
        nfft=settings.get("psd.nfft", 8192),
        window=settings.get("psd.window", "hann"),
        scaling=settings.get("psd.scaling", "density"),
    )

    # Peak detection
    config.peak_detection = PeakDetectionConfig(
        prominence_db=settings.get("peak_detection.prominence_db", 10.0),
        min_distance_hz=settings.get("peak_detection.min_distance_hz", 10000),
        min_height_db=settings.get("peak_detection.min_height_db", -60.0),
    )

    # Bandwidth
    config.bandwidth = BandwidthConfig(
        method=settings.get("bandwidth.method", "occupied"),
        percentages=settings.get("bandwidth.percentages", [90.0, 95.0, 99.0]),
        interpolation=settings.get("bandwidth.interpolation", True),
    )

    # Noise floor
    config.noise_floor = NoiseFloorConfig(
        method=settings.get("snr.method", "percentile_excluding_peaks"),
        percentile=10.0,
        peak_prominence_db=settings.get("peak_detection.prominence_db", 10.0),
        peak_min_distance_hz=settings.get("peak_detection.min_distance_hz", 10000),
    )

    # SNR
    config.snr = SNRConfig(
        method=settings.get("snr.method", "spectral"),
        signal_region_margin_hz=settings.get("snr.signal_region_margin_hz", 5000),
    )

    # Instantaneous frequency
    config.instantaneous_frequency = InstantaneousFrequencyConfig(
        amplitude_threshold=0.01,
        unwrap_phase=True,
        differentiation_method="central",
    )

    # Classification
    config.classifier = ClassifierConfig(
        model_path=settings.get("ml.model_path", "models/trained/modulation_classifier.joblib"),
        feature_version=settings.get("ml.feature_version", "1.0"),
        confidence_threshold=settings.get("ml.confidence_threshold", 0.5),
        enabled=settings.get("ml.enabled", True),
    )

    # Quality score
    config.quality_score = QualityScoreConfig(
        enabled=settings.get("quality_score.enabled", True),
    )

    return config


def run_analysis_pipeline(
    file_path: Path,
    config: Optional[PipelineConfig] = None,
    sample_rate: Optional[float] = None,
    dtype: Optional[str] = None,
    endianness: Optional[str] = None,
    iq_layout: Optional[str] = None,
    force_iq: bool = False,
) -> AnalysisResult:
    """
    Run complete analysis pipeline on a signal file.

    Args:
        file_path: Path to signal file
        config: Pipeline configuration
        sample_rate: Sample rate for raw IQ files
        dtype: Data type for raw IQ files
        endianness: Endianness for raw IQ files
        iq_layout: IQ layout for raw IQ files
        force_iq: Force stereo WAV to be interpreted as IQ

    Returns:
        AnalysisResult with all computed parameters
    """
    start_time = time.perf_counter()
    monitor = get_performance_monitor()

    if config is None:
        config = create_pipeline_config_from_settings()

    warnings = []

    # Step 1: Detect file type
    monitor.start("file_detection")
    detection = detect_file_type(file_path)
    monitor.stop("file_detection")

    if detection.file_type == FileType.UNKNOWN:
        raise ValueError(f"Unsupported file format: {file_path}")

    # Step 2: Load file
    monitor.start("file_loading")
    if detection.file_type == FileType.WAV:
        load_result = load_wav(file_path, force_iq=force_iq)
        iq_data = load_result.iq_data
        actual_sample_rate = load_result.sample_rate
        metadata = load_result.metadata
        warnings.extend(load_result.warnings)
    else:  # RAW_IQ
        if sample_rate is None:
            sample_rate = detection.suggested_params.get("sample_rate", 2048000)
            warnings.append(f"No sample rate provided, using default: {sample_rate} Hz")

        if dtype is None:
            dtype = detection.suggested_params.get("dtype", "int16")
        if endianness is None:
            endianness = detection.suggested_params.get("endianness", "little")
        if iq_layout is None:
            iq_layout = detection.suggested_params.get("iq_layout", "interleaved")

        load_result = load_raw_iq(
            file_path,
            sample_rate=sample_rate,
            dtype=dtype,
            endianness=endianness,
            iq_layout=iq_layout,
        )
        iq_data = load_result.iq_data
        actual_sample_rate = load_result.sample_rate
        metadata = load_result.metadata
        warnings.extend(load_result.warnings)

    monitor.stop("file_loading")

    # Step 3: Validate input
    monitor.start("validation")
    val_result = validate_iq_data(iq_data, actual_sample_rate)
    if not val_result.is_valid:
        raise ValueError(f"Input validation failed: {val_result.errors}")
    warnings.extend(val_result.warnings)
    monitor.stop("validation")

    # Step 4: Preprocessing
    monitor.start("preprocessing")
    processed_iq, prep_metadata, final_sample_rate = preprocess_signal(
        iq_data, actual_sample_rate, config.preprocessing
    )
    warnings.extend(prep_metadata.warnings)
    monitor.stop("preprocessing")

    # Step 5: Time-domain analysis
    monitor.start("time_domain")
    time_domain = analyze_time_domain(processed_iq)
    monitor.stop("time_domain")

    # Step 6: FFT
    monitor.start("fft")
    fft_result = compute_fft(processed_iq, final_sample_rate, config.fft)
    monitor.stop("fft")

    # Step 7: PSD
    monitor.start("psd")
    psd_result = compute_psd(processed_iq, final_sample_rate, config.psd)
    monitor.stop("psd")

    # Step 8: Peak detection
    monitor.start("peak_detection")
    peaks = detect_peaks(
        psd_result.frequencies,
        psd_result.psd,
        config.peak_detection,
    )
    monitor.stop("peak_detection")

    # Step 9: Noise floor estimation
    monitor.start("noise_floor")
    noise_floor = estimate_noise_floor(
        psd_result.frequencies,
        psd_result.psd,
        config.noise_floor,
    )
    warnings.extend(noise_floor.warnings)
    monitor.stop("noise_floor")

    # Step 10: Signal region detection
    monitor.start("signal_detection")
    signal_regions = []
    if peaks:
        for peak in peaks:
            lower, upper = find_signal_edges(
                psd_result.frequencies,
                psd_result.psd,
                noise_floor.noise_floor_db,
                margin_db=3.0,
            )
            if lower is not None and upper is not None:
                # Refine for each peak
                peak_mask = (psd_result.frequencies >= lower) & (psd_result.frequencies <= upper)
                if np.any(peak_mask):
                    region_peak_idx = np.argmax(psd_result.psd[peak_mask])
                    peak_freq = psd_result.frequencies[peak_mask][region_peak_idx]
                    peak_power = psd_result.psd[peak_mask][region_peak_idx]

                    signal_regions.append(SignalRegion(
                        lower_frequency=float(lower),
                        upper_frequency=float(upper),
                        bandwidth=float(upper - lower),
                        peak_frequency=float(peak_freq),
                        peak_power=float(peak_power),
                    ))
    monitor.stop("signal_detection")

    # Step 11: Bandwidth estimation
    monitor.start("bandwidth")
    bw_results = estimate_bandwidth(
        psd_result.frequencies,
        psd_result.psd,
        config.bandwidth,
    )
    monitor.stop("bandwidth")

    # Step 12: SNR estimation
    monitor.start("snr")
    snr_result = estimate_snr(
        psd_result.frequencies,
        psd_result.psd,
        signal_regions,
        noise_floor.noise_floor_db,
        config.snr,
    )
    warnings.extend(snr_result.warnings)
    monitor.stop("snr")

    # Step 13: Instantaneous frequency
    monitor.start("instantaneous_frequency")
    inst_params = analyze_instantaneous_frequency(
        processed_iq,
        final_sample_rate,
        config.instantaneous_frequency,
    )
    monitor.stop("instantaneous_frequency")

    # Step 14: Spectral features
    monitor.start("spectral_features")
    moments = compute_spectral_moments(psd_result.frequencies, psd_result.psd)
    spectral_features = SpectralFeaturesResult(
        spectral_centroid=moments["centroid"],
        spectral_spread=moments["spread"],
        spectral_skewness=moments["skewness"],
        spectral_kurtosis=moments["kurtosis"],
        spectral_entropy=compute_spectral_entropy(psd_result.frequencies, psd_result.psd),
        spectral_flatness=compute_spectral_flatness(psd_result.frequencies, psd_result.psd),
        spectral_rolloff=compute_spectral_rolloff(psd_result.frequencies, psd_result.psd),
        peak_to_noise_ratio=compute_peak_to_noise_ratio(
            psd_result.frequencies,
            psd_result.psd,
            peaks[0].frequency if peaks else 0,
            noise_floor.noise_floor_db,
        ) if peaks else None,
    )
    monitor.stop("spectral_features")

    # Step 15: Frequency domain parameters
    freq_domain = FrequencyDomainParameters(
        fft_size=config.fft.size,
        frequency_resolution=final_sample_rate / config.fft.size,
        peak_frequency=peaks[0].frequency if peaks else None,
        peak_power=10 * np.log10(peaks[0].power + 1e-20) if peaks else None,
        noise_floor_db=noise_floor.noise_floor_db,
        signal_power_db=snr_result.signal_power_db,
        snr_db=snr_result.snr_db,
        lower_signal_frequency=signal_regions[0].lower_frequency if signal_regions else None,
        upper_signal_frequency=signal_regions[0].upper_frequency if signal_regions else None,
        occupied_bandwidth=bw_results.get("occupied_bandwidth"),
        bandwidth_90=bw_results.get("bw_90"),
        bandwidth_95=bw_results.get("bw_95"),
        bandwidth_99=bw_results.get("bw_99"),
        minus_3db_bandwidth=bw_results.get("minus_3db_bandwidth"),
        spectral_centroid=moments["centroid"],
        spectral_spread=moments["spread"],
        spectral_entropy=spectral_features.spectral_entropy,
        spectral_flatness=spectral_features.spectral_flatness,
        number_of_detected_peaks=len(peaks),
    )

    # Step 16: Classification (optional)
    monitor.start("classification")
    classification = None
    if config.classifier.enabled:
        classifier = ModulationClassifier(config.classifier)
        classification = predict_single(
            processed_iq,
            final_sample_rate,
            classifier=classifier,
            feature_config=config.features,
        )
        warnings.extend(classification.warnings)
    monitor.stop("classification")

    # Step 17: Quality score
    monitor.start("quality_score")
    quality_score = None
    if config.quality_score.enabled:
        quality_score = compute_signal_quality(
            time_domain=time_domain,
            freq_domain=freq_domain,
            inst_params=inst_params,
            snr_result=snr_result,
            sample_rate=final_sample_rate,
            config=config.quality_score,
        )
    monitor.stop("quality_score")

    # Build final result
    processing_time = time.perf_counter() - start_time

    result = AnalysisResult(
        signal_metadata=metadata,
        preprocessing_metadata=prep_metadata,
        analysis_timestamp=datetime.now(),
        software_version="0.1.0",
        configuration_used=config.__dict__ if hasattr(config, '__dict__') else {},
        time_domain=time_domain,
        frequency_domain=freq_domain,
        instantaneous=inst_params,
        spectral_features=spectral_features,
        detected_peaks=peaks,
        signal_regions=signal_regions,
        noise_floor=noise_floor,
        snr_result=snr_result,
        classification=classification,
        quality_score=quality_score,
        iq_data=processed_iq,
        fft_result=fft_result,
        psd_result=psd_result,
        warnings=warnings,
        processing_time_seconds=processing_time,
    )

    logger.info(f"Analysis complete in {processing_time:.3f}s")
    return result