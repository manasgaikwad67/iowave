#!/usr/bin/env python
"""Generate synthetic modulation dataset for training."""

import argparse
import sys
import json
from pathlib import Path
import numpy as np
from scipy import signal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from iq_analyzer.models import ModulationType
from iq_analyzer.utils import get_logger

logger = get_logger(__name__)


def generate_noise(duration, sample_rate, snr_db=None):
    """Generate AWGN noise."""
    n_samples = int(duration * sample_rate)
    noise = np.random.randn(n_samples) + 1j * np.random.randn(n_samples)
    noise = noise / np.sqrt(2)  # Unit variance
    return noise


def generate_am(duration, sample_rate, carrier_freq, mod_freq, mod_index=0.5):
    """Generate AM signal."""
    n_samples = int(duration * sample_rate)
    t = np.arange(n_samples) / sample_rate

    carrier = np.exp(1j * 2 * np.pi * carrier_freq * t)
    modulator = 1 + mod_index * np.cos(2 * np.pi * mod_freq * t)

    signal = modulator * carrier
    return signal


def generate_fm(duration, sample_rate, carrier_freq, mod_freq, freq_dev):
    """Generate FM signal."""
    n_samples = int(duration * sample_rate)
    t = np.arange(n_samples) / sample_rate

    # Frequency modulation: phase = 2π * ∫f(t)dt
    # f(t) = carrier_freq + freq_dev * cos(2π * mod_freq * t)
    # phase = 2π * carrier_freq * t + (freq_dev/mod_freq) * sin(2π * mod_freq * t)
    mod_index = freq_dev / mod_freq
    phase = 2 * np.pi * carrier_freq * t + mod_index * np.sin(2 * np.pi * mod_freq * t)

    signal = np.exp(1j * phase)
    return signal


def generate_pm(duration, sample_rate, carrier_freq, mod_freq, phase_dev):
    """Generate PM signal."""
    n_samples = int(duration * sample_rate)
    t = np.arange(n_samples) / sample_rate

    phase = 2 * np.pi * carrier_freq * t + phase_dev * np.cos(2 * np.pi * mod_freq * t)
    signal = np.exp(1j * phase)
    return signal


def generate_bpsk(duration, sample_rate, carrier_freq, symbol_rate):
    """Generate BPSK signal."""
    n_samples = int(duration * sample_rate)
    t = np.arange(n_samples) / sample_rate

    # Generate random symbols
    n_symbols = int(duration * symbol_rate) + 1
    symbols = np.random.choice([-1, 1], n_symbols)

    # Pulse shaping (rectangular for simplicity)
    samples_per_symbol = int(sample_rate / symbol_rate)
    signal = np.zeros(n_samples, dtype=complex)

    for i, sym in enumerate(symbols):
        start = i * samples_per_symbol
        end = min(start + samples_per_symbol, n_samples)
        if start < n_samples:
            signal[start:end] = sym

    # Modulate to carrier
    carrier = np.exp(1j * 2 * np.pi * carrier_freq * t)
    signal = signal * carrier

    return signal


def generate_qpsk(duration, sample_rate, carrier_freq, symbol_rate):
    """Generate QPSK signal."""
    n_samples = int(duration * sample_rate)
    t = np.arange(n_samples) / sample_rate

    # Generate random QPSK symbols
    n_symbols = int(duration * symbol_rate) + 1
    symbols = np.random.choice([1+1j, 1-1j, -1+1j, -1-1j], n_symbols) / np.sqrt(2)

    # Pulse shaping
    samples_per_symbol = int(sample_rate / symbol_rate)
    signal = np.zeros(n_samples, dtype=complex)

    for i, sym in enumerate(symbols):
        start = i * samples_per_symbol
        end = min(start + samples_per_symbol, n_samples)
        if start < n_samples:
            signal[start:end] = sym

    # Modulate to carrier
    carrier = np.exp(1j * 2 * np.pi * carrier_freq * t)
    signal = signal * carrier

    return signal


