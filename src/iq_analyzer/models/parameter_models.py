"""Additional parameter models for the analyzer."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import numpy as np


@dataclass
class FFTResult:
    """FFT analysis result."""

    frequencies: np.ndarray
    magnitude_spectrum: np.ndarray
    power_spectrum: np.ndarray
    phase_spectrum: np.ndarray
    fft_size: int
    sample_rate: float
    window_used: str

    def to_dict(self) -> dict:
        return {
            "frequencies": self.frequencies.tolist(),
            "magnitude_spectrum": self.magnitude_spectrum.tolist(),
            "power_spectrum": self.power_spectrum.tolist(),
            "phase_spectrum": self.phase_spectrum.tolist(),
            "fft_size": self.fft_size,
            "sample_rate": self.sample_rate,
            "window_used": self.window_used,
        }


@dataclass
class PSDResult:
    """PSD analysis result."""

    frequencies: np.ndarray
    psd: np.ndarray
    psd_db: np.ndarray
    sample_rate: float
    nperseg: int
    noverlap: int
    window_used: str
    method: str

    def to_dict(self) -> dict:
        return {
            "frequencies": self.frequencies.tolist(),
            "psd": self.psd.tolist(),
            "psd_db": self.psd_db.tolist(),
            "sample_rate": self.sample_rate,
            "nperseg": self.nperseg,
            "noverlap": self.noverlap,
            "window_used": self.window_used,
            "method": self.method,
        }


@dataclass
class SpectrogramResult:
    """Spectrogram analysis result."""

    frequencies: np.ndarray
    times: np.ndarray
    spectrogram: np.ndarray
    sample_rate: float
    nperseg: int
    noverlap: int
    window_used: str

    def to_dict(self) -> dict:
        return {
            "frequencies": self.frequencies.tolist(),
            "times": self.times.tolist(),
            "spectrogram": self.spectrogram.tolist(),
            "sample_rate": self.sample_rate,
            "nperseg": self.nperseg,
            "noverlap": self.noverlap,
            "window_used": self.window_used,
        }


@dataclass
class ConstellationResult:
    """Constellation analysis result."""

    I: np.ndarray
    Q: np.ndarray
    normalized_I: Optional[np.ndarray] = None
    normalized_Q: Optional[np.ndarray] = None
    centroid_I: float = 0.0
    centroid_Q: float = 0.0
    radius_mean: float = 0.0
    radius_std: float = 0.0
    phase_mean: float = 0.0
    phase_std: float = 0.0
    num_points: int = 0

    def to_dict(self) -> dict:
        return {
            "I": self.I.tolist(),
            "Q": self.Q.tolist(),
            "normalized_I": self.normalized_I.tolist() if self.normalized_I is not None else None,
            "normalized_Q": self.normalized_Q.tolist() if self.normalized_Q is not None else None,
            "centroid_I": self.centroid_I,
            "centroid_Q": self.centroid_Q,
            "radius_mean": self.radius_mean,
            "radius_std": self.radius_std,
            "phase_mean": self.phase_mean,
            "phase_std": self.phase_std,
            "num_points": self.num_points,
        }


@dataclass
class IQImpairmentResult:
    """I/Q impairment analysis result."""

    dc_offset_I: float
    dc_offset_Q: float
    amplitude_imbalance_db: float
    phase_imbalance_deg: float
    image_rejection_db: Optional[float] = None
    clipping_detected: bool = False
    clipping_percentage: float = 0.0
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "dc_offset_I": self.dc_offset_I,
            "dc_offset_Q": self.dc_offset_Q,
            "amplitude_imbalance_db": self.amplitude_imbalance_db,
            "phase_imbalance_deg": self.phase_imbalance_deg,
            "image_rejection_db": self.image_rejection_db,
            "clipping_detected": self.clipping_detected,
            "clipping_percentage": self.clipping_percentage,
            "warnings": self.warnings,
        }