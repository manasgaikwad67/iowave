# Automated IQ Signal Analyzer

A production-quality scientific signal-analysis application for automated analysis of IQ and WAV files with signal parameter extraction, modulation classification, and comprehensive reporting.

## Features

- **File Format Support**: WAV (mono, stereo, integer/float PCM) and Raw IQ (.iq, .bin, .dat, .raw)
- **Automatic Format Detection**: Inspects file signatures and extensions
- **Robust IQ Reconstruction**: Handles interleaved, separate I/Q, configurable endianness
- **Configurable Preprocessing**: DC removal, normalization, filtering (SOS), resampling, decimation
- **Time-Domain Analysis**: RMS, peak, PAPR, crest factor, amplitude/phase statistics
- **Frequency-Domain Analysis**: FFT with configurable windows, PSD (Welch's method), peak detection
- **Signal Detection**: Automatic signal region detection, noise floor estimation
- **Bandwidth Estimation**: Occupied bandwidth (90/95/99%), -3dB bandwidth
- **SNR Estimation**: Spectral-domain SNR calculation
- **Instantaneous Frequency**: Phase differentiation with amplitude masking
- **Spectral Features**: Centroid, spread, entropy, flatness, rolloff, skewness, kurtosis
- **Modulation Classification**: Optional ML classification (Random Forest, SVM) for AM, FM, PM, BPSK, QPSK, 8PSK, FSK, 16QAM
- **Signal Quality Score**: Interpretable 0-100 quality metric with component breakdown
- **Comprehensive Reporting**: JSON, CSV, and Markdown reports with full reproducibility
- **Visualization**: Waveforms, spectra, spectrograms, constellation diagrams
- **Streamlit Web Interface**: Interactive dashboard for analysis
- **CLI Tools**: Command-line analysis, dataset generation, model training
- **Synthetic Dataset Generator**: Creates labeled datasets for ML training

## Architecture

```
src/
├── config/          # Configuration management
├── models/          # Data models (metadata, parameters, results)
├── io/              # File I/O (WAV, raw IQ, detection, metadata)
├── processing/      # Validation, preprocessing pipeline
├── dsp/             # Digital signal processing algorithms
├── features/        # Feature extraction for ML
├── classification/  # ML classification (training, prediction, registry)
├── quality/         # Signal quality assessment
├── visualization/   # Plotting functions
├── reporting/       # Report generation (JSON, CSV, Markdown)
├── core/            # Analysis pipeline orchestration
└── utils/           # Logging, units, memory, performance
```

## Installation

```bash
# Clone repository
git clone <repository-url>
cd iq-signal-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # for development

# Install package in development mode
pip install -e .
```

## Usage

### Streamlit Web Interface

```bash
streamlit run app/streamlit_app.py
```

### Command Line

```bash
# Analyze WAV file
python scripts/analyze_file.py signal.wav

# Analyze raw IQ file
python scripts/analyze_file.py signal.iq --sample-rate 2400000 --dtype int16 --iq-layout interleaved

# Generate report only
python scripts/analyze_file.py signal.wav --output report.json --format json

# Disable ML classification
python scripts/analyze_file.py signal.wav --no-ml
```

### Generate Synthetic Dataset

```bash
python scripts/generate_dataset.py data/synthetic --samples-per-class 200
```

### Train Classification Model

```bash
python scripts/train_model.py data/synthetic models/trained/modulation_classifier.joblib
```

### Evaluate Model

```bash
python scripts/evaluate_model.py models/trained/modulation_classifier.joblib data/synthetic
```

## Configuration

Default configuration in `config/default_config.yaml`. All parameters can be overridden via:

- CLI arguments
- Streamlit sidebar
- Custom YAML config file (`--config`)

Key configuration sections:
- `file_loading`: File size limits, default IQ parameters
- `preprocessing`: DC removal, normalization, filtering, resampling
- `fft`: Size, window, zero-padding
- `psd`: Welch parameters (nperseg, noverlap, nfft)
- `peak_detection`: Prominence, distance, height thresholds
- `bandwidth`: Method (occupied/-3dB), percentages
- `snr`: Estimation method, signal region margin
- `ml`: Model path, feature version, confidence threshold
- `quality_score`: Component weights, thresholds

## Supported Modulation Types

| Type | Description |
|------|-------------|
| Noise | AWGN only |
| AM | Amplitude Modulation |
| FM | Frequency Modulation |
| PM | Phase Modulation |
| BPSK | Binary Phase Shift Keying |
| QPSK | Quadrature Phase Shift Keying |
| 8PSK | 8-ary Phase Shift Keying |
| FSK | Frequency Shift Keying |
| 16QAM | 16-Quadrature Amplitude Modulation |

## Raw IQ File Requirements

Raw IQ files have no headers. You **must** specify:
- Sample rate (`--sample-rate`)
- Data type (`--dtype`: int8, int16, int32, float32, float64)
- Endianness (`--endianness`: little, big)
- IQ layout (`--iq-layout`: interleaved, separate_i_q)

The tool will **not** guess these parameters automatically.

## Validation Framework

The project includes a validation framework for scientific correctness:

- Ground-truth signal generation with known parameters
- Frequency estimation validation (error in Hz and ppm)
- Bandwidth estimation validation
- SNR estimation validation with injected noise
- Classification evaluation at different SNR levels

Run validation:
```bash
pytest tests/ -v
```

## Requirements

- Python 3.11+
- numpy >= 1.26
- scipy >= 1.11
- pandas >= 2.1
- matplotlib >= 3.8
- pywavelets >= 1.5
- scikit-learn >= 1.3
- streamlit >= 1.28
- pyyaml >= 6.0
- joblib >= 1.3
- psutil >= 5.9

## Development

```bash
# Format code
black src/ tests/ app/ scripts/

# Lint
ruff check src/ tests/ app/ scripts/

# Type check
mypy src/

# Run tests
pytest tests/ -v --cov=src
```

## Project Structure

```
iq-signal-analyzer/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── config/
│   └── default_config.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   ├── synthetic/
│   └── sample/
├── models/
│   ├── trained/
│   └── metadata/
├── reports/
│   ├── generated/
│   └── plots/
├── notebooks/
│   └── exploration/
├── scripts/
│   ├── analyze_file.py
│   ├── generate_dataset.py
│   ├── train_model.py
│   └── evaluate_model.py
├── src/
│   └── iq_analyzer/
└── app/
    ├── streamlit_app.py
    └── components/
```

## Limitations

1. **Raw IQ files require manual parameter specification** - no automatic detection
2. **Classification accuracy depends on training data** - synthetic data may not match real signals
3. **Large file handling** - files are loaded into memory; very large files may require chunked processing
4. **Instantaneous frequency unreliable in low-amplitude regions** - amplitude masking helps but doesn't eliminate noise
5. **Bandwidth definitions vary** - occupied bandwidth ≠ -3dB bandwidth ≠ threshold bandwidth
6. **SNR estimation is method-dependent** - spectral SNR ≠ time-domain SNR ≠ instrument SNR

## Future Work

- [ ] Live SDR support (SoapySDR, RTL-SDR, HackRF)
- [ ] Deep learning classification (CNN, Transformer)
- [ ] IQ impairment analysis (DC offset, I/Q imbalance, image rejection)
- [ ] Anomaly detection (Isolation Forest, statistical)
- [ ] Real-time streaming analysis
- [ ] Export to SigMF format
- [ ] Batch processing of multiple files
- [ ] Docker containerization

## License

MIT License - see LICENSE file for details.

## Citation

If you use this software in academic work, please cite:

```bibtex
@software{iq_signal_analyzer,
  title = {Automated Model for Analysis of IQ and WAV Files Along with Signal Parameter Extraction},
  author = {Manas Gaikwad},
  year = {2024},
  url = {https://github.com/...}
}
```