def generate_8psk(duration, sample_rate, carrier_freq, symbol_rate):
    """Generate 8PSK signal."""
    n_samples = int(duration * sample_rate)
    t = np.arange(n_samples) / sample_rate

    # 8PSK constellation points
    phases = np.exp(1j * 2 * np.pi * np.arange(8) / 8)

    n_symbols = int(duration * symbol_rate) + 1
    symbols = np.random.choice(phases, n_symbols)

    samples_per_symbol = int(sample_rate / symbol_rate)
    signal = np.zeros(n_samples, dtype=complex)

    for i, sym in enumerate(symbols):
        start = i * samples_per_symbol
        end = min(start + samples_per_symbol, n_samples)
        if start < n_samples:
            signal[start:end] = sym

    carrier = np.exp(1j * 2 * np.pi * carrier_freq * t)
    signal = signal * carrier

    return signal


def generate_fsk(duration, sample_rate, carrier_freq, symbol_rate, freq_sep):
    """Generate 2FSK signal."""
    n_samples = int(duration * sample_rate)
    t = np.arange(n_samples) / sample_rate

    n_symbols = int(duration * symbol_rate) + 1
    symbols = np.random.choice([0, 1], n_symbols)

    samples_per_symbol = int(sample_rate / symbol_rate)
    freq0 = carrier_freq - freq_sep / 2
    freq1 = carrier_freq + freq_sep / 2

    signal = np.zeros(n_samples, dtype=complex)

    for i, sym in enumerate(symbols):
        start = i * samples_per_symbol
        end = min(start + samples_per_symbol, n_samples)
        if start < n_samples:
            f = freq0 if sym == 0 else freq1
            signal[start:end] = np.exp(1j * 2 * np.pi * f * t[start:end])

    return signal


def generate_16qam(duration, sample_rate, carrier_freq, symbol_rate):
    """Generate 16QAM signal."""
    n_samples = int(duration * sample_rate)
    t = np.arange(n_samples) / sample_rate

    # 16QAM constellation (normalized)
    constellation = np.array([
        -3-3j, -3-1j, -3+1j, -3+3j,
        -1-3j, -1-1j, -1+1j, -1+3j,
        1-3j, 1-1j, 1+1j, 1+3j,
        3-3j, 3-1j, 3+1j, 3+3j,
    ]) / np.sqrt(10)  # Normalize to unit average power

    n_symbols = int(duration * symbol_rate) + 1
    symbols = np.random.choice(constellation, n_symbols)

    samples_per_symbol = int(sample_rate / symbol_rate)
    signal = np.zeros(n_samples, dtype=complex)

    for i, sym in enumerate(symbols):
        start = i * samples_per_symbol
        end = min(start + samples_per_symbol, n_samples)
        if start < n_samples:
            signal[start:end] = sym

    carrier = np.exp(1j * 2 * np.pi * carrier_freq * t)
    signal = signal * carrier

    return signal


def add_noise(signal, snr_db):
    """Add AWGN to achieve target SNR."""
    signal_power = np.mean(np.abs(signal)**2)
    noise_power = signal_power / (10**(snr_db/10))
    noise = np.sqrt(noise_power/2) * (np.random.randn(*signal.shape) + 1j * np.random.randn(*signal.shape))
    return signal + noise


def apply_impairments(signal, sample_rate, freq_offset=0, phase_offset=0, iq_imbalance=0):
    """Apply realistic impairments."""
    n_samples = len(signal)
    t = np.arange(n_samples) / sample_rate

    # Frequency offset
    if freq_offset != 0:
        signal = signal * np.exp(1j * 2 * np.pi * freq_offset * t)

    # Phase offset
    if phase_offset != 0:
        signal = signal * np.exp(1j * phase_offset)

    # I/Q amplitude imbalance
    if iq_imbalance != 0:
        I = np.real(signal)
        Q = np.imag(signal)
        I = I * (1 + iq_imbalance)
        signal = I + 1j * Q

    return signal


