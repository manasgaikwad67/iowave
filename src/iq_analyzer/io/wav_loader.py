"""WAV file loader for IQ and audio signals."""

import wave
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, List
from dataclasses import dataclass
from ..models import SignalMetadata
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class WAVLoadResult:
    """Result of WAV file loading."""

    iq_data: np.ndarray  # Complex IQ samples: I + jQ
    sample_rate: float
    metadata: SignalMetadata
    warnings: List[str]


def load_wav(
    file_path: Path,
    force_iq: bool = False,
    channel_map: Optional[Tuple[int, int]] = None,
) -> WAVLoadResult:
    """
    Load a WAV file and convert to complex IQ data.

    Args:
        file_path: Path to WAV file
        force_iq: Force interpretation as IQ (stereo = I/Q)
        channel_map: Tuple of (I_channel, Q_channel) for multi-channel files

    Returns:
        WAVLoadResult with IQ data and metadata
    """
    path = Path(file_path)
    warnings = []

    try:
        with wave.open(str(path), "rb") as wav:
            n_channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            frame_rate = wav.getframerate()
            n_frames = wav.getnframes()
            comptype = wav.getcomptype()
            compname = wav.getcompname()

            # Read all frames
            raw_frames = wav.readframes(n_frames)
        alaw = False
    except wave.Error:
        n_channels, sample_width, frame_rate, n_frames, raw_frames = _read_alaw_wav(path)
        comptype = "ALAW"
        compname = "G.711 A-law"
        alaw = True

    # Determine data type from sample width
    dtype_map = {
        1: np.int8,
        2: np.int16,
        3: np.int32,  # 24-bit stored as 32-bit
        4: np.int32,
        8: np.float64,
    }
    # Check for float format
    if comptype == "NONE" and compname == "not compressed":
        # Standard PCM
        pass
    elif comptype == "FLOAT":
        dtype_map = {
            4: np.float32,
            8: np.float64,
        }

    if alaw:
        data = _decode_alaw(raw_frames)
        dtype = np.int16
    elif sample_width not in dtype_map:
        warnings.append(f"Unsupported sample width: {sample_width} bytes")
        sample_width = 2  # Default to int16
        dtype = np.int16
    else:
        dtype = dtype_map[sample_width]

    # Convert raw bytes to numpy array
    if alaw:
        pass
    elif sample_width == 3:
        # 24-bit PCM - special handling
        data = _read_24bit_pcm(raw_frames, n_frames, n_channels)
    else:
        data = np.frombuffer(raw_frames, dtype=dtype)

    # Reshape to (n_frames, n_channels)
    if len(data) != n_frames * n_channels:
        warnings.append(f"Frame count mismatch: expected {n_frames * n_channels}, got {len(data)}")
        n_frames = len(data) // n_channels
        data = data[: n_frames * n_channels]

    data = data.reshape(n_frames, n_channels)

    # Convert to float normalized to [-1, 1] for integer types
    if np.issubdtype(dtype, np.integer):
        max_val = np.iinfo(dtype).max
        data = data.astype(np.float64) / max_val
    elif np.issubdtype(dtype, np.floating):
        data = data.astype(np.float64)

    # Convert to IQ
    iq_data, iq_format, iq_warnings = _convert_to_iq(data, n_channels, force_iq, channel_map)
    warnings.extend(iq_warnings)

    # Create metadata
    duration = n_frames / frame_rate
    bit_depth = sample_width * 8

    metadata = SignalMetadata(
        filename=path.name,
        file_path=str(path),
        extension=path.suffix.lower(),
        format="wav",
        sample_rate=float(frame_rate),
        num_samples=n_frames,
        duration=duration,
        num_channels=n_channels,
        data_type=str(dtype),
        bit_depth=bit_depth,
        iq_format=iq_format,
        endianness="little",  # WAV is always little-endian
        scale_factor=1.0,
        warnings=warnings,
    )

    logger.info(f"Loaded WAV: {path.name}, {n_channels}ch, {frame_rate}Hz, {n_frames} frames, IQ format: {iq_format}")

    return WAVLoadResult(
        iq_data=iq_data,
        sample_rate=float(frame_rate),
        metadata=metadata,
        warnings=warnings,
    )


def _read_24bit_pcm(raw_frames: bytes, n_frames: int, n_channels: int) -> np.ndarray:
    """Read 24-bit PCM data."""
    # 24-bit is stored as 3 bytes per sample
    expected_bytes = n_frames * n_channels * 3
    if len(raw_frames) < expected_bytes:
        raw_frames += b"\x00" * (expected_bytes - len(raw_frames))

    # Convert 3-byte samples to 32-bit integers
    data = np.zeros(n_frames * n_channels, dtype=np.int32)
    for i in range(n_frames * n_channels):
        offset = i * 3
        # Little-endian 24-bit to 32-bit
        data[i] = (
            raw_frames[offset]
            | (raw_frames[offset + 1] << 8)
            | (raw_frames[offset + 2] << 16)
        )
        # Sign extend
        if data[i] & 0x800000:
            data[i] |= 0xFF000000

    return data


