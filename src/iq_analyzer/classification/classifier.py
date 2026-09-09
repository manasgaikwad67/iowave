"""Modulation classification module."""

import numpy as np
import joblib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from ..models import ClassificationResult, ModulationType
from ..features import extract_features, FeatureConfig
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class ClassifierConfig:
    """Configuration for classifier."""

    model_path: str = "models/trained/modulation_classifier.joblib"
    feature_version: str = "1.0"
    confidence_threshold: float = 0.5
    top_k: int = 3
    enabled: bool = True


class ModulationClassifier:
    """Modulation classifier using scikit-learn models."""

    def __init__(self, config: Optional[ClassifierConfig] = None):
        self.config = config or ClassifierConfig()
        self.model = None
        self.scaler = None
        self.classes: List[ModulationType] = []
        self.feature_names: List[str] = []
        self.model_metadata: Dict[str, Any] = {}

    def load_model(self, model_path: Optional[str] = None) -> bool:
        """Load trained model from file."""
        path = model_path or self.config.model_path

        try:
            model_data = joblib.load(path)

            # Handle different model formats
            if isinstance(model_data, dict):
                self.model = model_data.get("model")
                self.scaler = model_data.get("scaler")
                self.classes = model_data.get("classes", [])
                self.feature_names = model_data.get("feature_names", [])
                self.model_metadata = model_data.get("metadata", {})
            else:
                # Assume it's just the model
                self.model = model_data
                self.classes = list(ModulationType)

            # Convert class strings to ModulationType enum
            if self.classes and isinstance(self.classes[0], str):
                self.classes = [ModulationType(c) for c in self.classes]

            logger.info(f"Loaded model from {path}")
            logger.info(f"Model classes: {[c.value for c in self.classes]}")
            return True

        except FileNotFoundError:
            logger.warning(f"Model file not found: {path}")
            return False
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def predict(
        self,
        iq_data: np.ndarray,
        sample_rate: float,
        feature_config: Optional[FeatureConfig] = None,
    ) -> ClassificationResult:
        """
        Predict modulation type for IQ signal.

        Args:
            iq_data: Complex IQ signal
            sample_rate: Sample rate in Hz
            feature_config: Feature extraction configuration

        Returns:
            ClassificationResult
        """
        if not self.config.enabled:
            return ClassificationResult(
                predicted_class=ModulationType.UNKNOWN,
                confidence=0.0,
                probabilities={},
                model_name="disabled",
                model_version="0.0",
                feature_version=self.config.feature_version,
                features_used=[],
                warnings=["Classification disabled in configuration"],
            )

        if self.model is None:
            loaded = self.load_model()
            if not loaded:
                return ClassificationResult(
                    predicted_class=ModulationType.UNKNOWN,
                    confidence=0.0,
                    probabilities={},
                    model_name="none",
                    model_version="0.0",
                    feature_version=self.config.feature_version,
                    features_used=[],
                    warnings=["No model loaded"],
                )

        # Extract features
        features_dict = extract_features(iq_data, sample_rate, config=feature_config)
        feature_vector = np.array([features_dict.get(name, 0.0) for name in self.feature_names]).reshape(1, -1)

        # Scale features
        if self.scaler is not None:
            feature_vector = self.scaler.transform(feature_vector)

        # Predict
        try:
            pred_idx = self.model.predict(feature_vector)[0]
            probabilities = self.model.predict_proba(feature_vector)[0]
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return ClassificationResult(
                predicted_class=ModulationType.UNKNOWN,
                confidence=0.0,
                probabilities={},
                model_name=self.model_metadata.get("model_name", "unknown"),
                model_version=self.model_metadata.get("version", "0.0"),
                feature_version=self.config.feature_version,
                features_used=self.feature_names,
                warnings=[f"Prediction error: {e}"],
            )

        # Map prediction to ModulationType
        if pred_idx < len(self.classes):
            predicted_class = self.classes[pred_idx]
        else:
            predicted_class = ModulationType.UNKNOWN

        # Build probability dict
        prob_dict = {}
        for i, cls in enumerate(self.classes):
            if i < len(probabilities):
                prob_dict[cls] = float(probabilities[i])
            else:
                prob_dict[cls] = 0.0

        confidence = float(probabilities[pred_idx]) if pred_idx < len(probabilities) else 0.0

        # Check confidence threshold
        warnings = []
        if confidence < self.config.confidence_threshold:
            warnings.append(f"Low confidence: {confidence:.2f} < {self.config.confidence_threshold}")

        return ClassificationResult(
            predicted_class=predicted_class,
            confidence=confidence,
            probabilities=prob_dict,
            model_name=self.model_metadata.get("model_name", "sklearn_model"),
            model_version=self.model_metadata.get("version", "1.0"),
            feature_version=self.config.feature_version,
            features_used=self.feature_names,
            warnings=warnings,
        )

    def get_top_k_predictions(
        self,
        iq_data: np.ndarray,
        sample_rate: float,
        k: int = None,
    ) -> List[tuple]:
        """Get top-k predictions with probabilities."""
        result = self.predict(iq_data, sample_rate)

        # Sort by probability
        sorted_probs = sorted(
            result.probabilities.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        k = k or self.config.top_k
        return sorted_probs[:k]


def create_default_classifier() -> ModulationClassifier:
    """Create a classifier with default configuration."""
    return ModulationClassifier()