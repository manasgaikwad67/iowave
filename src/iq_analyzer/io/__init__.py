"""I/O module for signal file loading."""

from .file_detector import detect_file_type, FileType, DetectionResult, validate_file_readable
from .wav_loader import load_wav, get_wav_info, WAVLoadResult
from .iq_loader import (
    load_raw_iq,
    estimate_iq_params,
    IQFormat,
    Endianness,
    IQLayout,
    IQLoadResult,
)
from .metadata_parser import (
    parse_wav_metadata,
    parse_raw_iq_metadata,
    extract_timestamp_from_filename,
    merge_metadata,
)

__all__ = [
    "detect_file_type",
    "FileType",
    "DetectionResult",
    "validate_file_readable",
    "load_wav",
    "get_wav_info",
    "WAVLoadResult",
    "load_raw_iq",
    "estimate_iq_params",
    "IQFormat",
    "Endianness",
    "IQLayout",
    "IQLoadResult",
    "parse_wav_metadata",
    "parse_raw_iq_metadata",
    "extract_timestamp_from_filename",
    "merge_metadata",
]