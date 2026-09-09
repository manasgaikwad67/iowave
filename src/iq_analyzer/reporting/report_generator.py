"""Report generation module."""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..models import AnalysisResult, SignalQualityResult, ClassificationResult
from ..utils import format_frequency, format_db, format_duration, format_sample_rate
from ..config import settings
from .. import __version__ as software_version


def generate_json_report(result: AnalysisResult, output_path: Path) -> None:
    """Generate JSON report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result.to_dict(), f, indent=2, default=str)


def generate_csv_report(result: AnalysisResult, output_path: Path) -> None:
    """Generate CSV report with key parameters."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    # File info
    rows.append(["Category", "Parameter", "Value", "Unit"])
    rows.append(["File", "Filename", result.signal_metadata.filename, ""])
    rows.append(["File", "Format", result.signal_metadata.format, ""])
    rows.append(["File", "Sample Rate", result.signal_metadata.sample_rate, "Hz"])
    rows.append(["File", "Num Samples", result.signal_metadata.num_samples, ""])
    rows.append(["File", "Duration", result.signal_metadata.duration, "s"])
    rows.append(["File", "Channels", result.signal_metadata.num_channels, ""])
    rows.append(["File", "Data Type", result.signal_metadata.data_type, ""])
    rows.append(["File", "Bit Depth", result.signal_metadata.bit_depth, ""])
    rows.append(["File", "IQ Format", result.signal_metadata.iq_format, ""])

    # Time domain
    if result.time_domain:
        td = result.time_domain
        rows.append(["Time Domain", "RMS Magnitude", td.rms_magnitude, ""])
        rows.append(["Time Domain", "Peak Magnitude", td.peak_magnitude, ""])
        rows.append(["Time Domain", "Crest Factor", td.crest_factor, ""])
        rows.append(["Time Domain", "PAPR", td.papr_db, "dB"])
        rows.append(["Time Domain", "Amplitude Mean", td.amplitude_mean, ""])
        rows.append(["Time Domain", "Amplitude Std", td.amplitude_std, ""])

    # Frequency domain
    if result.frequency_domain:
        fd = result.frequency_domain
        rows.append(["Frequency Domain", "Peak Frequency", fd.peak_frequency, "Hz"])
        rows.append(["Frequency Domain", "Peak Power", fd.peak_power, "dB"])
        rows.append(["Frequency Domain", "Noise Floor", fd.noise_floor_db, "dB"])
        rows.append(["Frequency Domain", "SNR", fd.snr_db, "dB"])
        rows.append(["Frequency Domain", "Occupied BW 90%", fd.bandwidth_90, "Hz"])
        rows.append(["Frequency Domain", "Occupied BW 95%", fd.bandwidth_95, "Hz"])
        rows.append(["Frequency Domain", "Occupied BW 99%", fd.bandwidth_99, "Hz"])
        rows.append(["Frequency Domain", "-3dB BW", fd.minus_3db_bandwidth, "Hz"])
        rows.append(["Frequency Domain", "Spectral Centroid", fd.spectral_centroid, "Hz"])
        rows.append(["Frequency Domain", "Spectral Entropy", fd.spectral_entropy, ""])
        rows.append(["Frequency Domain", "Spectral Flatness", fd.spectral_flatness, ""])
        rows.append(["Frequency Domain", "Num Peaks", fd.number_of_detected_peaks, ""])

    # Instantaneous
    if result.instantaneous:
        inst = result.instantaneous
        rows.append(["Instantaneous", "Mean Freq", inst.instantaneous_frequency_mean, "Hz"])
        rows.append(["Instantaneous", "Freq Std", inst.instantaneous_frequency_std, "Hz"])
        rows.append(["Instantaneous", "Freq Deviation", inst.frequency_deviation, "Hz"])

    # SNR
    if result.snr_result:
        snr = result.snr_result
        rows.append(["SNR", "SNR", snr.snr_db, "dB"])
        rows.append(["SNR", "Signal Power", snr.signal_power_db, "dB"])
        rows.append(["SNR", "Noise Power", snr.noise_power_db, "dB"])
        rows.append(["SNR", "Method", snr.method, ""])

    # Classification
    if result.classification:
        cls = result.classification
        rows.append(["Classification", "Predicted Class", cls.predicted_class.value, ""])
        rows.append(["Classification", "Confidence", cls.confidence, ""])
        rows.append(["Classification", "Model", cls.model_name, ""])
        rows.append(["Classification", "Model Version", cls.model_version, ""])

    # Quality Score
    if result.quality_score:
        qs = result.quality_score
        rows.append(["Quality", "Overall Score", qs.overall_score, "/100"])
        rows.append(["Quality", "SNR Score", qs.snr_score, "/100"])
        rows.append(["Quality", "Freq Stability Score", qs.frequency_stability_score, "/100"])
        rows.append(["Quality", "Amp Stability Score", qs.amplitude_stability_score, "/100"])
        rows.append(["Quality", "Spectral Quality Score", qs.spectral_quality_score, "/100"])
        rows.append(["Quality", "Noise Score", qs.noise_score, "/100"])
        rows.append(["Quality", "Explanation", qs.explanation, ""])

    # Warnings
    for w in result.warnings:
        rows.append(["Warnings", "", w, ""])

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def generate_markdown_report(result: AnalysisResult, output_path: Path) -> None:
    """Generate human-readable Markdown report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []

    # Title
    lines.append("# AUTOMATED IQ SIGNAL ANALYSIS REPORT")
    lines.append("")
    lines.append(f"**Generated:** {result.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Software Version:** {software_version}")
    lines.append("")

    # File Information
    lines.append("## FILE INFORMATION")
    lines.append("")
    meta = result.signal_metadata
    lines.append(f"- **Filename:** {meta.filename}")
    lines.append(f"- **Format:** {meta.format}")
    lines.append(f"- **Sample Rate:** {format_sample_rate(meta.sample_rate)}")
    lines.append(f"- **Number of Samples:** {meta.num_samples:,}")
    lines.append(f"- **Duration:** {format_duration(meta.duration)}")
    lines.append(f"- **Channels:** {meta.num_channels}")
    lines.append(f"- **Data Type:** {meta.data_type}")
    lines.append(f"- **Bit Depth:** {meta.bit_depth}")
    lines.append(f"- **IQ Format:** {meta.iq_format}")
    lines.append(f"- **Endianness:** {meta.endianness}")
    if meta.center_frequency:
        lines.append(f"- **Center Frequency:** {format_frequency(meta.center_frequency)}")
    lines.append("")

    # Preprocessing
    if result.preprocessing_metadata:
        lines.append("## PREPROCESSING")
        lines.append("")
        pm = result.preprocessing_metadata
        lines.append(f"- **DC Removed:** {'Yes' if pm.dc_removed else 'No'}")
        lines.append(f"- **Normalized:** {'Yes' if pm.normalized else 'No'}")
        lines.append(f"- **Filter Applied:** {'Yes' if pm.filter_applied else 'No'}")
        if pm.filter_applied:
            lines.append(f"  - Filter Type: {pm.filter_type}")
            lines.append(f"  - Low Cut: {pm.low_cut} Hz" if pm.low_cut else "  - Low Cut: N/A")
            lines.append(f"  - High Cut: {pm.high_cut} Hz" if pm.high_cut else "  - High Cut: N/A")
        lines.append(f"- **Resampled:** {'Yes' if pm.resampled else 'No'}")
        if pm.resampled:
            lines.append(f"  - Original Sample Rate: {format_sample_rate(pm.original_sample_rate)}")
            lines.append(f"  - Final Sample Rate: {format_sample_rate(pm.final_sample_rate)}")
        lines.append(f"- **Samples Removed:** {pm.number_of_samples_removed}")
        lines.append("")

    # Time Domain
    if result.time_domain:
        lines.append("## TIME-DOMAIN PARAMETERS")
        lines.append("")
        td = result.time_domain
        lines.append(f"- **RMS Magnitude:** {td.rms_magnitude:.6f}")
        lines.append(f"- **Peak Magnitude:** {td.peak_magnitude:.6f}")
        lines.append(f"- **Peak-to-Peak:** {td.peak_to_peak:.6f}")
        lines.append(f"- **Crest Factor:** {td.crest_factor:.3f}")
        lines.append(f"- **PAPR:** {format_db(td.papr_db)}")
        lines.append(f"- **Amplitude Mean:** {td.amplitude_mean:.6f}")
        lines.append(f"- **Amplitude Std:** {td.amplitude_std:.6f}")
        lines.append(f"- **Phase Mean:** {td.phase_mean:.3f} rad")
        lines.append(f"- **Phase Std:** {td.phase_std:.3f} rad")
        lines.append("")

    # Frequency Domain
    if result.frequency_domain:
        lines.append("## FREQUENCY-DOMAIN PARAMETERS")
        lines.append("")
        fd = result.frequency_domain
        lines.append(f"- **FFT Size:** {fd.fft_size}")
        lines.append(f"- **Frequency Resolution:** {fd.frequency_resolution:.3f} Hz")
        if fd.peak_frequency:
            lines.append(f"- **Dominant Frequency:** {format_frequency(fd.peak_frequency)}")
        if fd.peak_power:
            lines.append(f"- **Peak Power:** {format_db(fd.peak_power)}")
        if fd.noise_floor_db:
            lines.append(f"- **Noise Floor:** {format_db(fd.noise_floor_db)}")
        if fd.snr_db:
            lines.append(f"- **SNR:** {format_db(fd.snr_db)}")
        lines.append(f"- **Spectral Centroid:** {format_frequency(fd.spectral_centroid) if fd.spectral_centroid else 'N/A'}")
        lines.append(f"- **Spectral Spread:** {format_frequency(fd.spectral_spread) if fd.spectral_spread else 'N/A'}")
        lines.append(f"- **Spectral Entropy:** {fd.spectral_entropy:.3f}" if fd.spectral_entropy is not None else "- **Spectral Entropy:** N/A")
        lines.append(f"- **Spectral Flatness:** {fd.spectral_flatness:.3f}" if fd.spectral_flatness is not None else "- **Spectral Flatness:** N/A")
        lines.append(f"- **Detected Peaks:** {fd.number_of_detected_peaks}")
        lines.append("")

    # Bandwidth
    if result.frequency_domain:
        fd = result.frequency_domain
        lines.append("## BANDWIDTH ESTIMATES")
        lines.append("")
        if fd.bandwidth_90:
            lines.append(f"- **Occupied Bandwidth (90%):** {format_frequency(fd.bandwidth_90)}")
        if fd.bandwidth_95:
            lines.append(f"- **Occupied Bandwidth (95%):** {format_frequency(fd.bandwidth_95)}")
        if fd.bandwidth_99:
            lines.append(f"- **Occupied Bandwidth (99%):** {format_frequency(fd.bandwidth_99)}")
        if fd.minus_3db_bandwidth:
            lines.append(f"- **-3 dB Bandwidth:** {format_frequency(fd.minus_3db_bandwidth)}")
        if fd.occupied_bandwidth:
            lines.append(f"- **Occupied Bandwidth:** {format_frequency(fd.occupied_bandwidth)}")
        lines.append("")

    # SNR
    if result.snr_result:
        lines.append("## SNR ESTIMATION")
        lines.append("")
        snr = result.snr_result
        if snr.snr_db is not None:
            lines.append(f"- **SNR:** {format_db(snr.snr_db)}")
        if snr.signal_power_db is not None:
            lines.append(f"- **Signal Power:** {format_db(snr.signal_power_db)}")
        if snr.noise_power_db is not None:
            lines.append(f"- **Noise Power:** {format_db(snr.noise_power_db)}")
        lines.append(f"- **Method:** {snr.method}")
        for a in snr.assumptions:
            lines.append(f"  - Assumption: {a}")
        for w in snr.warnings:
            lines.append(f"  - Warning: {w}")
        lines.append("")

    # Signal Detection
    if result.signal_regions:
        lines.append("## DETECTED SIGNALS")
        lines.append("")
        for i, region in enumerate(result.signal_regions):
            lines.append(f"### Signal {i+1}")
            lines.append(f"- **Frequency Range:** {format_frequency(region.lower_frequency)} - {format_frequency(region.upper_frequency)}")
            lines.append(f"- **Bandwidth:** {format_frequency(region.bandwidth)}")
            lines.append(f"- **Peak Frequency:** {format_frequency(region.peak_frequency)}")
            lines.append(f"- **Peak Power:** {format_db(region.peak_power)}")
            if region.estimated_snr_db:
                lines.append(f"- **Estimated SNR:** {format_db(region.estimated_snr_db)}")
            lines.append("")

    # Instantaneous Frequency
    if result.instantaneous:
        lines.append("## INSTANTANEOUS PARAMETERS")
        lines.append("")
        inst = result.instantaneous
        if inst.instantaneous_frequency_mean:
            lines.append(f"- **Mean Instantaneous Frequency:** {format_frequency(inst.instantaneous_frequency_mean)}")
        if inst.instantaneous_frequency_std:
            lines.append(f"- **Instantaneous Frequency Std:** {format_frequency(inst.instantaneous_frequency_std)}")
        if inst.frequency_deviation:
            lines.append(f"- **Frequency Deviation:** {format_frequency(inst.frequency_deviation)}")
        if inst.instantaneous_amplitude_mean:
            lines.append(f"- **Mean Instantaneous Amplitude:** {inst.instantaneous_amplitude_mean:.6f}")
        if inst.instantaneous_amplitude_std:
            lines.append(f"- **Instantaneous Amplitude Std:** {inst.instantaneous_amplitude_std:.6f}")
        lines.append("")

    # Classification
    if result.classification:
        lines.append("## MODULATION CLASSIFICATION")
        lines.append("")
        cls = result.classification
        lines.append(f"- **Predicted Modulation:** {cls.predicted_class.value}")
        lines.append(f"- **Confidence:** {cls.confidence:.2%}")
        lines.append(f"- **Model:** {cls.model_name} v{cls.model_version}")
        lines.append(f"- **Feature Version:** {cls.feature_version}")
        lines.append("")
        lines.append("### Class Probabilities")
        for mod, prob in sorted(cls.probabilities.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **{mod.value}:** {prob:.2%}")
        lines.append("")

    # Signal Quality
    if result.quality_score:
        lines.append("## SIGNAL QUALITY ASSESSMENT")
        lines.append("")
        qs = result.quality_score
        lines.append(f"- **Overall Score:** {qs.overall_score:.1f}/100")
        lines.append(f"- **SNR Score:** {qs.snr_score:.1f}/100")
        lines.append(f"- **Frequency Stability Score:** {qs.frequency_stability_score:.1f}/100")
        lines.append(f"- **Amplitude Stability Score:** {qs.amplitude_stability_score:.1f}/100")
        lines.append(f"- **Spectral Quality Score:** {qs.spectral_quality_score:.1f}/100")
        lines.append(f"- **Noise Score:** {qs.noise_score:.1f}/100")
        lines.append("")
        lines.append(f"**Explanation:** {qs.explanation}")
        lines.append("")

    # Warnings
    if result.warnings:
        lines.append("## WARNINGS")
        lines.append("")
        for w in result.warnings:
            lines.append(f"- {w}")
        lines.append("")

    # Configuration
    lines.append("## CONFIGURATION USED")
    lines.append("")
    for key, value in result.configuration_used.items():
        lines.append(f"- **{key}:** {value}")
    lines.append("")

    # Performance
    if result.processing_time_seconds:
        lines.append("## PERFORMANCE")
        lines.append("")
        lines.append(f"- **Total Processing Time:** {result.processing_time_seconds:.3f} s")
        lines.append("")

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))


def generate_report(
    result: AnalysisResult,
    output_dir: Path,
    formats: List[str] = None,
) -> Dict[str, Path]:
    """
    Generate reports in multiple formats.

    Args:
        result: Analysis result
        output_dir: Output directory
        formats: List of formats ('json', 'csv', 'markdown')

    Returns:
        Dictionary mapping format to output path
    """
    if formats is None:
        formats = ["json", "csv", "markdown"]

    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = f"analysis_{result.signal_metadata.filename}_{result.analysis_timestamp.strftime('%Y%m%d_%H%M%S')}"

    output_paths = {}

    if "json" in formats:
        path = output_dir / f"{base_name}.json"
        generate_json_report(result, path)
        output_paths["json"] = path

    if "csv" in formats:
        path = output_dir / f"{base_name}.csv"
        generate_csv_report(result, path)
        output_paths["csv"] = path

    if "markdown" in formats:
        path = output_dir / f"{base_name}.md"
        generate_markdown_report(result, path)
        output_paths["markdown"] = path

    return output_paths