def save_iq_file(signal, filepath, dtype="int16"):
    """Save IQ signal to raw binary file."""
    # Normalize to [-1, 1] range
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val

    # Convert to specified dtype
    if dtype == "int16":
        data = np.int16(signal.real * 32767) + 1j * np.int16(signal.imag * 32767)
        # Interleave I/Q
        interleaved = np.empty(len(data) * 2, dtype=np.int16)
        interleaved[0::2] = np.int16(data.real)
        interleaved[1::2] = np.int16(data.imag)
        interleaved.tofile(filepath)
    elif dtype == "float32":
        interleaved = np.empty(len(signal) * 2, dtype=np.float32)
        interleaved[0::2] = signal.real.astype(np.float32)
        interleaved[1::2] = signal.imag.astype(np.float32)
        interleaved.tofile(filepath)
    else:
        raise ValueError(f"Unsupported dtype: {dtype}")


def generate_dataset(
    output_dir: Path,
    num_samples_per_class: int = 100,
    sample_rates: list = None,
    durations: list = None,
    snr_range: tuple = (-5, 30),
    seed: int = 42,
):
    """
    Generate synthetic modulation dataset.

    Args:
        output_dir: Output directory
        num_samples_per_class: Number of samples per modulation type
        sample_rates: List of sample rates to use
        durations: List of durations to use
        snr_range: (min, max) SNR in dB
        seed: Random seed
    """
    np.random.seed(seed)

    if sample_rates is None:
        sample_rates = [1000000, 2000000, 5000000]  # 1, 2, 5 MHz
    if durations is None:
        durations = [0.01, 0.02, 0.05]  # 10, 20, 50 ms

    modulation_types = [
        ModulationType.NOISE,
        ModulationType.AM,
        ModulationType.FM,
        ModulationType.PM,
        ModulationType.BPSK,
        ModulationType.QPSK,
        ModulationType.PSK8,
        ModulationType.FSK,
        ModulationType.QAM16,
    ]

    generators = {
        ModulationType.NOISE: lambda duration, sample_rate, carrier_freq, snr_db, **kwargs: add_noise(generate_noise(duration, sample_rate), snr_db) if snr_db < 100 else generate_noise(duration, sample_rate),
        ModulationType.AM: lambda duration, sample_rate, carrier_freq, **kwargs: generate_am(duration, sample_rate, carrier_freq, **kwargs),
        ModulationType.FM: lambda duration, sample_rate, carrier_freq, **kwargs: generate_fm(duration, sample_rate, carrier_freq, **kwargs),
        ModulationType.PM: lambda duration, sample_rate, carrier_freq, **kwargs: generate_pm(duration, sample_rate, carrier_freq, **kwargs),
        ModulationType.BPSK: lambda duration, sample_rate, carrier_freq, **kwargs: generate_bpsk(duration, sample_rate, carrier_freq, **kwargs),
        ModulationType.QPSK: lambda duration, sample_rate, carrier_freq, **kwargs: generate_qpsk(duration, sample_rate, carrier_freq, **kwargs),
        ModulationType.PSK8: lambda duration, sample_rate, carrier_freq, **kwargs: generate_8psk(duration, sample_rate, carrier_freq, **kwargs),
        ModulationType.FSK: lambda duration, sample_rate, carrier_freq, **kwargs: generate_fsk(duration, sample_rate, carrier_freq, **kwargs),
        ModulationType.QAM16: lambda duration, sample_rate, carrier_freq, **kwargs: generate_16qam(duration, sample_rate, carrier_freq, **kwargs),
    }

    # Generator parameters
    gen_params = {
        ModulationType.NOISE: {},
        ModulationType.AM: {"mod_freq": 1000, "mod_index": 0.5},
        ModulationType.FM: {"mod_freq": 1000, "freq_dev": 5000},
        ModulationType.PM: {"mod_freq": 1000, "phase_dev": np.pi/4},
        ModulationType.BPSK: {"symbol_rate": 10000},
        ModulationType.QPSK: {"symbol_rate": 10000},
        ModulationType.PSK8: {"symbol_rate": 10000},
        ModulationType.FSK: {"symbol_rate": 10000, "freq_sep": 20000},
        ModulationType.QAM16: {"symbol_rate": 10000},
    }

    output_dir.mkdir(parents=True, exist_ok=True)

    total_generated = 0

    for mod_type in modulation_types:
        class_dir = output_dir / mod_type.value
        class_dir.mkdir(exist_ok=True)

        print(f"Generating {mod_type.value}...")

        for i in range(num_samples_per_class):
            # Randomize parameters
            sample_rate = np.random.choice(sample_rates)
            duration = np.random.choice(durations)
            carrier_freq = np.random.uniform(0.1 * sample_rate, 0.4 * sample_rate)
            snr_db = np.random.uniform(snr_range[0], snr_range[1])

            # Generate signal
            params = gen_params[mod_type].copy()
            params.update({
                "duration": duration,
                "sample_rate": sample_rate,
                "carrier_freq": carrier_freq,
                "snr_db": snr_db,
            })

            try:
                sig = generators[mod_type](**params)

                # Add impairments
                freq_offset = np.random.uniform(-0.001 * sample_rate, 0.001 * sample_rate)
                phase_offset = np.random.uniform(-np.pi, np.pi)
                iq_imbalance = np.random.uniform(-0.1, 0.1)

                sig = apply_impairments(sig, sample_rate, freq_offset, phase_offset, iq_imbalance)

                # Add noise
                if mod_type != ModulationType.NOISE and snr_db < 50:
                    sig = add_noise(sig, snr_db)

                # Save
                filename = f"{mod_type.value}_{i:04d}_fs{sample_rate/1e6:.1f}MHz_fc{carrier_freq/1e6:.3f}MHz_snr{snr_db:.1f}dB.iq"
                filepath = class_dir / filename
                save_iq_file(sig, filepath, "int16")

                # Save metadata
                meta = {
                    "modulation": mod_type.value,
                    "sample_rate": sample_rate,
                    "duration": duration,
                    "carrier_freq": carrier_freq,
                    "snr_db": snr_db,
                    "freq_offset": freq_offset,
                    "phase_offset": phase_offset,
                    "iq_imbalance": iq_imbalance,
                    "dtype": "int16",
                    "endianness": "little",
                    "iq_layout": "interleaved",
                }
                meta_file = filepath.with_suffix(".json")
                with open(meta_file, "w") as f:
                    json.dump(meta, f, indent=2)

                total_generated += 1

            except Exception as e:
                logger.warning(f"Failed to generate sample {i}: {e}")

    print(f"\nGenerated {total_generated} samples in {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic modulation dataset")
    parser.add_argument("output_dir", type=Path, help="Output directory")
    parser.add_argument("--samples-per-class", type=int, default=100, help="Samples per modulation type")
    parser.add_argument("--sample-rates", type=float, nargs="+", default=[1e6, 2e6, 5e6], help="Sample rates (Hz)")
    parser.add_argument("--durations", type=float, nargs="+", default=[0.01, 0.02, 0.05], help="Durations (s)")
    parser.add_argument("--snr-min", type=float, default=-5, help="Minimum SNR (dB)")
    parser.add_argument("--snr-max", type=float, default=30, help="Maximum SNR (dB)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args()

    generate_dataset(
        output_dir=args.output_dir,
        num_samples_per_class=args.samples_per_class,
        sample_rates=args.sample_rates,
        durations=args.durations,
        snr_range=(args.snr_min, args.snr_max),
        seed=args.seed,
    )


if __name__ == "__main__":
    main()