"""Streamlit web application for IQ Signal Analyzer."""

import streamlit as st
import numpy as np
import tempfile
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from scipy.signal import spectrogram as scipy_spectrogram

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from iq_analyzer.core import analyze_file, PipelineConfig
from iq_analyzer.config import settings
from iq_analyzer.reporting import generate_report
from iq_analyzer.models import ModulationType
from iq_analyzer.utils import format_frequency, format_db, format_duration, format_sample_rate
from iq_analyzer.visualization import (
    plot_waveform,
    plot_magnitude_phase,
    plot_spectrum_combined,
    plot_spectrogram,
    plot_constellation,
)


st.set_page_config(
    page_title="Automated IQ Signal Analyzer",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_pipeline_config():
    """Get pipeline config from settings."""
    return PipelineConfig()


def load_file(uploaded_file, file_type, sample_rate, dtype, endianness, iq_layout, force_iq):
    """Load uploaded file to temporary location and analyze."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = Path(tmp.name)

    try:
        config = get_pipeline_config()
        if not settings.get("ml.enabled", True):
            config.classifier.enabled = False

        result = analyze_file(
            file_path=tmp_path,
            sample_rate=sample_rate,
            dtype=dtype,
            endianness=endianness,
            iq_layout=iq_layout,
            force_iq=force_iq,
            config=config,
        )
        return result
    finally:
        os.unlink(tmp_path)


def display_overview(result):
    """Display overview tab."""
    meta = result.signal_metadata

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Format", meta.format.upper())
    with col2:
        st.metric("Sample Rate", format_sample_rate(meta.sample_rate))
    with col3:
        st.metric("Duration", format_duration(meta.duration))
    with col4:
        st.metric("Samples", f"{meta.num_samples:,}")

    st.markdown("---")
    st.markdown("### File Details")
    details = {
        "Filename": meta.filename,
        "Format": meta.format,
        "Sample Rate": format_sample_rate(meta.sample_rate),
        "Number of Samples": f"{meta.num_samples:,}",
        "Duration": format_duration(meta.duration),
        "Channels": meta.num_channels,
        "Data Type": meta.data_type,
        "Bit Depth": meta.bit_depth,
        "IQ Format": meta.iq_format,
        "Endianness": meta.endianness,
        "Scale Factor": meta.scale_factor,
    }
    if meta.center_frequency:
        details["Center Frequency"] = format_frequency(meta.center_frequency)

    for k, v in details.items():
        st.text(f"{k}: {v}")


def display_parameters(result):
    """Display signal parameters tab."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Time Domain")
        if result.time_domain:
            td = result.time_domain
            st.metric("RMS Magnitude", f"{td.rms_magnitude:.6f}")
            st.metric("Peak Magnitude", f"{td.peak_magnitude:.6f}")
            st.metric("PAPR", format_db(td.papr_db))
            st.metric("Crest Factor", f"{td.crest_factor:.3f}")

    with col2:
        st.markdown("### Frequency Domain")
        if result.frequency_domain:
            fd = result.frequency_domain
            if fd.peak_frequency:
                st.metric("Peak Frequency", format_frequency(fd.peak_frequency))
            if fd.snr_db is not None:
                st.metric("SNR", format_db(fd.snr_db))
            if fd.noise_floor_db is not None:
                st.metric("Noise Floor", format_db(fd.noise_floor_db))
            if fd.spectral_entropy is not None:
                st.metric("Spectral Entropy", f"{fd.spectral_entropy:.3f}")
            if fd.spectral_flatness is not None:
                st.metric("Spectral Flatness", f"{fd.spectral_flatness:.3f}")

    if result.signal_regions:
        st.markdown("### Detected Signals")
        for i, r in enumerate(result.signal_regions):
            with st.expander(f"Signal {i+1}: {format_frequency(r.peak_frequency)}"):
                st.write(f"**Frequency Range:** {format_frequency(r.lower_frequency)} - {format_frequency(r.upper_frequency)}")
                st.write(f"**Bandwidth:** {format_frequency(r.bandwidth)}")
                st.write(f"**Peak Power:** {format_db(r.peak_power)}")
                if r.estimated_snr_db:
                    st.write(f"**Estimated SNR:** {format_db(r.estimated_snr_db)}")


def display_time_domain(result):
    """Display time domain visualizations."""
    if result.iq_data is not None:
        st.pyplot(plot_waveform(result.iq_data, result.signal_metadata.sample_rate), clear_figure=True)
        st.pyplot(plot_magnitude_phase(result.iq_data, result.signal_metadata.sample_rate), clear_figure=True)

    # Placeholder for actual plots
    if result.time_domain:
        td = result.time_domain
        st.markdown("### Statistics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Mean I", f"{td.mean_I:.6f}")
        col2.metric("Mean Q", f"{td.mean_Q:.6f}")
        col3.metric("Phase Std", f"{td.phase_std:.3f} rad")


