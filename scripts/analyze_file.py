#!/usr/bin/env python
"""Command-line script for analyzing signal files."""

import argparse
import sys
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from iq_analyzer.core import analyze_file, PipelineConfig
from iq_analyzer.reporting import generate_report
from iq_analyzer.config import settings


def main():
    parser = argparse.ArgumentParser(
        description="Analyze IQ/WAV signal files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/analyze_file.py signal.wav
  python scripts/analyze_file.py signal.iq --sample-rate 2400000 --dtype int16
  python scripts/analyze_file.py signal.wav --output report.json --save-plots
  python scripts/analyze_file.py signal.iq --no-ml --fft-size 16384
        """
    )

    # File input
    parser.add_argument("file", type=Path, help="Input signal file (WAV or raw IQ)")

    # Raw IQ options
    parser.add_argument("--sample-rate", type=float, help="Sample rate in Hz (required for raw IQ)")
    parser.add_argument("--dtype", choices=["int8", "int16", "int32", "float32", "float64"],
                       default="int16", help="Data type for raw IQ")
    parser.add_argument("--endianness", choices=["little", "big"], default="little",
                       help="Endianness for raw IQ")
    parser.add_argument("--iq-layout", choices=["interleaved", "separate_i_q"], default="interleaved",
                       help="IQ layout for raw IQ")

    # Analysis options
    parser.add_argument("--fft-size", type=int, help="FFT size")
    parser.add_argument("--fft-window", choices=["hann", "hamming", "blackman", "bartlett", "flattop"],
                       help="FFT window")
    parser.add_argument("--no-ml", action="store_true", help="Disable modulation classification")
    parser.add_argument("--force-iq", action="store_true", help="Force stereo WAV as IQ")

    # Output options
    parser.add_argument("--output", "-o", type=Path, help="Output report file")
    parser.add_argument("--format", choices=["json", "csv", "markdown", "all"], default="all",
                       help="Output format")
    parser.add_argument("--save-plots", action="store_true", help="Save plots to files")
    parser.add_argument("--plot-dir", type=Path, help="Directory for saving plots")

    # Configuration
    parser.add_argument("--config", type=Path, help="Custom config file")

    args = parser.parse_args()

    # Validate file
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    # Load custom config if provided
    if args.config:
        settings.load_from_file(args.config)

    # Override config from command line
    if args.fft_size:
        settings.set("fft.size", args.fft_size)
    if args.fft_window:
        settings.set("fft.window", args.fft_window)
    if args.no_ml:
        settings.set("ml.enabled", False)

    # Create pipeline config
    config = PipelineConfig()

    try:
        print(f"Analyzing: {args.file}")
        result = analyze_file(
            file_path=args.file,
            sample_rate=args.sample_rate,
            dtype=args.dtype,
            endianness=args.endianness,
            iq_layout=args.iq_layout,
            force_iq=args.force_iq,
            config=config,
        )

        # Print summary
        print_summary(result)

        # Generate reports
        if args.output or args.format != "all":
            formats = [args.format] if args.format != "all" else ["json", "csv", "markdown"]
            if args.output:
                # If output is a file path, use its parent as directory
                output_dir = args.output.parent if args.output.suffix else args.output
            else:
                output_dir = Path("reports/generated")
            output_paths = generate_report(result, output_dir, formats)
            
            # If user specified a specific output file and single format, copy/rename to match
            if args.output and len(formats) == 1:
                import shutil
                expected_path = args.output
                actual_path = output_paths[formats[0]]
                if actual_path != expected_path:
                    expected_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(actual_path, expected_path)
                    output_paths[formats[0]] = expected_path
            
            print("\nReports generated:")
            for fmt, path in output_paths.items():
                print(f"  {fmt}: {path}")

        # Save plots if requested
        if args.save_plots:
            save_plots(result, args.plot_dir or Path("reports/plots"))

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def print_summary(result):
    """Print analysis summary to console."""
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)

    meta = result.signal_metadata
    print(f"File: {meta.filename} ({meta.format})")
    print(f"Sample Rate: {meta.sample_rate/1e6:.3f} MHz")
    print(f"Duration: {meta.duration:.3f} s")
    print(f"Samples: {meta.num_samples:,}")

    if result.time_domain:
        td = result.time_domain
        print(f"\nTime Domain:")
        print(f"  RMS Magnitude: {td.rms_magnitude:.6f}")
        print(f"  Peak Magnitude: {td.peak_magnitude:.6f}")
        print(f"  PAPR: {td.papr_db:.1f} dB")

    if result.frequency_domain:
        fd = result.frequency_domain
        print(f"\nFrequency Domain:")
        if fd.peak_frequency:
            print(f"  Peak Frequency: {fd.peak_frequency/1e6:.3f} MHz")
        if fd.snr_db is not None:
            print(f"  SNR: {fd.snr_db:.1f} dB")
        if fd.noise_floor_db is not None:
            print(f"  Noise Floor: {fd.noise_floor_db:.1f} dB")
        print(f"  Spectral Entropy: {fd.spectral_entropy:.3f}" if fd.spectral_entropy else "  Spectral Entropy: N/A")
        print(f"  Spectral Flatness: {fd.spectral_flatness:.3f}" if fd.spectral_flatness else "  Spectral Flatness: N/A")
        print(f"  Detected Peaks: {fd.number_of_detected_peaks}")

    if result.signal_regions:
        print(f"\nDetected Signals: {len(result.signal_regions)}")
        for i, r in enumerate(result.signal_regions):
            print(f"  Signal {i+1}: {r.lower_frequency/1e6:.3f}-{r.upper_frequency/1e6:.3f} MHz "
                  f"(BW: {r.bandwidth/1e6:.3f} MHz, Peak: {r.peak_frequency/1e6:.3f} MHz)")

    if result.classification:
        cls = result.classification
        print(f"\nClassification:")
        print(f"  Modulation: {cls.predicted_class.value}")
        print(f"  Confidence: {cls.confidence:.1%}")

    if result.quality_score:
        qs = result.quality_score
        print(f"\nSignal Quality: {qs.overall_score:.1f}/100")
        print(f"  {qs.explanation}")

    if result.warnings:
        print(f"\nWarnings:")
        for w in result.warnings:
            print(f"  - {w}")

    print(f"\nProcessing Time: {result.processing_time_seconds:.3f} s")


def save_plots(result, plot_dir: Path):
    """Save visualization plots."""
    plot_dir.mkdir(parents=True, exist_ok=True)

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from visualization import (
            plot_waveform, plot_magnitude_phase,
            plot_spectrum_combined, plot_constellation,
            plot_instantaneous_frequency, plot_spectrogram
        )
        from dsp import compute_psd, compute_fft
        from config import settings

        # We need the original IQ data - for now just save what we can
        print(f"\nPlot saving not fully implemented yet. Directory: {plot_dir}")

    except Exception as e:
        print(f"Warning: Could not save plots: {e}")


if __name__ == "__main__":
    sys.exit(main())