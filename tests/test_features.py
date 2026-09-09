"""Tests for feature extraction."""

import pytest
import numpy as np

from iq_analyzer.features.feature_extractor import (
    extract_features,
    extract_temporal_features,
    extract_spectral_features,
    extract_modulation_features,
    extract_constellation_features,
    FeatureConfig,
)
from iq_analyzer.models import TimeDomainParameters, FrequencyDomainParameters, InstantaneousParameters


def generate_test_signal(mod_type, sample_rate=1e6, duration=0.01):
    """Generate test signals for different modulation types."""
    n_samples = int(sample_rate * duration)
    t = np.arange(n_samples) / sample_rate

    if mod_type == "BPSK":
        # BPSK
        symbol_rate = 10000
        n_symbols = int(duration * symbol_rate) + 1
        symbols = np.random.choice([-1, 1], n_symbols)
        samples_per_symbol = int(sample_rate / symbol_rate)
        signal = np.zeros(n_samples, dtype=complex)
        for i, sym in enumerate(symbols):
            start = i * samples_per_symbol
            end = min(start + samples_per_symbol, n_samples)
            if start < n_samples:
                signal[start:end] = sym
        carrier = np.exp(1j * 2 * np.pi * 100e3 * t)
        signal = signal * carrier

    elif mod_type == "QPSK":
        # QPSK
        symbol_rate = 10000
        n_symbols = int(duration * symbol_rate) + 1
        symbols = np.random.choice([1+1j, 1-1j, -1+1j, -1-1j], n_symbols) / np.sqrt(2)
        samples_per_symbol = int(sample_rate / symbol_rate)
        signal = np.zeros(n_samples, dtype=complex)
        for i, sym in enumerate(symbols):
            start = i * samples_per_symbol
            end = min(start + samples_per_symbol, n_samples)
            if start < n_samples:
                signal[start:end] = sym
        carrier = np.exp(1j * 2 * np.pi * 100e3 * t)
        signal = signal * carrier

    elif mod_type == "FM":
        # FM
        mod_freq = 1000
        freq_dev = 5000
        mod_index = freq_dev / mod_freq
        phase = 2 * np.pi * 100e3 * t + mod_index * np.sin(2 * np.pi * mod_freq * t)
        signal = np.exp(1j * phase)

    else:
        # Default: tone + noise
        signal = np.exp(1j * 2 * np.pi * 100e3 * t) + 0.1 * (np.random.randn(n_samples) + 1j * np.random.randn(n_samples))

    return signal


def test_extract_temporal_features():
    """Test temporal feature extraction."""
    sample_rate = 1e6
    iq_data = generate_test_signal("BPSK", sample_rate)

    features = extract_temporal_features(iq_data, sample_rate)

    assert "mean_I" in features
    assert "mean_Q" in features
    assert "rms_magnitude" in features
    assert "crest_factor" in features
    assert "papr_db" in features
    assert "iq_correlation" in features
    assert "amplitude_skewness" in features
    assert "amplitude_kurtosis" in features


def test_extract_spectral_features():
    """Test spectral feature extraction."""
    sample_rate = 1e6
    iq_data = generate_test_signal("QPSK", sample_rate)

    features = extract_spectral_features(iq_data, sample_rate)

    assert "spectral_centroid" in features
    assert "spectral_spread" in features
    assert "spectral_entropy" in features
    assert "spectral_flatness" in features
    assert "spectral_rolloff" in features
    assert "num_peaks" in features


def test_extract_modulation_features():
    """Test modulation feature extraction."""
    sample_rate = 1e6
    iq_data = generate_test_signal("FM", sample_rate)

    features = extract_modulation_features(iq_data, sample_rate)

    assert "inst_freq_mean" in features
    assert "inst_freq_std" in features
    assert "freq_deviation" in features
    assert "phase_diff_std" in features
    assert "I_zero_crossings" in features


def test_extract_constellation_features():
    """Test constellation feature extraction."""
    sample_rate = 1e6
    iq_data = generate_test_signal("BPSK", sample_rate)

    features = extract_constellation_features(iq_data)

    assert "constellation_centroid_I" in features
    assert "constellation_centroid_Q" in features
    assert "constellation_radius_mean" in features
    assert "constellation_radius_std" in features
    assert "constellation_num_rings" in features


def test_extract_all_features():
    """Test complete feature extraction."""
    sample_rate = 1e6
    iq_data = generate_test_signal("QPSK", sample_rate)

    config = FeatureConfig()
    features = extract_features(iq_data, sample_rate, config=config)

    # Should have features from all categories
    assert len(features) > 30
    assert "crest_factor" in features  # temporal
    assert "spectral_entropy" in features  # spectral
    assert "inst_freq_std" in features  # modulation
    assert "constellation_radius_std" in features  # constellation


def test_feature_config_disabled():
    """Test feature extraction with disabled categories."""
    sample_rate = 1e6
    iq_data = generate_test_signal("BPSK", sample_rate)

    config = FeatureConfig(
        include_temporal=True,
        include_spectral=False,
        include_modulation=False,
        include_constellation=False,
    )
    features = extract_features(iq_data, sample_rate, config=config)

    # Should only have temporal features
    temporal_names = ["mean_I", "mean_Q", "rms_magnitude", "crest_factor", "papr_db"]
    for name in temporal_names:
        assert name in features

    spectral_names = ["spectral_centroid", "spectral_entropy"]
    for name in spectral_names:
        assert name not in features


def test_get_feature_names():
    """Test getting feature names list."""
    config = FeatureConfig()
    names = extract_features.get_feature_names(config) if hasattr(extract_features, 'get_feature_names') else []

    # Use the actual function
    from iq_analyzer.features.feature_extractor import get_feature_names
    names = get_feature_names(config)

    assert len(names) > 0
    assert "crest_factor" in names
    assert "spectral_entropy" in names