def display_frequency_domain(result):
    """Display frequency domain visualizations."""
    if result.fft_result is not None and result.psd_result is not None:
        noise_floor_db = result.noise_floor.noise_floor_db if result.noise_floor else None
        st.pyplot(
            plot_spectrum_combined(
                result.fft_result,
                result.psd_result,
                result.detected_peaks,
                noise_floor_db,
            ),
            clear_figure=True,
        )

    if result.frequency_domain:
        fd = result.frequency_domain
        if fd.peak_frequency:
            st.metric("Peak Frequency", format_frequency(fd.peak_frequency))
        if fd.snr_db is not None:
            st.metric("SNR", format_db(fd.snr_db))

    if result.detected_peaks:
        st.markdown("### Detected Peaks")
        for peak in result.detected_peaks[:10]:
            st.write(f"{format_frequency(peak.frequency)} - {format_db(10*np.log10(peak.power))} (prom: {peak.prominence:.1f})")


def display_spectrogram(result):
    """Display spectrogram."""
    if result.iq_data is None:
        st.info("Spectrogram is unavailable for this result.")
        return

    frequencies, times, values = scipy_spectrogram(
        result.iq_data,
        fs=result.signal_metadata.sample_rate,
        return_onesided=False,
    )
    order = np.argsort(frequencies)
    spectrogram_result = SimpleNamespace(
        frequencies=frequencies[order],
        times=times,
        spectrogram=values[order],
        nperseg=256,
        noverlap=128,
    )
    st.pyplot(plot_spectrogram(spectrogram_result), clear_figure=True)


def display_constellation(result):
    """Display constellation."""
    if result.iq_data is not None:
        st.pyplot(plot_constellation(result.iq_data), clear_figure=True)


def display_classification(result):
    """Display classification results."""
    if result.classification:
        cls = result.classification
        st.markdown("### Classification Result")
        st.metric("Predicted Modulation", cls.predicted_class.value)
        st.metric("Confidence", f"{cls.confidence:.1%}")

        st.markdown("### Class Probabilities")
        for mod, prob in sorted(cls.probabilities.items(), key=lambda x: x[1], reverse=True):
            st.progress(prob, text=f"{mod.value}: {prob:.1%}")

        st.markdown("### Model Info")
        st.write(f"**Model:** {cls.model_name} v{cls.model_version}")
        st.write(f"**Feature Version:** {cls.feature_version}")

        if cls.warnings:
            for w in cls.warnings:
                st.warning(w)
    else:
        st.info("Classification not available (disabled or no model loaded)")


def display_quality(result):
    """Display signal quality assessment."""
    if result.quality_score:
        qs = result.quality_score
        st.markdown("### Overall Quality Score")
        st.metric("Score", f"{qs.overall_score:.1f}/100")

        st.markdown("### Component Scores")
        col1, col2, col3 = st.columns(3)
        col1.metric("SNR", f"{qs.snr_score:.1f}/100")
        col2.metric("Freq Stability", f"{qs.frequency_stability_score:.1f}/100")
        col3.metric("Amp Stability", f"{qs.amplitude_stability_score:.1f}/100")

        col1, col2 = st.columns(2)
        col1.metric("Spectral Quality", f"{qs.spectral_quality_score:.1f}/100")
        col2.metric("Noise", f"{qs.noise_score:.1f}/100")

        st.markdown("### Explanation")
        st.write(qs.explanation)
    else:
        st.info("Quality assessment not available")


def display_report(result):
    """Display report generation options."""
    st.markdown("### Generate Report")

    formats = st.multiselect(
        "Output Formats",
        ["JSON", "CSV", "Markdown"],
        default=["JSON", "CSV", "Markdown"],
    )

    if st.button("Generate Report"):
        with st.spinner("Generating reports..."):
            output_dir = Path("reports/generated")
            format_list = [f.lower() for f in formats]
            paths = generate_report(result, output_dir, format_list)

            for fmt, path in paths.items():
                with open(path, "r") as f:
                    content = f.read()
                st.download_button(
                    f"Download {fmt.upper()}",
                    content,
                    file_name=path.name,
                    mime="application/json" if fmt == "json" else "text/plain",
                )

    if result.warnings:
        st.markdown("### Warnings")
        for w in result.warnings:
            st.warning(w)


