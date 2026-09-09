"""Signal quality assessment."""

import numpy as np
from typing import Optional, Dict, Any
from dataclasses import dataclass
from ..models import SignalQualityResult, TimeDomainParameters, FrequencyDomainParameters, InstantaneousParameters, SNRResult
from ..dsp import compute_spectral_entropy, compute_spectral_flatness
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class QualityScoreConfig:
    """Configuration for signal quality scoring."""

    enabled: bool = True
    weights: Dict[str, float] = None
    snr_thresholds_db: list = None
    frequency_stability_thresholds_ppm: list = None

    def __post_init__(self):
        if self.weights is None:
            self.weights = {
                "snr": 0.30,
                "frequency_stability": 0.25,
                "amplitude_stability": 0.20,
                "spectral_quality": 0.15,
                "noise": 0.10,
            }
        if self.snr_thresholds_db is None:
            self.snr_thresholds_db = [0, 10, 20, 30, 40]
        if self.frequency_stability_thresholds_ppm is None:
            self.frequency_stability_thresholds_ppm = [1000, 100, 10, 1, 0.1]


def normalize_score(value: float, thresholds: list, higher_is_better: bool = True) -> float:
    """
    Normalize a value to 0-100 scale based on thresholds.

    Args:
        value: Value to normalize
        thresholds: List of threshold values defining quality levels
        higher_is_better: Whether higher values are better

    Returns:
        Score from 0-100
    """
    if len(thresholds) < 2:
        return 50.0

    if higher_is_better:
        if value <= thresholds[0]:
            return 0.0
        if value >= thresholds[-1]:
            return 100.0

        # Find interval
        for i in range(len(thresholds) - 1):
            if thresholds[i] <= value <= thresholds[i + 1]:
                # Linear interpolation
                t = (value - thresholds[i]) / (thresholds[i + 1] - thresholds[i])
                return (i + t) * 100 / (len(thresholds) - 1)

        return 50.0
    else:
        # Lower is better
        if value <= thresholds[0]:
            return 100.0
        if value >= thresholds[-1]:
            return 0.0

        for i in range(len(thresholds) - 1):
            if thresholds[i] <= value <= thresholds[i + 1]:
                t = (value - thresholds[i]) / (thresholds[i + 1] - thresholds[i])
                return (1 - t) * 100 + i * 100 / (len(thresholds) - 1)

        return 50.0


def compute_snr_score(snr_db: Optional[float], config: QualityScoreConfig) -> float:
    """Compute SNR component score (0-100)."""
    if snr_db is None:
        return 0.0
    return normalize_score(snr_db, config.snr_thresholds_db, higher_is_better=True)


def compute_frequency_stability_score(
    inst_params: Optional[InstantaneousParameters],
    sample_rate: float,
    config: QualityScoreConfig,
) -> float:
    """Compute frequency stability component score (0-100)."""
    if inst_params is None or inst_params.instantaneous_frequency_std is None:
        return 0.0

    freq_std = inst_params.instantaneous_frequency_std
    # Convert to ppm relative to center frequency
    center_freq = inst_params.instantaneous_frequency_mean or (sample_rate / 4)
    if center_freq > 0:
        stability_ppm = (freq_std / center_freq) * 1e6
    else:
        stability_ppm = 1000  # Default poor

    return normalize_score(stability_ppm, config.frequency_stability_thresholds_ppm, higher_is_better=False)


def compute_amplitude_stability_score(
    time_domain: Optional[TimeDomainParameters],
) -> float:
    """Compute amplitude stability component score (0-100)."""
    if time_domain is None:
        return 0.0

    # Use coefficient of variation of amplitude
    if time_domain.amplitude_mean > 0:
        cv = time_domain.amplitude_std / time_domain.amplitude_mean
    else:
        cv = 1.0

    # Lower CV is better (more stable)
    # Thresholds for CV: [0.01, 0.05, 0.1, 0.2, 0.5]
    cv_thresholds = [0.01, 0.05, 0.1, 0.2, 0.5]
    return normalize_score(cv, cv_thresholds, higher_is_better=False)


def compute_spectral_quality_score(
    freq_domain: Optional[FrequencyDomainParameters],
) -> float:
    """Compute spectral quality component score (0-100)."""
    if freq_domain is None:
        return 0.0

    # Use spectral entropy and flatness
    entropy = freq_domain.spectral_entropy or 0.5
    flatness = freq_domain.spectral_flatness or 0.5

    # For modulated signals, moderate entropy is good
    # Too low = pure tone, too high = noise
    # Ideal range depends on modulation type
    # We'll use a heuristic: entropy around 0.3-0.7 is good
    if entropy < 0.1:
        entropy_score = 20  # Too tonal
    elif entropy > 0.9:
        entropy_score = 20  # Too noisy
    else:
        entropy_score = 100 - abs(entropy - 0.5) * 200  # Peak at 0.5

    # Flatness: lower is better for modulated signals (more structured)
    flatness_score = 100 - flatness * 100

    return max(0, min(100, (entropy_score + flatness_score) / 2))