def _read_alaw_wav(path: Path) -> Tuple[int, int, int, int, bytes]:
    """Read the basic RIFF chunks needed for a G.711 A-law WAV file."""
    raw = path.read_bytes()
    if len(raw) < 12 or raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise wave.Error("not a RIFF/WAVE file")

    fmt = None
    audio = None
    offset = 12
    while offset + 8 <= len(raw):
        chunk_id = raw[offset : offset + 4]
        chunk_size = int.from_bytes(raw[offset + 4 : offset + 8], "little")
        chunk_start = offset + 8
        chunk_end = chunk_start + chunk_size
        if chunk_end > len(raw):
            raise wave.Error("truncated WAV chunk")
        if chunk_id == b"fmt ":
            fmt = raw[chunk_start:chunk_end]
        elif chunk_id == b"data":
            audio = raw[chunk_start:chunk_end]
        offset = chunk_end + (chunk_size & 1)

    if fmt is None or audio is None or len(fmt) < 16:
        raise wave.Error("WAV is missing fmt or data chunk")

    audio_format = int.from_bytes(fmt[0:2], "little")
    if audio_format != 6:
        raise wave.Error(f"unsupported WAV format: {audio_format}")
    n_channels = int.from_bytes(fmt[2:4], "little")
    frame_rate = int.from_bytes(fmt[4:8], "little")
    block_align = int.from_bytes(fmt[12:14], "little")
    n_frames = len(audio) // block_align
    return n_channels, 1, frame_rate, n_frames, audio[: n_frames * block_align]


def _decode_alaw(raw_frames: bytes) -> np.ndarray:
    """Decode G.711 A-law bytes to signed 16-bit PCM samples."""
    encoded = np.frombuffer(raw_frames, dtype=np.uint8)
    value = (encoded ^ 0x55).astype(np.int32)
    segment = (value & 0x70) >> 4
    quantization = value & 0x0F
    shift = np.maximum(segment - 1, 0)
    decoded = np.where(
        segment == 0,
        (quantization << 4) + 8,
        np.where(segment == 1, (quantization << 5) + 0x108, ((quantization << 4) + 0x108) << shift),
    )
    return np.where((value & 0x80) != 0, decoded, -decoded).astype(np.int16)


def _convert_to_iq(
    data: np.ndarray,
    n_channels: int,
    force_iq: bool,
    channel_map: Optional[Tuple[int, int]] = None,
) -> Tuple[np.ndarray, str, List[str]]:
    """Convert multi-channel data to complex IQ."""
    warnings = []

    if n_channels == 1:
        # Mono - treat as real signal, Q = 0
        I = data[:, 0]
        Q = np.zeros_like(I)
        iq_format = "mono_real"
        warnings.append("Mono WAV loaded as real signal (Q=0)")

    elif n_channels == 2:
        # Stereo - could be IQ or left/right audio
        if force_iq or channel_map is not None:
            # User explicitly wants IQ interpretation
            if channel_map:
                i_ch, q_ch = channel_map
                if i_ch >= 2 or q_ch >= 2:
                    warnings.append(f"Invalid channel map {channel_map} for 2-channel file")
                    i_ch, q_ch = 0, 1
            else:
                i_ch, q_ch = 0, 1  # Default: ch0=I, ch1=Q

            I = data[:, i_ch]
            Q = data[:, q_ch]
            iq_format = "stereo_iq"
            warnings.append(f"Stereo WAV interpreted as IQ (ch{i_ch}=I, ch{q_ch}=Q)")
        else:
            # Default: treat as stereo audio, not IQ
            I = data[:, 0]
            Q = data[:, 1]
            iq_format = "stereo_audio"
            warnings.append(
                "Stereo WAV loaded as stereo audio (not IQ). "
                "Use force_iq=True or channel_map to interpret as IQ."
            )

    else:
        # Multi-channel - need channel map
        if channel_map:
            i_ch, q_ch = channel_map
            if i_ch >= n_channels or q_ch >= n_channels:
                warnings.append(f"Invalid channel map {channel_map} for {n_channels}-channel file")
                i_ch, q_ch = 0, 1 if n_channels > 1 else 0
            I = data[:, i_ch]
            Q = data[:, q_ch]
            iq_format = f"multichannel_iq_ch{i_ch}_{q_ch}"
        else:
            # Default to first two channels
            I = data[:, 0]
            Q = data[:, 1] if n_channels > 1 else np.zeros_like(I)
            iq_format = f"multichannel_default_ch0_1"
            warnings.append(f"{n_channels}-channel WAV: using first two channels as I/Q")

    iq_data = I + 1j * Q
    return iq_data, iq_format, warnings


def get_wav_info(file_path: Path) -> dict:
    """Get basic WAV file info without loading all data."""
    with wave.open(str(file_path), "rb") as wav:
        return {
            "n_channels": wav.getnchannels(),
            "sample_width": wav.getsampwidth(),
            "frame_rate": wav.getframerate(),
            "n_frames": wav.getnframes(),
            "comptype": wav.getcomptype(),
            "compname": wav.getcompname(),
            "duration": wav.getnframes() / wav.getframerate(),
        }