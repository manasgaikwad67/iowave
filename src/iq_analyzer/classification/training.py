"""Model training module."""

import numpy as np
import joblib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from ..features import extract_features, FeatureConfig
from ..models import ModulationType
from ..utils import get_logger

logger = get_logger(__name__)


@dataclass
class TrainingConfig:
    """Configuration for model training."""

    model_type: str = "random_forest"  # random_forest, svm
    n_estimators: int = 200
    max_depth: int = 20
    min_samples_split: int = 5
    min_samples_leaf: int = 2
    random_state: int = 42
    test_size: float = 0.2
    cv_folds: int = 5
    feature_config: Optional[FeatureConfig] = None


@dataclass
class TrainingData:
    """Container for training data."""

    iq_signals: List[np.ndarray]
    labels: List[ModulationType]
    sample_rates: List[float]
    metadata: List[Dict[str, Any]]


def generate_training_data(
    dataset_path: Path,
    max_samples_per_class: Optional[int] = None,
) -> TrainingData:
    """
    Load training data from dataset directory.

    Expected structure:
    dataset_path/
        class_name/
            signal_1.iq
            signal_1.json (metadata)
            ...
    """
    iq_signals = []
    labels = []
    sample_rates = []
    metadata = []

    class_dirs = [d for d in dataset_path.iterdir() if d.is_dir()]

    for class_dir in class_dirs:
        try:
            mod_type = ModulationType(class_dir.name.upper())
        except ValueError:
            logger.warning(f"Unknown modulation class: {class_dir.name}")
            continue

        iq_files = list(class_dir.glob("*.iq")) + list(class_dir.glob("*.bin"))

        for iq_file in iq_files:
            if max_samples_per_class and len([l for l in labels if l == mod_type]) >= max_samples_per_class:
                break

            # Load metadata
            meta_file = iq_file.with_suffix(".json")
            meta = {}
            if meta_file.exists():
                import json
                with open(meta_file) as f:
                    meta = json.load(f)

            sample_rate = meta.get("sample_rate", 2048000)

            # Load IQ data
            from ..io import load_raw_iq
            try:
                result = load_raw_iq(
                    iq_file,
                    sample_rate=sample_rate,
                    dtype=meta.get("dtype", "int16"),
                    endianness=meta.get("endianness", "little"),
                    iq_layout=meta.get("iq_layout", "interleaved"),
                )
                iq_signals.append(result.iq_data)
                labels.append(mod_type)
                sample_rates.append(sample_rate)
                metadata.append(meta)
            except Exception as e:
                logger.warning(f"Failed to load {iq_file}: {e}")

    logger.info(f"Loaded {len(iq_signals)} training samples from {dataset_path}")
    return TrainingData(iq_signals, labels, sample_rates, metadata)


