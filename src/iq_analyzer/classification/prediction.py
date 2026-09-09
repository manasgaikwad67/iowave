"""Prediction utilities for modulation classification."""

import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from ..models import ClassificationResult, ModulationType
from .classifier import ModulationClassifier, ClassifierConfig
from ..features import FeatureConfig
from ..utils import get_logger

logger = get_logger(__name__)


def predict_single(
    iq_data: np.ndarray,
    sample_rate: float,
    model_path: Optional[str] = None,
    classifier: Optional[ModulationClassifier] = None,
    feature_config: Optional[FeatureConfig] = None,
) -> ClassificationResult:
    """
    Predict modulation for a single signal.

    Args:
        iq_data: Complex IQ signal
        sample_rate: Sample rate in Hz
        model_path: Path to model file (if not using existing classifier)
        classifier: Pre-loaded classifier instance
        feature_config: Feature extraction configuration

    Returns:
        ClassificationResult
    """
    if classifier is None:
        config = ClassifierConfig(model_path=model_path) if model_path else ClassifierConfig()
        classifier = ModulationClassifier(config)

    return classifier.predict(iq_data, sample_rate, feature_config)


def predict_batch(
    iq_signals: List[np.ndarray],
    sample_rates: List[float],
    model_path: Optional[str] = None,
    feature_config: Optional[FeatureConfig] = None,
) -> List[ClassificationResult]:
    """
    Predict modulation for multiple signals.

    Args:
        iq_signals: List of complex IQ signals
        sample_rates: List of sample rates
        model_path: Path to model file
        feature_config: Feature extraction configuration

    Returns:
        List of ClassificationResult
    """
    config = ClassifierConfig(model_path=model_path) if model_path else ClassifierConfig()
    classifier = ModulationClassifier(config)

    results = []
    for iq_data, sample_rate in zip(iq_signals, sample_rates):
        result = classifier.predict(iq_data, sample_rate, feature_config)
        results.append(result)

    return results


def predict_from_file(
    file_path: Path,
    model_path: Optional[str] = None,
    sample_rate: Optional[float] = None,
    **load_kwargs,
) -> ClassificationResult:
    """
    Predict modulation from a signal file.

    Args:
        file_path: Path to signal file
        model_path: Path to model file
        sample_rate: Sample rate (required for raw IQ)
        **load_kwargs: Additional arguments for file loading

    Returns:
        ClassificationResult
    """
    from ..io import load_wav, load_raw_iq, detect_file_type, FileType

    detection = detect_file_type(file_path)

    if detection.file_type == FileType.WAV:
        result = load_wav(file_path, **load_kwargs)
        iq_data = result.iq_data
        sample_rate = result.sample_rate
    elif detection.file_type == FileType.RAW_IQ:
        if sample_rate is None:
            raise ValueError("Sample rate required for raw IQ files")
        result = load_raw_iq(file_path, sample_rate=sample_rate, **load_kwargs)
        iq_data = result.iq_data
    else:
        raise ValueError(f"Unsupported file type: {detection.file_type}")

    return predict_single(iq_data, sample_rate, model_path)


def analyze_classification_confidence(
    results: List[ClassificationResult],
    confidence_threshold: float = 0.5,
) -> Dict[str, any]:
    """
    Analyze classification confidence across multiple predictions.

    Returns:
        Dictionary with confidence statistics
    """
    if not results:
        return {"error": "No results provided"}

    confidences = [r.confidence for r in results]
    predictions = [r.predicted_class for r in results]

    high_conf = [r for r in results if r.confidence >= confidence_threshold]
    low_conf = [r for r in results if r.confidence < confidence_threshold]

    # Class distribution
    class_dist = {}
    for pred in predictions:
        class_dist[pred.value] = class_dist.get(pred.value, 0) + 1

    return {
        "total_predictions": len(results),
        "high_confidence_count": len(high_conf),
        "low_confidence_count": len(low_conf),
        "mean_confidence": float(np.mean(confidences)),
        "std_confidence": float(np.std(confidences)),
        "min_confidence": float(np.min(confidences)),
        "max_confidence": float(np.max(confidences)),
        "class_distribution": class_dist,
        "low_confidence_samples": [
            {"predicted": r.predicted_class.value, "confidence": r.confidence}
            for r in low_conf
        ],
    }


def get_class_probabilities(
    result: ClassificationResult,
    top_k: int = 5,
) -> List[Tuple[ModulationType, float]]:
    """Get top-k class probabilities sorted by probability."""
    sorted_probs = sorted(
        result.probabilities.items(),
        key=lambda x: x[1],
        reverse=True,
    )
    return sorted_probs[:top_k]