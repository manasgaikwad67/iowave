"""Signal metadata data model."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List


@dataclass
class SignalMetadata:
    """Metadata extracted from signal file."""

    filename: str
    file_path: str
    extension: str
    format: str  # "wav", "raw_iq", "unknown"
    sample_rate: float
    num_samples: int
    duration: float
    num_channels: int
    data_type: str  # e.g., "int16", "float32", "int8"
    bit_depth: int
    iq_format: str  # "interleaved", "separate_channels", "unknown"
    endianness: str  # "little", "big", "unknown"
    scale_factor: float = 1.0
    center_frequency: Optional[float] = None
    timestamp: Optional[datetime] = None
    source_info: str = ""
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate metadata after initialization."""
        if self.sample_rate <= 0:
            self.warnings.append(f"Invalid sample rate: {self.sample_rate}")
        if self.num_samples <= 0:
            self.warnings.append(f"Invalid number of samples: {self.num_samples}")
        if self.num_channels <= 0:
            self.warnings.append(f"Invalid number of channels: {self.num_channels}")
        if self.duration <= 0:
            self.warnings.append(f"Invalid duration: {self.duration}")

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "filename": self.filename,
            "file_path": self.file_path,
            "extension": self.extension,
            "format": self.format,
            "sample_rate": self.sample_rate,
            "num_samples": self.num_samples,
            "duration": self.duration,
            "num_channels": self.num_channels,
            "data_type": self.data_type,
            "bit_depth": self.bit_depth,
            "iq_format": self.iq_format,
            "endianness": self.endianness,
            "scale_factor": self.scale_factor,
            "center_frequency": self.center_frequency,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "source_info": self.source_info,
            "warnings": self.warnings,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SignalMetadata":
        """Create from dictionary."""
        timestamp = None
        if data.get("timestamp"):
            timestamp = datetime.fromisoformat(data["timestamp"])
        return cls(
            filename=data["filename"],
            file_path=data["file_path"],
            extension=data["extension"],
            format=data["format"],
            sample_rate=data["sample_rate"],
            num_samples=data["num_samples"],
            duration=data["duration"],
            num_channels=data["num_channels"],
            data_type=data["data_type"],
            bit_depth=data["bit_depth"],
            iq_format=data["iq_format"],
            endianness=data["endianness"],
            scale_factor=data.get("scale_factor", 1.0),
            center_frequency=data.get("center_frequency"),
            timestamp=timestamp,
            source_info=data.get("source_info", ""),
            warnings=data.get("warnings", []),
        )


@dataclass
class PreprocessingMetadata:
    """Metadata about preprocessing operations applied."""

    dc_removed: bool = False
    normalized: bool = False
    filter_applied: bool = False
    filter_type: Optional[str] = None
    low_cut: Optional[float] = None
    high_cut: Optional[float] = None
    resampled: bool = False
    original_sample_rate: Optional[float] = None
    final_sample_rate: Optional[float] = None
    number_of_samples_removed: int = 0
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "dc_removed": self.dc_removed,
            "normalized": self.normalized,
            "filter_applied": self.filter_applied,
            "filter_type": self.filter_type,
            "low_cut": self.low_cut,
            "high_cut": self.high_cut,
            "resampled": self.resampled,
            "original_sample_rate": self.original_sample_rate,
            "final_sample_rate": self.final_sample_rate,
            "number_of_samples_removed": self.number_of_samples_removed,
            "warnings": self.warnings,
        }