def compute_noise_score(
    snr_result: Optional[SNRResult],
    freq_domain: Optional[FrequencyDomainParameters],
) -> float:
    """Compute noise component score (0-100)."""
    if snr_result is None:
        return 0.0

    # Use SNR-based score
    snr_db = snr_result.snr_db
    if snr_db is None:
        return 0.0

    # Higher SNR = lower noise = better score
    if snr_db >= 30:
        return 100
    elif snr_db >= 20:
        return 80
    elif snr_db >= 10:
        return 60
    elif snr_db >= 0:
        return 40
    else:
        return 20


def compute_signal_quality(
    time_domain: Optional[TimeDomainParameters] = None,
    freq_domain: Optional[FrequencyDomainParameters] = None,
    inst_params: Optional[InstantaneousParameters] = None,
    snr_result: Optional[SNRResult] = None,
    sample_rate: float = 1e6,
    config: Optional[QualityScoreConfig] = None,
) -> SignalQualityResult:
    """
    Compute overall signal quality score.

    Args:
        time_domain: Time domain parameters
        freq_domain: Frequency domain parameters
        inst_params: Instantaneous parameters
        snr_result: SNR result
        sample_rate: Sample rate in Hz
        config: Quality score configuration

    Returns:
        SignalQualityResult with overall and component scores
    """
    if config is None:
        config = QualityScoreConfig()

    # Compute component scores
    snr_score = compute_snr_score(snr_result.snr_db if snr_result else None, config)
    freq_stability_score = compute_frequency_stability_score(inst_params, sample_rate, config)
    amp_stability_score = compute_amplitude_stability_score(time_domain)
    spectral_quality_score = compute_spectral_quality_score(freq_domain)
    noise_score = compute_noise_score(snr_result, freq_domain)

    # Weighted overall score
    weights = config.weights
    overall = (
        weights.get("snr", 0) * snr_score +
        weights.get("frequency_stability", 0) * freq_stability_score +
        weights.get("amplitude_stability", 0) * amp_stability_score +
        weights.get("spectral_quality", 0) * spectral_quality_score +
        weights.get("noise", 0) * noise_score
    )

    # Generate explanation
    components = {
        "SNR": snr_score,
        "Frequency Stability": freq_stability_score,
        "Amplitude Stability": amp_stability_score,
        "Spectral Quality": spectral_quality_score,
        "Noise": noise_score,
    }

    # Find lowest components
    sorted_components = sorted(components.items(), key=lambda x: x[1])
    worst = sorted_components[0]
    second_worst = sorted_components[1] if len(sorted_components) > 1 else None

    if overall >= 80:
        explanation = "Excellent signal quality."
    elif overall >= 60:
        explanation = f"Good signal quality. Main limitation: {worst[0]} ({worst[1]:.0f}/100)."
    elif overall >= 40:
        explanation = f"Fair signal quality. Primary issues: {worst[0]} ({worst[1]:.0f}/100)"
        if second_worst:
            explanation += f" and {second_worst[0]} ({second_worst[1]:.0f}/100)."
        else:
            explanation += "."
    else:
        explanation = f"Poor signal quality. Main problems: {worst[0]} ({worst[1]:.0f}/100)"
        if second_worst:
            explanation += f" and {second_worst[0]} ({second_worst[1]:.0f}/100)."
        else:
            explanation += "."

    component_details = {
        "snr": {"raw": snr_result.snr_db if snr_result else None, "score": snr_score, "weight": weights.get("snr", 0)},
        "frequency_stability": {"raw": inst_params.instantaneous_frequency_std if inst_params else None, "score": freq_stability_score, "weight": weights.get("frequency_stability", 0)},
        "amplitude_stability": {"raw": time_domain.amplitude_std if time_domain else None, "score": amp_stability_score, "weight": weights.get("amplitude_stability", 0)},
        "spectral_quality": {"raw": {"entropy": freq_domain.spectral_entropy, "flatness": freq_domain.spectral_flatness} if freq_domain else None, "score": spectral_quality_score, "weight": weights.get("spectral_quality", 0)},
        "noise": {"raw": snr_result.noise_power_db if snr_result else None, "score": noise_score, "weight": weights.get("noise", 0)},
    }

    return SignalQualityResult(
        overall_score=overall,
        snr_score=snr_score,
        frequency_stability_score=freq_stability_score,
        amplitude_stability_score=amp_stability_score,
        spectral_quality_score=spectral_quality_score,
        noise_score=noise_score,
        explanation=explanation,
        component_details=component_details,
    )