def extract_feature_matrix(
    training_data: TrainingData,
    feature_config: Optional[FeatureConfig] = None,
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Extract feature matrix from training data.

    Returns:
        Tuple of (X, y, feature_names)
    """
    if feature_config is None:
        feature_config = FeatureConfig()

    X = []
    y = []
    feature_names = None

    for iq_data, label, sample_rate in zip(
        training_data.iq_signals, training_data.labels, training_data.sample_rates
    ):
        features_dict = extract_features(iq_data, sample_rate, config=feature_config)

        if feature_names is None:
            feature_names = list(features_dict.keys())

        # Ensure consistent feature ordering
        feature_vector = [features_dict.get(name, 0.0) for name in feature_names]
        X.append(feature_vector)
        y.append(label.value)  # Use string value

    return np.array(X), np.array(y), feature_names


def train_model(
    X: np.ndarray,
    y: np.ndarray,
    config: Optional[TrainingConfig] = None,
) -> Tuple[Any, StandardScaler]:
    """
    Train modulation classification model.

    Returns:
        Tuple of (trained_model, scaler)
    """
    if config is None:
        config = TrainingConfig()

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Create model
    if config.model_type == "random_forest":
        model = RandomForestClassifier(
            n_estimators=config.n_estimators,
            max_depth=config.max_depth,
            min_samples_split=config.min_samples_split,
            min_samples_leaf=config.min_samples_leaf,
            random_state=config.random_state,
            n_jobs=-1,
            class_weight="balanced",
        )
    elif config.model_type == "svm":
        model = SVC(
            kernel="rbf",
            probability=True,
            class_weight="balanced",
            random_state=config.random_state,
        )
    else:
        raise ValueError(f"Unknown model type: {config.model_type}")

    # Train
    logger.info(f"Training {config.model_type} model on {X.shape[0]} samples...")
    model.fit(X_scaled, y)

    return model, scaler


def evaluate_model(
    model: Any,
    scaler: StandardScaler,
    X_test: np.ndarray,
    y_test: np.ndarray,
    class_names: List[str],
) -> Dict[str, Any]:
    """
    Evaluate trained model.

    Returns:
        Dictionary with evaluation metrics
    """
    X_test_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled) if hasattr(model, "predict_proba") else None

    # Classification report
    report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    # Per-class metrics
    per_class = {}
    for i, cls in enumerate(class_names):
        if cls in report:
            per_class[cls] = {
                "precision": report[cls]["precision"],
                "recall": report[cls]["recall"],
                "f1_score": report[cls]["f1-score"],
                "support": report[cls]["support"],
            }

    return {
        "accuracy": report["accuracy"],
        "macro_avg": report["macro avg"],
        "weighted_avg": report["weighted avg"],
        "per_class": per_class,
        "confusion_matrix": cm.tolist(),
        "class_names": class_names,
    }


def cross_validate_model(
    model: Any,
    scaler: StandardScaler,
    X: np.ndarray,
    y: np.ndarray,
    cv_folds: int = 5,
) -> Dict[str, float]:
    """Perform cross-validation."""
    X_scaled = scaler.transform(X)
    scores = cross_val_score(model, X_scaled, y, cv=cv_folds, scoring="accuracy")

    return {
        "cv_scores": scores.tolist(),
        "cv_mean": float(np.mean(scores)),
        "cv_std": float(np.std(scores)),
    }


def save_model(
    model: Any,
    scaler: StandardScaler,
    feature_names: List[str],
    classes: List[ModulationType],
    output_path: Path,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Save trained model with metadata."""
    model_data = {
        "model": model,
        "scaler": scaler,
        "feature_names": feature_names,
        "classes": [c.value for c in classes],
        "metadata": {
            "model_name": "modulation_classifier",
            "version": "1.0",
            "feature_version": "1.0",
            "training_date": datetime.now().isoformat(),
            "num_features": len(feature_names),
            "num_classes": len(classes),
            **(metadata or {}),
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model_data, output_path)
    logger.info(f"Model saved to {output_path}")


def run_training_pipeline(
    dataset_path: Path,
    output_path: Path,
    config: Optional[TrainingConfig] = None,
) -> Dict[str, Any]:
    """
    Run complete training pipeline.

    Returns:
        Dictionary with training results
    """
    if config is None:
        config = TrainingConfig()

    # Load data
    training_data = generate_training_data(dataset_path)

    if len(training_data.iq_signals) == 0:
        raise ValueError("No training data found")

    # Extract features
    X, y, feature_names = extract_feature_matrix(training_data, config.feature_config)

    # Get unique classes
    unique_classes = sorted(list(set(y)))
    class_enums = [ModulationType(c) for c in unique_classes]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.test_size, random_state=config.random_state, stratify=y
    )

    # Train
    model, scaler = train_model(X_train, y_train, config)

    # Evaluate
    eval_results = evaluate_model(model, scaler, X_test, y_test, unique_classes)

    # Cross-validation
    cv_results = cross_validate_model(model, scaler, X, y, config.cv_folds)

    # Save model
    save_model(
        model,
        scaler,
        feature_names,
        class_enums,
        output_path,
        metadata={
            "training_config": config.__dict__,
            "evaluation": eval_results,
            "cross_validation": cv_results,
        },
    )

    return {
        "model_path": str(output_path),
        "num_samples": len(X),
        "num_features": len(feature_names),
        "num_classes": len(unique_classes),
        "classes": unique_classes,
        "evaluation": eval_results,
        "cross_validation": cv_results,
    }