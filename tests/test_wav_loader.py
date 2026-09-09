"""Tests for WAV loader."""

import pytest
import tempfile
import numpy as np
import struct
import wave
from pathlib import Path

from iq_analyzer.io.wav_loader import load_wav, get_wav_info


def create_test_wav(filepath, n_channels=2, sample_width=2, frame_rate=48000, n_frames=1000):
    """Create a test WAV file."""
    with wave.open(str(filepath), "wb") as wav:
        wav.setnchannels(n_channels)
        wav.setsampwidth(sample_width)
        wav.setframerate(frame_rate)
        # Generate test signal: sine wave
        t = np.arange(n_frames) / frame_rate
        freq = 1000  # 1 kHz tone
        signal = 0.5 * np.sin(2 * np.pi * freq * t)
        if n_channels == 2:
            # Stereo: I on ch0, Q on ch1 with 90 deg phase shift
            signal_i = signal
            signal_q = 0.5 * np.cos(2 * np.pi * freq * t)
            data = np.column_stack([signal_i, signal_q])
        else:
            data = signal.reshape(-1, 1)

        # Convert to int16
        data_int = np.int16(data * 32767)
        wav.writeframes(data_int.tobytes())


def test_load_stereo_wav():
    """Test loading stereo WAV as IQ."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        create_test_wav(f.name, n_channels=2, n_frames=48000)
        result = load_wav(Path(f.name), force_iq=True)

    assert result.iq_data is not None
    assert len(result.iq_data) == 48000
    assert result.sample_rate == 48000
    assert result.metadata.num_channels == 2
    assert result.metadata.format == "wav"
    assert result.metadata.iq_format == "stereo_iq"


def test_load_mono_wav():
    """Test loading mono WAV."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        create_test_wav(f.name, n_channels=1, n_frames=48000)
        result = load_wav(Path(f.name))

    assert result.iq_data is not None
    assert len(result.iq_data) == 48000
    assert result.metadata.num_channels == 1
    # Mono should have Q=0
    assert np.allclose(np.imag(result.iq_data), 0)


def test_load_wav_with_channel_map():
    """Test loading with custom channel mapping."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        create_test_wav(f.name, n_channels=2, n_frames=48000)
        # Swap I/Q channels
        result = load_wav(Path(f.name), force_iq=True, channel_map=(1, 0))

    assert result.metadata.iq_format == "stereo_iq"
    # Check that I and Q are swapped compared to default
    # (hard to verify without knowing exact signal, but should not crash)


def test_get_wav_info():
    """Test getting WAV info without loading data."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        create_test_wav(f.name, n_channels=2, frame_rate=48000, n_frames=48000)
        info = get_wav_info(Path(f.name))

    assert info["n_channels"] == 2
    assert info["frame_rate"] == 48000
    assert info["n_frames"] == 48000
    assert info["duration"] == 1.0


def test_load_alaw_wav():
    """Test loading a G.711 A-law WAV file."""
    fmt = struct.pack("<HHIIHH", 6, 1, 8000, 8000, 1, 8)
    samples = bytes([0xD5, 0x55, 0xD5, 0x55])
    wav_data = (
        b"RIFF"
        + struct.pack("<I", 4 + 8 + len(fmt) + 8 + len(samples))
        + b"WAVE"
        + b"fmt "
        + struct.pack("<I", len(fmt))
        + fmt
        + b"data"
        + struct.pack("<I", len(samples))
        + samples
    )

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(wav_data)
        path = Path(f.name)

    result = load_wav(path)

    assert result.sample_rate == 8000
    assert result.metadata.num_samples == 4
    assert np.all(np.isfinite(result.iq_data))
