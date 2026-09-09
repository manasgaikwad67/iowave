"""Metadata parser for extracting information from signal files."""

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json
from ..models import SignalMetadata
from ..utils import get_logger

logger = get_logger(__name__)


def parse_wav_metadata(file_path: Path) -> Dict[str, Any]:
    """Extract extended metadata from WAV file if available."""
    metadata = {}

    # Try to read INFO chunk
    try:
        import wave
        with wave.open(str(file_path), "rb") as wav:
            # Standard wave module doesn't expose INFO chunk easily
            # This would require more complex parsing
            pass
    except Exception:
        pass

    return metadata


def parse_raw_iq_metadata(file_path: Path) -> Dict[str, Any]:
    """Look for companion metadata files for raw IQ."""
    path = Path(file_path)
    metadata = {}

    # Check for .json metadata file
    json_path = path.with_suffix(".json")
    if json_path.exists():
        try:
            with open(json_path, "r") as f:
                metadata = json.load(f)
            logger.info(f"Loaded metadata from {json_path}")
        except Exception as e:
            logger.warning(f"Failed to load metadata from {json_path}: {e}")

    # Check for .meta file
    meta_path = path.with_suffix(".meta")
    if meta_path.exists():
        try:
            with open(meta_path, "r") as f:
                meta_data = json.load(f)
            metadata.update(meta_data)
        except Exception:
            pass

    return metadata


def extract_timestamp_from_filename(filename: str) -> Optional[datetime]:
    """Try to extract timestamp from filename."""
    # Common patterns: YYYYMMDD_HHMMSS, YYYY-MM-DD_HH-MM-SS, etc.
    import re

    patterns = [
        r"(\d{4})(\d{2})(\d{2})[_-](\d{2})(\d{2})(\d{2})",
        r"(\d{4})-(\d{2})-(\d{2})[_-](\d{2})-(\d{2})-(\d{2})",
        r"(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})",
    ]

    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            try:
                groups = match.groups()
                year, month, day, hour, minute, second = map(int, groups)
                return datetime(year, month, day, hour, minute, second)
            except ValueError:
                continue

    return None


def merge_metadata(
    primary: SignalMetadata,
    secondary: Dict[str, Any],
) -> SignalMetadata:
    """Merge secondary metadata into primary, overwriting only None values."""
    # This is a simple merge - in practice you might want more sophisticated logic
    for key, value in secondary.items():
        if hasattr(primary, key) and getattr(primary, key) is None:
            setattr(primary, key, value)
    return primary