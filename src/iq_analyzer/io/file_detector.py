"""File type detection."""

from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
import struct


class FileType(Enum):
    """Supported file types."""

    WAV = "wav"
    RAW_IQ = "raw_iq"
    UNKNOWN = "unknown"


@dataclass
class DetectionResult:
    """Result of file type detection."""

    file_type: FileType
    confidence: float  # 0.0 to 1.0
    extension: str
    mime_type: Optional[str] = None
    warnings: List[str] = None
    suggested_params: dict = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.suggested_params is None:
            self.suggested_params = {}


def detect_file_type(file_path: Path) -> DetectionResult:
    """Detect the type of a signal file."""
    path = Path(file_path)
    extension = path.suffix.lower()

    # Check extension first
    if extension == ".wav":
        return _detect_wav(path)
    elif extension in [".iq", ".bin", ".dat", ".raw"]:
        return _detect_raw_iq(path)
    else:
        # Try to detect by content
        return _detect_by_content(path)


def _detect_wav(path: Path) -> DetectionResult:
    """Detect WAV file by reading header."""
    try:
        with open(path, "rb") as f:
            header = f.read(12)
        if len(header) < 12:
            return DetectionResult(
                file_type=FileType.UNKNOWN,
                confidence=0.0,
                extension=path.suffix.lower(),
                warnings=["File too small to be a valid WAV"],
            )

        # Check RIFF header
        if header[:4] != b"RIFF":
            return DetectionResult(
                file_type=FileType.UNKNOWN,
                confidence=0.0,
                extension=path.suffix.lower(),
                warnings=["Missing RIFF header"],
            )

        # Check WAVE format
        if header[8:12] != b"WAVE":
            return DetectionResult(
                file_type=FileType.UNKNOWN,
                confidence=0.0,
                extension=path.suffix.lower(),
                warnings=["Not a WAVE format"],
            )

        return DetectionResult(
            file_type=FileType.WAV,
            confidence=1.0,
            extension=path.suffix.lower(),
            mime_type="audio/wav",
        )
    except Exception as e:
        return DetectionResult(
            file_type=FileType.UNKNOWN,
            confidence=0.0,
            extension=path.suffix.lower(),
            warnings=[f"Error reading file: {e}"],
        )


def _detect_raw_iq(path: Path) -> DetectionResult:
    """Detect raw IQ file (ambiguous binary)."""
    # Raw IQ files have no header - we can only guess by extension
    return DetectionResult(
        file_type=FileType.RAW_IQ,
        confidence=0.7,  # Not certain without metadata
        extension=path.suffix.lower(),
        warnings=[
            "Raw IQ format detected - requires manual configuration of sample rate, "
            "data type, endianness, and IQ layout"
        ],
        suggested_params={
            "sample_rate": 2048000,
            "dtype": "int16",
            "endianness": "little",
            "iq_layout": "interleaved",
        },
    )


def _detect_by_content(path: Path) -> DetectionResult:
    """Try to detect file type by content inspection."""
    try:
        with open(path, "rb") as f:
            header = f.read(512)

        # Check for WAV signature
        if len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WAVE":
            return DetectionResult(
                file_type=FileType.WAV,
                confidence=0.9,
                extension=path.suffix.lower(),
                warnings=["Detected WAV by content despite extension"],
            )

        # Could add more format detection here

        return DetectionResult(
            file_type=FileType.UNKNOWN,
            confidence=0.0,
            extension=path.suffix.lower(),
            warnings=["Unknown file format - no recognized signature"],
        )
    except Exception as e:
        return DetectionResult(
            file_type=FileType.UNKNOWN,
            confidence=0.0,
            extension=path.suffix.lower(),
            warnings=[f"Error reading file: {e}"],
        )


def validate_file_readable(file_path: Path) -> List[str]:
    """Validate that a file exists and is readable."""
    warnings = []
    path = Path(file_path)

    if not path.exists():
        warnings.append(f"File does not exist: {path}")
        return warnings

    if not path.is_file():
        warnings.append(f"Path is not a file: {path}")
        return warnings

    try:
        with open(path, "rb") as f:
            f.read(1)
    except PermissionError:
        warnings.append(f"Permission denied reading file: {path}")
    except Exception as e:
        warnings.append(f"Error reading file: {e}")

    return warnings