def main():
    st.title("📡 Automated IQ Signal Analyzer")

    # Sidebar
    with st.sidebar:
        st.header("📁 File Input")
        uploaded_file = st.file_uploader(
            "Upload Signal File",
            type=["wav", "iq", "bin", "dat", "raw"],
            help="Supported formats: WAV, raw IQ (.iq, .bin, .dat, .raw)"
        )

        if uploaded_file:
            ext = Path(uploaded_file.name).suffix.lower()
            st.write(f"**File:** {uploaded_file.name}")
            st.write(f"**Size:** {len(uploaded_file.getvalue()) / 1024:.1f} KB")
            st.write(f"**Type:** {ext}")

        st.header("⚙️ Raw IQ Settings")
        sample_rate = st.number_input(
            "Sample Rate (Hz)",
            value=2048000,
            min_value=1000,
            help="Required for raw IQ files"
        )
        dtype = st.selectbox(
            "Data Type",
            ["int8", "int16", "int32", "float32", "float64"],
            index=1,
        )
        endianness = st.selectbox("Endianness", ["little", "big"], index=0)
        iq_layout = st.selectbox("IQ Layout", ["interleaved", "separate_i_q"], index=0)
        force_iq = st.checkbox("Force Stereo WAV as IQ", value=False)

        st.header("🔧 Preprocessing")
        dc_removal = st.checkbox("Remove DC Offset", value=True)
        normalize = st.checkbox("Normalize", value=False)
        filter_enabled = st.checkbox("Apply Filter", value=False)
        if filter_enabled:
            filter_type = st.selectbox("Filter Type", ["lowpass", "highpass", "bandpass", "notch"])
            low_cut = st.number_input("Low Cut (Hz)", value=1000)
            high_cut = st.number_input("High Cut (Hz)", value=100000)

        st.header("📊 Analysis")
        fft_size = st.selectbox("FFT Size", [2048, 4096, 8192, 16384, 32768], index=2)
        fft_window = st.selectbox("FFT Window", ["hann", "hamming", "blackman", "bartlett", "flattop"])

        st.header("🤖 Machine Learning")
        ml_enabled = st.checkbox("Enable Classification", value=True)
        if ml_enabled:
            st.write(f"Model: {settings.get('ml.model_path', 'default')}")

        st.header("🎯 Quality Score")
        quality_enabled = st.checkbox("Enable Quality Score", value=True)

    # Main content
    if uploaded_file:
        if st.button("🔍 Analyze", type="primary"):
            with st.spinner("Analyzing signal..."):
                try:
                    # Update settings from UI
                    settings.set("preprocessing.remove_dc_offset", dc_removal)
                    settings.set("preprocessing.normalize", normalize)
                    settings.set("preprocessing.filter_enabled", filter_enabled)
                    settings.set("fft.size", fft_size)
                    settings.set("fft.window", fft_window)
                    settings.set("ml.enabled", ml_enabled)
                    settings.set("quality_score.enabled", quality_enabled)

                    result = load_file(
                        uploaded_file,
                        ext,
                        sample_rate,
                        dtype,
                        endianness,
                        iq_layout,
                        force_iq,
                    )

                    # Store in session state
                    st.session_state.result = result
                    st.success("Analysis complete!")

                except Exception as e:
                    st.error(f"Analysis failed: {e}")

        # Display results if available
        if "result" in st.session_state:
            result = st.session_state.result

            tabs = st.tabs([
                "📋 Overview",
                "📊 Parameters",
                "📈 Time Domain",
                "📡 Frequency Domain",
                "🌈 Spectrogram",
                "🔮 Constellation",
                "🤖 Classification",
                "⭐ Quality",
                "📄 Report",
            ])

            with tabs[0]:
                display_overview(result)
            with tabs[1]:
                display_parameters(result)
            with tabs[2]:
                display_time_domain(result)
            with tabs[3]:
                display_frequency_domain(result)
            with tabs[4]:
                display_spectrogram(result)
            with tabs[5]:
                display_constellation(result)
            with tabs[6]:
                display_classification(result)
            with tabs[7]:
                display_quality(result)
            with tabs[8]:
                display_report(result)
    else:
        st.info("👈 Upload a signal file to begin analysis")

        st.markdown("""
        ## Features
        - **File Support**: WAV (mono/stereo/IQ), Raw IQ (.iq, .bin, .dat, .raw)
        - **Time-Domain Analysis**: RMS, peak, PAPR, crest factor, amplitude/phase statistics
        - **Frequency-Domain Analysis**: FFT, PSD (Welch), peak detection, bandwidth estimation
        - **Signal Detection**: Automatic signal region detection, noise floor estimation
        - **SNR Estimation**: Spectral-domain SNR calculation
        - **Instantaneous Frequency**: Phase differentiation with amplitude masking
        - **Spectral Features**: Centroid, spread, entropy, flatness, rolloff
        - **Modulation Classification**: Optional ML-based classification (RF, SVM)
        - **Signal Quality Score**: Interpretable 0-100 quality metric
        - **Report Generation**: JSON, CSV, Markdown reports
        - **Visualization**: Waveforms, spectra, spectrograms, constellation diagrams
        """)


if __name__ == "__main__":
    main()